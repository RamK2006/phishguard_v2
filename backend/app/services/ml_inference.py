import lightgbm as lgb
import torch
from transformers import DistilBertTokenizer, DistilBertModel
import numpy as np
from typing import Dict, Any, Tuple
import os
from ..core.config import settings


class MLInferenceService:
    """ML inference service for phishing detection"""
    
    def __init__(self):
        self.lgb_model = None
        self.bert_tokenizer = None
        self.bert_model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._load_models()
    
    def _load_models(self):
        """Load LightGBM and DistilBERT models"""
        # Load LightGBM model
        lgb_model_path = os.path.join(settings.ML_MODEL_PATH, 'lightgbm_model.txt')
        if os.path.exists(lgb_model_path):
            self.lgb_model = lgb.Booster(model_file=lgb_model_path)
        else:
            print(f"Warning: LightGBM model not found at {lgb_model_path}")
        
        # Load DistilBERT model
        try:
            self.bert_tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
            self.bert_model = DistilBertModel.from_pretrained('distilbert-base-uncased')
            self.bert_model.to(self.device)
            self.bert_model.eval()
        except Exception as e:
            print(f"Warning: Failed to load DistilBERT model: {e}")
    
    def predict(self, url: str, features: Dict[str, float]) -> Tuple[float, bool, float, Dict[str, Any]]:
        """
        Predict if URL is phishing
        
        Returns:
            - phishing_score: 0-1 probability
            - is_phishing: boolean classification
            - confidence: confidence score
            - ml_features: additional ML features
        """
        # Extract feature vector for LightGBM
        feature_vector = self._prepare_feature_vector(features)
        
        # Get LightGBM prediction
        lgb_score = 0.5  # Default
        if self.lgb_model:
            lgb_pred = self.lgb_model.predict([feature_vector])[0]
            lgb_score = float(lgb_pred)
        
        # Get BERT embedding and score
        bert_score = 0.5  # Default
        bert_embedding = None
        if self.bert_model and self.bert_tokenizer:
            bert_score, bert_embedding = self._get_bert_score(url)
        
        # Ensemble: weighted average
        phishing_score = 0.7 * lgb_score + 0.3 * bert_score
        
        # Classification with threshold
        threshold = 0.5
        is_phishing = phishing_score >= threshold
        
        # Calculate confidence
        confidence = abs(phishing_score - threshold) / threshold
        confidence = min(confidence, 1.0)
        
        ml_features = {
            'lgb_score': lgb_score,
            'bert_score': bert_score,
            'ensemble_score': phishing_score,
            'bert_embedding': bert_embedding.tolist() if bert_embedding is not None else None
        }
        
        return phishing_score, is_phishing, confidence, ml_features
    
    def _prepare_feature_vector(self, features: Dict[str, float]) -> list:
        """Prepare feature vector for LightGBM"""
        # Expected feature order (47 features)
        feature_names = [
            'url_length', 'domain_length', 'path_length', 'query_length', 'fragment_length',
            'hostname_length', 'subdomain_length', 'tld_length', 'num_subdomains', 'num_path_segments',
            'num_dots', 'num_hyphens', 'num_underscores', 'num_slashes', 'num_question_marks',
            'num_ampersands', 'num_equals', 'num_at_symbols', 'num_digits', 'num_special_chars',
            'digit_ratio', 'special_char_ratio', 'uppercase_ratio', 'lowercase_ratio', 'letter_ratio',
            'has_ip_address', 'has_suspicious_tld', 'has_suspicious_keywords', 'has_punycode', 'has_port',
            'has_https', 'has_www', 'has_shortening_service', 'has_redirect', 'has_double_slash_in_path',
            'num_query_params', 'has_url_in_query', 'max_query_param_length', 'avg_query_param_length',
            'has_suspicious_query_params', 'domain_entropy', 'path_entropy', 'url_entropy',
            'consonant_vowel_ratio', 'longest_word_length', 'has_brand_name', 'brand_name_position'
        ]
        
        return [features.get(name, 0.0) for name in feature_names]
    
    def _get_bert_score(self, url: str) -> Tuple[float, np.ndarray]:
        """Get BERT-based phishing score and embedding"""
        try:
            # Tokenize URL
            inputs = self.bert_tokenizer(
                url,
                return_tensors='pt',
                truncation=True,
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get BERT embeddings
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                # Use [CLS] token embedding
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
            
            # Simple heuristic: calculate score based on embedding statistics
            # In production, this would be a trained classifier on top of BERT
            embedding_mean = np.mean(embedding)
            embedding_std = np.std(embedding)
            
            # Normalize to 0-1 range (simple heuristic)
            score = 1 / (1 + np.exp(-embedding_mean))
            
            return float(score), embedding
            
        except Exception as e:
            print(f"BERT inference error: {e}")
            return 0.5, np.zeros(768)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from LightGBM model"""
        if not self.lgb_model:
            return {}
        
        importance = self.lgb_model.feature_importance(importance_type='gain')
        feature_names = [
            'url_length', 'domain_length', 'path_length', 'query_length', 'fragment_length',
            'hostname_length', 'subdomain_length', 'tld_length', 'num_subdomains', 'num_path_segments',
            'num_dots', 'num_hyphens', 'num_underscores', 'num_slashes', 'num_question_marks',
            'num_ampersands', 'num_equals', 'num_at_symbols', 'num_digits', 'num_special_chars',
            'digit_ratio', 'special_char_ratio', 'uppercase_ratio', 'lowercase_ratio', 'letter_ratio',
            'has_ip_address', 'has_suspicious_tld', 'has_suspicious_keywords', 'has_punycode', 'has_port',
            'has_https', 'has_www', 'has_shortening_service', 'has_redirect', 'has_double_slash_in_path',
            'num_query_params', 'has_url_in_query', 'max_query_param_length', 'avg_query_param_length',
            'has_suspicious_query_params', 'domain_entropy', 'path_entropy', 'url_entropy',
            'consonant_vowel_ratio', 'longest_word_length', 'has_brand_name', 'brand_name_position'
        ]
        
        return dict(zip(feature_names, importance.tolist()))


# Global instance
ml_service = MLInferenceService()

import httpx
from typing import Dict, Any, List
from ..core.config import settings


class LLMExplainerService:
    """LLM-based explanation service using Groq API"""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = "llama-3.1-70b-versatile"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.timeout = 30.0
    
    async def generate_explanation(
        self,
        url: str,
        phishing_score: float,
        is_phishing: bool,
        features: Dict[str, Any],
        threat_intel: Dict[str, Any],
        visual_similarity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate human-readable explanation of phishing detection"""
        
        if not self.api_key:
            return {
                'available': False,
                'reason': 'Groq API key not configured'
            }
        
        try:
            # Build context for LLM
            context = self._build_context(
                url, phishing_score, is_phishing, features, threat_intel, visual_similarity
            )
            
            # Create prompt
            prompt = self._create_prompt(context)
            
            # Call Groq API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': self.model,
                        'messages': [
                            {
                                'role': 'system',
                                'content': 'You are a cybersecurity expert explaining phishing detection results to users. Be clear, concise, and actionable.'
                            },
                            {
                                'role': 'user',
                                'content': prompt
                            }
                        ],
                        'temperature': 0.3,
                        'max_tokens': 500
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    explanation = data['choices'][0]['message']['content']
                    
                    # Extract risk factors
                    risk_factors = self._extract_risk_factors(features, threat_intel, visual_similarity)
                    
                    return {
                        'available': True,
                        'explanation': explanation,
                        'risk_factors': risk_factors,
                        'recommendation': self._get_recommendation(is_phishing, phishing_score)
                    }
                else:
                    return {
                        'available': False,
                        'error': f'API returned status {response.status_code}'
                    }
                    
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def _build_context(
        self,
        url: str,
        phishing_score: float,
        is_phishing: bool,
        features: Dict[str, Any],
        threat_intel: Dict[str, Any],
        visual_similarity: Dict[str, Any]
    ) -> str:
        """Build context string for LLM"""
        context_parts = [
            f"URL: {url}",
            f"Phishing Score: {phishing_score:.2f}",
            f"Classification: {'PHISHING' if is_phishing else 'SAFE'}",
            "",
            "Key Features:"
        ]
        
        # Add suspicious features
        if features.get('has_ip_address'):
            context_parts.append("- URL uses IP address instead of domain name")
        if features.get('has_suspicious_tld'):
            context_parts.append("- URL uses suspicious top-level domain")
        if features.get('has_suspicious_keywords'):
            context_parts.append("- URL contains suspicious keywords (login, verify, account, etc.)")
        if not features.get('has_https'):
            context_parts.append("- URL does not use HTTPS")
        if features.get('has_shortening_service'):
            context_parts.append("- URL uses URL shortening service")
        if features.get('url_length', 0) > 100:
            context_parts.append(f"- URL is unusually long ({features['url_length']} characters)")
        if features.get('domain_entropy', 0) > 4.0:
            context_parts.append("- Domain has high entropy (random-looking)")
        if features.get('has_brand_name'):
            context_parts.append("- URL contains brand name (possible impersonation)")
        
        # Add threat intelligence
        context_parts.append("")
        context_parts.append("Threat Intelligence:")
        
        vt_data = threat_intel.get('virustotal', {})
        if vt_data.get('available') and vt_data.get('is_malicious'):
            context_parts.append(f"- VirusTotal: {vt_data.get('malicious_count', 0)} engines flagged as malicious")
        
        urlhaus_data = threat_intel.get('urlhaus', {})
        if urlhaus_data.get('listed'):
            context_parts.append(f"- URLhaus: Listed as {urlhaus_data.get('threat', 'threat')}")
        
        abuseipdb_data = threat_intel.get('abuseipdb', {})
        if abuseipdb_data.get('is_malicious'):
            context_parts.append(f"- AbuseIPDB: Abuse score {abuseipdb_data.get('abuse_score', 0)}")
        
        # Add visual similarity
        if visual_similarity.get('has_match'):
            context_parts.append("")
            context_parts.append("Visual Similarity:")
            context_parts.append(f"- Matches {visual_similarity.get('matched_brand')} with {visual_similarity.get('similarity_score', 0):.2%} similarity")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, context: str) -> str:
        """Create prompt for LLM"""
        return f"""Analyze this phishing detection result and provide a clear, concise explanation for the user.

{context}

Provide:
1. A brief summary of whether this URL is safe or dangerous
2. The main reasons for this classification
3. Specific risks the user should be aware of
4. What action the user should take

Keep the explanation under 150 words and use simple language."""
    
    def _extract_risk_factors(
        self,
        features: Dict[str, Any],
        threat_intel: Dict[str, Any],
        visual_similarity: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract structured risk factors"""
        risk_factors = []
        
        # URL structure risks
        if features.get('has_ip_address'):
            risk_factors.append({
                'category': 'URL Structure',
                'risk': 'IP Address Used',
                'severity': 'high',
                'description': 'Legitimate sites rarely use IP addresses'
            })
        
        if not features.get('has_https'):
            risk_factors.append({
                'category': 'Security',
                'risk': 'No HTTPS',
                'severity': 'medium',
                'description': 'Connection is not encrypted'
            })
        
        if features.get('has_suspicious_keywords'):
            risk_factors.append({
                'category': 'Content',
                'risk': 'Suspicious Keywords',
                'severity': 'high',
                'description': 'URL contains phishing-related keywords'
            })
        
        if features.get('has_brand_name'):
            risk_factors.append({
                'category': 'Impersonation',
                'risk': 'Brand Name Detected',
                'severity': 'high',
                'description': 'Possible brand impersonation attempt'
            })
        
        # Threat intelligence risks
        vt_data = threat_intel.get('virustotal', {})
        if vt_data.get('is_malicious'):
            risk_factors.append({
                'category': 'Threat Intelligence',
                'risk': 'Known Malicious',
                'severity': 'critical',
                'description': f"Flagged by {vt_data.get('malicious_count', 0)} security vendors"
            })
        
        urlhaus_data = threat_intel.get('urlhaus', {})
        if urlhaus_data.get('listed'):
            risk_factors.append({
                'category': 'Threat Intelligence',
                'risk': 'Listed in URLhaus',
                'severity': 'critical',
                'description': 'Known malicious URL database listing'
            })
        
        # Visual similarity risks
        if visual_similarity.get('has_match'):
            risk_factors.append({
                'category': 'Visual Similarity',
                'risk': 'Brand Impersonation',
                'severity': 'critical',
                'description': f"Visually similar to {visual_similarity.get('matched_brand')}"
            })
        
        return risk_factors
    
    def _get_recommendation(self, is_phishing: bool, phishing_score: float) -> str:
        """Get action recommendation"""
        if is_phishing:
            if phishing_score > 0.8:
                return "🚨 DO NOT VISIT - This URL is highly likely to be a phishing attempt. Close this page immediately and do not enter any personal information."
            else:
                return "⚠️ CAUTION - This URL shows signs of phishing. Avoid entering sensitive information and verify the URL carefully."
        else:
            if phishing_score < 0.2:
                return "✅ SAFE - This URL appears to be legitimate. However, always verify URLs before entering sensitive information."
            else:
                return "⚡ PROCEED WITH CAUTION - This URL appears safe but has some suspicious characteristics. Verify before entering sensitive data."


# Global instance
llm_explainer_service = LLMExplainerService()

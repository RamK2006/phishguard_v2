import re
import tldextract
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any
import ipaddress
import math
from collections import Counter


class URLFeatureExtractor:
    """Extract 47 features from URL for phishing detection"""
    
    SUSPICIOUS_KEYWORDS = [
        'login', 'signin', 'account', 'verify', 'secure', 'update', 'confirm',
        'banking', 'paypal', 'ebay', 'amazon', 'apple', 'microsoft', 'google',
        'password', 'suspended', 'locked', 'unusual', 'activity', 'click'
    ]
    
    SUSPICIOUS_TLDS = [
        '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work', '.click',
        '.link', '.download', '.stream', '.racing', '.bid', '.win'
    ]
    
    def extract_features(self, url: str) -> Dict[str, Any]:
        """Extract all 47 features from URL"""
        parsed = urlparse(url)
        extracted = tldextract.extract(url)
        
        features = {}
        
        # 1-10: URL Length Features
        features['url_length'] = len(url)
        features['domain_length'] = len(extracted.domain)
        features['path_length'] = len(parsed.path)
        features['query_length'] = len(parsed.query) if parsed.query else 0
        features['fragment_length'] = len(parsed.fragment) if parsed.fragment else 0
        features['hostname_length'] = len(parsed.netloc)
        features['subdomain_length'] = len(extracted.subdomain) if extracted.subdomain else 0
        features['tld_length'] = len(extracted.suffix)
        features['num_subdomains'] = len(extracted.subdomain.split('.')) if extracted.subdomain else 0
        features['num_path_segments'] = len([p for p in parsed.path.split('/') if p])
        
        # 11-20: Character Count Features
        features['num_dots'] = url.count('.')
        features['num_hyphens'] = url.count('-')
        features['num_underscores'] = url.count('_')
        features['num_slashes'] = url.count('/')
        features['num_question_marks'] = url.count('?')
        features['num_ampersands'] = url.count('&')
        features['num_equals'] = url.count('=')
        features['num_at_symbols'] = url.count('@')
        features['num_digits'] = sum(c.isdigit() for c in url)
        features['num_special_chars'] = sum(not c.isalnum() and c not in '/:.-_?&=' for c in url)
        
        # 21-25: Ratio Features
        total_chars = len(url) if len(url) > 0 else 1
        features['digit_ratio'] = features['num_digits'] / total_chars
        features['special_char_ratio'] = features['num_special_chars'] / total_chars
        features['uppercase_ratio'] = sum(c.isupper() for c in url) / total_chars
        features['lowercase_ratio'] = sum(c.islower() for c in url) / total_chars
        features['letter_ratio'] = sum(c.isalpha() for c in url) / total_chars
        
        # 26-30: Suspicious Pattern Features
        features['has_ip_address'] = int(self._has_ip_address(parsed.netloc))
        features['has_suspicious_tld'] = int(any(url.endswith(tld) for tld in self.SUSPICIOUS_TLDS))
        features['has_suspicious_keywords'] = int(any(kw in url.lower() for kw in self.SUSPICIOUS_KEYWORDS))
        features['has_punycode'] = int('xn--' in url.lower())
        features['has_port'] = int(bool(parsed.port))
        
        # 31-35: URL Structure Features
        features['has_https'] = int(parsed.scheme == 'https')
        features['has_www'] = int('www' in extracted.subdomain.lower())
        features['has_shortening_service'] = int(self._is_shortening_service(extracted.domain))
        features['has_redirect'] = int('redirect' in url.lower() or 'redir' in url.lower())
        features['has_double_slash_in_path'] = int('//' in parsed.path)
        
        # 36-40: Query Parameter Features
        query_params = parse_qs(parsed.query)
        features['num_query_params'] = len(query_params)
        features['has_url_in_query'] = int(any('http' in str(v) for v in query_params.values()))
        features['max_query_param_length'] = max([len(str(v)) for v in query_params.values()], default=0)
        features['avg_query_param_length'] = sum([len(str(v)) for v in query_params.values()]) / len(query_params) if query_params else 0
        features['has_suspicious_query_params'] = int(any(kw in parsed.query.lower() for kw in ['login', 'verify', 'account', 'password']))
        
        # 41-45: Entropy and Complexity Features
        features['domain_entropy'] = self._calculate_entropy(extracted.domain)
        features['path_entropy'] = self._calculate_entropy(parsed.path) if parsed.path else 0
        features['url_entropy'] = self._calculate_entropy(url)
        features['consonant_vowel_ratio'] = self._consonant_vowel_ratio(extracted.domain)
        features['longest_word_length'] = self._longest_word_length(url)
        
        # 46-47: Brand Impersonation Features
        features['has_brand_name'] = int(self._has_brand_name(url))
        features['brand_name_position'] = self._brand_name_position(url)
        
        return features
    
    def _has_ip_address(self, netloc: str) -> bool:
        """Check if netloc is an IP address"""
        try:
            # Remove port if present
            host = netloc.split(':')[0]
            ipaddress.ip_address(host)
            return True
        except ValueError:
            return False
    
    def _is_shortening_service(self, domain: str) -> bool:
        """Check if domain is a URL shortening service"""
        shorteners = [
            'bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'is.gd',
            'buff.ly', 'adf.ly', 'bit.do', 'short.link', 'tiny.cc'
        ]
        return domain.lower() in shorteners
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0
        
        counter = Counter(text)
        length = len(text)
        entropy = 0.0
        
        for count in counter.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _consonant_vowel_ratio(self, text: str) -> float:
        """Calculate ratio of consonants to vowels"""
        vowels = 'aeiou'
        text_lower = text.lower()
        
        num_vowels = sum(1 for c in text_lower if c in vowels)
        num_consonants = sum(1 for c in text_lower if c.isalpha() and c not in vowels)
        
        if num_vowels == 0:
            return float(num_consonants)
        
        return num_consonants / num_vowels
    
    def _longest_word_length(self, url: str) -> int:
        """Find longest word in URL"""
        words = re.findall(r'[a-zA-Z]+', url)
        return max([len(w) for w in words], default=0)
    
    def _has_brand_name(self, url: str) -> bool:
        """Check if URL contains popular brand names"""
        brands = [
            'paypal', 'amazon', 'apple', 'microsoft', 'google', 'facebook',
            'netflix', 'ebay', 'instagram', 'twitter', 'linkedin', 'dropbox',
            'chase', 'wellsfargo', 'bankofamerica', 'citibank', 'usbank'
        ]
        url_lower = url.lower()
        return any(brand in url_lower for brand in brands)
    
    def _brand_name_position(self, url: str) -> float:
        """Get position of brand name in URL (0-1, -1 if not found)"""
        brands = [
            'paypal', 'amazon', 'apple', 'microsoft', 'google', 'facebook',
            'netflix', 'ebay', 'instagram', 'twitter', 'linkedin', 'dropbox',
            'chase', 'wellsfargo', 'bankofamerica', 'citibank', 'usbank'
        ]
        url_lower = url.lower()
        
        for brand in brands:
            if brand in url_lower:
                position = url_lower.index(brand)
                return position / len(url_lower)
        
        return -1.0

import httpx
import asyncio
from typing import Dict, Any, Optional
from ..core.config import settings
import hashlib


class ThreatIntelService:
    """Threat intelligence service integrating multiple CTI APIs"""
    
    def __init__(self):
        self.virustotal_api_key = settings.VIRUSTOTAL_API_KEY
        self.abuseipdb_api_key = settings.ABUSEIPDB_API_KEY
        self.timeout = 10.0
    
    async def check_url(self, url: str, domain: str) -> Dict[str, Any]:
        """Check URL against multiple threat intelligence sources"""
        results = await asyncio.gather(
            self._check_virustotal(url),
            self._check_urlhaus(url),
            self._check_abuseipdb(domain),
            return_exceptions=True
        )
        
        virustotal_data, urlhaus_data, abuseipdb_data = results
        
        # Handle exceptions
        if isinstance(virustotal_data, Exception):
            virustotal_data = {'error': str(virustotal_data)}
        if isinstance(urlhaus_data, Exception):
            urlhaus_data = {'error': str(urlhaus_data)}
        if isinstance(abuseipdb_data, Exception):
            abuseipdb_data = {'error': str(abuseipdb_data)}
        
        # Aggregate results
        threat_intel = {
            'virustotal': virustotal_data,
            'urlhaus': urlhaus_data,
            'abuseipdb': abuseipdb_data,
            'aggregate_score': self._calculate_aggregate_score(
                virustotal_data, urlhaus_data, abuseipdb_data
            )
        }
        
        return threat_intel
    
    async def _check_virustotal(self, url: str) -> Dict[str, Any]:
        """Check URL against VirusTotal API"""
        if not self.virustotal_api_key:
            return {'available': False, 'reason': 'API key not configured'}
        
        try:
            # URL ID for VirusTotal is base64 encoded URL
            url_id = hashlib.sha256(url.encode()).hexdigest()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # First, submit URL for scanning
                response = await client.post(
                    'https://www.virustotal.com/api/v3/urls',
                    headers={'x-apikey': self.virustotal_api_key},
                    data={'url': url}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    analysis_id = data.get('data', {}).get('id')
                    
                    # Get analysis results
                    if analysis_id:
                        analysis_response = await client.get(
                            f'https://www.virustotal.com/api/v3/analyses/{analysis_id}',
                            headers={'x-apikey': self.virustotal_api_key}
                        )
                        
                        if analysis_response.status_code == 200:
                            analysis_data = analysis_response.json()
                            stats = analysis_data.get('data', {}).get('attributes', {}).get('stats', {})
                            
                            malicious = stats.get('malicious', 0)
                            suspicious = stats.get('suspicious', 0)
                            total = sum(stats.values())
                            
                            return {
                                'available': True,
                                'malicious_count': malicious,
                                'suspicious_count': suspicious,
                                'total_scans': total,
                                'score': malicious + suspicious,
                                'is_malicious': malicious > 0,
                                'stats': stats
                            }
                
                return {'available': True, 'score': 0, 'is_malicious': False}
                
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    async def _check_urlhaus(self, url: str) -> Dict[str, Any]:
        """Check URL against URLhaus database"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    'https://urlhaus-api.abuse.ch/v1/url/',
                    data={'url': url}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('query_status') == 'ok':
                        return {
                            'available': True,
                            'listed': True,
                            'threat': data.get('threat'),
                            'tags': data.get('tags', []),
                            'url_status': data.get('url_status'),
                            'date_added': data.get('date_added')
                        }
                    else:
                        return {
                            'available': True,
                            'listed': False
                        }
                
                return {'available': False, 'error': 'API request failed'}
                
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    async def _check_abuseipdb(self, domain: str) -> Dict[str, Any]:
        """Check domain/IP against AbuseIPDB"""
        if not self.abuseipdb_api_key:
            return {'available': False, 'reason': 'API key not configured'}
        
        try:
            # Try to resolve domain to IP
            import socket
            try:
                ip_address = socket.gethostbyname(domain)
            except:
                return {'available': True, 'score': 0, 'is_malicious': False, 'reason': 'Could not resolve domain'}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    'https://api.abuseipdb.com/api/v2/check',
                    headers={
                        'Key': self.abuseipdb_api_key,
                        'Accept': 'application/json'
                    },
                    params={
                        'ipAddress': ip_address,
                        'maxAgeInDays': 90
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ip_data = data.get('data', {})
                    
                    abuse_score = ip_data.get('abuseConfidenceScore', 0)
                    total_reports = ip_data.get('totalReports', 0)
                    
                    return {
                        'available': True,
                        'ip_address': ip_address,
                        'abuse_score': abuse_score,
                        'total_reports': total_reports,
                        'is_malicious': abuse_score > 50,
                        'country': ip_data.get('countryCode'),
                        'usage_type': ip_data.get('usageType')
                    }
                
                return {'available': False, 'error': 'API request failed'}
                
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    def _calculate_aggregate_score(
        self,
        virustotal_data: Dict[str, Any],
        urlhaus_data: Dict[str, Any],
        abuseipdb_data: Dict[str, Any]
    ) -> float:
        """Calculate aggregate threat score from all sources (0-100)"""
        score = 0.0
        weight_sum = 0.0
        
        # VirusTotal (weight: 0.5)
        if virustotal_data.get('available') and not virustotal_data.get('error'):
            vt_score = virustotal_data.get('score', 0)
            total_scans = virustotal_data.get('total_scans', 1)
            normalized_score = (vt_score / max(total_scans, 1)) * 100
            score += normalized_score * 0.5
            weight_sum += 0.5
        
        # URLhaus (weight: 0.3)
        if urlhaus_data.get('available') and not urlhaus_data.get('error'):
            if urlhaus_data.get('listed'):
                score += 100 * 0.3
            weight_sum += 0.3
        
        # AbuseIPDB (weight: 0.2)
        if abuseipdb_data.get('available') and not abuseipdb_data.get('error'):
            abuse_score = abuseipdb_data.get('abuse_score', 0)
            score += abuse_score * 0.2
            weight_sum += 0.2
        
        # Normalize by actual weights used
        if weight_sum > 0:
            return score / weight_sum
        
        return 0.0


# Global instance
threat_intel_service = ThreatIntelService()

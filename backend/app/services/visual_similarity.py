import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import Dict, Any, List, Optional, Tuple
import hashlib
from PIL import Image
import imagehash
from io import BytesIO
from ..core.config import settings


class VisualSimilarityService:
    """Visual similarity service using Qdrant and perceptual hashing"""
    
    def __init__(self):
        self.qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.collection_name = "brand_screenshots"
        self.timeout = 15.0
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure Qdrant collection exists"""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                # Create collection with 64-dim vectors (perceptual hash)
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=64, distance=Distance.COSINE)
                )
        except Exception as e:
            print(f"Error ensuring Qdrant collection: {e}")
    
    async def check_visual_similarity(self, url: str, screenshot_url: Optional[str] = None) -> Dict[str, Any]:
        """Check visual similarity against known brand pages"""
        try:
            # If no screenshot provided, try to capture one
            if not screenshot_url:
                screenshot_data = await self._capture_screenshot(url)
                if not screenshot_data:
                    return {
                        'available': False,
                        'reason': 'Could not capture screenshot'
                    }
            else:
                screenshot_data = await self._download_image(screenshot_url)
            
            # Calculate perceptual hash
            phash = self._calculate_perceptual_hash(screenshot_data)
            if not phash:
                return {
                    'available': False,
                    'reason': 'Could not calculate perceptual hash'
                }
            
            # Convert hash to vector
            hash_vector = self._hash_to_vector(phash)
            
            # Search for similar screenshots in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=hash_vector,
                limit=5,
                score_threshold=0.85  # High similarity threshold
            )
            
            if search_results:
                best_match = search_results[0]
                
                return {
                    'available': True,
                    'has_match': True,
                    'matched_brand': best_match.payload.get('brand'),
                    'similarity_score': best_match.score,
                    'matched_url': best_match.payload.get('url'),
                    'all_matches': [
                        {
                            'brand': r.payload.get('brand'),
                            'score': r.score,
                            'url': r.payload.get('url')
                        }
                        for r in search_results
                    ]
                }
            else:
                return {
                    'available': True,
                    'has_match': False,
                    'similarity_score': 0.0
                }
                
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    async def _capture_screenshot(self, url: str) -> Optional[bytes]:
        """Capture screenshot of URL (placeholder - would use Playwright/Selenium)"""
        # In production, use Playwright or Selenium to capture screenshots
        # For now, return None to indicate screenshot capture not available
        return None
    
    async def _download_image(self, image_url: str) -> Optional[bytes]:
        """Download image from URL"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(image_url)
                if response.status_code == 200:
                    return response.content
        except Exception as e:
            print(f"Error downloading image: {e}")
        return None
    
    def _calculate_perceptual_hash(self, image_data: bytes) -> Optional[imagehash.ImageHash]:
        """Calculate perceptual hash of image"""
        try:
            image = Image.open(BytesIO(image_data))
            # Use average hash (fast and effective)
            phash = imagehash.average_hash(image, hash_size=8)
            return phash
        except Exception as e:
            print(f"Error calculating perceptual hash: {e}")
            return None
    
    def _hash_to_vector(self, phash: imagehash.ImageHash) -> List[float]:
        """Convert perceptual hash to vector for Qdrant"""
        # Convert hash to binary string, then to vector
        hash_array = phash.hash.flatten()
        # Normalize to 0-1 range
        vector = [float(x) for x in hash_array]
        return vector
    
    def add_brand_screenshot(
        self,
        brand: str,
        url: str,
        screenshot_data: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add brand screenshot to Qdrant collection"""
        try:
            phash = self._calculate_perceptual_hash(screenshot_data)
            if not phash:
                return False
            
            hash_vector = self._hash_to_vector(phash)
            point_id = hashlib.md5(f"{brand}:{url}".encode()).hexdigest()
            
            payload = {
                'brand': brand,
                'url': url,
                'hash': str(phash),
                **(metadata or {})
            }
            
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=hash_vector,
                        payload=payload
                    )
                ]
            )
            
            return True
            
        except Exception as e:
            print(f"Error adding brand screenshot: {e}")
            return False
    
    def seed_brand_database(self):
        """Seed database with known brand screenshots"""
        # In production, this would load screenshots of legitimate brand pages
        # For now, this is a placeholder
        brands = [
            {'brand': 'PayPal', 'url': 'https://www.paypal.com'},
            {'brand': 'Amazon', 'url': 'https://www.amazon.com'},
            {'brand': 'Apple', 'url': 'https://www.apple.com'},
            {'brand': 'Microsoft', 'url': 'https://www.microsoft.com'},
            {'brand': 'Google', 'url': 'https://www.google.com'},
        ]
        
        print(f"Brand database seeding would add {len(brands)} brands")
        # Implementation would capture and store screenshots


# Global instance
visual_similarity_service = VisualSimilarityService()

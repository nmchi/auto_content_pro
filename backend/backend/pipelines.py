"""
Scrapy Pipelines - V3 Universal System ONLY
Clean version - No V1, No V2, Only V3

File: backend/backend/pipelines.py
"""

import os
import requests
import json
import time
from google import genai
from google.genai import types
from scrapy.exceptions import DropItem

# V3: Universal Intelligent Generator (ONLY)
try:
    from backend.universal_intelligent_generator import UniversalIntelligentGenerator
    V3_AVAILABLE = True
except ImportError:
    try:
        from universal_intelligent_generator import UniversalIntelligentGenerator
        V3_AVAILABLE = True
    except ImportError:
        V3_AVAILABLE = False
        print("⚠️ V3 Universal Generator not found!")


class AiGenerationPipeline:
    """
    AI Generation Pipeline - V3 Universal System
    
    Chỉ sử dụng V3 Universal Intelligent Generator
    Tự động adapt với mọi niche: tech, health, finance, education...
    """
    
    def __init__(self):
        self.client = None
        self.universal_generator = None
    
    def open_spider(self, spider):
        """Initialize when spider starts"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            spider.logger.error("❌ Thiếu GEMINI_API_KEY!")
            return
        
        self.client = genai.Client(api_key=api_key)
        spider.logger.info("✅ Gemini Client ready")
        
        # V3: Initialize Universal Generator
        if V3_AVAILABLE:
            try:
                self.universal_generator = UniversalIntelligentGenerator(api_key)
                spider.logger.info("✨ V3 Universal Generator ready")
            except Exception as e:
                spider.logger.error(f"❌ V3 init failed: {e}")
        else:
            spider.logger.error("❌ V3 not available - Cannot generate content!")
    
    def process_item(self, item, spider):
        """Process each item with V3 Universal System"""
        
        if not self.client:
            raise DropItem("❌ Gemini Client not initialized")
        
        if not V3_AVAILABLE or not self.universal_generator:
            raise DropItem("❌ V3 Universal Generator not available!")

        spider.logger.info(f"--- 🤖 Processing: {item['keyword']} ---")

        # Get configurations from environment
        brand_name = os.getenv("BRAND_NAME", "Website")
        category_name = os.getenv("CATEGORY_NAME", "")
        wp_url = os.getenv("WP_URL", "")
        site_description = os.getenv("SITE_DESCRIPTION", "")
        
        # Get sample keywords (for first-time website analysis)
        sample_keywords_str = os.getenv("SAMPLE_KEYWORDS", "")
        sample_keywords = None
        if sample_keywords_str:
            sample_keywords = [k.strip() for k in sample_keywords_str.split(',') if k.strip()]
        
        spider.logger.info(f"📁 Category: {category_name or 'N/A'}")
        spider.logger.info(f"✨ Using V3 Universal System")
        
        # === V3: Generate Universal Prompt ===
        try:
            final_prompt = self.universal_generator.generate_with_auto_analysis(
                keyword=item['keyword'],
                category_name=category_name,
                brand_name=brand_name,
                site_url=wp_url,
                base_content=item['raw_text'],
                site_description=site_description,
                sample_keywords=sample_keywords
            )
            
            spider.logger.info("✅ V3 prompt generated")
            
        except Exception as e:
            spider.logger.error(f"❌ V3 prompt generation failed: {e}")
            raise DropItem(f"V3 failed for keyword: {item['keyword']}")
        
        # === Call AI API ===
        result = self._call_ai_api(final_prompt, spider)
        
        if result is None:
            raise DropItem(f"AI failed: {item['keyword']}")
        
        # Assign data to item
        item['ai_title'] = result['title']
        item['ai_content'] = result['content']
        item['ai_excerpt'] = result.get('excerpt', '')
        
        spider.logger.info(f"✅ AI generated content for: {item['keyword']}")
        
        return item
    
    def _call_ai_api(self, prompt, spider):
        """
        Call Gemini API with retry logic
        
        Args:
            prompt: The prompt to send to AI
            spider: Spider instance for logging
        
        Returns:
            dict: Parsed JSON response with title, content, excerpt
        """
        
        preferred_model = os.getenv("PREFERRED_MODEL", "gemini-2.5-flash")
        all_models = ['gemini-2.5-flash', 'gemini-2.5-pro']
        
        # Prioritize preferred model
        if preferred_model in all_models:
            candidate_models = [preferred_model] + [m for m in all_models if m != preferred_model]
        else:
            candidate_models = all_models
        
        spider.logger.info(f"🎯 Preferred Model: {preferred_model}")
        
        max_retries = 3
        
        for model_name in candidate_models:
            spider.logger.info(f"→ Trying model: {model_name}")
            
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.7,
                            max_output_tokens=8192,
                        )
                    )
                    
                    result_text = response.text
                    
                    # Parse JSON from response
                    clean_json = self._extract_json(result_text)
                    data = json.loads(clean_json)
                    
                    # Validate response
                    if not data.get('title') or not data.get('content'):
                        raise ValueError("Missing title or content in response")
                    
                    spider.logger.info(f"✅ AI success with {model_name}")
                    data['_model_used'] = model_name
                    
                    return data
                    
                except json.JSONDecodeError as e:
                    spider.logger.warning(f"⚠️ JSON parse error (attempt {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    spider.logger.error(f"❌ JSON parsing failed after {max_retries} attempts with {model_name}")
                    break
                    
                except Exception as e:
                    err_msg = str(e).lower()
                    
                    # Rate limit error
                    if "429" in str(e) or "quota" in err_msg or "rate" in err_msg:
                        wait_time = 30 * (attempt + 1)
                        spider.logger.warning(f"⚠️ Rate limit hit! Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    
                    # Model not found
                    elif "404" in str(e) or "not found" in err_msg:
                        spider.logger.warning(f"❌ Model {model_name} not found, trying next model...")
                        break
                    
                    # Other errors
                    else:
                        spider.logger.error(f"❌ Error with {model_name}: {e}")
                        if attempt < max_retries - 1:
                            spider.logger.info(f"→ Retrying in 5s... (attempt {attempt+2}/{max_retries})")
                            time.sleep(5)
                            continue
                        break
        
        spider.logger.error("❌ All models failed!")
        return None
    
    def _extract_json(self, text):
        """
        Extract JSON from AI response text
        
        Handles cases where AI includes markdown code blocks
        
        Args:
            text: Raw text from AI
        
        Returns:
            str: Clean JSON string
        """
        # Remove markdown code blocks
        text = text.replace('```json', '').replace('```', '')
        
        # Find JSON object
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start != -1 and end > start:
            return text[start:end]
        
        return text.strip()


class WordPressPublisherPipeline:
    """
    WordPress Publisher Pipeline
    
    Uploads image and publishes post to WordPress
    """
    
    def process_item(self, item, spider):
        """Publish item to WordPress"""
        
        wp_url = os.getenv("WP_URL")
        wp_user = os.getenv("WP_USER")
        wp_pass = os.getenv("WP_APP_PASSWORD")
        
        if not all([wp_url, wp_user, wp_pass]):
            spider.logger.error("❌ Missing WordPress credentials!")
            return item
        
        # Get category ID
        cat_id_env = os.getenv("WP_CATEGORY_ID")
        category_ids = []
        if cat_id_env and cat_id_env.strip() and cat_id_env != "None":
            try:
                category_ids = [int(cat_id_env)]
            except:
                spider.logger.warning(f"⚠️ Invalid category ID: {cat_id_env}")

        auth = (wp_user, wp_pass)

        # 1. Upload Featured Image
        media_id = 0
        if item.get('image_url'):
            media_id = self._upload_image(item, auth, wp_url, spider)

        # 2. Create Post
        post_data = {
            'title': item['ai_title'],
            'content': item['ai_content'],
            'excerpt': item['ai_excerpt'],
            'status': 'publish',
            'featured_media': media_id,
            'categories': category_ids,
            'meta': {
                # RankMath SEO
                'rank_math_focus_keyword': item['keyword'],
                'rank_math_description': item['ai_excerpt'],
                'rank_math_robots': ['index', 'follow'],
                # Yoast SEO
                '_yoast_wpseo_focuskw': item['keyword'],
                '_yoast_wpseo_metadesc': item['ai_excerpt']
            }
        }

        try:
            spider.logger.info(f"📤 Publishing to WordPress...")
            res = requests.post(
                f"{wp_url}/posts", 
                json=post_data, 
                auth=auth, 
                timeout=30
            )
            
            if res.status_code == 201:
                post_link = res.json().get('link', '')
                spider.logger.info(f"✅ PUBLISHED: {item['keyword']}")
                spider.logger.info(f"   Link: {post_link}")
            else:
                spider.logger.error(f"❌ Publish failed: HTTP {res.status_code}")
                spider.logger.error(f"   Response: {res.text[:500]}")
                
        except Exception as e:
            spider.logger.error(f"❌ WordPress publish error: {e}")

        return item
    
    def _upload_image(self, item, auth, wp_url, spider):
        """
        Upload image to WordPress media library
        
        Args:
            item: Item with image_url
            auth: WordPress auth tuple
            wp_url: WordPress API URL
            spider: Spider for logging
        
        Returns:
            int: Media ID (0 if failed)
        """
        try:
            spider.logger.info(f"📷 Uploading image: {item['image_url'][:80]}...")
            
            # Download image with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': item.get('source_url', ''),
            }
            
            img_response = requests.get(
                item['image_url'], 
                headers=headers, 
                verify=False, 
                timeout=20
            )
            
            if img_response.status_code == 200:
                # Determine file extension from content type
                content_type = img_response.headers.get('content-type', 'image/jpeg')
                ext = 'jpg'
                if 'png' in content_type:
                    ext = 'png'
                elif 'webp' in content_type:
                    ext = 'webp'
                elif 'gif' in content_type:
                    ext = 'gif'
                
                # Create SEO-friendly filename
                keyword_clean = item['keyword'].replace(' ', '-')[:40]
                keyword_clean = ''.join(c for c in keyword_clean if c.isalnum() or c == '-')
                filename = f"seo-{keyword_clean}.{ext}"
                
                # Upload to WordPress
                files = {'file': (filename, img_response.content, content_type)}
                
                res = requests.post(
                    f"{wp_url}/media", 
                    files=files, 
                    auth=auth, 
                    timeout=30
                )
                
                if res.status_code == 201:
                    media_id = res.json()['id']
                    spider.logger.info(f"✅ Image uploaded. Media ID: {media_id}")
                    return media_id
                else:
                    spider.logger.warning(f"⚠️ Image upload failed: HTTP {res.status_code}")
                    spider.logger.warning(f"   Response: {res.text[:300]}")
            else:
                spider.logger.warning(f"⚠️ Image download failed: HTTP {img_response.status_code}")
                
        except Exception as e:
            spider.logger.error(f"❌ Image upload error: {e}")
        
        return 0
"""
Scrapy Pipelines - Optimized with vnrewrite-style prompt system
"""

import os
import requests
import json
import time
import random
from google import genai
from google.genai import types
from scrapy.exceptions import DropItem

# Import prompt configuration
try:
    from backend.prompt_config import PromptConfig, build_final_prompt, get_role_for_category
except ImportError:
    # Fallback if running standalone
    from prompt_config import PromptConfig, build_final_prompt, get_role_for_category


class AiGenerationPipeline:
    """
    AI Generation Pipeline with vnrewrite-style prompt system
    Features:
    - Dynamic word count (800-2200 words, 5 tiers)
    - Keyword density optimization
    - A/B/C prompt variation
    - Natural writing style enforcement
    """
    
    def __init__(self):
        self.client = None
        self.prompt_config = None
    
    def open_spider(self, spider):
        """Initialize when spider starts"""
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            spider.logger.info("✅ Đã khởi tạo Gemini Client")
        
        # Initialize prompt config
        brand_name = os.getenv("BRAND_NAME", "Website")
        self.prompt_config = PromptConfig(brand_name=brand_name)
    
    def process_item(self, item, spider):
        if not self.client:
            raise DropItem("Thiếu Gemini API Key hoặc Client chưa khởi tạo")

        spider.logger.info(f"--- 🤖 Đang xử lý AI: {item['keyword']} ---")

        # Get configurations from environment
        brand_name = os.getenv("BRAND_NAME", "Website")
        category_name = os.getenv("CATEGORY_NAME", "")
        
        spider.logger.info(f"📁 Danh mục: {category_name or 'Không xác định'}")
        
        # Check for custom prompt from dashboard
        custom_prompt = os.getenv("CHOSEN_PROMPT") or os.getenv("CUSTOM_PROMPT_TEMPLATE")
        
        if custom_prompt:
            # Use custom prompt with placeholder replacement
            final_prompt = self._build_custom_prompt(
                custom_prompt, 
                item['keyword'], 
                item['raw_text'],
                brand_name
            )
            article_config = {'word_count': 'custom', 'variation': 'custom'}
        else:
            # Use vnrewrite-style prompt system
            final_prompt, article_config = build_final_prompt(
                keyword=item['keyword'],
                content=item['raw_text'],
                category_name=category_name,
                brand_name=brand_name,
                config=self.prompt_config
            )
        
        spider.logger.info(f"📝 Config: {article_config.get('word_count', 'N/A')} từ, "
                          f"Variation: {article_config.get('variation', 'N/A')}")

        # Call AI API
        result = self._call_ai_api(final_prompt, spider)
        
        if result is None:
            raise DropItem(f"AI Thất bại: {item['keyword']}")
        
        # Assign data
        item['ai_title'] = result['title']
        item['ai_content'] = result['content']
        item['ai_excerpt'] = result.get('excerpt', '')
        
        # Record variation usage
        if self.prompt_config and article_config.get('variation'):
            self.prompt_config.record_variation_usage(article_config['variation'])
        
        return item
    
    def _build_custom_prompt(self, template, keyword, content, brand_name):
        """Build prompt from custom template with placeholder replacement"""
        
        # Generate random config for placeholders
        word_count = random.randint(1200, 1800)
        primary_kw = random.randint(6, 12)
        secondary_kw = random.randint(4, 7)
        
        # Replace placeholders
        prompt = template
        prompt = prompt.replace("{keyword}", keyword)
        prompt = prompt.replace("{{keyword}}", keyword)
        prompt = prompt.replace("{content}", content)
        prompt = prompt.replace("{{content}}", content)
        prompt = prompt.replace("{brand_name}", brand_name)
        prompt = prompt.replace("{{brand_name}}", brand_name)
        prompt = prompt.replace("BRAND_CUA_BAN", brand_name)
        
        # vnrewrite-style placeholders
        prompt = prompt.replace("{{WORD_COUNT}}", str(word_count))
        prompt = prompt.replace("{{PRIMARY_KEYWORD_COUNT}}", str(primary_kw))
        prompt = prompt.replace("{{SECONDARY_KEYWORD_COUNT}}", str(secondary_kw))
        
        # Ensure content is included
        if "{content}" not in template and "{{content}}" not in template:
            prompt += f"\n\n## NỘI DUNG GỐC\n{content}"
        
        return prompt
    
    def _call_ai_api(self, prompt, spider):
        """Call Gemini API with retry logic"""
        
        candidate_models = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash']
        max_retries = 3
        
        for model_name in candidate_models:
            spider.logger.info(f"--> Đang thử Model: {model_name}")
            
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.7,
                            max_output_tokens=8192,  # Tăng để đủ cho bài dài
                        )
                    )
                    
                    result_text = response.text
                    
                    # Parse JSON
                    clean_json = self._extract_json(result_text)
                    data = json.loads(clean_json)
                    
                    # Validate
                    if not data.get('title') or not data.get('content'):
                        raise ValueError("Missing title or content in response")
                    
                    spider.logger.info(f"✅ AI xử lý thành công với {model_name}")
                    return data
                    
                except json.JSONDecodeError as e:
                    spider.logger.warning(f"⚠️ JSON lỗi (attempt {attempt+1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    break
                    
                except Exception as e:
                    err_msg = str(e).lower()
                    
                    if "429" in str(e) or "quota" in err_msg or "rate" in err_msg:
                        wait_time = 30 * (attempt + 1)
                        spider.logger.warning(f"⚠️ Rate limit! Chờ {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    
                    elif "404" in str(e) or "not found" in err_msg:
                        spider.logger.warning(f"❌ Model {model_name} không tìm thấy")
                        break
                    
                    else:
                        spider.logger.error(f"❌ Lỗi: {e}")
                        if attempt < max_retries - 1:
                            time.sleep(5)
                            continue
                        break
        
        return None
    
    def _extract_json(self, text):
        """Extract JSON from AI response"""
        # Remove markdown code blocks
        text = text.replace('```json', '').replace('```', '')
        
        # Try to find JSON object
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start != -1 and end > start:
            return text[start:end]
        
        return text.strip()


class WordPressPublisherPipeline:
    """
    Pipeline đăng bài lên WordPress
    """
    
    def process_item(self, item, spider):
        wp_url = os.getenv("WP_URL")
        wp_user = os.getenv("WP_USER")
        wp_pass = os.getenv("WP_APP_PASSWORD")
        
        if not all([wp_url, wp_user, wp_pass]):
            spider.logger.error("Thiếu thông tin WordPress!")
            return item
        
        # Category ID
        cat_id_env = os.getenv("WP_CATEGORY_ID")
        category_ids = []
        if cat_id_env and cat_id_env.strip() and cat_id_env != "None":
            try:
                category_ids = [int(cat_id_env)]
            except:
                pass

        auth = (wp_user, wp_pass)

        # 1. Upload Image
        media_id = 0
        if item.get('image_url'):
            media_id = self._upload_image(item, auth, wp_url, spider)

        # 2. Post article
        post_data = {
            'title': item['ai_title'],
            'content': item['ai_content'],
            'excerpt': item['ai_excerpt'],
            'status': 'publish',
            'featured_media': media_id,
            'categories': category_ids,
            'meta': {
                # Rank Math SEO
                'rank_math_focus_keyword': item['keyword'],
                'rank_math_description': item['ai_excerpt'],
                'rank_math_robots': ['index', 'follow'],
                # Yoast SEO
                '_yoast_wpseo_focuskw': item['keyword'],
                '_yoast_wpseo_metadesc': item['ai_excerpt']
            }
        }

        try:
            res = requests.post(f"{wp_url}/posts", json=post_data, auth=auth, timeout=30)
            if res.status_code == 201:
                link = res.json().get('link', '')
                spider.logger.info(f"✅ DANG BAI THANH CONG: {item['keyword']} -> {link}")
            else:
                spider.logger.error(f"❌ Đăng bài thất bại: {res.text[:500]}")
        except Exception as e:
            spider.logger.error(f"❌ Lỗi kết nối WP: {e}")

        return item
    
    def _upload_image(self, item, auth, wp_url, spider):
        """Upload image to WordPress"""
        try:
            spider.logger.info(f"📷 Đang tải ảnh: {item['image_url'][:80]}...")
            
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
                # Determine file extension
                content_type = img_response.headers.get('content-type', 'image/jpeg')
                ext = 'jpg'
                if 'png' in content_type:
                    ext = 'png'
                elif 'webp' in content_type:
                    ext = 'webp'
                elif 'gif' in content_type:
                    ext = 'gif'
                
                # Clean filename
                keyword_clean = item['keyword'].replace(' ', '-')[:40]
                keyword_clean = ''.join(c for c in keyword_clean if c.isalnum() or c == '-')
                filename = f"seo-{keyword_clean}.{ext}"
                
                files = {'file': (filename, img_response.content, content_type)}
                
                res = requests.post(f"{wp_url}/media", files=files, auth=auth, timeout=30)
                
                if res.status_code == 201:
                    media_id = res.json()['id']
                    spider.logger.info(f"✅ Upload ảnh OK. ID: {media_id}")
                    return media_id
                else:
                    spider.logger.warning(f"⚠️ Lỗi WP Media: {res.status_code}")
            else:
                spider.logger.warning(f"⚠️ Không tải được ảnh: HTTP {img_response.status_code}")
                
        except Exception as e:
            spider.logger.error(f"❌ Lỗi xử lý ảnh: {e}")
        
        return 0
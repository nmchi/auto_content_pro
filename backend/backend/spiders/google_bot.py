"""
Google Search Spider - FLEXIBLE VERSION
✅ Blacklist bad domains (Facebook, YouTube - không scrape được)
✅ KHÔNG ưu tiên domain nào (100% linh hoạt)
✅ Tin tưởng Google ranking
✅ Try multiple results nếu scrape fail

File: backend/backend/spiders/google_bot.py
"""

import scrapy
import os
import json
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re


class GoogleBotSpider(scrapy.Spider):
    name = "google_bot"
    
    # === CHỈ BLACKLIST - Domains KHÔNG scrape được ===
    # Không ưu tiên domain nào cả!
    
    BLACKLIST_DOMAINS = [
        # Social media - Cần login hoặc không có text content
        'facebook.com',
        'fb.com',
        'youtube.com',
        'youtu.be',
        'twitter.com',
        'x.com',
        'instagram.com',
        'tiktok.com',
        'pinterest.com',
        
        # Forums/Q&A - Cần login
        'reddit.com',
        'quora.com',
        'linkedin.com',
        
        # Shopping - Product pages không phù hợp
        'shopee.vn',
        'lazada.vn',
        'tiki.vn',
        'sendo.vn',
        'amazon.com',
        'ebay.com',
        
        # App stores
        'play.google.com',
        'apps.apple.com',
        
        # PDF/Doc viewers (cần download)
        'docs.google.com',
        'drive.google.com',
        'scribd.com',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    def __init__(self, keyword='', *args, **kwargs):
        super(GoogleBotSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or os.getenv('KEYWORD', '')
        
        if not self.keyword:
            raise ValueError("Keyword is required!")
        
        self.logger.info(f"🔍 Spider initialized for keyword: {self.keyword}")
    
    def start_requests(self):
        """Start with Google Custom Search"""
        
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        
        if not api_key or not cse_id:
            self.logger.error("❌ Missing GOOGLE_API_KEY or GOOGLE_CSE_ID")
            return
        
        search_query = self.keyword
        
        self.logger.info(f"🔍 Searching Google for: {search_query}")
        
        # Lấy 10 results để có nhiều backup
        search_url = (
            f"https://www.googleapis.com/customsearch/v1"
            f"?key={api_key}"
            f"&cx={cse_id}"
            f"&q={search_query}"
            f"&num=10"
        )
        
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_google_results,
            errback=self.errback_httpbin,
            dont_filter=True,
            meta={'keyword': self.keyword}
        )
    
    def is_blacklisted(self, url):
        """Check if URL is in blacklist"""
        domain = urlparse(url).netloc.lower()
        
        for blocked in self.BLACKLIST_DOMAINS:
            if blocked in domain:
                return True
        return False
    
    def parse_google_results(self, response):
        """Parse Google results - Trust Google ranking, only filter blacklist"""
        
        try:
            data = json.loads(response.text)
            items = data.get('items', [])
            
            if not items:
                self.logger.warning("⚠️ No search results found")
                yield {
                    'keyword': self.keyword,
                    'source_url': '',
                    'raw_text': '',
                    'image_url': ''
                }
                return
            
            self.logger.info(f"✅ Found {len(items)} search results")
            
            # === ONLY FILTER BLACKLIST ===
            # Giữ nguyên thứ tự Google ranking!
            
            valid_items = []
            for idx, item in enumerate(items, 1):
                url = item.get('link', '')
                domain = urlparse(url).netloc
                
                if not url:
                    continue
                
                if self.is_blacklisted(url):
                    self.logger.info(f"  #{idx} ⛔ SKIP: {domain} (blacklisted)")
                else:
                    valid_items.append(item)
                    self.logger.info(f"  #{idx} ✅ OK: {domain}")
            
            if not valid_items:
                self.logger.warning("⚠️ All results are blacklisted!")
                yield {
                    'keyword': self.keyword,
                    'source_url': '',
                    'raw_text': '',
                    'image_url': ''
                }
                return
            
            self.logger.info(f"📊 Valid results: {len(valid_items)}/{len(items)}")
            
            # === TRY VALID RESULTS IN ORDER ===
            # Thử từng URL theo thứ tự Google ranking
            # Dừng khi scrape thành công
            
            for idx, result_item in enumerate(valid_items, 1):
                target_url = result_item.get('link', '')
                
                self.logger.info(f"📄 [{idx}/{len(valid_items)}] Trying: {target_url[:80]}...")
                
                # Get metadata
                google_snippet = result_item.get('snippet', '')
                google_title = result_item.get('title', '')
                
                image_url = ''
                if 'pagemap' in result_item:
                    pagemap = result_item['pagemap']
                    if 'cse_image' in pagemap:
                        image_url = pagemap['cse_image'][0].get('src', '')
                    elif 'metatags' in pagemap and pagemap['metatags']:
                        meta = pagemap['metatags'][0]
                        image_url = (meta.get('og:image') or 
                                   meta.get('twitter:image') or 
                                   meta.get('image', ''))
                
                # Scrape
                yield scrapy.Request(
                    url=target_url,
                    callback=self.parse_content,
                    errback=self.errback_httpbin,
                    dont_filter=True,
                    meta={
                        'keyword': self.keyword,
                        'source_url': target_url,
                        'google_image': image_url,
                        'google_snippet': google_snippet,
                        'google_title': google_title,
                        'try_index': idx,
                        'total_valid': len(valid_items)
                    },
                    priority=100 - idx  # Higher priority for earlier results
                )
            
        except Exception as e:
            self.logger.error(f"❌ Error in parse_google_results: {e}")
            yield {
                'keyword': self.keyword,
                'source_url': '',
                'raw_text': '',
                'image_url': ''
            }
    
    def parse_content(self, response):
        """Parse article content - FLEXIBLE for any site"""
        
        keyword = response.meta.get('keyword', self.keyword)
        source_url = response.meta.get('source_url', '')
        google_image = response.meta.get('google_image', '')
        google_snippet = response.meta.get('google_snippet', '')
        google_title = response.meta.get('google_title', '')
        try_index = response.meta.get('try_index', 1)
        total_valid = response.meta.get('total_valid', 1)
        
        domain = urlparse(source_url).netloc
        self.logger.info(f"📝 [{try_index}/{total_valid}] Extracting from: {domain}")
        
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Remove unwanted
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
                tag.decompose()
            
            # Remove clutter
            clutter_classes = ['navigation', 'sidebar', 'menu', 'footer', 'header', 'ads', 'advertisement', 'cookie', 'popup']
            for clutter in clutter_classes:
                for elem in soup.find_all(class_=lambda x: x and clutter in x.lower()):
                    elem.decompose()
            
            content = ''
            
            # === FLEXIBLE EXTRACTION - Works for most sites ===
            
            # Strategy 1: Specific selectors for known platforms
            if 'fandom.com' in source_url or 'wikia.com' in source_url:
                main_content = soup.find('div', class_='mw-parser-output')
                if main_content:
                    for elem in main_content.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'ol']):
                        text = elem.get_text(separator=' ', strip=True)
                        if text and len(text) > 10:
                            content += text + '\n\n'
            
            # Strategy 2: WordPress (very common)
            if not content and ('wordpress' in response.text.lower() or 'wp-content' in response.text.lower()):
                for class_hint in ['entry-content', 'post-content', 'article-content', 'content-area']:
                    post_content = soup.find(['div', 'article'], class_=lambda x: x and class_hint in x.lower())
                    if post_content:
                        content = post_content.get_text(separator='\n', strip=True)
                        break
            
            # Strategy 3: Semantic HTML5 tags
            if not content:
                article = soup.find('article')
                if article:
                    content = article.get_text(separator='\n', strip=True)
            
            if not content:
                main = soup.find('main')
                if main:
                    content = main.get_text(separator='\n', strip=True)
            
            if not content:
                main_role = soup.find(attrs={'role': 'main'})
                if main_role:
                    content = main_role.get_text(separator='\n', strip=True)
            
            # Strategy 4: Common class names
            if not content:
                for class_name in ['content', 'article', 'post', 'entry', 'body', 'main-content', 'page-content']:
                    candidates = soup.find_all(['div', 'section'], class_=lambda x: x and class_name in x.lower())
                    if candidates:
                        # Get longest div (likely main content)
                        best_candidate = max(candidates, key=lambda d: len(d.get_text(strip=True)))
                        text = best_candidate.get_text(separator='\n', strip=True)
                        if len(text) > 100:
                            content = text
                            break
            
            # Strategy 5: Last resort - body
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator='\n', strip=True)
            
            # === CLEAN CONTENT ===
            
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Remove very short lines (navigation, menu items)
            lines = [line for line in lines if len(line) > 15]
            
            # Remove duplicates
            cleaned_lines = []
            prev_line = None
            for line in lines:
                if line != prev_line:
                    cleaned_lines.append(line)
                    prev_line = line
            
            content = '\n'.join(cleaned_lines)
            
            # Limit but keep substantial content
            if len(content) > 20000:
                content = content[:20000]
            
            # === EVALUATE SUCCESS ===
            
            chars = len(content)
            
            if chars >= 300:
                self.logger.info(f"✅ SUCCESS! {chars} chars from {domain}")
                success = True
            elif chars >= 100:
                self.logger.warning(f"⚠️ Partial: {chars} chars from {domain}")
                success = True  # Acceptable
            else:
                self.logger.warning(f"❌ Failed: Only {chars} chars from {domain}")
                success = False
            
            # === FALLBACK TO SNIPPET ===
            
            if not success and (google_snippet or google_title):
                self.logger.info("📋 Using Google snippet as fallback")
                fallback = ""
                if google_title:
                    fallback += f"Title: {google_title}\n\n"
                if google_snippet:
                    fallback += f"Summary: {google_snippet}\n"
                
                if fallback:
                    content = fallback
                    self.logger.info(f"✅ Fallback: {len(content)} chars")
            
            # === FIND IMAGE ===
            
            image_url = google_image
            
            if not image_url:
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    image_url = og_image.get('content')
            
            if not image_url:
                tw_image = soup.find('meta', attrs={'name': 'twitter:image'})
                if tw_image and tw_image.get('content'):
                    image_url = tw_image.get('content')
            
            if not image_url:
                # Find first reasonable img
                imgs = soup.find_all('img')
                for img in imgs:
                    src = img.get('src') or img.get('data-src')
                    if src and not any(skip in src.lower() for skip in ['logo', 'icon', 'avatar', 'ad', 'banner']):
                        if src.startswith('//'):
                            image_url = 'https:' + src
                        elif src.startswith('/'):
                            parsed = urlparse(source_url)
                            image_url = f"{parsed.scheme}://{parsed.netloc}{src}"
                        elif src.startswith('http'):
                            image_url = src
                        
                        if image_url:
                            break
            
            if image_url:
                self.logger.info(f"🖼️ Image: {image_url[:60]}...")
            
            # === YIELD RESULT ===
            
            yield {
                'keyword': keyword,
                'source_url': source_url,
                'raw_text': content,
                'image_url': image_url
            }
            
        except Exception as e:
            self.logger.error(f"❌ Parse error on {domain}: {e}")
            
            # Fallback to snippet
            fallback = ""
            if google_title:
                fallback += f"Title: {google_title}\n\n"
            if google_snippet:
                fallback += f"Summary: {google_snippet}\n"
            
            yield {
                'keyword': keyword,
                'source_url': source_url,
                'raw_text': fallback,
                'image_url': google_image
            }
    
    def errback_httpbin(self, failure):
        """Handle request errors"""
        self.logger.error(f"❌ Request failed: {failure.value}")
        
        # Don't yield - let next URL try
        return
import scrapy
import os
import requests
import trafilatura
from urllib.parse import urljoin, urlparse
from twisted.internet import error as twisted_error
from backend.items import BlogPostItem

class GoogleSpider(scrapy.Spider):
    name = "google_bot"
    
    # Cấu hình retry và timeout
    custom_settings = {
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
        'DOWNLOAD_TIMEOUT': 30,
        'ROBOTSTXT_OBEY': False,
        'COOKIES_ENABLED': True,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    }

    def __init__(self, keyword=None, url=None, *args, **kwargs):
        super(GoogleSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword
        self.direct_url = url

    def start_requests(self):
        """
        Tìm kiếm Google hoặc dùng URL trực tiếp
        """
        # Nếu có URL trực tiếp thì dùng luôn
        if self.direct_url:
            self.logger.info(f"Sử dụng URL trực tiếp: {self.direct_url}")
            yield scrapy.Request(
                url=self.direct_url, 
                callback=self.parse, 
                meta={'keyword': self.keyword or 'unknown'}
            )
            return
        
        # Nếu không có keyword thì báo lỗi
        if not self.keyword:
            self.logger.error("Thiếu keyword! Dùng: -a keyword='từ khóa'")
            return
        
        # Lấy API keys từ environment
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        
        if not api_key or not cse_id:
            self.logger.error("Thiếu GOOGLE_API_KEY hoặc GOOGLE_CSE_ID!")
            return
        
        # Gọi Google Custom Search API
        self.logger.info(f"Đang tìm kiếm Google cho: {self.keyword}")
        
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': self.keyword,
            'num': 10,  # Lấy 10 kết quả để có nhiều lựa chọn
            'lr': 'lang_vi',  # Ưu tiên tiếng Việt
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=15)
            data = response.json()
            
            # Debug: In ra response để kiểm tra
            if 'error' in data:
                self.logger.error(f"Google API Error: {data['error'].get('message', data['error'])}")
                return
            
            if 'items' not in data or len(data['items']) == 0:
                self.logger.error(f"Không tìm thấy kết quả cho: {self.keyword}")
                self.logger.info(f"Response từ Google: {data.get('searchInformation', {})}")
                return
            
            # Lấy URL phù hợp nhất
            target_url = None
            target_image = None
            
            # Các domain không mong muốn
            skip_domains = [
                'youtube.com', 'facebook.com', 'tiktok.com', 
                'twitter.com', 'instagram.com', 'pinterest.com',
                'amazon.com', 'shopee.vn', 'lazada.vn'
            ]
            
            # Các domain ưu tiên (có nội dung chất lượng)
            priority_domains = [
                'truyenfull', 'truyen', 'metruyencv', 'tangthuvien',
                'wikidich', 'sstruyen', 'truyenyy', 'novelhall'
            ]
            
            for item in data['items']:
                url = item.get('link', '')
                domain = urlparse(url).netloc.lower()
                
                # Bỏ qua các trang không mong muốn
                if any(skip in domain for skip in skip_domains):
                    continue
                
                # Ưu tiên các trang truyện
                is_priority = any(p in domain for p in priority_domains)
                
                # Lấy hình ảnh từ kết quả tìm kiếm (nếu có)
                pagemap = item.get('pagemap', {})
                
                # Thử lấy ảnh từ nhiều nguồn
                image_url = None
                
                # 1. Từ cse_image
                if 'cse_image' in pagemap:
                    image_url = pagemap['cse_image'][0].get('src', '')
                
                # 2. Từ cse_thumbnail
                if not image_url and 'cse_thumbnail' in pagemap:
                    image_url = pagemap['cse_thumbnail'][0].get('src', '')
                
                # 3. Từ metatags og:image
                if not image_url and 'metatags' in pagemap:
                    for meta in pagemap['metatags']:
                        if 'og:image' in meta:
                            image_url = meta['og:image']
                            break
                
                if is_priority or target_url is None:
                    target_url = url
                    target_image = image_url
                    if is_priority:
                        break  # Dừng nếu tìm thấy trang ưu tiên
            
            if target_url:
                self.logger.info(f"✅ Tìm thấy URL: {target_url}")
                if target_image:
                    self.logger.info(f"✅ Tìm thấy ảnh từ Google: {target_image}")
                
                yield scrapy.Request(
                    url=target_url,
                    callback=self.parse,
                    errback=self.handle_error,  # Xử lý lỗi
                    meta={
                        'keyword': self.keyword,
                        'google_image': target_image,
                        'dont_retry': False,
                    },
                    dont_filter=True
                )
            else:
                self.logger.error("Không tìm thấy URL phù hợp!")
                
        except Exception as e:
            self.logger.error(f"Lỗi khi gọi Google API: {e}")

    def handle_error(self, failure):
        """Xử lý lỗi khi request thất bại"""
        request = failure.request
        self.logger.error(f"❌ Request thất bại: {request.url}")
        self.logger.error(f"   Lỗi: {failure.value}")
        
        # Log chi tiết hơn
        if failure.check(twisted_error.ConnectionRefusedError):
            self.logger.error("   → Website từ chối kết nối (có thể bị chặn IP)")
        elif failure.check(twisted_error.TimeoutError):
            self.logger.error("   → Timeout - website phản hồi quá chậm")
        elif failure.check(twisted_error.DNSLookupError):
            self.logger.error("   → Không thể phân giải DNS - website có thể không tồn tại")

    def parse(self, response):
        """
        Trích xuất nội dung và hình ảnh từ trang web
        """
        self.logger.info(f"Đang parse: {response.url}")
        
        # === 1. TRÍCH XUẤT NỘI DUNG ===
        # Dùng Trafilatura để lọc nội dung sạch
        downloaded = trafilatura.fetch_url(response.url)
        clean_text = trafilatura.extract(
            downloaded, 
            include_comments=False, 
            include_tables=True,
            include_images=False
        )
        
        # Fallback nếu trafilatura thất bại
        if not clean_text or len(clean_text) < 200:
            self.logger.warning("Trafilatura không lấy được, dùng Scrapy...")
            
            # Thử nhiều selector khác nhau
            content_selectors = [
                'article p::text',
                '.post-content p::text',
                '.entry-content p::text',
                '.content p::text',
                '#content p::text',
                '.chapter-content::text',
                '.chapter-c::text',
                'p::text'
            ]
            
            paragraphs = []
            for selector in content_selectors:
                paragraphs = response.css(selector).getall()
                if paragraphs and len(' '.join(paragraphs)) > 200:
                    break
            
            clean_text = ' '.join(paragraphs)
        
        if not clean_text or len(clean_text) < 100:
            self.logger.error("❌ Không lấy được nội dung từ trang!")
            return

        # === 2. TRÍCH XUẤT HÌNH ẢNH ===
        image_url = ""
        
        # Ưu tiên 1: Ảnh từ Google Search (đã lấy ở bước trước)
        google_image = response.meta.get('google_image')
        if google_image and google_image.startswith('http'):
            image_url = google_image
            self.logger.info(f"Dùng ảnh từ Google Search: {image_url}")
        
        # Ưu tiên 2: Open Graph image (thường là ảnh đại diện chất lượng)
        if not image_url:
            og_image = response.css('meta[property="og:image"]::attr(content)').get()
            if og_image:
                image_url = self._normalize_url(og_image, response.url)
                self.logger.info(f"Dùng og:image: {image_url}")
        
        # Ưu tiên 3: Twitter card image
        if not image_url:
            twitter_image = response.css('meta[name="twitter:image"]::attr(content)').get()
            if twitter_image:
                image_url = self._normalize_url(twitter_image, response.url)
                self.logger.info(f"Dùng twitter:image: {image_url}")
        
        # Ưu tiên 4: Ảnh trong article/post
        if not image_url:
            img_selectors = [
                'article img::attr(src)',
                '.post-thumbnail img::attr(src)',
                '.featured-image img::attr(src)',
                '.entry-content img::attr(src)',
                '.post-content img::attr(src)',
                '.wp-post-image::attr(src)',
                '.book-cover img::attr(src)',
                '.cover img::attr(src)',
            ]
            
            for selector in img_selectors:
                img = response.css(selector).get()
                if img:
                    # Lọc bỏ các ảnh icon, avatar nhỏ
                    if self._is_valid_image(img):
                        image_url = self._normalize_url(img, response.url)
                        self.logger.info(f"Dùng ảnh từ selector '{selector}': {image_url}")
                        break
        
        # Ưu tiên 5: Ảnh đầu tiên trong trang (fallback)
        if not image_url:
            all_images = response.css('img::attr(src)').getall()
            for img in all_images:
                if self._is_valid_image(img):
                    image_url = self._normalize_url(img, response.url)
                    self.logger.info(f"Dùng ảnh fallback: {image_url}")
                    break
        
        if not image_url:
            self.logger.warning("⚠️ Không tìm thấy hình ảnh phù hợp")

        # === 3. TẠO ITEM ===
        item = BlogPostItem()
        item['keyword'] = response.meta['keyword']
        item['source_url'] = response.url
        item['raw_text'] = clean_text
        item['image_url'] = image_url
        
        self.logger.info(f"✅ Đã lấy {len(clean_text)} ký tự nội dung")
        if image_url:
            self.logger.info(f"✅ Đã lấy hình ảnh: {image_url[:80]}...")
        
        yield item
    
    def _normalize_url(self, url, base_url):
        """Chuyển URL tương đối thành URL tuyệt đối"""
        if not url:
            return ""
        
        url = url.strip()
        
        # Đã là URL đầy đủ
        if url.startswith('http://') or url.startswith('https://'):
            return url
        
        # URL protocol-relative
        if url.startswith('//'):
            return 'https:' + url
        
        # URL tương đối
        return urljoin(base_url, url)
    
    def _is_valid_image(self, url):
        """Kiểm tra xem URL có phải là ảnh hợp lệ không"""
        if not url:
            return False
        
        url_lower = url.lower()
        
        # Bỏ qua các ảnh nhỏ, icon
        skip_patterns = [
            'avatar', 'icon', 'logo', 'favicon', 'emoji',
            'button', 'banner-ad', 'advertisement', 'ads',
            '1x1', '16x16', '32x32', '64x64',
            'pixel', 'tracking', 'blank', 'spacer',
            'loading', 'spinner', 'placeholder'
        ]
        
        if any(pattern in url_lower for pattern in skip_patterns):
            return False
        
        # Phải là định dạng ảnh
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        has_valid_ext = any(ext in url_lower for ext in valid_extensions)
        
        # Hoặc là URL không có extension (có thể là ảnh động)
        if not has_valid_ext:
            # Kiểm tra xem có phải URL ảnh từ CDN không
            cdn_patterns = ['images', 'img', 'photo', 'pic', 'media', 'uploads', 'wp-content']
            if not any(pattern in url_lower for pattern in cdn_patterns):
                return False
        
        return True
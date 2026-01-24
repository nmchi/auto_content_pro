"""
Prompt Configuration System - Optimized Version
Features:
- 5-tier word count distribution (800-2200 words)
- Dynamic keyword calculation based on word count
- A/B/C prompt variation system
- Category-specific configurations with context guides
- Keyword context awareness (tên tác giả vs tên truyện vs chủ đề)
"""

import random
import json
import os

# ============== CONSTANTS ==============

PRIMARY_DENSITY_MIN = 0.60
PRIMARY_DENSITY_MAX = 0.75
SECONDARY_TO_PRIMARY_RATIO = 0.60

PRIMARY_MIN_BOUND = 5
PRIMARY_MAX_BOUND = 16
SECONDARY_MIN_BOUND = 3
SECONDARY_MAX_BOUND = 10

WORD_COUNT_DISTRIBUTION = {
    'short': 30,        # 30% bài: 1200-1400 từ
    'balanced': 50,     # 50% bài: 1400-1600 từ
    'long': 20          # 20% bài: 1600-1800 từ
}

WORD_COUNT_RANGES = {
    'short': {'min': 1200, 'max': 1400},
    'balanced': {'min': 1400, 'max': 1600},
    'long': {'min': 1600, 'max': 1800}
}

DEFAULT_VARIATION_DISTRIBUTION = {
    'A': 50,
    'B': 30,
    'C': 20
}


# ============== CATEGORY CONFIGURATIONS ==============
# Mỗi category có: role, keyword_context, content_guide

CATEGORY_CONFIGS = {
    # === REVIEW TÁC GIẢ ===
    "review tác giả": {
        "role": "Với tư cách là nhà phê bình văn học chuyên về tác giả truyện mạng, bạn am hiểu về phong cách viết, sự nghiệp và các tác phẩm của các tác giả nổi tiếng trong giới tiểu thuyết mạng Trung Quốc, Hàn Quốc, Nhật Bản.",
        "keyword_context": "TÊN TÁC GIẢ/BÚT DANH",
        "content_guide": """
**⚠️ QUAN TRỌNG - ĐỌC KỸ:**
Từ khóa `{keyword}` là **TÊN TÁC GIẢ/BÚT DANH**, KHÔNG phải tên truyện, nhân vật hay vật phẩm.

**Bài viết BẮT BUỘC phải tập trung vào:**
- Giới thiệu về tác giả {keyword} (tiểu sử, xuất thân nếu có)
- Phong cách viết đặc trưng của tác giả {keyword}
- Danh sách các tác phẩm nổi bật của {keyword}
- Đánh giá, nhận xét về tác giả {keyword} từ cộng đồng
- Thành tựu, giải thưởng của {keyword} (nếu có)
- So sánh với các tác giả cùng thể loại

**TUYỆT ĐỐI KHÔNG được viết về:**
- Nội dung chi tiết cốt truyện của một bộ truyện cụ thể
- Hệ thống tu luyện, vật phẩm, kỹ năng trong truyện
- Phân tích nhân vật trong truyện như thể đó là chủ đề chính
"""
    },
    
    # === REVIEW TRUYỆN ===
    "review truyện": {
        "role": "Với tư cách là reviewer truyện chuyên nghiệp, bạn có khả năng phân tích cốt truyện, nhân vật, thế giới quan và đưa ra đánh giá khách quan, hấp dẫn người đọc.",
        "keyword_context": "TÊN BỘ TRUYỆN",
        "content_guide": """
**Từ khóa `{keyword}` là TÊN BỘ TRUYỆN cần review.**

**Bài viết nên bao gồm:**
- Giới thiệu tổng quan về bộ truyện {keyword}
- Thông tin tác giả (nếu biết)
- Tóm tắt cốt truyện (không spoil quá nhiều)
- Đánh giá nhân vật chính, nhân vật phụ
- Điểm mạnh, điểm yếu của {keyword}
- So sánh với các bộ truyện cùng thể loại
- Đề xuất đối tượng độc giả phù hợp
"""
    },
    
    # === TRUYỆN TRANH ===
    "truyện tranh": {
        "role": "Với tư cách là biên tập viên chuyên về truyện tranh/manga/manhwa/manhua, bạn am hiểu sâu sắc về các thể loại, tác giả, và xu hướng đọc truyện của độc giả Việt Nam.",
        "keyword_context": "TÊN TRUYỆN hoặc CHỦ ĐỀ",
        "content_guide": ""
    },
    
    # === TIÊN HIỆP ===
    "tiên hiệp": {
        "role": "Với tư cách là chuyên gia về thể loại tiên hiệp/huyền huyễn, bạn am hiểu hệ thống tu luyện, cảnh giới, và văn hóa tiểu thuyết Trung Quốc.",
        "keyword_context": "TÊN TRUYỆN TIÊN HIỆP",
        "content_guide": """
**Từ khóa `{keyword}` là TÊN BỘ TRUYỆN TIÊN HIỆP.**

**Bài viết nên bao gồm:**
- Giới thiệu về {keyword} và tác giả
- Hệ thống tu luyện, cảnh giới trong truyện
- Nhân vật chính và các tuyến nhân vật quan trọng
- Thế giới quan, bối cảnh
- Điểm nổi bật, độc đáo của {keyword}
- Đánh giá và đề xuất
"""
    },
    
    # === MANGA ===
    "manga": {
        "role": "Với tư cách là chuyên gia manga Nhật Bản, bạn am hiểu văn hóa otaku, các nhà xuất bản, mangaka nổi tiếng và xu hướng manga hiện tại.",
        "keyword_context": "TÊN MANGA hoặc MANGAKA",
        "content_guide": ""
    },
    
    # === MANHWA ===
    "manhwa": {
        "role": "Với tư cách là chuyên gia manhwa Hàn Quốc, bạn am hiểu về webtoon, các nền tảng phát hành và đặc trưng của truyện tranh Hàn.",
        "keyword_context": "TÊN MANHWA hoặc TÁC GIẢ",
        "content_guide": ""
    },
    
    # === MANHUA ===
    "manhua": {
        "role": "Với tư cách là chuyên gia manhua Trung Quốc, bạn am hiểu về các thể loại tu chân, huyền huyễn và thị trường truyện tranh Trung Quốc.",
        "keyword_context": "TÊN MANHUA",
        "content_guide": ""
    },
    
    # === GIẢI MÃ GIẤC MƠ ===
    "giải mã giấc mơ": {
        "role": "Với tư cách là chuyên gia giải mã giấc mơ am hiểu sâu sắc văn hóa và tâm linh người Việt, đặc biệt là mối liên hệ giữa giấc mơ và các con số may mắn.",
        "keyword_context": "CHỦ ĐỀ GIẤC MƠ",
        "content_guide": """
**Từ khóa `{keyword}` là CHỦ ĐỀ GIẤC MƠ cần giải mã.**

**Bài viết BẮT BUỘC bao gồm:**
- Ý nghĩa tổng quát của giấc mơ về {keyword}
- Các trường hợp cụ thể/biến thể của giấc mơ này
- Giải mã theo tâm linh/phong thủy Việt Nam
- Con số may mắn liên quan (lô đề, xổ số)
- Lời khuyên cho người mơ thấy {keyword}
"""
    },
    
    # === PHONG THỦY ===
    "phong thủy": {
        "role": "Với tư cách là chuyên gia phong thủy, bạn am hiểu về ngũ hành, bát quái, và cách ứng dụng phong thủy trong đời sống hiện đại.",
        "keyword_context": "CHỦ ĐỀ PHONG THỦY",
        "content_guide": ""
    },
    
    # === TỬ VI ===
    "tử vi": {
        "role": "Với tư cách là chuyên gia tử vi/chiêm tinh, bạn am hiểu về 12 cung hoàng đạo, tử vi Việt Nam và cách luận giải vận mệnh.",
        "keyword_context": "CUNG HOÀNG ĐẠO hoặc CHỦ ĐỀ TỬ VI",
        "content_guide": ""
    },
    
    # === TIN TỨC ===
    "tin tức": {
        "role": "Với tư cách là phóng viên/biên tập viên tin tức, bạn có khả năng tổng hợp và trình bày thông tin một cách khách quan, chính xác và dễ hiểu.",
        "keyword_context": "CHỦ ĐỀ/SỰ KIỆN",
        "content_guide": ""
    },
    
    # === GAME ===
    "game": {
        "role": "Với tư cách là chuyên gia về game, bạn am hiểu về các thể loại game, tin tức gaming và cộng đồng game thủ Việt Nam.",
        "keyword_context": "TÊN GAME hoặc CHỦ ĐỀ GAMING",
        "content_guide": ""
    },
    
    # === DEFAULT ===
    "default": {
        "role": "Với tư cách là nhà sáng tạo nội dung chuyên nghiệp, bạn có khả năng viết bài hấp dẫn, chuẩn SEO và phù hợp với độc giả Việt Nam.",
        "keyword_context": "CHỦ ĐỀ BÀI VIẾT",
        "content_guide": ""
    }
}


class PromptConfig:
    """Prompt configuration system with variation support"""
    
    def __init__(self, category_name="", brand_name=""):
        self.category_name = category_name
        self.brand_name = brand_name
        self.variation_stats = {'A': 0, 'B': 0, 'C': 0, 'total': 0}
    
    def get_random_word_count(self):
        rand = random.randint(1, 100)
        cumulative = 0
        
        for tier, percentage in WORD_COUNT_DISTRIBUTION.items():
            cumulative += percentage
            if rand <= cumulative:
                range_data = WORD_COUNT_RANGES[tier]
                return random.randint(range_data['min'], range_data['max']), tier
        
        return random.randint(1400, 1700), 'balanced'
    
    def calculate_keyword_config(self, word_count):
        primary_min = int(word_count * PRIMARY_DENSITY_MIN / 100)
        primary_max = int(word_count * PRIMARY_DENSITY_MAX / 100) + 1
        
        primary_variation = random.randint(-1, 1)
        primary_count = random.randint(primary_min, primary_max) + primary_variation
        primary_count = max(PRIMARY_MIN_BOUND, min(PRIMARY_MAX_BOUND, primary_count))
        
        secondary_count = int(primary_count * SECONDARY_TO_PRIMARY_RATIO)
        secondary_variation = random.randint(-1, 1)
        secondary_count += secondary_variation
        secondary_count = max(SECONDARY_MIN_BOUND, min(SECONDARY_MAX_BOUND, secondary_count))
        
        return {
            'primary': primary_count,
            'secondary': secondary_count,
            'word_count': word_count,
            'primary_density': round(primary_count / word_count * 100, 2),
            'secondary_density': round(secondary_count / word_count * 100, 2)
        }
    
    def select_variation(self, available_variations=['A', 'B', 'C']):
        if len(available_variations) == 1:
            return available_variations[0]
        
        total = self.variation_stats['total']
        
        if total == 0:
            return self.weighted_random_selection(DEFAULT_VARIATION_DISTRIBUTION)
        
        differences = {}
        for var in available_variations:
            current_pct = (self.variation_stats.get(var, 0) / total) * 100
            differences[var] = current_pct - DEFAULT_VARIATION_DISTRIBUTION.get(var, 33)
        
        sorted_vars = sorted(differences.items(), key=lambda x: x[1])
        selected = sorted_vars[0][0]
        
        if abs(sorted_vars[0][1]) < 5:
            selected = self.weighted_random_selection(DEFAULT_VARIATION_DISTRIBUTION)
        
        return selected
    
    def weighted_random_selection(self, distribution):
        rand = random.randint(1, 100)
        cumulative = 0
        
        for variant, percentage in distribution.items():
            cumulative += percentage
            if rand <= cumulative:
                return variant
        
        return 'A'
    
    def record_variation_usage(self, variation):
        if variation in self.variation_stats:
            self.variation_stats[variation] += 1
            self.variation_stats['total'] += 1
    
    def get_article_config(self):
        word_count, tier = self.get_random_word_count()
        keyword_config = self.calculate_keyword_config(word_count)
        variation = self.select_variation()
        
        return {
            'word_count': word_count,
            'tier': tier,
            'keyword_config': keyword_config,
            'variation': variation
        }


def get_category_config(category_name):
    """Get configuration for a category"""
    category_lower = category_name.lower()
    
    for key, config in CATEGORY_CONFIGS.items():
        if key in category_lower:
            return config
    
    return CATEGORY_CONFIGS["default"]


def get_base_prompt_template():
    """Advanced SEO prompt template with web research and internal links support"""
    return """## VAI TRÒ
{role_description}

## NHIỆM VỤ
Viết lại bài viết dưới đây thành bài viết **mới hoàn toàn**, chuẩn SEO, hấp dẫn người đọc.

## TỪ KHÓA CHÍNH
`{keyword}` — Đây là {keyword_context}
{content_guide}

## THƯƠNG HIỆU
`{brand_name}`

## CẤU TRÚC BÀI VIẾT

### TIÊU ĐỀ (H1)
- Tự nhiên, hấp dẫn và phải chứa từ khóa chính

### CẤU TRÚC NỘI DUNG

**Không bắt buộc theo số phần cố định. Hãy linh hoạt theo nội dung thực tế:**
- **Mở đầu** (không tiêu đề): 2-3 câu giới thiệu chính, nhắc đến {brand_name} tự nhiên
- **Các phần chính** (H2): Tùy thuộc vào nội dung bài gốc
  - Ít nhất 4-5 phần H2, nhiều nhất 7-8 phần
  - Mỗi phần có nội dung thực chất, không viết cho có
- **Kết luận** (H2): Tổng kết, ý nghĩa, lời khuyên hoặc kêu gọi

**Nguyên tắc quan trọng:** Cấu trúc phải phục vụ nội dung, không phải ngược lại. Viết những gì cần thiết, không viết những gì không cần.

## PHONG CÁCH VIẾT - GIỌNG NGƯỜI THẬT

**Nguyên Tắc Vàng: Viết Như Người, Không Như AI**

**1. Sử dụng ngôn ngữ đời thường**
- Viết bằng tiếng Việt tự nhiên, gần gũi
- Tránh văn phong sách vở, cứng nhắc

**2. Đa dạng độ dài đoạn văn**
- Đoạn ngắn (1-2 câu): Tạo nhấn mạnh, chuyển ý
- Đoạn trung bình (3-4 câu): Phần lớn bài viết
- Đoạn dài (5-6 câu): Khi kể chuyện hoặc giải thích chi tiết
- **Không viết đều đặn** - thay đổi nhịp điệu liên tục

**3. Đa dạng câu văn**
- Kết hợp câu ngắn (3-5 từ) và câu dài
- Một vài câu bắt đầu bằng "Và", "Nhưng", "Còn" để tự nhiên
- Đôi khi dùng câu đứt quãng. Tạo hiệu ứng.
- Dùng gạch ngang — như thế này — cho ý phụ

**4. Giọng văn chân thực**
- Viết như đang kể chuyện cho bạn bè
- Thể hiện cảm xúc qua chi tiết, không nói trực tiếp "đây là cảm động"
- Dùng ví dụ cụ thể, không chung chung
- Có quan điểm, có góc nhìn riêng

**TUYỆT ĐỐI KHÔNG dùng các cụm từ sáo rỗng:**
- "Trong thế giới ngày nay..."
- "Không thể phủ nhận rằng..."
- "Điều đáng nói là..."
- "Như chúng ta đã biết..."
- "Có thể nói rằng..."
- "giữa vô vàn..."
- "rốt cuộc..."

## NGHIÊN CỨU & XÁC MINH - QUAN TRỌNG NHẤT

### BẮT BUỘC: TÌM KIẾM ĐỂ BỔ SUNG & XÁC MINH

**Sau khi đọc bài gốc, PHẢI tìm kiếm web để:**
1. Xác minh thông tin trong bài gốc (đặc biệt con số, tên riêng, ngày tháng)
2. Bổ sung chi tiết thiếu (nếu cần và phù hợp)
3. Tìm góc nhìn, bối cảnh rộng hơn

### QUY TẮC VÀNG: AN TOÀN HƠN LÀ SAI LẦM

**✅ AN TOÀN ĐỂ BỔ SUNG:**
- Thông tin từ nguồn uy tín, chính thống
- Dữ liệu được nhiều nguồn xác nhận
- Sự kiện lịch sử, công khai
- Thống kê, nghiên cứu đã công bố
- Giải thưởng, thành tích được công nhận

**❌ TUYỆT ĐỐI KHÔNG BỔ SUNG:**
- Thông tin chỉ có 1 nguồn duy nhất
- Tin đồn, lời đồn, suy đoán
- Chi tiết nhạy cảm không có trong bài gốc
- Thông tin mâu thuẫn giữa các nguồn
- Dữ liệu không có nguồn rõ ràng

**⚠️ XÁC MINH ĐỒNG BỘ - KIỂM TRA CHÉO:**

Khi tìm được thông tin từ web, phải đảm bảo:
- Tên, đối tượng CHÍNH XÁC khớp với bài gốc
- Thời gian, địa điểm phù hợp
- Bối cảnh không mâu thuẫn
- Ít nhất 2-3 nguồn uy tín xác nhận

**Nếu nghi ngờ 1% → Bỏ qua thông tin đó**

### THỨ TỰ ƯU TIÊN NGUỒN

**Đáng tin cậy (ưu tiên sử dụng):**
1. Website chính thức của tổ chức, cơ quan
2. Báo chí uy tín: VnExpress, Tuổi Trẻ, Thanh Niên, BBC, CNN...
3. Tạp chí chuyên ngành có uy tín
4. Nghiên cứu khoa học, báo cáo chính thức
5. Chuyên gia được công nhận trong lĩnh vực

**Không sử dụng:**
- Blog cá nhân không rõ nguồn gốc
- Diễn đàn, hỏi đáp chưa xác minh
- Website giật gân, câu view
- Mạng xã hội cá nhân (trừ khi là người nổi tiếng xác minh)
- Wikipedia (có thể tham khảo nhưng phải kiểm tra nguồn gốc)

### XỬ LÝ THÔNG TIN THIẾU HOẶC KHÔNG RÕ

**Khi bài gốc thiếu thông tin quan trọng:**
- Tìm kiếm để bổ sung (nếu an toàn)
- Nếu không tìm được nguồn tin cậy: Viết "Thông tin về... hiện chưa được công bố rộng rãi"
- KHÔNG đoán, KHÔNG bịa, KHÔNG suy luận

**Khi thông tin mâu thuẫn giữa các nguồn:**
- Nêu cả hai quan điểm (nếu cần)
- Ưu tiên nguồn chính thức hơn
- Hoặc bỏ qua thông tin đó nếu không chắc chắn

## TĂNG CƯỜNG CHIỀU SÂU NỘI DUNG

- Mục tiêu là **viết lại và mở rộng**, không chỉ diễn đạt lại.
- Mỗi phần nội dung nên **phong phú hơn ít nhất 20–40%** so với bài gốc.
- Có thể thêm:
  - Bối cảnh nền
  - Phân tích, so sánh, hoặc phản ứng từ cộng đồng / giới chuyên môn
  - Thông tin bổ trợ từ nguồn uy tín
- Không chèn đoạn "vô nghĩa" để kéo dài.
- Mỗi H2 cần ít nhất 2 đoạn văn hoàn chỉnh (từ 80–120 từ/đoạn).

## TỐI ƯU SEO & TỪ KHÓA

**Yêu cầu về độ dài:**
- Bài viết phải đạt tối thiểu **{word_count} từ** (không bao gồm tiêu đề)
- Nếu nội dung bài gốc ngắn, bổ sung thêm phân tích, bối cảnh, hoặc thông tin liên quan từ nghiên cứu web

**Yêu cầu về từ khóa:**
- Tiêu đề (H1) phải rõ ràng, có từ khóa chính `{keyword}`
- Từ khóa chính phải xuất hiện **ít nhất {primary_keyword_count} lần** trong toàn bài
- Trong 100 từ đầu tiên, xuất hiện ít nhất 1 lần từ khóa chính
- Các tiêu đề H2/H3 nên chứa biến thể của từ khóa hoặc câu hỏi phổ biến
- Không nhồi nhét từ khóa - phân bố tự nhiên trong bài
- Sử dụng từ khóa trong anchor text của liên kết nội bộ (nếu có)

## TÍCH HỢP THƯƠNG HIỆU

**Thương hiệu:** `{brand_name}`

**Cách sử dụng:**
- Tự nhiên đề cập đến thương hiệu `{brand_name}` trong bài viết, như một **nguồn biên soạn, nền tảng xuất bản, hoặc đơn vị cung cấp thông tin**.
- Chỉ nhắc thương hiệu 1–2 lần trong toàn bài, ở các vị trí hợp lý:
  - 1 lần trong **phần mở đầu hoặc kết bài**, ví dụ:
    - ✅ "Theo dữ liệu tổng hợp từ {brand_name}, …"
    - ✅ "Bài viết được biên soạn bởi {brand_name}, nhằm mang đến cái nhìn toàn diện về chủ đề."
  - Không chèn trong phần giữa trừ khi thực sự liên quan.
- Không sử dụng thương hiệu theo cách quảng cáo hoặc PR.
  Ví dụ:
  - ❌ "Hãy truy cập {brand_name} để biết thêm."
  - ❌ "Sản phẩm tuyệt vời của {brand_name}."

## TÍNH NHẤT QUÁN & CHẤT LƯỢNG

- Mỗi phần H2 có tối thiểu 2 đoạn văn, không để phần rỗng
- Giữ mạch thông tin liền lạc, tránh lặp ý giữa các phần
- Không dùng danh sách bullet quá dài (tối đa 5 mục)
- Kiểm tra để đảm bảo bài viết không có lỗi chính tả hoặc ngữ pháp
- Đảm bảo đạt đủ **{word_count} từ** và **{primary_keyword_count} lần từ khóa chính**

[internal_links]

## ĐỊNH DẠNG OUTPUT

**CHỈ TRẢ VỀ JSON, KHÔNG CÓ TEXT NÀO KHÁC:**
```json
{{
    "title": "Tiêu đề bài viết (có từ khóa {keyword})",
    "excerpt": "Mô tả 150-160 ký tự cho SEO",
    "content": "<h2>Tiêu đề phần 1</h2><p>Nội dung...</p>..."
}}
```

## NỘI DUNG GỐC CẦN VIẾT LẠI

{content}
"""


def build_final_prompt(keyword, content, category_name="", brand_name="", config=None):
    """
    Build final prompt with all placeholders replaced and category-specific guides
    """
    if config is None:
        config = PromptConfig(category_name, brand_name)
    
    # Get article configuration
    article_config = config.get_article_config()
    
    # Get category-specific configuration
    cat_config = get_category_config(category_name)
    
    # Build content guide with keyword replaced
    content_guide = cat_config.get('content_guide', '')
    if content_guide:
        content_guide = content_guide.replace('{keyword}', keyword)
    
    # Build prompt
    template = get_base_prompt_template()
    
    final_prompt = template.format(
        role_description=cat_config['role'],
        keyword=keyword,
        keyword_context=cat_config.get('keyword_context', 'CHỦ ĐỀ BÀI VIẾT'),
        content_guide=content_guide,
        brand_name=brand_name or "Website",
        word_count=article_config['word_count'],
        primary_keyword_count=article_config['keyword_config']['primary'],
        secondary_keyword_count=article_config['keyword_config']['secondary'],
        content=content
    )
    
    return final_prompt, article_config


# ============== LEGACY SUPPORT ==============

def get_role_for_category(category_name):
    """Legacy function - returns just the role string"""
    config = get_category_config(category_name)
    return config['role']


# ============== TEST ==============

if __name__ == "__main__":
    print("=== Test Category Configs ===")
    
    test_cases = [
        ("Review Tác Giả", "thiên tằm thổ đậu"),
        ("Tiên Hiệp", "đấu phá thương khung"),
        ("Giải Mã Giấc Mơ", "mơ thấy rắn"),
    ]
    
    for cat, kw in test_cases:
        print(f"\n--- {cat}: {kw} ---")
        cat_config = get_category_config(cat)
        print(f"Role: {cat_config['role'][:50]}...")
        print(f"Keyword Context: {cat_config['keyword_context']}")
        if cat_config['content_guide']:
            print(f"Has Content Guide: Yes")
        
    print("\n=== Test Article Config ===")
    config = PromptConfig("Review Tác Giả", "VanGioiComics")
    
    for i in range(3):
        article_config = config.get_article_config()
        print(f"\nBài {i+1}: {article_config['word_count']} từ, "
              f"KW chính: {article_config['keyword_config']['primary']} lần, "
              f"Variation: {article_config['variation']}")
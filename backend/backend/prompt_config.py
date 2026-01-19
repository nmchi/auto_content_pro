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
    'very_short': 10,
    'short': 20,
    'balanced': 40,
    'long': 20,
    'very_long': 10
}

WORD_COUNT_RANGES = {
    'very_short': {'min': 800, 'max': 1100},
    'short': {'min': 1100, 'max': 1400},
    'balanced': {'min': 1400, 'max': 1700},
    'long': {'min': 1700, 'max': 2000},
    'very_long': {'min': 2000, 'max': 2200}
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
    """Base prompt template - will be customized per category"""
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
- Tự nhiên, hấp dẫn và phải chứa từ khóa chính `{keyword}`

### CẤU TRÚC NỘI DUNG
**Linh hoạt theo nội dung thực tế:**
- **Mở đầu** (không tiêu đề): 2-3 câu giới thiệu, có thể nhắc đến {brand_name} tự nhiên
- **Các phần chính** (H2): 4-7 phần, mỗi phần có nội dung thực chất
- **Kết luận** (H2): Tổng kết, ý nghĩa, lời khuyên

## PHONG CÁCH VIẾT

**Nguyên Tắc: Viết Như Người Thật, Không Như AI**

1. **Đa dạng độ dài đoạn văn** - Không viết đều đặn
2. **Đa dạng câu văn** - Kết hợp câu ngắn và dài
3. **Giọng văn chân thực** - Viết như kể chuyện cho bạn bè

**TUYỆT ĐỐI KHÔNG dùng:**
- "Trong thế giới ngày nay..."
- "Không thể phủ nhận rằng..."
- "Điều đáng nói là..."
- "Như chúng ta đã biết..."
- "Có thể nói rằng..."
- "giữa vô vàn..."
- "rốt cuộc..."

## YÊU CẦU SEO

- Bài viết tối thiểu **{word_count} từ**
- Từ khóa `{keyword}` xuất hiện **{primary_keyword_count} lần**, phân bố tự nhiên
- Trong 100 từ đầu phải có từ khóa chính
- Các H2 nên chứa biến thể của từ khóa

## TÍCH HỢP THƯƠNG HIỆU

- Nhắc `{brand_name}` 1-2 lần ở mở đầu hoặc kết bài
- Ví dụ: "Theo tổng hợp từ {brand_name}..." hoặc "Bài viết được biên soạn bởi {brand_name}..."
- KHÔNG quảng cáo, PR

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
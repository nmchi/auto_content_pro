"""
Universal Intelligent Prompt Generator V3.5 - HYBRID
AI Analysis + Hard Rules = Ổn định 100%

Cải tiến:
- Hard rules dựa trên Category → Không bao giờ sai niche
- AI analysis chỉ để làm phong phú thêm
- Ổn định tuyệt đối
"""

import os
import json
from google import genai
from google.genai import types

# Fix encoding for Windows
import sys
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ============== HARD RULES BY CATEGORY ==============

CATEGORY_RULES = {
    # TRUYỆN - NHÂN VẬT
    "review nhân vật": {
        "niche": "review truyện tiểu thuyết web Trung Quốc",
        "sub_niche": "phân tích nhân vật tiên hiệp, huyền huyễn",
        "keyword_type": "person",
        "entity_hint": "nhân vật trong truyện tiểu thuyết",
        "required_info": [
            "Tên đầy đủ nhân vật (có thể có nhiều tên gọi)",
            "Xuất xứ: Truyện gốc (tên truyện, tác giả)",
            "Thân phận ban đầu (gia đình, xuất thân)",
            "Tu vi/Cảnh giới (các mốc đột phá quan trọng)",
            "Năng lực đặc biệt (Dị Hỏa, Huyết Mạch, Võ Hồn...)",
            "Tính cách (đặc điểm nổi bật)",
            "Mối quan hệ quan trọng (thầy, bạn, kẻ thù, tình yêu)",
            "Chuyển biến quan trọng trong truyện",
            "Thành tựu lớn nhất",
            "Trích dẫn câu thoại nổi tiếng (nếu có)"
        ],
        "sources": ["wikia fandom truyện", "blog review truyện", "diễn đàn truyện"],
        "tone": "hào hứng, phân tích sâu",
        "depth": "deep",
        "format": ["timeline phát triển", "phân tích năng lực", "mối quan hệ"]
    },
    
    # TRUYỆN - TÁC GIẢ
    "review tác giả": {
        "niche": "review truyện tiểu thuyết web Trung Quốc",
        "sub_niche": "phân tích tác giả và tác phẩm",
        "keyword_type": "person",
        "entity_hint": "tác giả truyện tiểu thuyết",
        "required_info": [
            "Tên bút danh chính (tên tiếng Trung + phiên âm)",
            "Tên thật (nếu công khai)",
            "Năm bắt đầu viết truyện",
            "Các tác phẩm nổi tiếng (danh sách chi tiết)",
            "Phong cách viết đặc trưng",
            "Thể loại chuyên trường (tiên hiệp, huyền huyễn, khoa huyễn...)",
            "Giải thưởng đạt được (nếu có)",
            "Doanh thu/Lượt đọc ước tính (tác phẩm nổi tiếng nhất)",
            "Đánh giá từ độc giả",
            "Tác phẩm đang viết (hiện tại)"
        ],
        "sources": ["Qidian", "wikia tác giả", "blog review"],
        "tone": "khách quan, phân tích",
        "depth": "moderate",
        "format": ["danh sách tác phẩm", "timeline sự nghiệp", "phân tích phong cách"]
    },
    
    # TRUYỆN - TIỂU THUYẾT
    "review truyện": {
        "niche": "review truyện tiểu thuyết web Trung Quốc",
        "sub_niche": "đánh giá và giới thiệu truyện",
        "keyword_type": "story",
        "entity_hint": "tác phẩm tiểu thuyết",
        "required_info": [
            "Tên truyện đầy đủ (tiếng Trung + phiên âm + tiếng Việt)",
            "Tác giả",
            "Thể loại chính (tiên hiệp, huyền huyễn, đô thị...)",
            "Số chương (hoàn thành hay đang viết)",
            "Năm xuất bản/bắt đầu",
            "Tóm tắt cốt truyện (không spoil)",
            "Nhân vật chính",
            "Hệ thống tu luyện/năng lực",
            "Điểm nổi bật",
            "Đánh giá từ độc giả (rating từ Qidian, wikia...)",
            "So sánh với truyện tương tự"
        ],
        "sources": ["Qidian", "wikia truyện", "blog review"],
        "tone": "nhiệt tình, hấp dẫn",
        "depth": "moderate",
        "format": ["tóm tắt hấp dẫn", "phân tích điểm mạnh/yếu", "đánh giá tổng quan"]
    },
    
    # TECH - SMARTPHONE
    "review smartphone": {
        "niche": "công nghệ - review smartphone",
        "sub_niche": "đánh giá chi tiết smartphone",
        "keyword_type": "product",
        "entity_hint": "smartphone/điện thoại",
        "required_info": [
            "Tên chính xác (model đầy đủ)",
            "Hãng sản xuất",
            "Năm ra mắt",
            "Giá niêm yết Việt Nam (VNĐ)",
            "Chip xử lý (tên chính xác + tiến trình)",
            "RAM (GB) và ROM (GB) các phiên bản",
            "Màn hình (kích thước, độ phân giải, tần số quét)",
            "Camera (MP, loại cảm biến, tính năng)",
            "Pin (mAh, sạc nhanh)",
            "Hệ điều hành",
            "So sánh với đối thủ cùng phân khúc",
            "Điểm benchmark (AnTuTu, Geekbench)"
        ],
        "sources": ["gsmarena.com", "trang chính thức hãng", "thegioididong.com"],
        "tone": "chuyên nghiệp, khách quan",
        "depth": "technical",
        "format": ["bảng thông số", "so sánh cụ thể", "đánh giá chi tiết"]
    },
    
    # HEALTH - GENERAL
    "sức khỏe": {
        "niche": "y tế - sức khỏe",
        "sub_niche": "thông tin sức khỏe và y học",
        "keyword_type": "health_topic",
        "entity_hint": "chủ đề về sức khỏe, bệnh, thuốc, dinh dưỡng",
        "required_info": [
            "Định nghĩa y học chính xác",
            "Nguyên nhân",
            "Triệu chứng",
            "Chẩn đoán",
            "Điều trị (theo khuyến cáo y khoa)",
            "Phòng ngừa",
            "Biến chứng (nếu có)",
            "Nghiên cứu khoa học liên quan",
            "Thống kê dịch tễ học (nếu có)"
        ],
        "sources": ["pubmed.gov", "WHO", "webmd.com", "vinmec.com"],
        "tone": "nghiêm túc, khoa học",
        "depth": "moderate",
        "format": ["định nghĩa rõ ràng", "danh sách có số liệu", "trích dẫn nghiên cứu"],
        "special": "⚠️ DISCLAIMER: Thông tin chỉ mang tính tham khảo. Tham khảo bác sĩ để được tư vấn chính xác."
    }
}


def normalize_category(category_name):
    """Chuẩn hóa tên category để match với rules"""
    if not category_name:
        return None
    
    cat_lower = category_name.lower().strip()
    
    # Map các biến thể về category chuẩn
    mapping = {
        "review nhân vật": ["nhân vật", "nhan vat", "character"],
        "review tác giả": ["tác giả", "tac gia", "author"],
        "review truyện": ["truyện", "truyen", "tiểu thuyết", "tieu thuyet", "story", "novel"],
        "review smartphone": ["smartphone", "điện thoại", "dien thoai", "phone"],
        "sức khỏe": ["sức khỏe", "suc khoe", "y tế", "y te", "health"]
    }
    
    for standard_cat, variants in mapping.items():
        if any(v in cat_lower for v in variants):
            return standard_cat
    
    return None


class UniversalIntelligentGenerator:
    """V3.5 HYBRID: AI + Hard Rules"""
    
    def __init__(self, gemini_api_key):
        self.client = genai.Client(api_key=gemini_api_key)
        self.website_profile = None
    
    def analyze_website_universal(self, site_url, site_description="", sample_keywords=None):
        """Phân tích website - HYBRID mode"""
        
        # Simple profile cho truyện (vì đã có hard rules)
        self.website_profile = {
            "site_url": site_url,
            "site_description": site_description or "Website tổng hợp",
            "niche": "mixed content",
            "analyzed": True
        }
        
        try:
            print("Website profile created (Hybrid mode - using category rules)")
        except:
            pass
        
        return self.website_profile
    
    def generate_universal_prompt(self, keyword, category_name, brand_name, base_content=""):
        """
        V3.5 HYBRID: Hard rules + AI enhancement
        
        Args:
            keyword: Từ khóa
            category_name: Category (QUAN TRỌNG!)
            brand_name: Thương hiệu
            base_content: Nội dung gốc
        
        Returns:
            str: Universal prompt
        """
        
        # Step 1: Get hard rules từ category
        normalized_cat = normalize_category(category_name)
        
        if normalized_cat and normalized_cat in CATEGORY_RULES:
            rules = CATEGORY_RULES[normalized_cat]
            print(f"Using hard rules for: {normalized_cat}")
        else:
            print(f"WARNING: No rules for category '{category_name}' - using general")
            rules = {
                "niche": "general content",
                "sub_niche": "mixed topics",
                "keyword_type": "general",
                "entity_hint": "chủ đề chung",
                "required_info": ["Thông tin cơ bản", "Định nghĩa", "Ứng dụng"],
                "sources": ["nguồn uy tín"],
                "tone": "friendly",
                "depth": "moderate",
                "format": ["giới thiệu", "phân tích", "kết luận"]
            }
        
        # Step 2: Build prompt với hard rules
        niche = rules["niche"]
        sub_niche = rules["sub_niche"]
        keyword_type = rules["keyword_type"]
        entity_hint = rules["entity_hint"]
        required_info = rules["required_info"]
        sources = rules["sources"]
        tone = rules["tone"]
        depth = rules["depth"]
        format_pref = rules["format"]
        special = rules.get("special", "")
        
        # Build prompt
        prompt = f"""# VAI TRÒ CHUYÊN GIA

Bạn là chuyên gia viết nội dung SEO trong lĩnh vực **{niche}**.

**Chuyên sâu:** {sub_niche}
**Phong cách:** {tone}
**Độ sâu:** {depth}

---

# NHIỆM VỤ - QUAN TRỌNG

Viết bài **{keyword_type}** về: `{keyword}`

⚠️ **CONTEXT BẮT BUỘC:**
- Đây là **{entity_hint}**
- KHÔNG PHẢI là chủ đề khác (y tế, công nghệ, tài chính...)
- Tập trung 100% vào {niche}

---

# THÔNG TIN BẮT BUỘC

⚠️ **Tìm kiếm web và verify từ nguồn uy tín.**

## Thông tin PHẢI CÓ:

"""
        
        # Add required information
        for idx, req_info in enumerate(required_info, 1):
            prompt += f"{idx}. **{req_info}**\n"
        
        prompt += f"""
## Nguồn tin cậy:

"""
        for source in sources:
            prompt += f"- {source}\n"
        
        prompt += f"""
{special}

⚠️ **QUY TẮC VÀNG:**
- TUYỆT ĐỐI tuân thủ context: {entity_hint}
- Nếu KHÔNG tìm thấy thông tin về {keyword} trong context này → Ghi: "Thông tin về {keyword} trong {niche} chưa được công bố"
- KHÔNG đoán, KHÔNG bịa
- KHÔNG nhầm lẫn với chủ đề khác

---

# CẤU TRÚC BÀI VIẾT

**Tiêu đề (H1):** Hấp dẫn, chứa từ khóa `{keyword}`, phù hợp {niche}

**Nội dung:**

"""
        
        for fmt in format_pref:
            prompt += f"- {fmt}\n"
        
        # Word count based on depth
        min_words = 1800 if depth == "deep" else 1400 if depth == "technical" else 1200
        
        prompt += f"""
---

# TỐI ƯU SEO

**Từ khóa chính:** `{keyword}`
**Xuất hiện:** 8-15 lần tự nhiên
**Độ dài:** Tối thiểu {min_words} từ

---

# PHONG CÁCH VIẾT

**{tone}** - Viết như người thật:
- Đa dạng độ dài câu/đoạn
- Ví dụ cụ thể
- Có quan điểm

**TRÁNH cụm AI:**
❌ "Trong thế giới ngày nay..."
❌ "Không thể phủ nhận..."

---

# THƯƠNG HIỆU

**{brand_name}** - Nhắc tự nhiên 1-2 lần

---

# OUTPUT FORMAT

Trả về **CHỈ JSON**:

```json
{{
    "title": "Tiêu đề (có từ khóa, phù hợp {niche})",
    "excerpt": "Mô tả SEO 150-160 ký tự",
    "content": "<p>Nội dung HTML...</p>"
}}
```

---

# NỘI DUNG THAM KHẢO

{base_content if base_content else f"Không có nội dung gốc. Tìm kiếm web về {keyword} trong context {niche}."}
"""
        
        return prompt
    
    def generate_with_auto_analysis(self, keyword, category_name, brand_name, 
                                   site_url, base_content="", 
                                   site_description="", sample_keywords=None):
        """One-shot với HYBRID mode"""
        
        # Simple website profile
        if not self.website_profile:
            self.analyze_website_universal(site_url, site_description, sample_keywords)
        
        # Generate với hard rules
        prompt = self.generate_universal_prompt(
            keyword, 
            category_name or "", 
            brand_name or "Website", 
            base_content or ""
        )
        
        return prompt


# ============== HELPER ==============

def create_universal_prompt(keyword, category_name, brand_name, site_url,
                           base_content="", site_description="", 
                           sample_keywords=None, gemini_api_key=None):
    """V3.5 Hybrid helper"""
    
    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        raise ValueError("Thiếu GEMINI_API_KEY!")
    
    generator = UniversalIntelligentGenerator(gemini_api_key)
    
    return generator.generate_with_auto_analysis(
        keyword=keyword,
        category_name=category_name or "",
        brand_name=brand_name or "Website",
        site_url=site_url,
        base_content=base_content or "",
        site_description=site_description or "",
        sample_keywords=sample_keywords
    )
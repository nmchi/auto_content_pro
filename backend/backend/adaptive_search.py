"""
Adaptive Search System - Self-learning search configuration
Learns from user input and search results to improve accuracy over time
"""

import json
import os
from datetime import datetime
from pathlib import Path


class AdaptiveSearchSystem:
    """
    Hệ thống tìm kiếm tự học
    - Khởi tạo từ mô tả ngắn (cho website mới)
    - Tự học từ mỗi keyword
    - Tự động cải thiện profile
    """
    
    def __init__(self, site_id, ai_client=None):
        self.site_id = site_id
        self.ai_client = ai_client
        self.profile_path = Path(f"profiles/{site_id}_profile.json")
        self.history_path = Path(f"profiles/{site_id}_history.json")
        
        # Tạo thư mục nếu chưa có
        self.profile_path.parent.mkdir(exist_ok=True)
        
        # Load profile và history
        self.profile = self.load_profile()
        self.search_history = self.load_history()
    
    def load_profile(self):
        """Load profile từ file"""
        if self.profile_path.exists():
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def save_profile(self):
        """Lưu profile vào file"""
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)
    
    def load_history(self):
        """Load search history"""
        if self.history_path.exists():
            with open(self.history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_history(self):
        """Lưu search history"""
        with open(self.history_path, 'w', encoding='utf-8') as f:
            json.dump(self.search_history, f, ensure_ascii=False, indent=2)
    
    def initialize_from_description(self, site_description, ai_client):
        """
        Tạo profile ban đầu từ mô tả ngắn
        
        Args:
            site_description: Mô tả website (VD: "Website review truyện manga")
            ai_client: Google Gemini client
        """
        
        prompt = f"""
Tạo search profile cho website mới dựa trên mô tả:

MÔ TẢ WEBSITE: {site_description}

Phân tích và trả về JSON với cấu trúc sau:

{{
    "site_description": "{site_description}",
    "site_niche": "chủ đề chính của website",
    "content_focus": "review|news|tutorial|entertainment|mixed",
    "target_audience": "mô tả ngắn về độc giả",
    "initial_strategy": {{
        "search_patterns": {{
            "default": "từ khóa mặc định thêm vào search",
            "specific_type_1": "pattern cho loại keyword cụ thể",
            "specific_type_2": "pattern cho loại khác"
        }},
        "priority_signals": ["từ khóa quan trọng nên có trong kết quả"],
        "exclude_signals": ["từ khóa nên tránh trong kết quả"],
        "priority_domains": ["domain ưu tiên dựa trên niche"]
    }},
    "version": 1,
    "created_at": "{datetime.now().isoformat()}"
}}

Ví dụ:
- "Website review truyện manga" → niche: "manga review", focus: "review"
- "Blog công nghệ smartphone" → niche: "tech news", focus: "news"
- "Trang tin tức game" → niche: "gaming news", focus: "news"

Chỉ trả về JSON, không có text khác.
"""
        
        try:
            from google.genai import types
            
            response = ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                )
            )
            
            # Parse JSON
            result_text = response.text.strip()
            # Remove markdown code blocks if present
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            self.profile = json.loads(result_text)
            self.save_profile()
            
            return self.profile
            
        except Exception as e:
            # Fallback: Tạo profile cơ bản
            self.profile = {
                "site_description": site_description,
                "site_niche": "general",
                "content_focus": "mixed",
                "target_audience": "general audience",
                "initial_strategy": {
                    "search_patterns": {
                        "default": "thông tin"
                    },
                    "priority_signals": [],
                    "exclude_signals": ["mua", "bán", "giá"],
                    "priority_domains": []
                },
                "version": 1,
                "created_at": datetime.now().isoformat(),
                "error": str(e)
            }
            self.save_profile()
            return self.profile
    
    def classify_keyword(self, keyword, ai_client):
        """
        Phân loại keyword để chọn strategy phù hợp
        
        Returns:
            str: Loại keyword (VD: "anime_manga", "tech_product", "general")
        """
        
        if not self.profile:
            return "default"
        
        prompt = f"""
Phân loại keyword cho website: {self.profile['site_niche']}

KEYWORD: {keyword}

Dựa vào niche của website, keyword này thuộc loại nào?

Trả về 1 trong các loại sau (chỉ trả về tên loại, không giải thích):
- anime_manga (tên anime/manga/manhwa/manhua)
- tech_product (sản phẩm công nghệ: smartphone, laptop, etc)
- person_name (tên người/tác giả/nhân vật)
- game_title (tên game)
- general_topic (chủ đề chung)
- default (không xác định)

Chỉ trả về 1 từ, không có dấu câu hay giải thích.
"""
        
        try:
            from google.genai import types
            
            response = ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=20,
                )
            )
            
            keyword_type = response.text.strip().lower()
            # Clean up response
            keyword_type = keyword_type.replace('.', '').replace(',', '')
            
            return keyword_type if keyword_type else "default"
            
        except Exception as e:
            return "default"
    
    def get_search_strategy(self, keyword, keyword_type):
        """
        Lấy search strategy dựa trên loại keyword
        
        Returns:
            dict: Strategy với search_suffix, priority_signals, exclude_signals
        """
        
        if not self.profile:
            return {
                "search_suffix": "",
                "priority_signals": [],
                "exclude_signals": ["mua", "bán"]
            }
        
        patterns = self.profile['initial_strategy']['search_patterns']
        
        # Lấy pattern phù hợp
        if keyword_type in patterns:
            search_suffix = patterns[keyword_type]
        else:
            search_suffix = patterns.get('default', '')
        
        return {
            "search_suffix": search_suffix,
            "priority_signals": self.profile['initial_strategy'].get('priority_signals', []),
            "exclude_signals": self.profile['initial_strategy'].get('exclude_signals', []),
            "priority_domains": self.profile['initial_strategy'].get('priority_domains', [])
        }
    
    def build_search_query(self, keyword, strategy):
        """
        Tạo Google search query tối ưu
        
        Args:
            keyword: Từ khóa gốc
            strategy: Strategy dict
            
        Returns:
            str: Search query đã tối ưu
        """
        
        suffix = strategy.get('search_suffix', '')
        
        if suffix:
            return f"{keyword} {suffix}"
        else:
            return keyword
    
    def score_result_relevance(self, result_title, result_snippet, strategy):
        """
        Đánh giá độ liên quan của kết quả tìm kiếm
        
        Returns:
            float: Điểm từ 0-1
        """
        
        text = f"{result_title} {result_snippet}".lower()
        score = 0.5  # Base score
        
        # Check priority signals
        priority_signals = strategy.get('priority_signals', [])
        if priority_signals:
            matches = sum(1 for signal in priority_signals if signal.lower() in text)
            score += (matches / len(priority_signals)) * 0.3
        
        # Check exclude signals (penalty)
        exclude_signals = strategy.get('exclude_signals', [])
        if exclude_signals:
            matches = sum(1 for signal in exclude_signals if signal.lower() in text)
            score -= (matches / max(len(exclude_signals), 1)) * 0.4
        
        return max(0, min(1, score))
    
    def learn_from_search(self, keyword, keyword_type, search_query, result_url, result_title):
        """
        Học từ kết quả tìm kiếm
        
        Lưu vào history để sau này refine profile
        """
        
        self.search_history.append({
            'keyword': keyword,
            'keyword_type': keyword_type,
            'search_query': search_query,
            'result_url': result_url,
            'result_title': result_title,
            'timestamp': datetime.now().isoformat()
        })
        
        self.save_history()
        
        # Auto refine sau mỗi 10 searches
        if len(self.search_history) % 10 == 0:
            return True  # Signal to refine
        
        return False
    
    def refine_profile(self, ai_client):
        """
        Cải thiện profile dựa trên search history
        """
        
        if len(self.search_history) < 5:
            return False  # Chưa đủ data
        
        recent = self.search_history[-20:]  # 20 searches gần nhất
        
        # Format history for AI
        history_text = "\n".join([
            f"- Keyword: {h['keyword']} | Type: {h['keyword_type']} | Query: {h['search_query']}"
            for h in recent
        ])
        
        prompt = f"""
Phân tích search history và cải thiện profile:

CURRENT PROFILE:
{json.dumps(self.profile, ensure_ascii=False, indent=2)}

RECENT SEARCHES (20 gần nhất):
{history_text}

Dựa vào patterns trong search history, đề xuất cải thiện:

1. Có pattern nào lặp lại không? (VD: nhiều keyword về anime → nên thêm "anime" vào suffix)
2. Nên thêm/bỏ từ khóa nào trong priority_signals/exclude_signals?
3. Có domain nào thường cho kết quả tốt không?

Trả về JSON cập nhật cho "initial_strategy", giữ nguyên các field khác:

{{
    "initial_strategy": {{
        "search_patterns": {{...}},
        "priority_signals": [...],
        "exclude_signals": [...],
        "priority_domains": [...]
    }},
    "version": {self.profile.get('version', 1) + 1},
    "last_refined": "{datetime.now().isoformat()}"
}}

Chỉ trả về JSON, không có text khác.
"""
        
        try:
            from google.genai import types
            
            response = ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1500,
                )
            )
            
            # Parse JSON
            result_text = response.text.strip()
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            improvements = json.loads(result_text)
            
            # Update profile
            self.profile['initial_strategy'] = improvements['initial_strategy']
            self.profile['version'] = improvements.get('version', self.profile.get('version', 1) + 1)
            self.profile['last_refined'] = improvements.get('last_refined', datetime.now().isoformat())
            
            self.save_profile()
            
            return True
            
        except Exception as e:
            print(f"Refine error: {e}")
            return False
    
    def get_stats(self):
        """Lấy thống kê về learning progress"""
        
        return {
            'total_searches': len(self.search_history),
            'profile_version': self.profile.get('version', 1) if self.profile else 0,
            'site_niche': self.profile.get('site_niche', 'Unknown') if self.profile else 'Not initialized',
            'last_refined': self.profile.get('last_refined', 'Never') if self.profile else 'Never',
            'is_initialized': self.profile is not None
        }


# Helper function for easy access
def get_adaptive_system(site_id, ai_client=None):
    """Get or create adaptive search system for a site"""
    return AdaptiveSearchSystem(site_id, ai_client)

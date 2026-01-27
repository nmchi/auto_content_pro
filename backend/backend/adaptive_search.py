"""
Adaptive Search V2 - AI-Powered Search Query Optimization
Sử dụng AI để phân tích keyword và tạo search query chính xác
"""

import json
import os
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types


class AdaptiveSearchV2:
    """
    Adaptive Search với AI-powered query optimization
    
    Khác biệt so với v1:
    - AI phân tích keyword để hiểu ý định tìm kiếm
    - Tự động thêm context phù hợp (tác giả, năm, thể loại...)
    - Học từ kết quả tìm kiếm để cải thiện
    """
    
    def __init__(self, site_id, ai_client):
        self.site_id = site_id
        self.ai_client = ai_client
        self.profile_path = Path(f"profiles/{site_id}_profile.json")
        self.history_path = Path(f"profiles/{site_id}_history.json")
        
        # Tạo thư mục
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
        """Lưu profile"""
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)
    
    def load_history(self):
        """Load history"""
        if self.history_path.exists():
            with open(self.history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_history(self):
        """Lưu history"""
        with open(self.history_path, 'w', encoding='utf-8') as f:
            json.dump(self.search_history, f, ensure_ascii=False, indent=2)
    
    def initialize_from_description(self, site_description):
        """Tạo profile từ mô tả website"""
        
        prompt = f"""
Tạo search profile cho website:

MÔ TẢ: {site_description}

Trả về JSON:

{{
    "site_description": "{site_description}",
    "site_niche": "chủ đề chính",
    "content_focus": "review|news|tutorial|entertainment",
    "search_strategy": {{
        "default_context": "context mặc định thêm vào search",
        "domain_hints": ["domain ưu tiên"],
        "avoid_terms": ["từ cần tránh trong kết quả"]
    }},
    "version": 1,
    "created_at": "{datetime.now().isoformat()}"
}}

Chỉ trả về JSON.
"""
        
        try:
            response = self.ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                )
            )
            
            result_text = response.text.strip()
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            self.profile = json.loads(result_text)
            self.save_profile()
            
            return self.profile
            
        except Exception as e:
            # Fallback
            self.profile = {
                "site_description": site_description,
                "site_niche": "general",
                "content_focus": "mixed",
                "search_strategy": {
                    "default_context": "",
                    "domain_hints": [],
                    "avoid_terms": ["mua", "bán", "giá"]
                },
                "version": 1,
                "created_at": datetime.now().isoformat(),
                "error": str(e)
            }
            self.save_profile()
            return self.profile
    
    def analyze_keyword_for_search(self, keyword, category_name=""):
        """
        AI phân tích keyword để tạo search query tối ưu
        
        Args:
            keyword: Từ khóa gốc
            category_name: Danh mục (optional)
        
        Returns:
            dict: Search strategy
        """
        
        site_context = ""
        if self.profile:
            site_context = f"Website niche: {self.profile.get('site_niche', 'general')}"
        
        analysis_prompt = f"""
Phân tích keyword để tạo Google search query tối ưu.

{site_context}
CATEGORY: {category_name}
KEYWORD: {keyword}

Nhiệm vụ: Xác định keyword này là gì và cần search thế nào để tìm bài viết gốc chất lượng.

Trả về JSON:

{{
    "keyword_type": "author_name|book_title|character_name|topic|event",
    "search_intent": "find_bio|find_review|find_info|find_news",
    "optimal_query": "query tối ưu để search Google",
    "query_components": {{
        "base": "keyword gốc",
        "context": "context thêm vào (vd: tiểu thuyết, tác giả, review...)",
        "filters": "bộ lọc (vd: site:domain, filetype:...)"
    }},
    "expected_sources": ["domain hoặc loại nguồn mong đợi"],
    "avoid_sources": ["domain hoặc loại nguồn cần tránh"]
}}

VÍ DỤ:
- Keyword "Thiên Tằm Thổ Đậu" + Category "Review Tác Giả"
  → optimal_query: "Thiên Tằm Thổ Đậu tác giả tiểu thuyết"
  → expected_sources: ["wikipedia.org", "novelupdates.com"]

- Keyword "Đấu Phá Thương Khung" + Category "Review Truyện"
  → optimal_query: "Đấu Phá Thương Khung review truyện"
  → expected_sources: ["truyenfull.vn", "wikidich.com"]

Chỉ trả về JSON.
"""
        
        try:
            response = self.ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=analysis_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=800,
                )
            )
            
            result_text = response.text.strip()
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            strategy = json.loads(result_text)
            
            print(f"📊 Keyword type: {strategy.get('keyword_type', 'unknown')}")
            print(f"🔍 Optimal query: {strategy.get('optimal_query', keyword)}")
            
            return strategy
            
        except Exception as e:
            print(f"⚠️ Lỗi phân tích keyword: {e}")
            # Fallback: search query đơn giản
            return {
                "keyword_type": "unknown",
                "search_intent": "find_info",
                "optimal_query": keyword,
                "query_components": {
                    "base": keyword,
                    "context": "",
                    "filters": ""
                },
                "expected_sources": [],
                "avoid_sources": []
            }
    
    def build_search_query(self, keyword, category_name=""):
        """
        Tạo search query tối ưu
        
        Args:
            keyword: Từ khóa
            category_name: Danh mục
        
        Returns:
            str: Optimized search query
        """
        
        # Analyze keyword
        strategy = self.analyze_keyword_for_search(keyword, category_name)
        
        # Return optimal query
        return strategy.get('optimal_query', keyword)
    
    def score_search_result(self, result_url, result_title, result_snippet, strategy):
        """
        Đánh giá kết quả tìm kiếm
        
        Args:
            result_url: URL kết quả
            result_title: Tiêu đề
            result_snippet: Snippet
            strategy: Search strategy từ analyze_keyword_for_search
        
        Returns:
            float: Score 0-1
        """
        
        score = 0.5  # Base score
        
        url_lower = result_url.lower()
        title_lower = result_title.lower()
        snippet_lower = result_snippet.lower()
        
        # Check expected sources
        expected_sources = strategy.get('expected_sources', [])
        if expected_sources:
            for source in expected_sources:
                if source.lower() in url_lower:
                    score += 0.3
                    break
        
        # Check avoid sources (penalty)
        avoid_sources = strategy.get('avoid_sources', [])
        if avoid_sources:
            for source in avoid_sources:
                if source.lower() in url_lower:
                    score -= 0.4
                    break
        
        # Check keyword in title (relevance)
        keyword_type = strategy.get('keyword_type', '')
        
        # Keyword phải có trong title hoặc snippet
        query_base = strategy.get('query_components', {}).get('base', '').lower()
        if query_base:
            if query_base in title_lower:
                score += 0.2
            elif query_base in snippet_lower:
                score += 0.1
        
        return max(0, min(1, score))
    
    def learn_from_search(self, keyword, category_name, search_query, selected_url, selected_title):
        """
        Học từ kết quả tìm kiếm
        
        Args:
            keyword: Keyword
            category_name: Category
            search_query: Query đã dùng
            selected_url: URL đã chọn
            selected_title: Title của URL đã chọn
        """
        
        self.search_history.append({
            'keyword': keyword,
            'category': category_name,
            'search_query': search_query,
            'result_url': selected_url,
            'result_title': selected_title,
            'timestamp': datetime.now().isoformat()
        })
        
        self.save_history()
        
        # Auto refine sau 10 searches
        if len(self.search_history) % 10 == 0:
            return True
        
        return False
    
    def refine_profile(self):
        """
        Cải thiện profile dựa trên history
        """
        
        if len(self.search_history) < 5:
            return False
        
        recent = self.search_history[-20:]
        
        # Format history
        history_text = "\n".join([
            f"- Keyword: {h['keyword']} | Category: {h.get('category', 'N/A')} | Query: {h['search_query']}"
            for h in recent
        ])
        
        prompt = f"""
Phân tích search history và cải thiện profile:

CURRENT PROFILE:
{json.dumps(self.profile, ensure_ascii=False, indent=2)}

RECENT SEARCHES:
{history_text}

Dựa vào patterns, đề xuất cải thiện search_strategy:

{{
    "search_strategy": {{
        "default_context": "cập nhật context",
        "domain_hints": ["cập nhật domains"],
        "avoid_terms": ["cập nhật terms to avoid"]
    }},
    "version": {self.profile.get('version', 1) + 1},
    "last_refined": "{datetime.now().isoformat()}"
}}

Chỉ trả về JSON.
"""
        
        try:
            response = self.ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                )
            )
            
            result_text = response.text.strip()
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            improvements = json.loads(result_text)
            
            # Update profile
            self.profile['search_strategy'] = improvements['search_strategy']
            self.profile['version'] = improvements.get('version', self.profile.get('version', 1) + 1)
            self.profile['last_refined'] = improvements.get('last_refined', datetime.now().isoformat())
            
            self.save_profile()
            
            return True
            
        except Exception as e:
            print(f"Refine error: {e}")
            return False
    
    def get_stats(self):
        """Lấy stats"""
        return {
            'total_searches': len(self.search_history),
            'profile_version': self.profile.get('version', 0) if self.profile else 0,
            'site_niche': self.profile.get('site_niche', 'Unknown') if self.profile else 'Not initialized',
            'last_refined': self.profile.get('last_refined', 'Never') if self.profile else 'Never',
            'is_initialized': self.profile is not None
        }


# ============== HELPER FUNCTION ==============

def get_adaptive_search_v2(site_id, ai_client):
    """Get or create adaptive search v2 for a site"""
    return AdaptiveSearchV2(site_id, ai_client)


# ============== TEST ==============

if __name__ == "__main__":
    import sys
    from google import genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        sys.exit(1)
    
    # Test
    print("=== Testing Adaptive Search V2 ===\n")
    
    client = genai.Client(api_key=api_key)
    search = AdaptiveSearchV2("test_site", client)
    
    # Initialize
    print("1. Initializing profile...")
    profile = search.initialize_from_description("Website review truyện manga và tiểu thuyết")
    print(f"   ✅ Niche: {profile['site_niche']}\n")
    
    # Test keyword analysis
    test_keywords = [
        ("Thiên Tằm Thổ Đậu", "Review Tác Giả"),
        ("Đấu Phá Thương Khung", "Review Truyện"),
        ("mơ thấy rắn", "Giải Mã Giấc Mơ"),
    ]
    
    for keyword, category in test_keywords:
        print(f"2. Testing: {keyword} ({category})")
        query = search.build_search_query(keyword, category)
        print(f"   → Optimized query: {query}\n")
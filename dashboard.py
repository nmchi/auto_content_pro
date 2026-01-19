import streamlit as st
import subprocess
import os
import sys
import pandas as pd
import time
import requests
from google import genai
from google.genai import types
from requests.auth import HTTPBasicAuth

st.set_page_config(page_title="Auto Content Pro (Free Version)", layout="wide")
st.title("🚀 Auto Content Pro: All-in-One (Gemini Powered)")

# --- PROMPT MẪU CHUYÊN NGHIỆP (Theo chuẩn vnrewrite) ---
DEFAULT_PROMPT_TEMPLATE = """
## VAI TRÒ
{role_description}

## NHIỆM VỤ
Viết lại bài viết dưới đây thành bài viết **mới hoàn toàn**, chuẩn SEO, hấp dẫn người đọc.

## TỪ KHÓA CHÍNH
`{keyword}`

## THƯƠNG HIỆU
`{brand_name}`

## YÊU CẦU NỘI DUNG

### CẤU TRÚC BÀI VIẾT
- **Tiêu đề (H1)**: Tự nhiên, hấp dẫn, chứa từ khóa chính
- **Mở đầu** (2-3 câu): Giới thiệu vấn đề, nhắc đến thương hiệu tự nhiên
- **Các phần chính (H2)**: 4-7 phần, mỗi phần có nội dung thực chất
- **Kết luận (H2)**: Tổng kết, ý nghĩa

### PHONG CÁCH VIẾT
- Viết như người thật, không như AI
- Đa dạng độ dài đoạn văn (ngắn 1-2 câu, trung bình 3-4 câu, dài 5-6 câu)
- Giọng văn chân thực, kể chuyện cho bạn bè
- Dùng ví dụ cụ thể, có quan điểm riêng
- KHÔNG dùng các cụm từ sáo rỗng: "Trong thế giới...", "Không thể phủ nhận...", "Điều đáng nói là..."

### TỐI ƯU SEO
- Từ khóa chính xuất hiện ít nhất 5-7 lần, phân bố tự nhiên
- Trong 100 từ đầu tiên phải có từ khóa chính
- Các tiêu đề H2 nên chứa biến thể của từ khóa
- Bài viết tối thiểu 800 từ

### TÍCH HỢP THƯƠNG HIỆU
- Nhắc thương hiệu 1-2 lần ở mở đầu hoặc kết bài
- Ví dụ: "Theo tổng hợp từ {brand_name}..." hoặc "Bài viết được biên soạn bởi {brand_name}..."
- KHÔNG quảng cáo, PR

## ĐỊNH DẠNG OUTPUT
Trả về **DUY NHẤT** JSON với cấu trúc sau (không có text nào khác):
```json
{{
    "title": "Tiêu đề bài viết (có từ khóa)",
    "excerpt": "Mô tả ngắn 150-160 ký tự cho SEO",
    "content": "<p>Nội dung HTML đầy đủ với các thẻ h2, h3, p, ul, li...</p>"
}}
```

## NỘI DUNG GỐC CẦN VIẾT LẠI
{content}
"""

# --- PROMPT MẪU CHO TỪNG DANH MỤC ---
CATEGORY_ROLES = {
    "Truyện Tranh": "Với tư cách là biên tập viên chuyên về truyện tranh/manga/manhwa/manhua tại website, bạn am hiểu sâu sắc về các thể loại, tác giả, và xu hướng đọc truyện của độc giả Việt Nam.",
    "Review Truyện": "Với tư cách là reviewer truyện chuyên nghiệp, bạn có khả năng phân tích cốt truyện, nhân vật, và đưa ra đánh giá khách quan, hấp dẫn người đọc.",
    "Tiên Hiệp": "Với tư cách là chuyên gia về thể loại tiên hiệp/huyền huyễn, bạn am hiểu hệ thống tu luyên, cảnh giới, và văn hóa tiểu thuyết Trung Quốc.",
    "Manga": "Với tư cách là chuyên gia manga Nhật Bản, bạn am hiểu văn hóa otaku, các nhà xuất bản, mangaka nổi tiếng và xu hướng manga hiện tại.",
    "Manhwa": "Với tư cách là chuyên gia manhwa Hàn Quốc, bạn am hiểu về webtoon, các nền tảng phát hành và đặc trưng của truyện tranh Hàn.",
    "Manhua": "Với tư cách là chuyên gia manhua Trung Quốc, bạn am hiểu về các thể loại tu chân, huyền huyễn và thị trường truyện tranh Trung Quốc.",
    "Giải Mã Giấc Mơ": "Với tư cách là chuyên gia giải mã giấc mơ am hiểu sâu sắc văn hóa và tâm linh người Việt, đặc biệt là mối liên hệ giữa giấc mơ và các con số may mắn.",
    "Phong Thủy": "Với tư cách là chuyên gia phong thủy, bạn am hiểu về ngũ hành, bát quái, và cách ứng dụng phong thủy trong đời sống hiện đại.",
    "Tử Vi": "Với tư cách là chuyên gia tử vi/chiêm tinh, bạn am hiểu về 12 cung hoàng đạo, tử vi Việt Nam và cách luận giải vận mệnh.",
    "default": "Với tư cách là nhà sáng tạo nội dung chuyên nghiệp, bạn có khả năng viết bài hấp dẫn, chuẩn SEO và phù hợp với độc giả Việt Nam."
}

# --- KHỞI TẠO STATE ---
if 'wp_categories' not in st.session_state: st.session_state['wp_categories'] = {}
if 'is_connected' not in st.session_state: st.session_state['is_connected'] = False
if 'cat_prompts' not in st.session_state: st.session_state['cat_prompts'] = {}
if 'brand_name' not in st.session_state: st.session_state['brand_name'] = "VanGioiComics"

def get_role_for_category(category_name):
    """Lấy vai trò phù hợp cho danh mục"""
    for key, role in CATEGORY_ROLES.items():
        if key.lower() in category_name.lower():
            return role
    return CATEGORY_ROLES["default"]

def generate_prompt_for_category(category_name, brand_name):
    """Tạo prompt hoàn chỉnh cho danh mục"""
    role = get_role_for_category(category_name)
    
    prompt = DEFAULT_PROMPT_TEMPLATE.replace("{role_description}", role)
    prompt = prompt.replace("{brand_name}", brand_name)
    # Giữ nguyên {keyword} và {content} để pipeline thay thế sau
    
    return prompt

def generate_prompt_with_gemini(api_key, category_name="", brand_name=""):
    """Dùng Gemini để tạo prompt tùy chỉnh"""
    if not api_key:
        return "⚠️ Chưa có Gemini API Key!"
    
    try:
        client = genai.Client(api_key=api_key)
        
        base_role = get_role_for_category(category_name)
        
        user_request = f"""
Bạn là chuyên gia Prompt Engineering. Hãy tạo một System Prompt chuyên nghiệp để viết lại bài viết.

THÔNG TIN:
- Danh mục: {category_name}
- Thương hiệu: {brand_name}
- Vai trò gợi ý: {base_role}

YÊU CẦU PROMPT:
1. Bắt đầu bằng phần VAI TRÒ chi tiết, phù hợp với danh mục "{category_name}"
2. Có hướng dẫn cấu trúc bài viết (H1, H2, mở đầu, kết luận)
3. Yêu cầu phong cách viết tự nhiên như người thật
4. Tối ưu SEO với từ khóa
5. Tích hợp thương hiệu "{brand_name}" tự nhiên
6. Output BẮT BUỘC là JSON: {{"title": "...", "excerpt": "...", "content": "HTML..."}}
7. BẮT BUỘC giữ nguyên 2 placeholder: {{keyword}} và {{content}}

Trả về prompt hoàn chỉnh, sẵn sàng sử dụng.
"""

        candidate_models = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash']
        
        for model_name in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_request,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=3000,
                    )
                )
                return response.text.strip()
            except Exception as e:
                continue
        
        # Fallback: Trả về prompt mặc định
        return generate_prompt_for_category(category_name, brand_name)

    except Exception as e:
        return f"Lỗi: {str(e)}"

# --- SIDEBAR: CẤU HÌNH ---
with st.sidebar:
    st.header("1. API Keys & Search")
    gemini_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
    google_api_key = st.text_input("Google API Key", type="password")
    google_cse_id = st.text_input("Search Engine ID")
    
    st.header("2. Kết nối WordPress")
    wp_url = st.text_input("WP URL", value="https://vangioicomics.com/wp-json/wp/v2")
    wp_user = st.text_input("WP User", value="admin")
    wp_pass = st.text_input("WP App Pass", type="password")
    
    st.header("3. Thương hiệu")
    brand_name = st.text_input("Tên thương hiệu", value=st.session_state['brand_name'])
    st.session_state['brand_name'] = brand_name
    
    if st.button("🔄 Kết nối & Tải Chuyên mục", use_container_width=True):
        if wp_url and wp_pass:
            try:
                auth = HTTPBasicAuth(wp_user, wp_pass)
                res = requests.get(f"{wp_url}/categories?per_page=100", auth=auth, timeout=10)
                if res.status_code == 200:
                    st.session_state['wp_categories'] = {i['name']: i['id'] for i in res.json()}
                    st.session_state['is_connected'] = True
                    st.success(f"✅ Đã tải {len(res.json())} chuyên mục!")
                else: 
                    st.error(f"Lỗi kết nối: {res.status_code}")
            except Exception as e: 
                st.error(str(e))

# --- GIAO DIỆN CHÍNH ---
if not st.session_state['is_connected']:
    st.info("👋 Chào bạn! Hãy nhập thông tin bên trái và bấm **KẾT NỐI** để bắt đầu.")
    
    st.markdown("---")
    st.subheader("📋 Hướng dẫn nhanh")
    st.markdown("""
    1. **Gemini API Key**: Lấy từ [Google AI Studio](https://aistudio.google.com/apikey)
    2. **Google API Key + CSE ID**: Để tìm kiếm bài viết gốc
    3. **WP App Pass**: Tạo trong WordPress > Users > Application Passwords
    """)
else:
    # TẠO 3 TAB CHÍNH
    tab_run, tab_prompt, tab_settings = st.tabs(["🚀 Chạy", "✨ Quản lý Prompt", "⚙️ Cài đặt"])

    # === TAB QUẢN LÝ PROMPT ===
    with tab_prompt:
        st.subheader("Quản lý Prompt theo Danh mục")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            target_cat_name = st.selectbox(
                "Chọn danh mục:", 
                list(st.session_state['wp_categories'].keys()),
                key="prompt_cat_select"
            )
            
            st.markdown("---")
            st.markdown("**Tạo prompt nhanh:**")
            
            if st.button("📝 Tạo từ mẫu có sẵn", use_container_width=True):
                generated = generate_prompt_for_category(target_cat_name, brand_name)
                st.session_state['cat_prompts'][target_cat_name] = generated
                st.rerun()
            
            if st.button("🤖 Nhờ Gemini viết", use_container_width=True, type="primary"):
                if not gemini_key:
                    st.error("Thiếu Gemini API Key!")
                else:
                    with st.spinner("Gemini đang tạo prompt..."):
                        generated = generate_prompt_with_gemini(gemini_key, target_cat_name, brand_name)
                        st.session_state['cat_prompts'][target_cat_name] = generated
                        st.rerun()
        
        with col2:
            current_prompt = st.session_state['cat_prompts'].get(target_cat_name, "")
            
            if current_prompt:
                st.success(f"✅ Đã có prompt cho: {target_cat_name}")
            else:
                st.warning("⚠️ Chưa có prompt. Nhấn 'Tạo từ mẫu' hoặc 'Nhờ Gemini viết'.")
                current_prompt = generate_prompt_for_category(target_cat_name, brand_name)
            
            edited_prompt = st.text_area(
                "Nội dung Prompt (có thể chỉnh sửa):",
                value=current_prompt,
                height=500,
                key=f"prompt_editor_{target_cat_name}"
            )
            
            if st.button("💾 Lưu Prompt", use_container_width=True):
                st.session_state['cat_prompts'][target_cat_name] = edited_prompt
                st.success(f"✅ Đã lưu prompt cho {target_cat_name}!")

    # === TAB CHẠY ===
    with tab_run:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("1. Chọn danh mục đăng")
            run_cat_name = st.selectbox(
                "Đăng vào:", 
                list(st.session_state['wp_categories'].keys()), 
                key="run_cat_select"
            )
            selected_cat_id = st.session_state['wp_categories'][run_cat_name]
            
            # Kiểm tra prompt
            active_prompt = st.session_state['cat_prompts'].get(run_cat_name)
            if active_prompt:
                st.success(f"✅ Đã có Prompt cho: {run_cat_name}")
                with st.expander("Xem prompt"):
                    st.code(active_prompt[:500] + "..." if len(active_prompt) > 500 else active_prompt)
            else:
                st.warning("⚠️ Chưa có Prompt riêng, sẽ dùng mặc định.")
                active_prompt = generate_prompt_for_category(run_cat_name, brand_name)

        with col2:
            st.subheader("2. Nhập từ khóa")
            keywords_text = st.text_area(
                "Danh sách Keyword (mỗi dòng 1 từ khóa):", 
                height=200, 
                placeholder="vạn cổ thần đế\nđấu phá thương khung\ntru tiên"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                run_button = st.button("🔥 CHẠY NGAY", type="primary", use_container_width=True)
            with col_btn2:
                test_button = st.button("🧪 Test 1 keyword", use_container_width=True)
        
        if run_button or test_button:
            keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()]
            
            if test_button and keywords:
                keywords = [keywords[0]]  # Chỉ lấy keyword đầu tiên
            
            if not keywords:
                st.error("❌ Chưa nhập từ khóa!")
            elif not gemini_key:
                st.error("❌ Thiếu Gemini API Key!")
            elif not google_api_key or not google_cse_id:
                st.error("❌ Thiếu Google API Key hoặc CSE ID!")
            else:
                st.info(f"🚀 Đang chạy {len(keywords)} keyword vào mục: {run_cat_name}")
                progress = st.progress(0)
                status = st.empty()
                log_container = st.container()
                
                # Setup Environment
                env = os.environ.copy()
                env['GEMINI_API_KEY'] = gemini_key
                env['GOOGLE_API_KEY'] = google_api_key
                env['GOOGLE_CSE_ID'] = google_cse_id
                env['WP_URL'] = wp_url
                env['WP_USER'] = wp_user
                env['WP_APP_PASSWORD'] = wp_pass
                env['WP_CATEGORY_ID'] = str(selected_cat_id)
                env['BRAND_NAME'] = brand_name
                env['CATEGORY_NAME'] = run_cat_name  # Truyền tên danh mục để prompt hiểu context
                
                if active_prompt:
                    env['CHOSEN_PROMPT'] = active_prompt
                
                results = []
                for idx, kw in enumerate(keywords):
                    status.markdown(f"⏳ **Đang xử lý:** `{kw}` ({idx+1}/{len(keywords)})")
                    
                    cmd = [sys.executable, "-m", "scrapy", "crawl", "google_bot", "-a", f"keyword={kw}"]
                    proc = subprocess.run(
                        cmd, 
                        cwd=os.path.join(os.getcwd(), 'backend'), 
                        env=env, 
                        capture_output=True, 
                        text=True
                    )
                    
                    if "DANG BAI THANH CONG" in proc.stderr:
                        st.toast(f"✅ Thành công: {kw}")
                        results.append({"Keyword": kw, "Status": "✅ Thành công", "Details": ""})
                    else:
                        st.toast(f"❌ Lỗi: {kw}")
                        # Tìm lỗi cụ thể
                        error_detail = ""
                        if "Không tìm thấy kết quả" in proc.stderr:
                            error_detail = "Không tìm thấy bài viết gốc"
                        elif "AI Thất bại" in proc.stderr:
                            error_detail = "AI không xử lý được"
                        elif "403" in proc.stderr:
                            error_detail = "Google API bị chặn"
                        else:
                            error_detail = "Lỗi không xác định"
                        
                        results.append({"Keyword": kw, "Status": "❌ Lỗi", "Details": error_detail})
                        
                        with log_container.expander(f"📋 Log lỗi: {kw}"):
                            st.code(proc.stderr[-2000:] if len(proc.stderr) > 2000 else proc.stderr)
                    
                    progress.progress((idx+1)/len(keywords))
                    time.sleep(1)
                
                st.success("🎉 Hoàn tất!")
                st.dataframe(pd.DataFrame(results), use_container_width=True)

    # === TAB CÀI ĐẶT ===
    with tab_settings:
        st.subheader("⚙️ Cài đặt nâng cao")
        
        st.markdown("### Danh sách vai trò mẫu")
        st.markdown("Các vai trò này sẽ được sử dụng khi tạo prompt từ mẫu:")
        
        for cat, role in CATEGORY_ROLES.items():
            with st.expander(f"📁 {cat}"):
                st.text_area(f"Vai trò cho {cat}", value=role, height=100, disabled=True)
        
        st.markdown("---")
        st.markdown("### Xóa dữ liệu")
        if st.button("🗑️ Xóa tất cả Prompt đã lưu", type="secondary"):
            st.session_state['cat_prompts'] = {}
            st.success("Đã xóa tất cả prompt!")
            st.rerun()
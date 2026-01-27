"""
Auto Content Pro Dashboard - V3 Clean Version
Only uses V3 Universal System

File: dashboard.py
"""

import streamlit as st
import os
import subprocess
import sys
import time
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

# Page config
st.set_page_config(
    page_title="Auto Content Pro - V3",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🚀 Auto Content Pro - V3 Universal")
st.markdown("**V3 CLEAN** - Tự động adapt với mọi niche")

# Initialize session state
if 'is_connected' not in st.session_state:
    st.session_state['is_connected'] = False
if 'wp_categories' not in st.session_state:
    st.session_state['wp_categories'] = {}

# ============================================================
# SIDEBAR - Configuration
# ============================================================

with st.sidebar:
    st.header("1. API Keys & Search")
    
    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Get from: https://aistudio.google.com/app/apikey"
    )
    
    google_api_key = st.text_input(
        "Google API Key",
        type="password",
        help="Get from: https://console.cloud.google.com/"
    )
    
    google_cse_id = st.text_input(
        "Search Engine ID",
        help="Get from: https://programmablesearchengine.google.com/"
    )
    
    st.header("2. Kết nối WordPress")
    
    wp_url = st.text_input(
        "WP URL",
        value="https://yoursite.com/wp-json/wp/v2",
        help="WordPress REST API endpoint"
    )
    
    wp_user = st.text_input(
        "WP User",
        value="admin"
    )
    
    wp_pass = st.text_input(
        "WP App Pass",
        type="password",
        help="Application Password (not regular password)"
    )
    
    st.header("3. Thương hiệu")
    
    brand_name = st.text_input(
        "Tên thương hiệu",
        value=st.session_state.get('brand_name', 'YourBrand'),
        help="Tên brand sẽ xuất hiện trong nội dung"
    )
    st.session_state['brand_name'] = brand_name
    
    st.header("4. Model AI")
    
    preferred_model = st.selectbox(
        "Chọn model:",
        options=["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0,
        help="💡 Flash: Nhanh, rẻ (~$0.002/request) | Pro: Chất lượng cao (~$0.02/request)"
    )
    st.session_state['preferred_model'] = preferred_model
    
    st.header("5. V3 Universal System")
    
    st.success("✨ V3 CLEAN - Chỉ dùng Universal System")
    
    with st.expander("⚙️ Cấu hình V3 (Lần đầu tiên)", expanded=True):
        st.markdown("""
        **V3 cần hiểu website của bạn:**
        - **Mô tả**: 1 câu ngắn về niche
        - **Sample keywords**: 3-5 keywords đại diện
        
        **Chỉ cần nhập 1 lần**, V3 sẽ tự động cache!
        """)
        
        site_description = st.text_input(
            "Mô tả website",
            placeholder="VD: Website review smartphone và công nghệ",
            help="1 câu ngắn mô tả niche của bạn"
        )
        
        sample_keywords_input = st.text_area(
            "Sample Keywords (3-5 keywords)",
            placeholder="iPhone 15 Pro Max\nSamsung Galaxy S24\nXiaomi 14",
            help="Mỗi dòng 1 keyword. V3 sẽ học từ những keywords này.",
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset Cache", help="Xóa cache để V3 học lại từ đầu"):
                import shutil
                try:
                    shutil.rmtree('profiles')
                    st.success("✅ Cache cleared!")
                except:
                    st.info("No cache to clear")
        
        with col2:
            if os.path.exists('profiles'):
                st.info(f"📦 Cache exists")
            else:
                st.warning("⚠️ No cache")
        
        st.info("💡 **Tip:** Sample keywords giúp V3 hiểu niche nhanh hơn. Không bắt buộc nhưng khuyến nghị.")
    
    st.divider()
    
    if st.button("🔄 Kết nối & Tải Chuyên mục", use_container_width=True):
        if not wp_url or not wp_pass:
            st.error("❌ Thiếu WP URL hoặc App Password!")
        else:
            try:
                with st.spinner("Đang kết nối..."):
                    auth = HTTPBasicAuth(wp_user, wp_pass)
                    res = requests.get(
                        f"{wp_url}/categories?per_page=100", 
                        auth=auth, 
                        timeout=10
                    )
                    
                    if res.status_code == 200:
                        categories = res.json()
                        st.session_state['wp_categories'] = {
                            cat['name']: cat['id'] for cat in categories
                        }
                        st.session_state['is_connected'] = True
                        st.success(f"✅ Loaded {len(categories)} categories!")
                    else:
                        st.error(f"❌ Connection error: HTTP {res.status_code}")
                        st.error(res.text[:500])
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ============================================================
# MAIN CONTENT
# ============================================================

# Connection status
if st.session_state['is_connected']:
    st.success("✅ Đã kết nối WordPress")
else:
    st.warning("⚠️ Chưa kết nối WordPress. Vui lòng cấu hình ở sidebar.")

# Tabs
tab1, tab2, tab3 = st.tabs(["🚀 Chạy", "📊 Stats", "ℹ️ Hướng dẫn"])

# ============================================================
# TAB 1: RUN
# ============================================================

with tab1:
    st.header("🚀 Chạy Auto Content")
    
    if not st.session_state['is_connected']:
        st.error("❌ Chưa kết nối WordPress! Vui lòng kết nối ở sidebar trước.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            selected_category = st.selectbox(
                "Chọn danh mục WordPress:",
                options=list(st.session_state['wp_categories'].keys()),
                help="Danh mục để đăng bài"
            )
        
        with col2:
            selected_cat_id = st.session_state['wp_categories'].get(selected_category, 0)
            st.info(f"📁 Category ID: {selected_cat_id}")
        
        st.subheader("Nhập Keywords")
        
        keywords_input = st.text_area(
            "Keywords (mỗi dòng 1 keyword)",
            placeholder="iPhone 15 Pro Max\nSamsung Galaxy S24\nXiaomi 14 Ultra",
            height=200,
            help="Mỗi dòng 1 keyword. V3 sẽ tự động phân tích và tạo prompt phù hợp."
        )
        
        keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]
        
        if keywords:
            st.info(f"📝 Tổng số keywords: **{len(keywords)}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_button = st.button("🧪 Test 1 keyword", use_container_width=True, type="secondary")
        
        with col2:
            run_button = st.button("▶️ CHẠY NGAY", use_container_width=True, type="primary")
        
        # Run logic
        if test_button or run_button:
            run_cat_name = selected_category
            
            if test_button:
                keywords = keywords[:1]  # Only first keyword for test
                st.info(f"🧪 Test mode: Chỉ chạy keyword đầu tiên")
            
            if not keywords:
                st.error("❌ Chưa nhập từ khóa!")
            elif not gemini_key:
                st.error("❌ Thiếu Gemini API Key!")
            elif not google_api_key or not google_cse_id:
                st.error("❌ Thiếu Google API Key hoặc CSE ID!")
            else:
                st.info(f"🚀 Đang chạy {len(keywords)} keyword vào: **{run_cat_name}**")
                
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
                env['CATEGORY_NAME'] = run_cat_name
                env['PREFERRED_MODEL'] = st.session_state.get('preferred_model', 'gemini-2.5-flash')
                
                # V3 Configuration
                if site_description:
                    env['SITE_DESCRIPTION'] = site_description
                
                if sample_keywords_input:
                    sample_kw_list = [k.strip() for k in sample_keywords_input.split('\n') if k.strip()]
                    env['SAMPLE_KEYWORDS'] = ','.join(sample_kw_list)
                
                # Results tracking
                success_count = 0
                failed_keywords = []
                
                # Process each keyword
                for idx, kw in enumerate(keywords):
                    status.info(f"⏳ Processing: **{kw}** ({idx+1}/{len(keywords)})")
                    
                    env['KEYWORD'] = kw
                    
                    try:
                        # Run scrapy
                        cmd = [
                            sys.executable, '-m', 'scrapy', 'crawl', 'google_bot',
                            '-a', f'keyword={kw}',
                            '-s', 'LOG_ENABLED=True',
                            '-s', 'LOG_LEVEL=INFO'
                        ]
                        
                        result = subprocess.run(
                            cmd,
                            cwd='backend',
                            env=env,
                            capture_output=True,
                            text=True,
                            timeout=180
                        )
                        
                        # Display logs
                        with log_container:
                            with st.expander(f"📋 Log: {kw}", expanded=(idx == 0)):
                                st.code(result.stdout + result.stderr, language='log')
                        
                        # Check success
                        if 'PUBLISHED' in result.stdout or result.returncode == 0:
                            success_count += 1
                            status.success(f"✅ Success: **{kw}**")
                        else:
                            failed_keywords.append(kw)
                            status.error(f"❌ Failed: **{kw}**")
                        
                        time.sleep(2)
                        
                    except subprocess.TimeoutExpired:
                        failed_keywords.append(kw)
                        status.error(f"⏱️ Timeout: **{kw}**")
                    except Exception as e:
                        failed_keywords.append(kw)
                        status.error(f"❌ Error: **{kw}** - {str(e)}")
                    
                    # Update progress
                    progress.progress((idx + 1) / len(keywords))
                
                # Final results
                st.divider()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("✅ Thành công", success_count)
                
                with col2:
                    st.metric("❌ Thất bại", len(failed_keywords))
                
                with col3:
                    success_rate = (success_count / len(keywords) * 100) if keywords else 0
                    st.metric("📊 Tỷ lệ", f"{success_rate:.1f}%")
                
                if failed_keywords:
                    with st.expander("❌ Keywords thất bại"):
                        for kw in failed_keywords:
                            st.write(f"- {kw}")

# ============================================================
# TAB 2: STATS
# ============================================================

with tab2:
    st.header("📊 Thống kê")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ System")
        st.write(f"**Version:** V3 Clean")
        st.write(f"**Model:** {preferred_model}")
        st.write(f"**Brand:** {brand_name}")
        
        if os.path.exists('profiles'):
            import json
            try:
                profile_files = list(Path('profiles').glob('*_profile.json'))
                if profile_files:
                    with open(profile_files[0], 'r', encoding='utf-8') as f:
                        profile = json.load(f)
                        st.write(f"**Niche:** {profile.get('niche', 'N/A')}")
                        st.write(f"**Sub-niche:** {profile.get('sub_niche', 'N/A')}")
            except:
                pass
    
    with col2:
        st.subheader("💰 Cost Estimate")
        
        cost_per_keyword = 0.006  # V3 average
        
        num_keywords = st.number_input("Số keywords/ngày:", min_value=1, value=50)
        
        daily_cost = num_keywords * cost_per_keyword
        monthly_cost = daily_cost * 30
        
        st.metric("Chi phí/ngày", f"${daily_cost:.2f}")
        st.metric("Chi phí/tháng", f"${monthly_cost:.2f}")

# ============================================================
# TAB 3: GUIDE
# ============================================================

with tab3:
    st.header("ℹ️ Hướng dẫn V3 Universal")
    
    st.markdown("""
    ## 🎯 V3 là gì?
    
    **V3 Universal** là hệ thống AI tự động phân tích và adapt với **mọi niche**:
    - ✅ Tech review (smartphone, laptop...)
    - ✅ Health & wellness (vitamin, yoga...)
    - ✅ Finance (crypto, stocks...)
    - ✅ Education (courses, tutorials...)
    - ✅ Entertainment (movies, games...)
    
    **Không cần config thủ công!** V3 tự hiểu niche của bạn.
    
    ---
    
    ## 🚀 Quick Start
    
    ### Bước 1: Cấu hình API Keys (Sidebar)
    
    1. **Gemini API Key**: [Get here](https://aistudio.google.com/app/apikey)
    2. **Google API Key**: [Get here](https://console.cloud.google.com/)
    3. **Search Engine ID**: [Get here](https://programmablesearchengine.google.com/)
    
    ### Bước 2: Kết nối WordPress
    
    1. WP URL: `https://yoursite.com/wp-json/wp/v2`
    2. WP User: `admin`
    3. WP App Password: Tạo tại Users → Profile → Application Passwords
    
    ### Bước 3: Cấu hình V3 (Lần đầu tiên)
    
    1. **Mô tả website**: 1 câu ngắn
       - VD: "Website review smartphone và công nghệ"
    
    2. **Sample keywords**: 3-5 keywords đại diện
       - VD:
         ```
         iPhone 15 Pro Max
         Samsung Galaxy S24
         Xiaomi 14
         ```
    
    3. Click **"Kết nối & Tải Chuyên mục"**
    
    ### Bước 4: Test
    
    1. Nhập 1 keyword test
    2. Click **"🧪 Test 1 keyword"**
    3. Kiểm tra log có: "✨ V3 Universal Generator ready"
    4. Kiểm tra bài đăng trên WordPress
    
    ### Bước 5: Chạy Production
    
    1. Nhập 10-50 keywords
    2. Click **"▶️ CHẠY NGAY"**
    3. Chờ hoàn thành
    
    ---
    
    ## 💡 Tips
    
    ### Sample Keywords tốt
    
    ✅ Đa dạng và đại diện cho niche:
    ```
    iPhone 15 (flagship)
    Redmi Note 13 (mid-range)
    Samsung Galaxy A05 (budget)
    ```
    
    ❌ Không đa dạng:
    ```
    iPhone 15
    iPhone 15 Pro
    iPhone 15 Pro Max
    ```
    
    ### Reset Cache khi nào?
    
    - Đổi niche hoàn toàn
    - V3 phân tích sai
    - Muốn V3 học lại
    
    ---
    
    ## ❓ FAQ
    
    **Q: V3 có chậm hơn không?**  
    A: Lần đầu: ~7s (phân tích website). Lần sau: ~3s (chỉ phân tích keyword)
    
    **Q: V3 có tốn thêm tiền không?**  
    A: Có, thêm ~$0.004/keyword (2 API calls phân tích). Tổng: ~$0.006/keyword
    
    **Q: Sample keywords có bắt buộc không?**  
    A: Không bắt buộc nhưng **khuyến nghị cao**. Giúp V3 hiểu niche nhanh hơn.
    
    **Q: Có thể dùng cho nhiều website không?**  
    A: Có! Mỗi website sẽ có cache riêng.
    
    ---
    
    ## 🎓 Advanced
    
    ### Cache Location
    
    - `profiles/{site_id}_profile.json` - Website profile
    - Xóa cache: Delete folder `profiles/`
    
    ### Environment Variables
    
    V3 sử dụng:
    - `SITE_DESCRIPTION` - Mô tả website
    - `SAMPLE_KEYWORDS` - Keywords mẫu (comma-separated)
    
    ### Model Selection
    
    - **gemini-2.5-flash**: Nhanh, rẻ, chất lượng tốt (khuyến nghị)
    - **gemini-2.5-pro**: Chất lượng cao hơn, đắt hơn 10x
    
    ---
    
    ## 🆘 Support
    
    Nếu gặp vấn đề:
    1. Check log chi tiết
    2. Verify API keys
    3. Test với 1 keyword đơn giản
    4. Reset cache và thử lại
    """)

# Footer
st.divider()
st.caption("Auto Content Pro - V3 Universal System 🚀 | Made with ❤️")
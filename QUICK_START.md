# Auto Content Pro - Quick Start Guide

## 🚀 Tính năng chính

### ✨ V2.0 - SEO Optimization + Adaptive Learning

1. **Prompt SEO nâng cao** - Yêu cầu AI nghiên cứu web, viết tự nhiên
2. **Lựa chọn Model AI** - Gemini 2.5 Flash/Pro cho nội dung
3. **Claude cho Prompt** - Dùng Claude tạo prompt sáng tạo hơn
4. **Adaptive Search** - Tự học về website, tìm kiếm thông minh
5. **Internal Links** - Placeholder `[internal_links]` tự động

---

## 📋 Setup nhanh (5 phút)

### 1. API Keys cần thiết

```
✅ Gemini API Key - Bắt buộc
   → https://aistudio.google.com/apikey
   
✅ Google API Key + CSE ID - Bắt buộc
   → Xem: GOOGLE_API_SETUP.md
   
⭐ Anthropic API Key - Optional (cho Claude)
   → https://console.anthropic.com/
```

### 2. Khởi động

```bash
cd d:\auto_content_pro
python -m streamlit run dashboard.py
```

### 3. Cấu hình Sidebar

1. **API Keys & Search**
   - Gemini API Key
   - Anthropic API Key (nếu dùng Claude)
   - Google API Key
   - Search Engine ID

2. **WordPress**
   - WP URL: `https://yoursite.com/wp-json/wp/v2`
   - WP User: `admin`
   - WP App Pass

3. **Thương hiệu**
   - Nhập tên thương hiệu

4. **Model AI**
   - Chọn Flash (nhanh) hoặc Pro (chất lượng)

5. **Kết nối**
   - Click "🔄 Kết nối & Tải Chuyên mục"

---

## 🧠 Site Profile (Adaptive Search)

### Cho website MỚI:

```
1. Vào tab "⚙️ Cài đặt"
2. Tìm "🧠 Site Profile"
3. Nhập mô tả (1 câu):
   "Website review truyện manga"
4. Click "🚀 Khởi tạo"
5. Done! ✅
```

### Tự động học:

- Sau mỗi 10 keywords → Auto-refine
- Càng dùng càng chính xác
- Mỗi site có profile riêng

---

## ✨ Quản lý Prompt

### Tab "✨ Quản lý Prompt"

**Tạo prompt:**

1. **📝 Từ mẫu** - Nhanh, miễn phí
2. **🤖 Nhờ AI viết** - Chọn model:
   - Gemini Flash - Nhanh, rẻ
   - Gemini Pro - Cân bằng
   - Claude Sonnet - Sáng tạo nhất ⭐

**Chỉnh sửa:**
- Edit trực tiếp trong text area
- Click "💾 Lưu Prompt"

---

## 🚀 Chạy tạo nội dung

### Tab "🚀 Chạy"

1. **Chọn danh mục** đăng
2. **Nhập keywords** (mỗi dòng 1 từ):
   ```
   vạn cổ thần đế
   đấu phá thương khung
   tru tiên
   ```
3. **Chạy:**
   - 🔥 CHẠY NGAY - Tất cả keywords
   - 🧪 Test 1 keyword - Test trước

---

## 💰 Chi phí ước tính

### Free Tier (Khuyến nghị bắt đầu):

- Google Search: **100 queries/ngày** - FREE
- Gemini Flash: Rất rẻ (~$0.001/bài)
- **Total: ~$0-0.1/ngày** cho 50-100 bài

### Nếu scale up:

- Google Search: $5/1000 queries
- Gemini Pro: ~$0.02/bài
- Claude Sonnet: ~$0.05/prompt
- **Total: ~$5-20/tháng** cho 500-1000 bài

---

## 📊 So sánh Models

### Cho nội dung:

| Model | Tốc độ | Chi phí | Chất lượng | Dùng khi |
|-------|--------|---------|------------|----------|
| **Gemini Flash** | ⚡⚡⚡ | 💰 | ⭐⭐⭐ | Số lượng lớn |
| **Gemini Pro** | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐ | Bài quan trọng |

### Cho tạo prompt:

| Model | Chi phí | Chất lượng | Dùng khi |
|-------|---------|------------|----------|
| **Gemini Flash** | $0.001 | ⭐⭐⭐ | Test nhanh |
| **Gemini Pro** | $0.02 | ⭐⭐⭐⭐ | Cân bằng |
| **Claude Sonnet** | $0.05 | ⭐⭐⭐⭐⭐ | Danh mục quan trọng |

---

## 🎯 Workflow khuyến nghị

### Lần đầu:

```
1. Setup API keys (5 phút)
2. Kết nối WordPress
3. Tạo Site Profile (1 câu mô tả)
4. Test 1 keyword
5. Nếu OK → Chạy 10-20 keywords/ngày
```

### Hàng ngày:

```
1. Nhập 20-50 keywords
2. Chạy tự động
3. Kiểm tra kết quả
4. Hệ thống tự học và cải thiện
```

---

## 📚 Tài liệu chi tiết

- [README_SEO_UPDATE.md](file:///d:/auto_content_pro/README_SEO_UPDATE.md) - Tính năng SEO mới
- [GOOGLE_API_SETUP.md](file:///d:/auto_content_pro/GOOGLE_API_SETUP.md) - Lấy Google API Key
- [CLAUDE_PROMPT_GUIDE.md](file:///d:/auto_content_pro/CLAUDE_PROMPT_GUIDE.md) - Dùng Claude
- [Adaptive Search Walkthrough](file:///C:/Users/Admin/.gemini/antigravity/brain/f1dabb46-37b0-4091-a7dc-2f8aa413c0a2/adaptive_search_walkthrough.md) - Hệ thống tự học

---

## 🔧 Troubleshooting

### "Thiếu API Key"
→ Kiểm tra đã nhập đúng trong sidebar

### "Google API Error 403"
→ Hết quota 100/ngày, đợi ngày mai hoặc enable billing

### "Không tìm thấy kết quả"
→ Từ khóa quá cụ thể, thử keyword khác

### "AI Thất bại"
→ Thử đổi model hoặc kiểm tra quota

### "Chưa có Site Profile"
→ Vào Settings > Site Profile > Khởi tạo

---

## 💡 Tips

### Tối ưu chi phí:
1. Dùng Flash cho 80-90% bài
2. Dùng Pro cho bài pillar
3. Monitor quota Google Search

### Tăng chất lượng:
1. Tạo prompt riêng cho danh mục quan trọng
2. Dùng Claude cho prompt phức tạp
3. Để Site Profile tự học (10-20 keywords)

### Multi-site:
1. Mỗi site tự động có profile riêng
2. Chỉ cần đổi WP URL
3. Profile lưu tại `profiles/{site_id}_profile.json`

---

**Happy Content Creating! 🚀**

**Version:** 2.0  
**Updated:** 2026-01-23

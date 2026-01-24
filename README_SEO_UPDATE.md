# Auto Content Pro - SEO Optimization Update

## 🎉 Tính năng mới (v2.0)

### ✨ Highlights

1. **Prompt Template Nâng Cao**
   - Yêu cầu AI nghiên cứu web và xác minh thông tin
   - Hướng dẫn viết tự nhiên như người thật
   - Tăng chiều sâu nội dung 20-40%
   - Hỗ trợ internal links tự động

2. **Lựa Chọn Model AI**
   - Gemini 2.5 Flash (nhanh, rẻ)
   - Gemini 2.5 Pro (chất lượng cao)
   - Tự động fallback nếu model thất bại

3. **Word Count Distribution Mới**
   - 30% bài: 1200-1400 từ
   - 50% bài: 1400-1600 từ
   - 20% bài: 1600-1800 từ

---

## 🚀 Hướng dẫn sử dụng

### 1. Khởi động ứng dụng

```bash
cd d:\auto_content_pro
python -m streamlit run dashboard.py
```

### 2. Cấu hình ban đầu

#### Sidebar - Bên trái màn hình:

**1. API Keys & Search**
- `Gemini API Key`: Lấy từ [Google AI Studio](https://aistudio.google.com/apikey)
- `Google API Key`: Cho Google Custom Search
- `Search Engine ID`: CSE ID của bạn

**2. Kết nối WordPress**
- `WP URL`: https://yoursite.com/wp-json/wp/v2
- `WP User`: admin
- `WP App Pass`: Tạo trong WordPress > Users > Application Passwords

**3. Thương hiệu**
- Nhập tên thương hiệu của bạn (VD: VanGioiComics)

**4. Model AI** ⭐ MỚI
- Chọn model cho việc tạo nội dung:
  - `gemini-2.5-flash`: Nhanh, rẻ, phù hợp cho số lượng lớn
  - `gemini-2.5-pro`: Chất lượng cao hơn, chậm hơn, đắt hơn

**5. Kết nối**
- Click nút "🔄 Kết nối & Tải Chuyên mục"

---

### 3. Quản lý Prompt (Tab "✨ Quản lý Prompt")

#### Tạo prompt cho từng danh mục:

1. **Chọn danh mục** từ dropdown
2. **Tạo prompt** bằng một trong hai cách:
   - **📝 Tạo từ mẫu có sẵn**: Sử dụng template mặc định
   - **🤖 Nhờ Gemini viết**: AI tự động tạo prompt tùy chỉnh
3. **Chỉnh sửa** nội dung prompt nếu cần
4. **💾 Lưu Prompt**

#### Các placeholder tự động:

Trong prompt, các placeholder sau sẽ được thay thế tự động:

- `{{WORD_COUNT}}`: Số từ tối thiểu (random 1200-1800)
- `{{PRIMARY_KEYWORD_COUNT}}`: Số lần từ khóa chính (random 6-12)
- `{{SECONDARY_KEYWORD_COUNT}}`: Số lần từ khóa phụ (random 4-7)
- `{keyword}`: Từ khóa thực tế
- `{brand_name}`: Tên thương hiệu
- `{content}`: Nội dung gốc
- `[internal_links]`: Vị trí AI sẽ thêm liên kết nội bộ

---

### 4. Chạy tạo nội dung (Tab "🚀 Chạy")

#### Bước 1: Chọn danh mục đăng
- Chọn danh mục WordPress từ dropdown

#### Bước 2: Nhập từ khóa
- Nhập danh sách từ khóa, mỗi dòng 1 từ khóa
- Ví dụ:
  ```
  vạn cổ thần đế
  đấu phá thương khung
  tru tiên
  ```

#### Bước 3: Chạy
- **🔥 CHẠY NGAY**: Xử lý tất cả keywords
- **🧪 Test 1 keyword**: Chỉ test keyword đầu tiên

#### Kết quả:
- Thanh tiến độ hiển thị quá trình
- Bảng kết quả với status từng keyword
- Log chi tiết nếu có lỗi

---

## 📊 Prompt Template Mới

### Các section chính:

1. **Vai trò**: Theo danh mục (Truyện tranh, Manga, Giải mã giấc mơ...)
2. **Cấu trúc bài viết**: H1, H2, mở đầu, kết luận
3. **Phong cách viết - Giọng người thật** ⭐ MỚI
   - Đa dạng độ dài đoạn văn
   - Tránh cụm từ sáo rỗng AI
4. **Nghiên cứu & Xác minh** ⭐ MỚI
   - Bắt buộc tìm kiếm web
   - Quy tắc xác minh thông tin
5. **Tăng cường chiều sâu** ⭐ MỚI
   - Mở rộng 20-40% so với bài gốc
6. **Tối ưu SEO**: Word count, keyword density
7. **Tích hợp thương hiệu**: Nhắc 1-2 lần tự nhiên
8. **Internal Links** ⭐ MỚI: `[internal_links]`

---

## 🎯 So sánh Model

| Tiêu chí | Gemini 2.5 Flash | Gemini 2.5 Pro |
|----------|------------------|----------------|
| **Tốc độ** | ⚡ Rất nhanh | 🐢 Chậm hơn |
| **Chi phí** | 💰 Rẻ | 💰💰 Đắt hơn ~10x |
| **Chất lượng** | ✅ Tốt | ⭐ Xuất sắc |
| **Web research** | ⚠️ Hạn chế | ✅ Tốt hơn |
| **Phù hợp** | Số lượng lớn | Nội dung quan trọng |

### Khuyến nghị:

- **Flash**: Dùng cho bài viết thông thường, số lượng lớn
- **Pro**: Dùng cho bài viết quan trọng, cần chất lượng cao
- Hệ thống tự động fallback nếu model ưu tiên thất bại

---

## 🔧 Troubleshooting

### Lỗi thường gặp:

#### 1. "Thiếu Gemini API Key"
- Kiểm tra đã nhập API key chưa
- Lấy key mới tại: https://aistudio.google.com/apikey

#### 2. "Google API Error 403"
- Kiểm tra quota Google Custom Search
- Mỗi ngày free: 100 queries

#### 3. "AI Thất bại"
- Kiểm tra model có khả dụng không
- Thử đổi sang model khác
- Kiểm tra quota Gemini API

#### 4. "Không tìm thấy kết quả"
- Từ khóa quá cụ thể
- Thử từ khóa khác hoặc rộng hơn

#### 5. Bài viết không có internal links
- Placeholder `[internal_links]` đã có trong prompt
- AI tự quyết định có thêm hay không
- Phụ thuộc vào khả năng của model

---

## 📈 Best Practices

### 1. Quản lý Prompt
- Tạo prompt riêng cho từng danh mục quan trọng
- Test với 1 keyword trước khi chạy hàng loạt
- Lưu các prompt hiệu quả

### 2. Chọn Model
- Dùng Flash cho bài thông thường
- Dùng Pro cho bài pillar, cornerstone
- Monitor chi phí API

### 3. Từ khóa
- Nhóm từ khóa cùng chủ đề
- Tránh từ khóa quá chung chung
- Kiểm tra kết quả Google Search trước

### 4. WordPress
- Backup trước khi chạy số lượng lớn
- Kiểm tra category mapping
- Test với 1-2 bài trước

---

## 🆕 Changelog

### Version 2.0 (2026-01-23)

**Added:**
- ✅ Model selection (Gemini 2.5 Flash/Pro)
- ✅ Advanced SEO prompt template
- ✅ Web research requirements
- ✅ Content depth guidelines (20-40% expansion)
- ✅ Internal links placeholder support
- ✅ Natural writing style enforcement
- ✅ Model tracking in results

**Changed:**
- 📊 Word count distribution: 1200-1800 từ (3 tiers)
- 🎯 Removed Gemini 2.0 Flash from content generation
- 📝 Enhanced prompt with anti-AI-writing guidelines

**Fixed:**
- 🐛 Improved error handling for model failures
- 🔄 Better fallback mechanism

---

## 📞 Support

### Tài liệu:
- [Implementation Plan](file:///C:/Users/Admin/.gemini/antigravity/brain/f1dabb46-37b0-4091-a7dc-2f8aa413c0a2/implementation_plan.md)
- [Walkthrough](file:///C:/Users/Admin/.gemini/antigravity/brain/f1dabb46-37b0-4091-a7dc-2f8aa413c0a2/walkthrough.md)

### API Documentation:
- [Gemini API](https://ai.google.dev/gemini-api/docs)
- [Google Custom Search](https://developers.google.com/custom-search)
- [WordPress REST API](https://developer.wordpress.org/rest-api/)

---

## 🎓 Tips & Tricks

### Tối ưu chi phí:
1. Dùng Flash cho 80-90% bài viết
2. Chỉ dùng Pro cho bài quan trọng
3. Monitor usage qua Google AI Studio

### Tăng chất lượng:
1. Tạo prompt riêng cho từng danh mục
2. Thêm context cụ thể vào prompt
3. Test và điều chỉnh prompt thường xuyên

### Tăng tốc độ:
1. Chạy vào giờ thấp điểm (ít rate limit)
2. Dùng Flash thay vì Pro
3. Batch keywords theo chủ đề

---

**Happy Content Creating! 🚀**

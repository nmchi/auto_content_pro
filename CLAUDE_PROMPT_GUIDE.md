# Hướng dẫn sử dụng Claude cho tạo Prompt

## 🎯 Tổng quan

Bạn có thể sử dụng Claude (Anthropic) để tạo prompt tùy chỉnh cho từng danh mục. Claude thường cho kết quả sáng tạo và chi tiết hơn Gemini.

## 📋 Yêu cầu

### 1. Cài đặt thư viện Anthropic

```bash
pip install anthropic
```

### 2. Lấy API Key

1. Truy cập: https://console.anthropic.com/
2. Đăng ký/Đăng nhập
3. Vào **API Keys** > **Create Key**
4. Copy API key

### 3. Thiết lập Environment Variable

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-api03-..."
```

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-api03-...
```

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY=sk-ant-api03-...
```

**Hoặc thêm vào file `.env`:**
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## 🚀 Sử dụng

### Trong Dashboard:

1. Mở tab **"✨ Quản lý Prompt"**
2. Chọn danh mục cần tạo prompt
3. Trong phần **"Chọn model tạo prompt"**, chọn:
   - `claude-3-5-sonnet` (Khuyến nghị)
4. Click **"🤖 Nhờ AI viết prompt"**
5. Chờ Claude tạo prompt
6. Chỉnh sửa nếu cần và **💾 Lưu Prompt**

## 📊 So sánh Models

| Model | Tốc độ | Chi phí | Sáng tạo | Độ dài | Khuyến nghị |
|-------|--------|---------|----------|--------|-------------|
| **Gemini 2.5 Flash** | ⚡⚡⚡ Rất nhanh | 💰 Rẻ nhất | ⭐⭐⭐ | Trung bình | Tạo nhanh, test |
| **Gemini 2.5 Pro** | ⚡⚡ Nhanh | 💰💰 Trung bình | ⭐⭐⭐⭐ | Dài | Cân bằng tốt |
| **Claude 3.5 Sonnet** | ⚡ Chậm hơn | 💰💰💰 Đắt nhất | ⭐⭐⭐⭐⭐ | Rất dài | Prompt quan trọng |

## 💡 Tips

### Khi nào dùng Claude?

✅ **Nên dùng:**
- Tạo prompt cho danh mục quan trọng
- Cần prompt chi tiết, sáng tạo
- Danh mục phức tạp (Review, Giải mã giấc mơ...)

❌ **Không cần:**
- Tạo prompt nhanh để test
- Danh mục đơn giản
- Ngân sách hạn chế

### Tối ưu chi phí:

1. **Dùng Gemini Flash** cho hầu hết danh mục
2. **Dùng Claude** chỉ cho 3-5 danh mục chính
3. **Chỉnh sửa thủ công** từ template mặc định

## 🔧 Troubleshooting

### Lỗi: "Thiếu Anthropic API Key"

**Nguyên nhân:** Chưa set environment variable

**Giải pháp:**
```powershell
# Kiểm tra
echo $env:ANTHROPIC_API_KEY

# Set lại
$env:ANTHROPIC_API_KEY = "sk-ant-api03-YOUR_KEY_HERE"
```

### Lỗi: "Cần cài đặt: pip install anthropic"

**Giải pháp:**
```bash
pip install anthropic
```

### Lỗi: "Lỗi Claude: ..."

**Nguyên nhân:** API key sai, hết quota, hoặc lỗi mạng

**Giải pháp:**
1. Kiểm tra API key đúng chưa
2. Kiểm tra quota tại: https://console.anthropic.com/
3. Thử lại sau vài phút

## 📈 Pricing (Tham khảo)

**Claude 3.5 Sonnet:**
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens

**Gemini 2.5 Pro:**
- Input: $1.25 / 1M tokens
- Output: $5 / 1M tokens

**Gemini 2.5 Flash:**
- Input: $0.075 / 1M tokens
- Output: $0.30 / 1M tokens

> 💡 Tạo 1 prompt ≈ 500-1000 tokens input + 2000-3000 tokens output

**Ước tính chi phí tạo 1 prompt:**
- Gemini Flash: ~$0.001 (rất rẻ)
- Gemini Pro: ~$0.02
- Claude Sonnet: ~$0.05-0.06

## 🎓 Best Practices

### Workflow khuyến nghị:

```
1. Tạo prompt bằng Gemini Flash (test nhanh)
   ↓
2. Nếu không hài lòng → Thử Gemini Pro
   ↓
3. Nếu vẫn chưa ổn → Dùng Claude Sonnet
   ↓
4. Chỉnh sửa thủ công để hoàn thiện
```

### Lưu ý:

- ✅ Claude thường tạo prompt dài và chi tiết hơn
- ✅ Gemini Pro cân bằng tốt giữa chất lượng và chi phí
- ✅ Gemini Flash phù hợp cho test và iterate nhanh
- ⚠️ Luôn review và chỉnh sửa prompt trước khi dùng
- ⚠️ Không cần dùng Claude cho tất cả danh mục

## 📚 Tài liệu

- [Anthropic API Docs](https://docs.anthropic.com/)
- [Claude Models](https://docs.anthropic.com/en/docs/models-overview)
- [Pricing](https://www.anthropic.com/pricing)

---

**Cập nhật:** 2026-01-23

# Hướng dẫn lấy Google API Key và Search Engine ID

## 🎯 Tổng quan

Để hệ thống tự động tìm kiếm bài viết gốc trên Google, bạn cần:
1. **Google API Key** - Để gọi Google Custom Search API
2. **Search Engine ID (CSE ID)** - Để xác định phạm vi tìm kiếm

## 📋 Bước 1: Tạo Google API Key

### 1.1. Truy cập Google Cloud Console

1. Mở trình duyệt và truy cập: https://console.cloud.google.com/
2. Đăng nhập bằng tài khoản Google của bạn

### 1.2. Tạo Project mới (nếu chưa có)

1. Click vào dropdown **Select a project** ở góc trên bên trái
2. Click **NEW PROJECT**
3. Nhập tên project (VD: "Auto Content Pro")
4. Click **CREATE**
5. Đợi vài giây để project được tạo

### 1.3. Enable Custom Search API

1. Vào menu bên trái, chọn **APIs & Services** > **Library**
2. Tìm kiếm: `Custom Search API`
3. Click vào **Custom Search API**
4. Click nút **ENABLE**

### 1.4. Tạo API Key

1. Vào **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** ở trên cùng
3. Chọn **API key**
4. API key sẽ được tạo và hiển thị (dạng: `AIzaSy...`)
5. **Copy và lưu lại** API key này

### 1.5. (Optional) Bảo mật API Key

1. Click vào API key vừa tạo để chỉnh sửa
2. Trong **API restrictions**, chọn **Restrict key**
3. Chọn **Custom Search API**
4. Click **SAVE**

---

## 📋 Bước 2: Tạo Search Engine ID (CSE ID)

### 2.1. Truy cập Programmable Search Engine

1. Mở: https://programmablesearchengine.google.com/
2. Đăng nhập bằng cùng tài khoản Google

### 2.2. Tạo Search Engine mới

1. Click **Add** hoặc **Get started**
2. Điền thông tin:

**Search engine name:**
```
Auto Content Search
```

**What to search:**
- Chọn **Search the entire web**

**Search settings:**
- Bật **Image search**: ON
- Bật **SafeSearch**: OFF (để không bị lọc kết quả)

3. Click **CREATE**

### 2.3. Lấy Search Engine ID

1. Sau khi tạo xong, click vào search engine vừa tạo
2. Trong phần **Overview** hoặc **Setup**, tìm:
   - **Search engine ID** hoặc **cx**
   - Dạng: `a1b2c3d4e5f6g7h8i` (chuỗi ký tự ngẫu nhiên)
3. **Copy và lưu lại** Search Engine ID này

### 2.4. (Optional) Tùy chỉnh Search Engine

**Để tìm kiếm tốt hơn cho nội dung tiếng Việt:**

1. Vào **Setup** > **Basics**
2. Trong **Sites to search**, thêm các domain ưu tiên:
   ```
   *.truyenfull.vn
   *.wikidich.com
   *.tangthuvien.vn
   *.metruyencv.com
   ```
3. Hoặc để trống để tìm toàn bộ web

---

## 🔑 Cấu hình trong Dashboard

### Cách 1: Nhập trực tiếp trong Dashboard

1. Mở dashboard: `python -m streamlit run dashboard.py`
2. Trong **Sidebar** > **1. API Keys & Search**:
   - **Google API Key**: Paste API key vừa tạo
   - **Search Engine ID**: Paste CSE ID vừa tạo

### Cách 2: Dùng Environment Variables

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY = "AIzaSy..."
$env:GOOGLE_CSE_ID = "a1b2c3d4e5f6g7h8i"
```

**Linux/Mac:**
```bash
export GOOGLE_API_KEY="AIzaSy..."
export GOOGLE_CSE_ID="a1b2c3d4e5f6g7h8i"
```

**File `.env`:**
```env
GOOGLE_API_KEY=AIzaSy...
GOOGLE_CSE_ID=a1b2c3d4e5f6g7h8i
```

---

## 📊 Quota và Giới hạn

### Free Tier (Miễn phí)

**Google Custom Search API:**
- **100 queries/ngày** - MIỄN PHÍ
- Sau 100 queries: $5 / 1000 queries

**Lưu ý:**
- 1 keyword = 1 query
- Nếu chạy 50 keywords/ngày → OK
- Nếu chạy 200 keywords/ngày → Cần trả phí

### Kiểm tra Quota

1. Vào: https://console.cloud.google.com/
2. **APIs & Services** > **Dashboard**
3. Click vào **Custom Search API**
4. Xem **Quotas** để biết đã dùng bao nhiêu

---

## 🔧 Troubleshooting

### Lỗi: "Thiếu Google API Key hoặc CSE ID"

**Nguyên nhân:** Chưa nhập API key hoặc CSE ID

**Giải pháp:**
- Kiểm tra đã nhập đúng vào dashboard chưa
- Kiểm tra không có khoảng trắng thừa

### Lỗi: "Google API Error 403"

**Nguyên nhân:** 
- API key chưa được enable Custom Search API
- Hoặc đã hết quota (100 queries/ngày)

**Giải pháp:**
1. Kiểm tra đã enable Custom Search API chưa
2. Kiểm tra quota: https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas
3. Đợi đến ngày mai (quota reset)
4. Hoặc enable billing để tăng quota

### Lỗi: "Không tìm thấy kết quả"

**Nguyên nhân:**
- Từ khóa quá cụ thể
- Search Engine bị giới hạn domain

**Giải pháp:**
1. Thử từ khóa khác
2. Kiểm tra Search Engine settings
3. Đảm bảo chọn "Search the entire web"

### Lỗi: "API key not valid"

**Nguyên nhân:** API key sai hoặc bị vô hiệu hóa

**Giải pháp:**
1. Tạo API key mới
2. Kiểm tra API key đã copy đúng chưa
3. Kiểm tra API key chưa bị delete

---

## 💡 Tips & Best Practices

### Tối ưu Quota

1. **Test trước với 1-2 keywords** trước khi chạy hàng loạt
2. **Nhóm keywords** theo chủ đề để chạy từng đợt
3. **Dùng URL trực tiếp** nếu đã biết nguồn (bỏ qua search)

### Bảo mật

1. **Không share** API key công khai
2. **Restrict API key** chỉ cho Custom Search API
3. **Rotate API key** định kỳ nếu bị lộ

### Monitoring

1. Theo dõi quota hàng ngày
2. Set alert khi gần hết quota
3. Cân nhắc enable billing nếu cần chạy nhiều

---

## 📈 Pricing (Tham khảo)

| Số lượng queries | Chi phí |
|------------------|---------|
| 0 - 100/ngày | **MIỄN PHÍ** |
| 101 - 10,000/ngày | $5 / 1000 queries |
| > 10,000/ngày | Liên hệ Google |

**Ví dụ:**
- Chạy 50 keywords/ngày: **$0** (free)
- Chạy 200 keywords/ngày: **$0.50/ngày** ($15/tháng)
- Chạy 500 keywords/ngày: **$2/ngày** ($60/tháng)

---

## 🎓 Workflow Khuyến nghị

### Cho người mới:

```
1. Tạo Google API Key (5 phút)
   ↓
2. Tạo Search Engine ID (3 phút)
   ↓
3. Test với 1 keyword trong dashboard
   ↓
4. Nếu OK → Chạy 10-20 keywords/ngày (free tier)
```

### Cho người dùng nhiều:

```
1. Enable billing trên Google Cloud
   ↓
2. Set budget alert ($10-20/tháng)
   ↓
3. Chạy 100-200 keywords/ngày
   ↓
4. Monitor quota và chi phí hàng tuần
```

---

## 📚 Tài liệu tham khảo

- [Google Custom Search JSON API](https://developers.google.com/custom-search/v1/overview)
- [Programmable Search Engine](https://developers.google.com/custom-search/docs/tutorial/introduction)
- [API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)
- [Pricing](https://developers.google.com/custom-search/v1/overview#pricing)

---

## ❓ FAQ

**Q: Có thể dùng nhiều API key không?**
A: Có, bạn có thể tạo nhiều API key và rotate để tăng quota.

**Q: Search Engine ID có thể dùng chung không?**
A: Có, 1 CSE ID có thể dùng với nhiều API key.

**Q: Có cách nào miễn phí hoàn toàn không?**
A: Có, giới hạn 100 queries/ngày là miễn phí mãi mãi.

**Q: Tôi cần bật billing ngay không?**
A: Không, hãy dùng free tier trước. Chỉ bật billing khi thực sự cần.

---

**Cập nhật:** 2026-01-23

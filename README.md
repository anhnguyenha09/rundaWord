# HƯỚNG DẪN CHẠY ỨNG DỤNG RUNDAWORD - ĐƠN GIẢN

## CÁC LỆNH ĐỂ CHẠY CODE (quan trọng nhất):

### Bước 1: Mở Terminal/Command Prompt và di chuyển vào thư mục dự án
```bash
cd RundaWord
```

### Bước 2: Cài đặt các thư viện cần thiết
```bash
pip install Flask Flask-SQLAlchemy Flask-Login python-dotenv
```

### Bước 3: Chạy ứng dụng
```bash
python app_simple.py
```

### Bước 4: Mở trình duyệt
Truy cập: **http://localhost:5000**

---

## GIẢI THÍCH:

### File `app_simple.py` là file chính để chạy
File này chứa tất cả code cần thiết:
- Models (User, VocabPackage, Vocabulary)
- Routes (đăng nhập, đăng ký, quản lý gói từ)
- Database setup

### Cấu trúc thư mục:
```
RundaWord/
├── app_simple.py          ← FILE CHẠY CHÍNH
├── requirements.txt       ← Danh sách thư viện
├── .env                  ← Cấu hình (tùy chọn)
├── templates/            ← HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── index.html
│   ├── packages.html
│   ├── package_detail.html
│   ├── create_package.html
│   ├── edit_package.html
│   └── profile.html
├── static/
│   └── css/
│       └── main.css
└── uploads/              ← Thư mục upload file
```

---

## XỬ LÝ LỖI THƯỜNG GẶP:

### Lỗi: "No module named 'flask'"
**Giải pháp:**
```bash
pip install Flask Flask-SQLAlchemy Flask-Login python-dotenv
```

### Lỗi: "Address already in use"
**Giải pháp:** Đổi port trong file app_simple.py (dòng cuối):
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Đổi từ 5000 sang 5001
```

### Lỗi: "Unable to open database"
**Giải pháp:** Xóa file `rundaword.db` (nếu có) và chạy lại

---

## TẠO USER MẪU ĐỂ TEST:

Sau khi chạy app lần đầu, truy cập http://localhost:5000 và:
1. Click "Đăng ký"
2. Điền thông tin:
   - Username: admin
   - Email: admin@test.com
   - Password: 123456
   - Name: Admin User
3. Click "Đăng ký" → Đăng nhập

---

## TÍNH NĂNG CÓ SẴN:

✅ Đăng ký / Đăng nhập / Đăng xuất
✅ Tạo gói từ vựng mới
✅ Xem danh sách gói từ
✅ Xem chi tiết gói từ
✅ Sửa thông tin gói từ
✅ Xem hồ sơ cá nhân
✅ Dashboard với gói từ gần đây

---

## LƯU Ý QUAN TRỌNG:

1. **Python phiên bản:** Cần Python 3.8 trở lên
2. **Database:** SQLite (tự động tạo file `rundaword.db`)
3. **Debug mode:** Đang bật để dễ phát triển
4. **Port mặc định:** 5000

---

## NẾU MUỐN DỪNG SERVER:

Nhấn `Ctrl + C` trong Terminal/Command Prompt

---

## ĐỂ CHẠY TRÊN PRODUCTION (deploy lên server thật):

1. Tắt debug mode:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

2. Đổi SECRET_KEY trong file `.env`:
```
SECRET_KEY=random-string-rat-dai-va-phuc-tap-o-day
```

3. Sử dụng PostgreSQL thay vì SQLite
4. Sử dụng web server như Gunicorn, Nginx

---

## HỖ TRỢ:

Nếu gặp lỗi, kiểm tra:
1. Python đã được cài đặt chưa: `python --version`
2. Pip đã được cài đặt chưa: `pip --version`
3. Đã ở đúng thư mục dự án chưa: `pwd` (Mac/Linux) hoặc `cd` (Windows)
4. Đã cài đặt thư viện chưa: `pip list | grep Flask`

## DANH SÁCH TÀI KHOẢN
1) admin@admin.com ; 123456
2) thuannn@gmail.com ; 18052011
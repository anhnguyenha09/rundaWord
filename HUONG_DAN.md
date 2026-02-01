# HƯỚNG DẪN CHẠY ỨNG DỤNG RUNDAWORD

## Các bước để chạy code:

### 1. Cài đặt Python (nếu chưa có)
Tải và cài đặt Python 3.8 trở lên từ https://www.python.org/downloads/

### 2. Tạo môi trường ảo (Virtual Environment)
```bash
cd RundaWord
python -m venv venv
```

### 3. Kích hoạt môi trường ảo

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 5. Khởi tạo database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

Hoặc có thể tạo database đơn giản hơn:
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database created!')"
```

### 6. Chạy ứng dụng
```bash
python app.py
```

hoặc

```bash
flask run
```

### 7. Truy cập ứng dụng
Mở trình duyệt và truy cập: http://localhost:5000

## Các lệnh hữu ích khác:

### Tạo user mẫu (tùy chọn)
```bash
python -c "from app import create_app, db; from models.models import User; app = create_app(); app.app_context().push(); user = User('admin', 'admin@example.com', 'password123', 'Admin User'); db.session.add(user); db.session.commit(); print('User created!')"
```

### Kiểm tra cấu trúc database
```bash
flask shell
>>> from models.models import User, VocabPackage, Vocabulary
>>> User.query.all()
>>> exit()
```

## Cấu trúc thư mục:
```
RundaWord/
├── app.py                 # File chính khởi tạo ứng dụng
├── config.py              # Cấu hình ứng dụng
├── routes.py              # Các routes/endpoints
├── requirements.txt       # Danh sách thư viện cần cài
├── .env                   # File chứa biến môi trường (secret keys)
├── models/
│   ├── __init__.py
│   └── models.py         # Định nghĩa database models
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── index.html
│   ├── packages.html
│   └── ...
├── static/              # CSS, JS, images
│   └── css/
│       └── main.css
└── uploads/            # Thư mục lưu file upload
```

## Lưu ý:
- Đảm bảo đã kích hoạt virtual environment trước khi chạy
- File .env chứa các thông tin nhạy cảm, không nên commit lên Git
- Database sẽ được tạo tự động khi chạy lần đầu
- Mặc định ứng dụng chạy ở chế độ development với debug=True

## Xử lý lỗi thường gặp:

### Lỗi "No module named 'flask'"
→ Cài đặt lại: `pip install -r requirements.txt`

### Lỗi "Unable to open database file"
→ Kiểm tra quyền ghi trong thư mục hoặc chạy: `python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"`

### Lỗi import circular
→ Đảm bảo cấu trúc file đúng như hướng dẫn

### Port 5000 đã được sử dụng
→ Đổi port trong app.py: `app.run(port=5001)`

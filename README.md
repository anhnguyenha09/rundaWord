# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## RundaWord - Nền tảng Học Từ Vựng Tiếng Anh

**Phiên bản:** 1.0  
**Ngày cập nhật:** Tháng 4, 2026  
**Tác giả:** Nguyễn Hà Anh
**Trạng thái:** Active Development

---

## 1. GIỚI THIỆU

### 1.1 Tổng Quan Dự Án

**RundaWord** là một nền tảng học tập trực tuyến chuyên biệt cho việc học từ vựng tiếng Anh, cung cấp cho người dùng các công cụ và phương pháp học tập đa dạng, hiệu quả. Nền tảng cho phép người dùng:
- Tạo và quản lý các gói từ vựng cá nhân
- Chia sẻ gói từ với cộng đồng
- Sử dụng nhiều chế độ học khác nhau (Flashcard, Quiz, Test, Match)
- Theo dõi tiến độ học tập

### 1.2 Mục Tiêu Hệ Thống

| Mục tiêu | Mô tả |
|----------|--------|
| **Hiệu quả học tập** | Cung cấp các phương pháp học khoa học dựa trên spaced repetition và active recall |
| **Cộng đồng** | Cho phép chia sẻ gói từ vựng giữa các người dùng |
| **Ghi nhớ từ vựng** | Theo dõi tiến độ học từng từ vựng riêng lẻ |
| **Quản lý bộ sưu tập** | Cho phép người dùng tạo, chỉnh sửa, xóa các gói từ vựng |
| **Quản trị hệ thống** | Cung cấp bảng điều khiển admin cho nhân viên quản lý |

### 1.3 Phạm Vi Hệ Thống

**Những gì được bao gồm:**
- Xác thực người dùng (đăng ký, đăng nhập)
- Quản lý gói từ vựng (CRUD operations)
- Bốn chế độ học tập tương tác
- Theo dõi tiến độ học tập
- Hệ thống topic/category
- Quản trị hệ thống cơ bản

**Những gì không được bao gồm:**
- Xử lý thanh toán/subscription
- Tích hợp AI giáo dục nâng cao
- Ứng dụng di động native
- Tính năng video/âm thanh

---

## 2. MÔ TẢ CHUNG (GENERAL DESCRIPTION)

### 2.1 Ngữ Cảnh Sử Dụng

```
                    ┌─────────────────────────┐
                    │    RundaWord Platform   │
                    └─────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
            ┌────────┐   ┌────────┐   ┌────────┐
            │ Guest  │   │  User  │   │ Admin  │
            └────────┘   └────────┘   └────────┘
```

### 2.2 Các Loại Người Dùng

#### 2.2.1 Guest (Khách)
- Truy cập trang chủ và danh sách gói công khai
- Xem chi tiết gói từ vựng công khai
- Không thể tạo gói hoặc sử dụng chế độ học tập

#### 2.2.2 Regular User (Người dùng thường)
- Tạo, chỉnh sửa, xóa gói từ vựng riêng
- Sử dụng bốn chế độ học tập
- Lưu gói từ của người khác vào thư viện
- Xem và quản lý tiến độ học tập

#### 2.2.3 Admin
- Truy cập tất cả các chức năng của user
- Quản lý người dùng (tạo, chỉnh sửa, xóa)
- Quản lý tất cả gói từ vựng trong hệ thống
- Chuyển đổi trạng thái công khai/riêng tư của gói
- Xem thống kê hệ thống

### 2.3 Giả định và Ràng Buộc

**Giả định:**
- Người dùng có kết nối internet ổn định
- Dữ liệu từ vựng được nhập chính xác
- Người dùng hiểu tiếng Anh cơ bản

**Ràng buộc:**
- Kích thước tập tin tải lên tối đa: 5MB
- Độ dài tên gói: tối đa 100 ký tự
- Độ dài mô tả gói: tối đa 70 ký tự
- Phiên bản người dùng tồn tại 7 ngày (nếu chọn "Remember me")
- Tối đa 12 gói công khai được hiển thị trên trang chủ

---

## 3. YÊUTHẦU CHỨC NĂNG (FUNCTIONAL REQUIREMENTS)

### 3.1 Quản Lý Người Dùng

#### FR 1.1: Đăng Ký Người Dùng
**ID:** REQ-USER-001  
**Ưu tiên:** High  
**Mô tả:**
Hệ thống cho phép người dùng mới tạo tài khoản với các thông tin:
- Họ và tên (bắt buộc)
- Email (bắt buộc, phải duy nhất)
- Username (bắt buộc, phải duy nhất)
- Mật khẩu (bắt buộc, tối thiểu 8 ký tự nên có)
- Xác nhận mật khẩu

**Điều kiện tiên quyết:**
- User không đã đăng nhập
- Email chưa được đăng ký trước đó
- Username chưa được sử dụng

**Luồng chính:**
1. User điền form đăng ký
2. Hệ thống xác thực dữ liệu
3. Hệ thống kiểm tra email/username duy nhất
4. Tạo user mới với role = ROLE_USER
5. Mã hóa mật khẩu bằng werkzeug.security
6. Lưu user vào database
7. Hiển thị thông báo thành công
8. Redirect đến trang login

**Luồng ngoại lệ:**
- Email đã tồn tại → Hiển thị lỗi, yêu cầu nhập email khác
- Username đã tồn tại → Hiển thị lỗi, yêu cầu nhập username khác
- Mật khẩu không khớp → Hiển thị lỗi xác nhận
- Form trống → Từ chối submit

**Output:**
```python
User(
    username="curator_01",
    email="curator@scholar.edu",
    name="Julian Sterling",
    password_hash="pbkdf2:sha256:...",
    role=0,  # ROLE_USER
    created_at=datetime.utcnow()
)
```

#### FR 1.2: Đăng Nhập
**ID:** REQ-USER-002  
**Ưu tiên:** High  
**Mô tả:**
User đăng nhập bằng email hoặc username và mật khẩu.

**Điều kiện tiên quyết:**
- User chưa đăng nhập
- Tài khoản tồn tại

**Luồng chính:**
1. User nhập email/username và mật khẩu
2. Hệ thống tìm user trong database
3. Xác thực mật khẩu (check_password_hash)
4. Nếu chính xác → Tạo session, lưu user_id
5. Redirect đến /dashboard

**Luồng ngoại lệ:**
- User không tồn tại → Lỗi "Email/username không tồn tại"
- Mật khẩu sai → Lỗi "Mật khẩu không đúng"

**Yêu cầu bảo mật:**
- Mật khẩu không được hiển thị
- Sử dụng HTTPS
- Session timeout sau 7 ngày

#### FR 1.3: Chỉnh Sửa Hồ Sơ
**ID:** REQ-USER-003  
**Ưu tiên:** Medium  
**Mô tả:**
User có thể chỉnh sửa họ tên và username.

**Dữ liệu có thể chỉnh sửa:**
- Họ tên (name)
- Username (phải kiểm tra duy nhất)

**Dữ liệu không thể chỉnh sửa:**
- Email (một lần thiết lập là không thay đổi)
- Mật khẩu (sử dụng form riêng nếu cần)

#### FR 1.4: Đăng Xuất
**ID:** REQ-USER-004  
**Ưu tiên:** High  
**Mô tả:**
User có thể đăng xuất khỏi hệ thống.

**Luồng chính:**
1. User click "Logout"
2. Hệ thống xóa session
3. Redirect đến /home (trang public)

### 3.2 Quản Lý Gói Từ Vựng

#### FR 2.1: Tạo Gói Từ Vựng
**ID:** REQ-PKG-001  
**Ưu tiên:** High  
**Mô tả:**
User có thể tạo gói từ vựng mới. Gói có thể được tạo bằng:
1. Upload file (CSV, XLSX)
2. Nhập thủ công qua form

**Dữ liệu gói từ vựng:**
| Trường | Kiểu | Bắt buộc | Giới hạn | Mô tả |
|--------|------|----------|---------|-------|
| package_name | String | Có | Max 100 | Tên gói |
| package_description | Text | Không | Max 70 | Mô tả ngắn |
| topic | String | Không | - | Chủ đề (từ TopicCatalog) |
| is_public | Boolean | Có | - | Công khai/Riêng tư |
| user_id | Integer | Có (hệ thống) | - | ID người tạo |
| created_at | DateTime | Có (hệ thống) | - | Thời gian tạo |
| updated_at | DateTime | Có (hệ thống) | - | Lần cập nhật cuối |

**Dữ liệu từ vựng:**
| Trường | Kiểu | Bắt buộc | Giới hạn |
|--------|------|----------|---------|
| word_en | String | Có | Max 150 |
| word_vi | String | Có | Max 255 |
| package_id | Integer | Có (hệ thống) | FK |

**Luồng tạo từ upload file:**
1. User vào /create
2. Điền tên gói, mô tả, chủ đề, visibility
3. Upload file (CSV/XLSX)
4. Hệ thống parse file
5. Hiển thị preview review.html
6. User xác nhận hoặc chỉnh sửa
7. Submit → Lưu gói và từ vựng
8. Redirect đến /package/<id>

**Luồng tạo từ form:**
1. User vào /create
2. Điền thông tin gói
3. Click "Create Package" (không có file)
4. Tạo gói trống
5. Redirect đến /package/<id>
6. User có thể thêm từ sau

**Định dạng file CSV:**
```csv
Tiếng Anh,Tiếng Việt
apple,quả táo
book,quyển sách
car,xe hơi
```

**Định dạng file XLSX:**
- Hàng 1 (tùy chọn): Header (English, Tiếng Anh, etc.)
- Từ hàng 2 trở đi: Cột A = English, Cột B = Vietnamese

**Output:**
```python
VocabPackage(
    package_name="IELTS Academic 8.0+",
    package_description="Từ vựng học thuật cho IELTS",
    topic="IELTS Common Topics",
    user_id=5,
    is_public=True,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
# Kèm theo 0-n Vocabulary records
```

#### FR 2.2: Xem Chi Tiết Gói Từ Vựng
**ID:** REQ-PKG-002  
**Ưu tiên:** High  
**Mô tả:**
Hiển thị thông tin chi tiết của một gói từ vựng.

**Quyền truy cập:**
- Gói công khai: Ai cũng có thể xem
- Gói riêng tư: Chỉ chủ sở hữu + admin
- User đã lưu gói: Có quyền xem
- User admin: Có quyền xem tất cả

**Hiển thị:**
- Banner với thông tin gói (tên, tác giả, số từ, topic, visibility)
- Nút Save/Unsave (nếu không phải chủ sở hữu)
- Nút Edit/Delete (nếu là chủ sở hữu hoặc admin)
- 4 Mastery Pathways (Flashcard, Quiz, Test, Match)
- Vocabulary Ledger (danh sách từ với search)
- Số người đã lưu gói (learner count)

#### FR 2.3: Chỉnh Sửa Gói Từ Vựng
**ID:** REQ-PKG-003  
**Ưu tiên:** High  
**Mô tả:**
Chủ sở hữu hoặc admin có thể chỉnh sửa gói.

**Có thể chỉnh sửa:**
- Tên, mô tả, topic
- Visibility (công khai/riêng tư)
- Từ vựng (thêm, sửa, xóa)

**Hai cách chỉnh sửa từ vựng:**
1. **Upload file mới:** Thay thế tất cả từ hiện tại
2. **Chỉnh sửa từng từ:** Thêm hàng mới, sửa hàng cũ, xóa hàng

**Luồng chính:**
1. GET /package/<id>/edit → Hiển thị form
2. Người dùng chỉnh sửa
3. POST với dữ liệu mới
4. Nếu có file upload → Replace all vocabularies
5. Nếu có form input → Update từng từ
6. Cập nhật updated_at
7. Commit DB
8. Redirect đến /package/<id>

#### FR 2.4: Xóa Gói Từ Vựng
**ID:** REQ-PKG-004  
**Ưu tiên:** High  
**Mô tả:**
Chủ sở hữu hoặc admin có thể xóa gói.

**Quy trình:**
1. User click nút Delete
2. Hiển thị modal xác nhận
3. Nếu confirm → Xóa VocabPackage (cascade delete Vocabulary)
4. Xóa user_saved_packages relationships
5. Redirect đến /packages

**Cảnh báo:**
- Hiển thị tên gói sẽ bị xóa
- Tất cả từ vựng sẽ bị xóa vĩnh viễn

#### FR 2.5: Tìm Kiếm và Lọc Gói
**ID:** REQ-PKG-005  
**Ưu tiên:** Medium  
**Mô tả:**
User có thể tìm kiếm gói theo:
- Tên gói
- Tác giả (username)
- Chủ đề (topic)
- Mô tả

**Tìm kiếm:**
- Normalize text (xóa diacritics)
- Search trong package_name, user.username, topic, description
- Trả về tối đa 20 kết quả

**Lọc theo topic:**
- Chỉ hiển thị gói có topic == selected_topic
- Topic từ TopicCatalog database

**Vị trí:**
- /packages?q=IELTS → Tìm kiếm
- /packages?topic=Business → Lọc
- /dashboard?q=...&topic=... → Dashboard

### 3.3 Lưu Gói (Bookmarking)

#### FR 3.1: Lưu Gói Từ Vựng
**ID:** REQ-SAVE-001  
**Ưu tiên:** High  
**Mô tả:**
User có thể lưu gói công khai của người khác.

**Điều kiện:**
- Gói phải công khai (is_public=True)
- User không phải chủ sở hữu
- User chưa lưu gói này trước đó

**Luồng:**
1. User xem gói công khai
2. Click "Save Package"
3. POST /package/<id>/save
4. Hệ thống thêm record vào user_saved_packages
5. Hiển thị thông báo "Đã lưu"
6. Cập nhật UI (button → "Unsave")

**Data:**
```
user_saved_packages (junction table):
- user_id (FK → users)
- package_id (FK → vocab_packages)
```

#### FR 3.2: Bỏ Lưu Gói
**ID:** REQ-SAVE-002  
**Ưu tiên:** Medium  
**Mô tả:**
User có thể bỏ lưu gói đã lưu trước đó.

**Luồng:**
1. User click "Unsave"
2. POST /package/<id>/unsave
3. Xóa record từ user_saved_packages
4. Hiển thị "Đã xóa khỏi thư viện"
5. Cập nhật UI

### 3.4 Các Chế Độ Học Tập

#### FR 4.1: Flashcard (Lật Thẻ)
**ID:** REQ-STUDY-001  
**Ưu tiên:** High  
**Mô tả:**
Chế độ lật thẻ hai mặt để ghi nhớ từ vựng.

**Đặc tính:**
- Mặt trước: Hiển thị từ tiếng Anh
- Mặt sau: Hiển thị dịch tiếng Việt
- Có thể lật thẻ bằng click hoặc phím Space
- Điều hướng: Mũi tên trái/phải hoặc Next/Previous button

**Chức năng:**
- Shuffle: Đảo lộn thứ tự thẻ
- Reset: Quay lại thứ tự ban đầu
- Counter: Hiển thị vị trí hiện tại (n/total)
- Completion modal: Khi xem xong tất cả

**Phím tắt:**
| Phím | Chức năng |
|------|----------|
| Space | Lật thẻ |
| ← | Thẻ trước |
| → | Thẻ tiếp theo |
| Escape | Đóng modal |

**Tracking:**
- Gọi POST /api/progress/seen cho mỗi từ
- Cập nhật UserVocabProgress.seen_count += 1
- Cập nhật last_seen_at = now()

**Output:**
```
GET /package/<id>/flashcard
Template: flashcard.html
Data: {
    package: VocabPackage,
    words: ["apple", "book", ...],
    meanings: ["quả táo", "quyển sách", ...],
    vocabIds: [1, 2, ...]
}
```

#### FR 4.2: Quiz (Trắc Nghiệm)
**ID:** REQ-STUDY-002  
**Ưu tiên:** High  
**Mô tả:**
Chế độ trắc nghiệm đa lựa chọn với phương pháp học tập thích ứng.

**Cơ chế:**
- **Round:** Nhóm câu hỏi trong một vòng
- **Pool:** Tổng cộng tất cả từ vựng trong gói
- **Mastery:** Từ vựng có correct_streak >= 2 được coi là "mastered"

**Thuật toán chọn từ:**
1. Tập pool = tất cả từ vựng
2. Mỗi round:
   - Chọn những từ chưa "mastered" (correct_streak < 2)
   - Ưu tiên từ sai nhiều nhất
   - Rồi đến từ chưa thấy
   - Rồi đến từ thấy 1 lần nhưng chưa đúng
3. Kích thước round = 4-6 từ (tùy tổng số)

**Câu hỏi:**
- Ngẫu nhiên EN→VI hoặc VI→EN
- 4 lựa chọn: 1 đáp án đúng + 3 wrong từ pool
- Hiển thị progressbar (mastered vs. seen vs. unlearned)

**Luồng:**
1. GET /package/<id>/quiz
2. Xây dựng pool từ vựng
3. Render round đầu tiên
4. User chọn đáp án
5. Highlight đúng/sai
6. Cập nhật stats
7. Advance to next question
8. Nếu hết câu trong round → Xây dựng round tiếp theo
9. Nếu tất cả mastered → Show result modal

**Tracking:**
- POST /api/progress/answer {vocab_id, correct}
- Cập nhật correct_count hoặc wrong_count

**Result modal:**
```
Thành thạo: n/total
Vòng: m
Tổng sai: k
```

#### FR 4.3: Test (Kiểm Tra Viết)
**ID:** REQ-STUDY-003  
**Ưu tiên:** High  
**Mô tả:**
Chế độ kiểm tra viết lại từ tiếng Việt sang tiếng Anh (hoặc ngược lại).

**Đặc tính:**
- Hiển thị từ hoặc dịch
- User nhập từ tương ứng vào input text
- Hỗ trợ multiple answers (chuẩn hóa so sánh)
- Phím Enter → Jump to next question

**Chuẩn hóa so sánh:**
```python
def normalize(str):
    return str.lower().strip().replace(/\s+/g, ' ')
    # "  APPLE  " == "apple" ✓
```

**Luồng:**
1. GET /package/<id>/test
2. Xây dựng tất cả câu hỏi
3. Người dùng nhập đáp án cho từng câu
4. Highlight đúng/sai (có đáp án)
5. Click "Nộp bài" → Chấm điểm
6. Hiển thị kết quả: % đúng, số sai, số đúng

**Tracking:**
- POST /api/progress/answer cho mỗi câu

#### FR 4.4: Match (Ghép Thẻ)
**ID:** REQ-STUDY-004  
**Ưu tiên:** Medium  
**Mô tả:**
Chế độ chơi ghép thẻ tốc độ (memory game).

**Cơ chế:**
- Tối đa 10 cặp (20 thẻ) trên lưới
- Lưới responsive: 5 cột (desktop), 4 (tablet), 3 (mobile), 2 (phone)
- Các thẻ trộn lẫn: EN + VI từ cùng cặp
- Người dùng click để chọn 2 thẻ
- Nếu match → Thẻ biến mất
- Nếu không match → Thẻ lật ngược lại
- Timer hiển thị thời gian

**Luồng:**
1. GET /package/<id>/match
2. Lấy 10 cặp ngẫu nhiên từ gói
3. Xây dựng deck (EN + VI trộn lẫn)
4. Render lưới
5. User click thẻ
6. Logic matching
7. Khi match all → Show complete screen với time
8. "Play again" → Reset

**Tracking:**
- Ghi nhận thời gian hoàn thành
- Hiển thị kết quả

### 3.5 Theo Dõi Tiến Độ

#### FR 5.1: Lưu Tiến Độ Học Tập
**ID:** REQ-PROGRESS-001  
**Ưu tiên:** High  
**Mô tả:**
Hệ thống tự động theo dõi tiến độ của user cho từng từ vựng.

**Data Model:**
```python
UserVocabProgress(
    id: Integer (PK),
    user_id: Integer (FK),
    vocab_id: Integer (FK),
    package_id: Integer (FK),
    seen_count: Integer (default 0),
    correct_count: Integer (default 0),
    wrong_count: Integer (default 0),
    last_seen_at: DateTime
)
```

**API Endpoints:**

**POST /api/progress/seen**
```json
{
    "vocab_id": 5
}
```
Cập nhật: seen_count += 1, last_seen_at = now()

**POST /api/progress/answer**
```json
{
    "vocab_id": 5,
    "correct": true
}
```
Cập nhật:
- Nếu correct: correct_count += 1
- Nếu incorrect: wrong_count += 1
- last_seen_at = now()
- seen_count = max(seen_count, 1)

#### FR 5.2: Tính Toán Phần Trăm Hoàn Thành
**ID:** REQ-PROGRESS-002  
**Ưu tiên:** Medium  
**Mô tả:**
Hệ thống tính % hoàn thành của user cho mỗi gói.

**Công thức:**
```
percent_completed = round(
    (count_learned / total_vocab) * 100
)

Trong đó:
- count_learned = số từ có seen_count > 0
- total_vocab = tổng số từ trong gói
```

**Sử dụng:**
- Dashboard: Hiển thị progress bar cho "Recent Packages"
- Package detail: Hiển thị tiến độ (nếu cần)

**Function:**
```python
completion_percents_for_packages(
    user_id: int,
    package_ids: list[int]
) -> dict[int, int]
```

### 3.6 Quản Trị Hệ Thống

#### FR 6.1: Quản Lý Người Dùng (Admin)
**ID:** REQ-ADMIN-001  
**Ưu tiên:** Medium  
**Mô tả:**
Admin có thể tạo, chỉnh sửa, xóa người dùng.

**Admin Actions:**
- Tìm kiếm user theo username, email, name
- Tạo user mới (set role)
- Chỉnh sửa thông tin user (username, email, name, role, password)
- Xóa user (không thể xóa chính mình)

**Endpoints:**
- GET /admin/users → Danh sách user
- POST /admin/users/create → Tạo user mới
- GET /admin/users/<id>/edit → Form chỉnh sửa
- POST /admin/users/<id>/edit → Cập nhật
- POST /admin/users/<id>/delete → Xóa

#### FR 6.2: Quản Lý Gói (Admin)
**ID:** REQ-ADMIN-002  
**Ưu tiên:** Medium  
**Mô tả:**
Admin có thể quản lý tất cả gói từ vựng.

**Admin Actions:**
- Xem danh sách tất cả gói
- Tìm kiếm gói
- Chuyển đổi trạng thái công khai/riêng tư
- Xóa gói
- Xem số người đã lưu gói

**Endpoints:**
- GET /admin/packages → Danh sách
- POST /admin/packages/<id>/toggle_public → Chuyển visibility
- POST /admin/packages/<id>/delete → Xóa gói

#### FR 6.3: Bảng Điều Khiển Admin
**ID:** REQ-ADMIN-003  
**Ưu tiên:** Low  
**Mô tả:**
Hiển thị thống kê tổng quan hệ thống.

**Thông tin:**
- Tổng số user
- Tổng số gói
- Tổng số từ vựng
- 5 user mới nhất

### 3.7 Quản Lý Chủ Đề (Topic)

#### FR 7.1: Catalog Chủ Đề
**ID:** REQ-TOPIC-001  
**Ưu tiên:** Medium  
**Mô tả:**
Hệ thống duy trì danh sách chủ đề cố định.

**Danh sách chủ đề mặc định:**
1. Beginner English
2. Education & Learning
3. Work & Career
4. Business & Management
5. Technology & Digital Life
6. Environment & Sustainability
7. Health & Lifestyle
8. Communication & Social Skills
9. Travel & Cultural Experience
10. Society & Social Issues
11. Economics & Finance
12. Law & Government
13. Innovation & Entrepreneurship
14. IELTS Common Topics
15. Others

**Cơ chế:**
- Được lưu trong bảng TopicCatalog
- Được seed khi app startup
- Được hiển thị trong dropdown khi tạo/chỉnh sửa gói
- Được sử dụng để lọc trong Explore và Dashboard

---

## 4. YÊU CẦU KHÔNG CHỨC NĂNG (NONFUNCTIONAL REQUIREMENTS)

### 4.1 Hiệu Năng

#### NFR 1.1: Tốc Độ Load Trang
| Trang | Thời gian target | Ghi chú |
|-------|-----------------|--------|
| /home (Landing) | < 2s | Public page |
| /dashboard | < 1.5s | Fetching recent packages |
| /packages | < 1s | Paginated hoặc limited |
| /package/<id> | < 1s | Full detail load |
| Quiz questions | < 100ms | Per question |

#### NFR 1.2: Khả năng Mở Rộng
- Database: SQLite (có thể migrate sang PostgreSQL)
- Hỗ trợ tối thiểu: 10,000 user, 100,000 gói, 1M từ vựng
- Tối ưu hóa query: Eager loading, pagination, indexing

#### NFR 1.3: Độ Tin Cậy
- Uptime target: 99% (30 phút downtime/tháng)
- Backup database: Hàng ngày
- Error logging: Ghi lại tất cả lỗi 500+

### 4.2 Bảo Mật

#### NFR 2.1: Xác Thực
- Mật khẩu phải được hash (werkzeug.security)
- Session cookie với HttpOnly flag
- Session timeout: 7 ngày (nếu "Remember me")

#### NFR 2.2: Ủy Quyền
- Role-based access control (RBAC)
- Admin vs. Regular User
- Kiểm tra quyền truy cập gói (is_owner, is_public, is_saved)

#### NFR 2.3: Dữ Liệu
- Validate input trước khi lưu
- SQL injection prevention: Dùng ORM (SQLAlchemy)
- XSS prevention: Escape HTML output

#### NFR 2.4: File Upload
- Kích thước tối đa: 5MB
- Loại file cho phép: CSV, XLSX, XLS
- Validate MIME type
- Lưu trong /uploads folder

### 4.3 Khả Dụng

#### NFR 3.1: Responsive Design
- Desktop (≥1024px): Grid layout
- Tablet (768-1023px): 2-column layout
- Mobile (<768px): 1-column layout

#### NFR 3.2: Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

#### NFR 3.3: Accessibility
- Alt text cho images
- Semantic HTML5
- ARIA labels nơi cần
- Color contrast > 4.5:1

### 4.4 Dễ Bảo Trì

#### NFR 4.1: Code Quality
- Code style: PEP 8 (Python)
- Comments: Tối thiểu 50% complex functions
- Modular design: Services folder

#### NFR 4.2: Documentation
- Docstrings cho functions
- README.md với setup instructions
- API documentation

#### NFR 4.3: Logging
- Log level: DEBUG, INFO, WARNING, ERROR
- Destination: Console + file

### 4.5 Usability

#### NFR 5.1: Kinh Nghiệm Người Dùng
- Onboarding: Landing page rõ ràng
- Confirmation dialogs: Trước xóa
- Flash messages: Feedback tức thời
- Keyboard shortcuts: Space, Arrow keys

#### NFR 5.2: Responsive Feedback
- Loading indicators
- Success/error messages
- Progress bars (quiz, test)
- Scroll-to-top buttons

---

## 5. CẤU TRÚC DỮ LIỆU (DATA REQUIREMENTS)

### 5.1 Entity-Relationship Diagram

```
┌──────────────────┐         ┌─────────────────────┐
│     Users        │         │  VocabPackages     │
├──────────────────┤         ├─────────────────────┤
│ id (PK)          │────┐    │ id (PK)             │
│ username         │    │    │ package_name        │
│ name             │    └────│ user_id (FK)        │
│ email            │         │ package_description │
│ password_hash    │         │ topic               │
│ role             │         │ is_public           │
│ created_at       │         │ created_at          │
└──────────────────┘         │ updated_at          │
        │                    └─────────────────────┘
        │                              │
        │                              │
        │              ┌───────────────┴────────────┐
        │              │                            │
        │              │                     ┌──────────────────────┐
        │              │                     │  Vocabularies        │
        │              │                     ├──────────────────────┤
        │              │                     │ id (PK)              │
        │              │                     │ word_en              │
        │              │                     │ word_vi              │
        │              │                     │ package_id (FK)      │
        │              │                     └──────────────────────┘
        │              │                              │
        │              │                              │
        │              │                     ┌────────┴──────────────┐
        │              │                     │                       │
        │   ┌──────────────────────────────────┐   ┌─────────────────────────────┐
        │   │  UserVocabProgress               │   │  user_saved_packages        │
        │   ├──────────────────────────────────┤   ├─────────────────────────────┤
        │   │ id (PK)                          │   │ user_id (FK)                │
        │   │ user_id (FK) ─────────┐          │   │ package_id (FK)             │
        │   │ vocab_id (FK) ────────┼──┐       │   │ (composite PK)              │
        │   │ package_id (FK) ───┐  │  │       │   └─────────────────────────────┘
        │   │ seen_count         │  │  │       │
        │   │ correct_count      │  │  │       │
        │   │ wrong_count        │  │  │       │
        │   │ last_seen_at       │  │  │       │
        │   └────────────────────── ┘  │        │
        │                              │        │
        └────────────────────────────  ┘│       │
                                        │       │
        ┌───────────────────────────────┘       │
        │                                       │
        └───────────────────────────────────────┘

┌─────────────────────┐
│  TopicCatalog       │
├─────────────────────┤
│ id (PK)             │
│ name (UNIQUE)       │
└─────────────────────┘
```

### 5.2 Database Schema

```sql
-- Users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100),
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- VocabPackages
CREATE TABLE vocab_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name VARCHAR(100) NOT NULL,
    package_description TEXT,
    topic VARCHAR(80),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES users(id),
    is_public BOOLEAN DEFAULT TRUE
);

-- Vocabularies
CREATE TABLE vocabularies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_en VARCHAR(150) NOT NULL,
    word_vi VARCHAR(255) NOT NULL,
    package_id INTEGER NOT NULL REFERENCES vocab_packages(id)
);

-- UserVocabProgress
CREATE TABLE user_vocab_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    vocab_id INTEGER NOT NULL REFERENCES vocabularies(id),
    package_id INTEGER NOT NULL REFERENCES vocab_packages(id),
    seen_count INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    wrong_count INTEGER NOT NULL DEFAULT 0,
    last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, vocab_id)
);

-- user_saved_packages (junction table)
CREATE TABLE user_saved_packages (
    user_id INTEGER NOT NULL REFERENCES users(id),
    package_id INTEGER NOT NULL REFERENCES vocab_packages(id),
    PRIMARY KEY (user_id, package_id)
);

-- TopicCatalog
CREATE TABLE topic_catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) UNIQUE NOT NULL
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_vocab_packages_user_id ON vocab_packages(user_id);
CREATE INDEX idx_vocab_packages_topic ON vocab_packages(topic);
CREATE INDEX idx_vocabularies_package_id ON vocabularies(package_id);
CREATE INDEX idx_user_vocab_progress_user_id ON user_vocab_progress(user_id);
CREATE INDEX idx_user_vocab_progress_vocab_id ON user_vocab_progress(vocab_id);
```

### 5.3 Validation Rules

| Trường | Rule |
|--------|------|
| username | 3-50 ký tự, alphanumeric + underscore |
| email | Valid email format, unique |
| password | Min 8 ký tự (recommended) |
| package_name | 1-100 ký tự, required |
| package_description | 0-70 ký tự |
| word_en | 1-150 ký tự, required |
| word_vi | 1-255 ký tự, required |
| topic | Must exist in TopicCatalog |
| file_size | ≤ 5MB |
| file_type | CSV, XLSX, XLS only |

---

## 6. CÁC USE CASE CHÍNH

### 6.1 Use Case 1: Tạo và Học Gói Từ

```
Actor: Regular User
Precondition: User đã đăng nhập

Main Flow:
1. User vào /create
2. Điền tên gói "IELTS Vocabulary"
3. Upload file CSV
4. Hệ thống parse và preview
5. User review từ vựng
6. Click "Create Package"
7. System lưu gói vào database
8. Redirect đến /package/<id>
9. User click Flashcard
10. Học 25 từ bằng phương pháp flashcard
11. System track từng từ (seen_count)
12. Hoàn thành → Show "Well done!" modal
13. Redirect đến quiz

Postcondition:
- VocabPackage mới được tạo
- 25 Vocabulary records được lưu
- UserVocabProgress entries được tạo
```

### 6.2 Use Case 2: Khám Phá và Lưu Gói

```
Actor: Regular User
Precondition: User đã đăng nhập

Main Flow:
1. User vào /explore
2. Tìm kiếm "IELTS"
3. System hiển thị 20 gói public
4. User click gói "IELTS Academic 8.0+"
5. Xem chi tiết gói
6. Click "Save Package"
7. System thêm vào user_saved_packages
8. User vào /packages?tab=saved
9. Xem gói đã lưu
10. Click Quiz
11. Thực hiện quiz 3 vòng
12. System calculate % mastered
13. Show result modal

Postcondition:
- Package được lưu vào thư viện user
- UserVocabProgress records updated
- Stats tính toán (% mastered)
```

### 6.3 Use Case 3: Quản Lý Gói (Edit)

```
Actor: Regular User (owner)
Precondition: User là chủ sở hữu gói

Main Flow:
1. User vào /packages (tab: mine)
2. Click gói "My Vocab Collection"
3. Click Edit (hamburger menu)
4. Edit tên thành "Advanced Vocabulary"
5. Upload file XLSX mới (100 từ)
6. System parse file, show confirmation
7. User confirm → Replace all vocabularies
8. Update topic = "Business & Management"
9. Click "Save Package"
10. Redirect đến package detail
11. Thấy 100 từ mới

Postcondition:
- VocabPackage updated (name, topic, updated_at)
- Cũ Vocabulary entries deleted
- 100 Vocabulary records created mới
```

### 6.4 Use Case 4: Admin Quản Lý Hệ Thống

```
Actor: Admin
Precondition: User có role=ROLE_ADMIN

Main Flow:
1. Admin vào /admin
2. Xem dashboard: 150 users, 500 packages, 50K words
3. Vào /admin/packages
4. Tìm kiếm "inappropriate"
5. Tìm thấy gói công khai có nội dung không phù hợp
6. Click toggle_public → Set is_public=False
7. Gói không xuất hiện trên /explore
8. Vào /admin/users
9. Tìm user spam
10. Click Delete
11. Confirm → User + packages + progress deleted (cascade)

Postcondition:
- Gói không phù hợp bị ẩn
- User spam bị xóa vĩnh viễn
```

---

## 7. LUỒNG CƠ BẢN (BASIC FLOW)

### 7.1 Luồng Trang Chủ (Landing Page)

```
Guest/User
    ↓
GET /home (if not authenticated) / /dashboard (if authenticated)
    ↓
Hiển thị hero banner
    ↓
Hiển thị 4 phương pháp học
    ↓
Hiển thị 12 gói public ngẫu nhiên
    ↓
CTA: "Get started" / "Explore"
```

### 7.2 Luồng Đăng Ký

```
Guest
    ↓
GET /register (form)
    ↓
POST /register (data)
    ↓
Validate (email/username unique)
    ↓
Tạo User
    ↓
Hash password
    ↓
Lưu database
    ↓
Flash success message
    ↓
Redirect /login
```

### 7.3 Luồng Học Tập (Quiz)

```
User
    ↓
GET /package/<id>/quiz
    ↓
Build pool từ tất cả vocabulary
    ↓
Build round 1 (4-6 từ chưa mastered)
    ↓
Loop:
  - Render question
  - User select option
  - Check answer
  - POST /api/progress/answer
  - Update stats (correct_count / wrong_count)
  - Show feedback (correct/wrong)
  - Next question
    ↓
Round complete?
  ↓ No: Build next round
  ↓ Yes: All mastered?
    ↓
Show result modal (mastery %, rounds, wrong count)
    ↓
User: "Làm lại" or "Flashcard" or "Đóng"
```

---

## 8. CÁC ĐIỀU KIỆN TIÊN QUYẾT VÀ GIẢ ĐỊNH

### 8.1 Giả Định

1. **Người dùng:**
   - Có kết nối internet
   - Hiểu tiếng Anh ở mức cơ bản
   - Sử dụng browser hiện đại

2. **Dữ liệu:**
   - Từ vựng được nhập chính xác
   - File upload không bị corrupt
   - Email hợp lệ

3. **Hệ thống:**
   - Server có thể truy cập database
   - Disk space đủ cho uploads
   - Network latency < 2s

### 8.2 Giới Hạn

1. **Thực tế:**
   - SQLite (có thể chuyển sang PostgreSQL)
   - Server đơn (không load balancing)
   - Không có real-time notifications

2. **Kỹ thuật:**
   - Max file upload: 5MB
   - Max package name: 100 chars
   - Max description: 70 chars
   - Max trie trong database: 1M vocabularies

---

## 9. INTERFACE REQUIREMENTS

### 9.1 User Interface

**Pages:**
| Route | Name | Access | Template |
|-------|------|--------|----------|
| / | Home | All | Redirect /home or /dashboard |
| /home | Landing | Guest | landing.html |
| /explore | Explore | All | explore.html |
| /login | Login | Guest | login.html |
| /register | Register | Guest | register.html |
| /dashboard | Dashboard | User+ | index.html |
| /profile | Profile | User+ | profile.html |
| /profile/edit | Edit Profile | User+ | edit_profile.html |
| /packages | Library | User+ | packages.html |
| /package/<id> | Detail | All* | package_detail.html |
| /package/<id>/edit | Edit | Owner+Admin | edit_package.html |
| /create | Create | User+ | create_package.html |
| /package/<id>/flashcard | Flashcard | User+* | flashcard.html |
| /package/<id>/quiz | Quiz | User+* | quiz.html |
| /package/<id>/test | Test | User+* | test_mode.html |
| /package/<id>/match | Match | User+* | match_mode.html |
| /admin | Admin Dashboard | Admin | admin/dashboard.html |
| /admin/users | User Management | Admin | admin/users.html |
| /admin/packages | Package Mgmt | Admin | admin/packages.html |

*Access: All = Guests & Users, User+ = Authenticated users, Owner+Admin = Package owner or admin

### 9.2 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /login | No | User login |
| POST | /register | No | User register |
| GET | /logout | Yes | User logout |
| POST | /profile/edit | Yes | Update profile |
| POST | /api/progress/seen | Yes | Mark vocab as seen |
| POST | /api/progress/answer | Yes | Record quiz answer |
| GET | /download_template | Yes | Download CSV template |
| POST | /package/<id>/save | Yes | Save package |
| POST | /package/<id>/unsave | Yes | Unsave package |
| POST | /delete_package/<id> | Yes* | Delete package |
| POST | /word/<id>/delete | Yes* | Delete vocab |
| POST | /admin/users | Admin | Create user |
| POST | /admin/users/<id>/edit | Admin | Edit user |
| POST | /admin/users/<id>/delete | Admin | Delete user |
| POST | /admin/packages/<id>/toggle_public | Admin | Toggle visibility |
| POST | /admin/packages/<id>/delete | Admin | Delete package |

### 9.3 Responsive Breakpoints

```
xs: < 576px   (extra small devices)
sm: 576-768px (phones)
md: 768-992px (tablets)
lg: 992-1200px (desktops)
xl: ≥ 1200px (large desktops)
```

---

## 10. TIÊU CHÍ CHẤP NHẬN (ACCEPTANCE CRITERIA)

### 10.1 Authentication Module

- [x] User có thể đăng ký với email, username, password
- [x] Kiểm tra email/username unique
- [x] Hash password bằng werkzeug.security
- [x] User có thể đăng nhập bằng email hoặc username
- [x] Session timeout 7 ngày
- [x] User có thể đăng xuất
- [x] User có thể chỉnh sửa profile

### 10.2 Package Management Module

- [x] User có thể tạo gói từ file (CSV/XLSX)
- [x] User có thể tạo gói thủ công
- [x] User có thể xem danh sách gói
- [x] User có thể tìm kiếm gói
- [x] User có thể lọc gói theo topic
- [x] User có thể chỉnh sửa gói
- [x] User có thể xóa gói
- [x] User có thể lưu gói công khai

### 10.3 Study Modes Module

- [x] Flashcard mode hoạt động đầy đủ (flip, navigate, shuffle)
- [x] Quiz mode có algorithm mastery
- [x] Test mode nhập text và chấm điểm
- [x] Match mode chơi memory game
- [x] Mỗi mode track progress

### 10.4 Progress Tracking Module

- [x] Hệ thống ghi nhận seen_count
- [x] Hệ thống ghi nhận correct/wrong count
- [x] Tính toán % completion chính xác
- [x] Hiển thị progress bar

### 10.5 Admin Module

- [x] Admin quản lý user
- [x] Admin quản lý gói
- [x] Admin xem dashboard stats

---

## 11. RÀNG BUỘC VÀ PHỤ THUỘC

### 11.1 Phụ Thuộc Công Nghệ

| Thành phần | Yêu cầu | Ghi chú |
|-----------|--------|--------|
| Framework | Flask 2.0+ | Web framework |
| Database | SQLAlchemy ORM | Database abstraction |
| Auth | Flask-Login | Session management |
| Security | werkzeug | Password hashing |
| Frontend | Bootstrap 5.3 | CSS framework |
| JS Libs | FontAwesome 6.5 | Icons |
| Python | 3.8+ | Runtime |

### 11.2 Ràng Buộc Kinh Doanh

1. **Miễn phí:** Không có mô hình subscription ban đầu
2. **Công khai:** Gói được chia sẻ công khai theo mặc định
3. **Dữ liệu:** Người dùng là chủ sở hữu dữ liệu của họ
4. **Admin:** Default admin tạo khi startup (admin / admin123)

---

## 12. LỘ TRÌNH PHÁT TRIỂN (ROADMAP)

### Phase 1 (v1.0) - MVP ✓
- [x] Auth (register/login/logout)
- [x] Package CRUD
- [x] Flashcard mode
- [x] Quiz mode
- [x] Basic progress tracking
- [x] Admin dashboard

### Phase 2 (v1.1) - Enhancement
- [ ] Test mode ✓
- [ ] Match mode ✓
- [ ] Topic catalog ✓
- [ ] Save packages ✓

### Phase 3 (v2.0) - Growth
- [ ] Mobile app (React Native)
- [ ] AI-powered hints
- [ ] Social features (comments, ratings)
- [ ] Export progress (PDF)
- [ ] Integration email (stats reminder)

### Phase 4 (v2.5) - Monetization
- [ ] Premium features
- [ ] Subscription plans
- [ ] Content marketplace

---

## 13. GLOSSARY (THUẬT NGỮ)

| Thuật ngữ | Định nghĩa |
|----------|-----------|
| **Package** | Gói từ vựng chứa một nhóm các từ tiếng Anh |
| **Vocabulary** | Từ vựng đơn lẻ (cặp EN-VI) |
| **Flashcard** | Thẻ học hai mặt (EN mặt trước, VI mặt sau) |
| **Quiz** | Câu hỏi trắc nghiệm đa lựa chọn |
| **Test** | Kiểm tra viết lại từ tiếng Việt sang tiếng Anh |
| **Match** | Trò chơi ghép cặp từ-dịch |
| **Mastery** | Từ vựng được coi là "thành thạo" (correct_streak >= 2) |
| **Seen Count** | Số lần từ xuất hiện trong học tập |
| **Correct Count** | Số lần trả lời đúng |
| **Wrong Count** | Số lần trả lời sai |
| **Topic** | Chủ đề phân loại gói từ vựng |
| **Public** | Gói công khai (ai cũng xem được) |
| **Private** | Gói riêng tư (chỉ chủ sở hữu xem được) |
| **Learner** | Người dùng đã lưu gói từ vựng |
| **Admin** | Quản trị viên hệ thống |
| **Role** | Vai trò người dùng (User=0, Admin=1) |

---

## 14. THAM CHIẾU VÀ TÀI LIỆU LIÊN QUAN

- Database Schema: /database/schema.sql
- API Documentation: /docs/api.md
- User Stories: /docs/user_stories.md
- Wireframes: /docs/wireframes/
- Deployment Guide: /docs/deployment.md

---

**END OF DOCUMENT**

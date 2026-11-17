# 🎓 TÀI LIỆU ÔN TẬP PHỎNG VẤN (INTERVIEW CHEAT SHEET)
### Vị trí: Lập trình viên ERP/CRM (Node.js / Express)

Tài liệu này dùng từ ngữ **bình dân, thực tế, dễ nhớ** để bạn hoàn toàn làm chủ mã nguồn và tự tin đối đáp với người phỏng vấn.

---

## 🎯 1. BẠN GIỚI THIỆU TỔNG QUAN VỀ DỰ ÁN NHƯ THẾ NÀO?
> *"Dạ em chào anh/chị, dự án em nộp được xây dựng bằng **Node.js và Express**, sử dụng cơ sở dữ liệu **SQLite**. Dự án gồm 4 phần chính:*
> 1. *`database.js`: Khởi tạo bảng `orders` và lưu trữ dữ liệu.*
> 2. *`routes/orders.js`: Xử lý toàn bộ logic kiểm tra nghiệp vụ ở server: tự tính thành tiền (`quantity * unit_price`), kiểm tra số lượng và đơn giá dương, và khóa đơn khi trạng thái đã là 'Đã giao' hoặc 'Hủy'.*
> 3. *`routes/reports.js`: API báo cáo doanh thu theo ngày bằng câu lệnh SQL nhóm theo ngày tạo đơn và chỉ lọc các đơn đã giao.*
> 4. *`public/index.html`: Giao diện Desk trực quan có đầy đủ bảng danh sách, form tạo đơn và biểu đồ doanh thu.*
> *Đặc biệt, dự án có sẵn bộ Unit Test tự động trong `test.js` chạy bằng lệnh `npm test` với 100% bài kiểm tra đạt chuẩn."*

---

## 🔥 2. CÂU HỎI "ĂN ĐIỂM" NHẤT VỀ VIỆC CHỌN EXPRESS

### Câu hỏi: "Sao đề bài ghi ưu tiên Frappe mà em lại chọn Express?"
- **Trả lời (Cực kỳ thông minh và trung thực):**
  > *"Dạ đề bài có mở rộng cho phép sử dụng framework quen thuộc (Django, Laravel, Express...). Trước đây em làm việc chủ yếu với hệ sinh thái JavaScript/Node.js. Em chủ động chọn Express vì 3 lý do:*
  > 1. *Giúp em kiểm soát 100% từng dòng code logic từ validation, state machine đến câu truy vấn SQL mà không bị phụ thuộc vào "magic" ngầm của framework.*
  > 2. *Đảm bảo khi đi phỏng vấn, anh/chị yêu cầu sửa bất kỳ logic nào em cũng có thể live-code sửa ngay lập tức.*
  > 3. *Với nền tảng tư duy nghiệp vụ và kiến trúc sạch này, khi công ty yêu cầu dùng Frappe, em tự tin có thể nắm bắt và học rất nhanh trong vòng 1-2 tuần ạ."*

---

## 💡 3. BỘ CÂU HỎI VỀ LOGIC NGHIỆP VỤ

### Câu 1: "Tại sao thành tiền lại tính ở server mà không tin dữ liệu client gửi lên?"
- **Trả lời:**
  > *"Dạ để đảm bảo tính an toàn và toàn vẹn dữ liệu (Data Integrity). Người dùng có thể F12 (Inspect Element) hoặc dùng Postman gọi API để gửi số tiền sai lệch lên. Do đó, Frontend chỉ tính nhẩm để người dùng nhìn thấy trước, còn Server luôn luôn tự nhân lại `quantity * unit_price` trước khi INSERT/UPDATE vào Database."*

---

### Câu 2: "Cơ chế nào giúp em chặn người dùng sửa đơn khi đã 'Đã giao' hoặc 'Hủy'?"
- **Trả lời:**
  > *"Trong file `routes/orders.js`, trước khi cập nhật (ở cả route đổi trạng thái và route sửa thông tin), em luôn query DB để lấy trạng thái hiện tại của đơn hàng:*
  > ```javascript
  > const existing = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId);
  > if (existing.status === 'Đã giao' || existing.status === 'Hủy') {
  >     return res.status(400).json({ error: "Đơn hàng đã khóa, không thể sửa!" });
  > }
  > ```
  > *Dù người dùng thao tác trên giao diện hay cố tình gửi request PUT/PATCH qua Postman thì Server đều chặn đứng với mã lỗi 400."*

---

### Câu 3: "Câu truy vấn Báo cáo doanh thu theo ngày của em hoạt động thế nào?"
- **Trả lời:**
  > *"Dạ em viết câu truy vấn SQL chuẩn trong `routes/reports.js`:*
  > ```sql
  > SELECT 
  >     DATE(created_at) AS order_date,
  >     COUNT(id) AS total_orders,
  >     SUM(total_amount) AS total_revenue
  > FROM orders
  > WHERE status = 'Đã giao'
  > GROUP BY DATE(created_at)
  > ORDER BY order_date DESC;
  > ```
  > - *Lọc `status = 'Đã giao'` để loại bỏ đơn Mới và đơn Hủy.*
  > - *Dùng hàm `DATE(created_at)` để gom tất cả các đơn tạo trong cùng 1 ngày lại làm 1 dòng.*
  > - *Tính `COUNT(id)` để đếm số đơn và `SUM(total_amount)` để tính tổng tiền."*

---

## 🛠️ 4. NẾU NGƯỜI PHỎNG VẤN BẢO MỞ MÁY RA SỬA CODE (LIVE-CODING)

### Tình huống 1: "Bây giờ anh muốn số lượng tối thiểu phải từ 5 trở lên, em sửa ở đâu?"
- **Cách làm:**
  1. Mở file: `routes/orders.js`
  2. Tìm đến dòng 46:
     ```javascript
     // Sửa dòng này:
     if (isNaN(qty) || qty < 5) {
       return res.status(400).json({ error: `Số lượng tối thiểu phải từ 5 trở lên.` });
     }
     ```
  3. Bấm `Ctrl + S`, server reload là xong ngay trong 5 giây!

---

### Tình huống 2: "Nếu muốn thêm trường 'Ghi chú' (note) vào đơn hàng thì làm thế nào?"
- **Cách làm:**
  1. Vào `database.js`: Thêm cột `note TEXT` vào câu `CREATE TABLE orders`.
  2. Vào `routes/orders.js`: Lấy `const { note } = req.body;` và thêm `note` vào câu lệnh `INSERT INTO orders`.
  3. Vào `public/index.html`: Thêm 1 ô input `<input id="input-note">`.

---

### Tình huống 3: "Nếu sau này 1 đơn có nhiều mặt hàng (1 Order - Nhiều Items) thì em thiết kế DB thế nào?"
- **Cách trả lời (Tư duy kiến trúc Senior):**
  > *"Dạ lúc đó ta sẽ áp dụng quan hệ 1 - Nhiều (One-to-Many):*
  > 1. *Tách làm 2 bảng: Bảng `orders` (chứa `id`, `order_code`, `customer`, `total_amount`, `status`, `created_at`) và Bảng `order_items` (chứa `id`, `order_id`, `item`, `quantity`, `unit_price`, `amount`).*
  > 2. *Khi tạo đơn: Dùng Transaction, insert vào bảng `orders` trước, sau đó loop qua danh sách mặt hàng để insert vào `order_items` và tính tổng tiền cập nhật lại cho `orders`."*

---

## 🚀 5. LỆNH CẦN NHỚ
- Chạy server: `npm start` (Mở `http://localhost:3000`)
- Chạy test tự động: `npm test` (Chạy 8 bài test)

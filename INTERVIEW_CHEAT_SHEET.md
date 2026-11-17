# 🎓 TÀI LIỆU ÔN TẬP PHỎNG VẤN (INTERVIEW CHEAT SHEET)
### Vị trí: Lập trình viên ERP/CRM (Frappe / ERPNext)

Tài liệu này được biên soạn riêng cho bạn, dùng từ ngữ **bình dân, dễ nhớ, dễ hiểu** để bạn tự tin giải thích mã nguồn và xử lý các câu hỏi "xoáy" của người phỏng vấn.

---

## 🎯 1. BẠN GIỚI THIỆU TỔNG QUAN VỀ DỰ ÁN NHƯ THẾ NÀO?
> *"Dạ em chào anh/chị, dự án em nộp là một Frappe App tên là `order_management`. App gồm 3 phần chính:*
> 1. *Một DocType tên là `Order` để quản lý đơn hàng.*
> 2. *Controller ở file `order.py` chạy ở server để tính toán thành tiền, validate số lượng/đơn giá dương, và khóa đơn khi đã Giao hoặc Hủy.*
> 3. *Một Script Report tên là `Daily Revenue Report` dùng câu lệnh SQL nhóm theo ngày tạo đơn để tính tổng doanh thu các đơn đã giao.*
> *Toàn bộ logic nghiệp vụ đều có Unit Test tự động đi kèm trong `test_order.py`."*

---

## 🔥 2. BỘ CÂU HỎI KINH ĐIỂN VỀ LOGIC CODE

### Câu 1: "Tại sao em phải tính thành tiền ở Server mà không để Frontend tính rồi gửi lên?"
- **Trả lời:** 
  > *"Dạ để đảm bảo tính an toàn dữ liệu (Data Integrity). Người dùng có thể F12 (Inspect Element) hoặc dùng Postman gọi API để gửi số tiền sai lệch lên. Do đó, Frontend chỉ tính nhẩm để người dùng nhìn thấy trước, còn Server luôn luôn tự nhân lại `quantity * unit_price` để lưu vào Database."*

---

### Câu 2: "Cơ chế nào giúp em chặn người dùng sửa đơn khi đã 'Đã giao' hoặc 'Hủy'?"
- **Trả lời:**
  > *"Em sử dụng hook `validate()` trong file `order.py`. Khi một đơn hàng được cập nhật, em dùng hàm `self.get_doc_before_save()` của Frappe để lấy ra trạng thái cũ đang lưu trong Database.*
  > *Nếu trạng thái cũ là 'Đã giao' hoặc 'Hủy', em dùng `frappe.throw()` để chặn ngay lập tức. Dù người dùng bấm trên giao diện hay gọi API từ bên ngoài vào thì Server đều chặn đứng."*

---

### Câu 3: "Tại sao em lại dùng hook `validate()` mà không phải `before_save()` hay `on_update()`?"
- **Trả lời:**
  > *"Trong vòng đời (Lifecycle) của DocType trong Frappe, `validate()` là hook chuẩn nhất để kiểm tra tính hợp lệ của dữ liệu trước khi lưu. Nếu có lỗi và gọi `frappe.throw()`, toàn bộ giao dịch (Transaction) sẽ tự động rollback, dữ liệu sai không bao giờ bị ghi vào DB."*

---

### Câu 4: "Dữ liệu của DocType này nằm ở bảng nào trong Database?"
- **Trả lời:**
  > *"Trong Frappe, mọi DocType đều được tự động ánh xạ thành một bảng trong MariaDB có tiền tố `tab`. Vì vậy DocType `Order` sẽ nằm ở bảng **`tabOrder`** ạ."*

---

### Câu 5: "Báo cáo doanh thu theo ngày được lấy dữ liệu như thế nào?"
- **Trả lời:**
  > *"Em tạo một Script Report, trong file `daily_revenue_report.py` em viết một câu lệnh SQL query trực tiếp vào bảng `tabOrder`:*
  > - *Lọc `status = 'Đã giao'`*
  > - *Hàm `DATE(creation)` để lấy ngày tạo đơn*
  > - *`GROUP BY DATE(creation)`*
  > - *Tính `COUNT(name)` để ra số đơn và `SUM(total_amount)` để ra tổng doanh thu theo từng ngày."*

---

## 🛠️ 3. KỊCH BẢN "LIVE-CODING": NẾU NGƯỜI PHỎNG VẤN BẢO SỬA CODE

Người phỏng vấn rất hay bảo: *"Bây giờ anh muốn đổi yêu cầu này, em mở code ra sửa cho anh xem?"*
Dưới đây là 3 tình huống họ hay hỏi nhất:

### Tình huống 1: "Nếu muốn số lượng tối thiểu phải là 5 (thay vì > 0) thì sửa ở đâu?"
- **Cách làm:**
  1. Mở file: `order_management/order_management/doctype/order/order.py`
  2. Tìm hàm `validate_quantities_and_prices`:
     ```python
     # Sửa dòng này:
     if flt(self.quantity) < 5:
         frappe.throw(_("Số lượng tối thiểu phải từ 5 trở lên."))
     ```

---

### Tình huống 2: "Nếu muốn thêm trường 'Ghi chú' (Note) vào đơn hàng thì sửa ở đâu?"
- **Cách làm:**
  1. Mở file: `order_management/order_management/doctype/order/order.json`
  2. Thêm vào mảng `fields`:
     ```json
     {
      "fieldname": "note",
      "fieldtype": "Small Text",
      "label": "Ghi chú"
     }
     ```
  3. Sau đó chạy lệnh `bench --site [sitename] migrate` để Frappe cập nhật cột mới vào MariaDB.

---

### Tình huống 3: "Nếu sau này 1 đơn hàng có NHIỀU mặt hàng (Order có nhiều Items) thì thiết kế thế nào?"
- **Cách trả lời (Tư duy kiến trúc Senior):**
  > *"Dạ lúc đó ta sẽ dùng mô hình Master-Detail (Child Table) của Frappe:*
  > 1. *Tạo một DocType con tên là `Order Item`, đánh dấu là `Is Child Table` (chứa item, quantity, unit_price, amount).*
  > 2. *Trên DocType cha `Order`, thêm một field kiểu `Table` trỏ vào `Order Item`.*
  > 3. *Trong hàm `validate()` của `Order`, ta chỉ cần duyệt vòng lặp `for item in self.items:` để cộng dồn tiền từng dòng con vào `self.total_amount`."*
  > *(Trả lời câu này thì 100% người phỏng vấn sẽ gật gù khen bạn có tư duy chuẩn ERP).*

---

## 🚀 4. DANH SÁCH LỆNH CẦN THUỘC LÒNG (KHI THAO TÁC TERMINAL)

- Khởi động server Frappe: `bench start`
- Chạy unit test kiểm tra code: `bench --site [sitename] run-tests --app order_management`
- Cập nhật database khi sửa doctype json: `bench --site [sitename] migrate`
- Xóa cache khi sửa code JS/Python: `bench --site [sitename] clear-cache`

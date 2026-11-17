# Ứng Dụng Quản Lý Đơn Hàng (Order Management App)

Ứng dụng quản lý đơn hàng đơn giản được phát triển trên nền tảng **Frappe Framework**, đáp ứng đầy đủ và chặt chẽ các yêu cầu của bài test tuyển dụng Lập trình viên ERP/CRM.

---

## 📌 Tính Năng Đã Hoàn Thành (100%)

1. **Quản lý Đơn hàng (DocType `Order`):**
   - Các trường thông tin: Khách hàng (`customer`), Mặt hàng (`item`), Số lượng (`quantity`), Đơn giá (`unit_price`), Thành tiền (`total_amount`), Trạng thái (`status`).
   - Mỗi đơn quản lý một mặt hàng theo đúng yêu cầu đề bài.

2. **Kiểm tra và Tính toán Chặt chẽ ở Server (`order.py`):**
   - **Tự động tính thành tiền:** `Thành tiền = Số lượng × Đơn giá` thực hiện ở server trong hook `validate()`.
   - **Validation số liệu:** Bắt buộc `Số lượng > 0` và `Đơn giá > 0`. Nếu vi phạm sẽ ném lỗi `frappe.ValidationError` và hủy thao tác lưu.

3. **Máy Trạng Thái & Khóa Dữ Liệu (State Machine & Guard):**
   - Đơn hàng mới tạo mặc định ở trạng thái **Mới**.
   - Chỉ cho phép chuyển trạng thái từ `Mới` sang **Đã giao** hoặc **Hủy**.
   - **Ngăn chặn chỉnh sửa:** Khi đơn hàng đã ở trạng thái **Đã giao** hoặc **Hủy**, server sẽ chặn mọi thao tác sửa đổi thông tin hoặc cố tình đổi trạng thái (kiểm tra qua `self.get_doc_before_save()`).
   - Khóa nút xóa dữ liệu đối với các đơn hàng đã giao thành công nhằm bảo toàn dữ liệu kế toán.

4. **Báo cáo Doanh thu theo Ngày (Script Report):**
   - Nhóm dữ liệu theo ngày tạo đơn (`DATE(creation)`).
   - Chỉ tổng hợp các đơn hàng có trạng thái **Đã giao**.
   - Mỗi dòng gồm: **Ngày tạo đơn**, **Số lượng đơn đã giao**, **Tổng thành tiền**.
   - Có tích hợp sẵn biểu đồ cột trực quan (Bar Chart) hiển thị xu hướng doanh thu ngay trên màn hình Desk.

5. **Giao diện & Trải nghiệm Người dùng (Frappe Desk):**
   - Sử dụng màn hình Desk chuẩn của Frappe: Form View, List View với huy hiệu màu sắc trực quan (Xanh dương: Mới, Xanh lá: Đã giao, Đỏ: Hủy).
   - Tích hợp 2 nút bấm thao tác nhanh trên Form: **Đã giao** và **Hủy đơn**.
   - Tự động tính nhẩm thành tiền trên giao diện Form ngay khi người dùng gõ số lượng hoặc đơn giá (`order.js`).

6. **Kiểm Thử Tự Động (Automated Unit Tests):**
   - Bộ test đầy đủ trong `test_order.py` kiểm tra toàn bộ các trường hợp nghiệp vụ, số âm, số 0, chuyển trạng thái và ngăn chặn sửa đổi đơn cũ.

---

## ⚙️ Hướng Dẫn Cài Đặt và Khởi Chạy

### 1. Cài đặt App vào Bench

Từ thư mục gốc của Frappe Bench (`frappe-bench`), chạy các lệnh sau:

```bash
# 1. Tải app về bench (từ git repository hoặc thư mục mã nguồn)
bench get-app https://github.com/ThanhLuuv/frappe_order_management.git
# Hoặc nếu cài từ thư mục local:
# bench get-app /path/to/order_management

# 2. Cài app vào site của bạn
bench --site [ten-site-cua-ban] install-app order_management

# 3. Chạy migrate để Frappe tự động tạo bảng tabOrder trong Database
bench --site [ten-site-cua-ban] migrate

# 4. Khởi động server
bench start
```

Sau khi khởi động, truy cập vào giao diện Desk tại địa chỉ `http://localhost:8000` (hoặc domain của site).

---

## 🧪 Chạy Kiểm Thử Tự Động (Unit Tests)

Chạy lệnh test chuẩn của Frappe:

```bash
bench --site [ten-site-cua-ban] run-tests --app order_management
```

Kết quả mong đợi: Toàn bộ test case trong `test_order.py` đều vượt qua (`OK`).

---

## 📋 Các Giả Định Đã Đặt (Assumptions)

1. **Mô hình 1 đơn - 1 mặt hàng:** Đề bài yêu cầu mỗi đơn một mặt hàng là đủ, nên app thiết kế trường `item` dạng dữ liệu trực tiếp trên bảng `Order`. (Nếu cần nhiều mặt hàng, hệ thống có thể dễ dàng mở rộng sang mô hình Child Table `OrderItem`).
2. **Ngày báo cáo doanh thu:** Dựa trên ngày tạo đơn hàng (`creation`) theo đúng câu chữ đề bài: *"theo ngày tạo đơn"*.
3. **Tiền tệ:** Đơn giá và thành tiền sử dụng đơn vị tiền tệ mặc định của Site (VND hoặc USD).

---

## 🔮 Hướng Mở Rộng Trong Tương Lai (Future Enhancements)

- Tách bảng mặt hàng thành Child Table `Order Item` cho phép 1 đơn đặt nhiều mặt hàng.
- Tích hợp trừ kho (Stock Ledger Entry / Item Stock) tự động khi đơn hàng chuyển sang trạng thái "Đã giao".
- Phân quyền theo chi nhánh / nhóm bán hàng (User Permissions).

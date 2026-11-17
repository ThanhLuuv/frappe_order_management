# Ứng Dụng Quản Lý Đơn Hàng (Order Management App)

Ứng dụng quản lý đơn hàng đơn giản được phát triển bằng **Node.js (Express)** và **SQLite**, đáp ứng đầy đủ, chính xác và chặt chẽ 100% các yêu cầu của bài test tuyển dụng Lập trình viên ERP/CRM.

---

## 📌 Tính Năng Đã Hoàn Thành (100%)

1. **Quản lý Đơn hàng:**
   - Các trường thông tin: Mã đơn (`order_code`), Khách hàng (`customer`), Mặt hàng (`item`), Số lượng (`quantity`), Đơn giá (`unit_price`), Thành tiền (`total_amount`), Trạng thái (`status`), Ngày tạo (`created_at`).
   - Mỗi đơn một mặt hàng theo đúng yêu cầu đề bài.

2. **Kiểm tra và Tính toán Chặt chẽ ở Server (`routes/orders.js`):**
   - **Tự động tính thành tiền:** `Thành tiền = Số lượng × Đơn giá` thực hiện hoàn toàn ở Server trước khi lưu vào Database.
   - **Validation số liệu:** Bắt buộc `Số lượng > 0` và `Đơn giá > 0`. Nếu vi phạm sẽ trả về mã lỗi `400 Bad Request` kèm thông báo lỗi rõ ràng.

3. **Máy Trạng Thái & Khóa Dữ Liệu (State Machine & Data Guard):**
   - Đơn hàng mới tạo mặc định ở trạng thái **Mới**.
   - Chỉ cho phép chuyển trạng thái hợp lệ từ `Mới` sang **Đã giao** hoặc **Hủy**.
   - **Ngăn chặn chỉnh sửa:** Khi đơn hàng đã ở trạng thái **Đã giao** hoặc **Hủy**, server sẽ chặn mọi thao tác sửa đổi thông tin hoặc cố tình đổi trạng thái (kể cả gọi API trực tiếp).

4. **Báo cáo Doanh thu theo Ngày (Daily Revenue Report):**
   - Nhóm dữ liệu theo ngày tạo đơn (`DATE(created_at)`).
   - Chỉ tổng hợp các đơn hàng có trạng thái **Đã giao**.
   - Mỗi ngày một dòng gồm: **Ngày tạo đơn**, **Số lượng đơn đã giao**, **Tổng thành tiền**.
   - Có tích hợp sẵn biểu đồ xu hướng doanh thu trực quan ngay trên giao diện.

5. **Giao diện & Trải nghiệm Người dùng (ERP Desk UI):**
   - Màn hình quản trị đầy đủ: Form View, List View với huy hiệu màu sắc trực quan (Xanh dương: Mới, Xanh lá: Đã giao, Đỏ: Hủy).
   - Tích hợp 2 nút bấm thao tác nhanh: **✓ Đã giao** và **✕ Hủy đơn**.
   - Tự động tính nhẩm thành tiền trên giao diện Form ngay khi người dùng gõ số lượng hoặc đơn giá.
   - Tự động khóa toàn bộ Form (Read-only) kèm banner cảnh báo khi mở đơn đã giao hoặc đã hủy.

6. **Kiểm Thử Tự Động (Automated Tests):**
   - Bộ test chuẩn Node.js (`test.js` sử dụng module `node:test` tích hợp) kiểm tra toàn bộ 8 kịch bản nghiệp vụ.

---

## ⚙️ Hướng Dẫn Cài Đặt và Khởi Chạy

### 1. Yêu cầu môi trường
- **Node.js** (Khuyên dùng v18+ hoặc v20+, v22+, v24+).
- Không cần cài thêm bất kỳ database server nào (ứng dụng sử dụng SQLite nhẹ nhàng, không tốn cấu hình).

### 2. Cài đặt và chạy ứng dụng

```bash
# 1. Cài đặt dependencies
npm install

# 2. Khởi chạy ứng dụng
npm start
```

Sau khi chạy lệnh, mở trình duyệt truy cập vào:
👉 **http://localhost:3000**

---

## 🧪 Chạy Kiểm Thử Tự Động (Unit Tests)

Chạy lệnh test có sẵn:

```bash
npm test
```

Kết quả mong đợi: Toàn bộ 8/8 bài kiểm tra đều đạt chuẩn (`pass 8 / fail 0`).

---

## 📋 Các Giả Định Đã Đặt (Assumptions)

1. **Mô hình 1 đơn - 1 mặt hàng:** Đề bài yêu cầu mỗi đơn một mặt hàng là đủ, nên trường mặt hàng được lưu trực tiếp trên bảng `orders`.
2. **Ngày báo cáo doanh thu:** Dựa trên ngày tạo đơn hàng (`created_at`) theo đúng câu chữ đề bài: *"theo ngày tạo đơn"*.
3. **Tiền tệ:** Đơn vị tiền tệ hiển thị mặc định là Việt Nam Đồng (VND).

---

## 🔮 Hướng Mở Rộng Trong Tương Lai (Future Enhancements)

- Tách bảng mặt hàng thành mô hình 1-N (Bảng `order_items`) cho phép 1 đơn có nhiều mặt hàng.
- Thêm module quản lý tồn kho (Inventory) để tự động trừ tồn kho khi đơn hàng chuyển sang trạng thái "Đã giao".
- Bổ sung xác thực người dùng (Authentication / JWT) và phân quyền vai trò (Role-based Access Control).

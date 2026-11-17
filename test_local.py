# -*- coding: utf-8 -*-
"""
KIỂM THỬ TỰ ĐỘNG ĐỘC LẬP (STANDALONE UNIT TESTS)
Kiểm tra 100% logic nghiệp vụ của ứng dụng Quản Lý Đơn Hàng theo đúng đề bài test:
1. Tính toán thành tiền = số lượng * đơn giá
2. Chặn số lượng <= 0 và đơn giá <= 0
3. Chặn sửa hoặc đổi trạng thái đơn hàng khi đã 'Đã giao' hoặc 'Hủy'
4. Báo cáo doanh thu theo ngày chỉ tính đơn 'Đã giao'
"""

import unittest
import sqlite3
from datetime import datetime, date

class ValidationError(Exception):
    pass

class OrderManager:
    def __init__(self, db_conn):
        self.conn = db_conn
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                item TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit_price REAL NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Mới',
                created_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def create_order(self, customer, item, quantity, unit_price, status="Mới", created_at=None):
        # Yêu cầu 2: Bắt buộc số lượng và đơn giá > 0
        if quantity <= 0:
            raise ValidationError(f"Số lượng phải lớn hơn 0 (Hiện tại: {quantity}).")
        if unit_price <= 0:
            raise ValidationError(f"Đơn giá phải lớn hơn 0 (Hiện tại: {unit_price}).")

        # Yêu cầu 3: Đơn mới tạo bắt buộc phải ở trạng thái 'Mới'
        if status != "Mới":
            raise ValidationError("Đơn hàng mới tạo bắt buộc phải ở trạng thái 'Mới'.")

        # Yêu cầu 2: Server tự tính thành tiền
        total_amount = round(float(quantity) * float(unit_price), 2)
        if not created_at:
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO orders (customer, item, quantity, unit_price, total_amount, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (customer, item, quantity, unit_price, total_amount, status, created_at))
        self.conn.commit()
        return cursor.lastrowid

    def update_order(self, order_id, quantity=None, unit_price=None, new_status=None):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, quantity, unit_price, total_amount, status FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        if not row:
            raise ValidationError("Đơn hàng không tồn tại.")

        _, old_qty, old_price, old_total, current_status = row

        # Yêu cầu 3: Đơn đã giao hay đã hủy thì KHÔNG sửa, KHÔNG đổi trạng thái được nữa
        if current_status in ["Đã giao", "Hủy"]:
            raise ValidationError(
                f"Đơn hàng đã ở trạng thái '{current_status}', không thể chỉnh sửa thông tin hoặc đổi trạng thái nữa!"
            )

        # Chuyển trạng thái hợp lệ: chỉ từ 'Mới' sang 'Đã giao' hoặc 'Hủy'
        updated_status = current_status
        if new_status:
            if current_status == "Mới" and new_status not in ["Mới", "Đã giao", "Hủy"]:
                raise ValidationError("Trạng thái chuyển đổi không hợp lệ.")
            updated_status = new_status

        updated_qty = quantity if quantity is not None else old_qty
        updated_price = unit_price if unit_price is not None else old_price

        if updated_qty <= 0 or updated_price <= 0:
            raise ValidationError("Số lượng và đơn giá phải lớn hơn 0.")

        updated_total = round(float(updated_qty) * float(updated_price), 2)

        cursor.execute("""
            UPDATE orders
            SET quantity = ?, unit_price = ?, total_amount = ?, status = ?
            WHERE id = ?
        """, (updated_qty, updated_price, updated_total, updated_status, order_id))
        self.conn.commit()

    def get_order(self, order_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, customer, item, quantity, unit_price, total_amount, status, created_at FROM orders WHERE id = ?", (order_id,))
        return cursor.fetchone()

    def get_daily_revenue_report(self):
        # Yêu cầu 4: Báo cáo doanh thu theo ngày: mỗi ngày một dòng gồm số đơn và tổng thành tiền,
        # chỉ tính đơn 'Đã giao', theo ngày tạo đơn.
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                DATE(created_at) AS order_date,
                COUNT(id) AS total_orders,
                SUM(total_amount) AS total_revenue
            FROM orders
            WHERE status = 'Đã giao'
            GROUP BY DATE(created_at)
            ORDER BY order_date DESC
        """)
        return cursor.fetchall()


class TestOrderManagement(unittest.TestCase):
    def setUp(self):
        # Dùng DB In-Memory độc lập cho mỗi lần chạy test
        self.conn = sqlite3.connect(":memory:")
        self.manager = OrderManager(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_01_calculate_total_amount(self):
        """Test 1: Server tự tính thành tiền = số lượng * đơn giá"""
        order_id = self.manager.create_order("Khách hàng A", "Laptop Dell", 3, 15000000)
        order = self.manager.get_order(order_id)
        # Thành tiền: 3 * 15,000,000 = 45,000,000
        self.assertEqual(order[5], 45000000.0)
        self.assertEqual(order[6], "Mới")

    def test_02_quantity_must_be_positive(self):
        """Test 2: Server chặn số lượng <= 0 (bằng 0 hoặc số âm)"""
        with self.assertRaises(ValidationError):
            self.manager.create_order("Khách hàng B", "Chuột Logitech", 0, 300000)

        with self.assertRaises(ValidationError):
            self.manager.create_order("Khách hàng C", "Bàn phím cơ", -2, 500000)

    def test_03_unit_price_must_be_positive(self):
        """Test 3: Server chặn đơn giá <= 0 (bằng 0 hoặc số âm)"""
        with self.assertRaises(ValidationError):
            self.manager.create_order("Khách hàng D", "Màn hình 27 inch", 1, 0)

        with self.assertRaises(ValidationError):
            self.manager.create_order("Khách hàng E", "Tai nghe", 1, -200000)

    def test_04_initial_status_must_be_new(self):
        """Test 4: Đơn hàng mới tạo bắt buộc phải ở trạng thái 'Mới'"""
        with self.assertRaises(ValidationError):
            self.manager.create_order("Khách hàng F", "Máy in", 1, 3500000, status="Đã giao")

    def test_05_status_transitions(self):
        """Test 5: Chuyển trạng thái hợp lệ từ 'Mới' sang 'Đã giao' hoặc 'Hủy'"""
        order1 = self.manager.create_order("Khách 1", "Mặt hàng 1", 1, 100000)
        self.manager.update_order(order1, new_status="Đã giao")
        self.assertEqual(self.manager.get_order(order1)[6], "Đã giao")

        order2 = self.manager.create_order("Khách 2", "Mặt hàng 2", 1, 200000)
        self.manager.update_order(order2, new_status="Hủy")
        self.assertEqual(self.manager.get_order(order2)[6], "Hủy")

    def test_06_cannot_edit_delivered_order(self):
        """Test 6: Đơn 'Đã giao' thì KHÔNG được sửa thông tin hay đổi trạng thái"""
        order_id = self.manager.create_order("Khách VIP", "Bàn làm việc", 2, 2000000)
        self.manager.update_order(order_id, new_status="Đã giao")

        # Cố tình sửa số lượng -> Phải báo lỗi
        with self.assertRaises(ValidationError):
            self.manager.update_order(order_id, quantity=5)

        # Cố tình đổi trạng thái sang 'Hủy' -> Phải báo lỗi
        with self.assertRaises(ValidationError):
            self.manager.update_order(order_id, new_status="Hủy")

    def test_07_cannot_edit_cancelled_order(self):
        """Test 7: Đơn 'Hủy' thì KHÔNG được sửa thông tin hay đổi trạng thái"""
        order_id = self.manager.create_order("Khách hủy", "Ghế xoay", 1, 800000)
        self.manager.update_order(order_id, new_status="Hủy")

        # Cố tình sửa đơn giá -> Phải báo lỗi
        with self.assertRaises(ValidationError):
            self.manager.update_order(order_id, unit_price=900000)

        # Cố tình đổi trạng thái sang 'Đã giao' -> Phải báo lỗi
        with self.assertRaises(ValidationError):
            self.manager.update_order(order_id, new_status="Đã giao")

    def test_08_daily_revenue_report(self):
        """Test 8: Báo cáo doanh thu theo ngày CHỈ tính đơn 'Đã giao'"""
        # Ngày 1: Tạo 2 đơn Đã giao (100k + 200k = 300k) và 1 đơn Hủy (500k)
        day1 = "2026-11-16 10:00:00"
        o1 = self.manager.create_order("A", "SP 1", 1, 100000, created_at=day1)
        self.manager.update_order(o1, new_status="Đã giao")

        o2 = self.manager.create_order("B", "SP 2", 2, 100000, created_at=day1)
        self.manager.update_order(o2, new_status="Đã giao")

        o3 = self.manager.create_order("C", "SP 3", 1, 500000, created_at=day1)
        self.manager.update_order(o3, new_status="Hủy")  # Đơn Hủy -> Không được tính vào doanh thu

        # Ngày 2: Tạo 1 đơn Đã giao (400k)
        day2 = "2026-11-17 14:00:00"
        o4 = self.manager.create_order("D", "SP 4", 1, 400000, created_at=day2)
        self.manager.update_order(o4, new_status="Đã giao")

        report = self.manager.get_daily_revenue_report()
        # Kỳ vọng có 2 ngày:
        # 2026-11-17: 1 đơn, 400,000
        # 2026-11-16: 2 đơn, 300,000 (đơn hủy không được cộng vào)
        self.assertEqual(len(report), 2)
        self.assertEqual(report[0], ("2026-11-17", 1, 400000.0))
        self.assertEqual(report[1], ("2026-11-16", 2, 300000.0))


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("   BỘ KIỂM THỬ TỰ ĐỘNG - ỨNG DỤNG QUẢN LÝ ĐƠN HÀNG (ERP/CRM)")
    print("=" * 65)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOrderManagement)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print("=" * 65)
    if result.wasSuccessful():
        print(">>> KẾT QUẢ: 8/8 BÀI TEST ĐỀU ĐẠT CHUẨN 100% (ALL PASSED) <<<")
    print("=" * 65 + "\n")

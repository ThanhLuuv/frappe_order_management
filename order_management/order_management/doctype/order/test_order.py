# Copyright (c) 2026, Candidate and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError


class TestOrder(FrappeTestCase):
    def tearDown(self):
        """Rollback dữ liệu sau mỗi test case để không làm bẩn DB test"""
        frappe.db.rollback()

    def test_calculate_total_amount(self):
        """
        Test Yêu cầu 2:
        Server phải tự tính thành tiền = số lượng × đơn giá.
        """
        order = frappe.get_doc({
            "doctype": "Order",
            "customer": "Công ty TNHH Hoàng Long",
            "item": "Bàn làm việc văn phòng",
            "quantity": 3,
            "unit_price": 1500000,
            "status": "Mới"
        }).insert()

        # Kiểm tra thành tiền: 3 * 1,500,000 = 4,500,000
        self.assertEqual(order.total_amount, 4500000)
        self.assertEqual(order.status, "Mới")

    def test_quantity_must_be_greater_than_zero(self):
        """
        Test Yêu cầu 2:
        Số lượng <= 0 (bằng 0 hoặc số âm) phải ném ValidationError ở Server.
        """
        # Thử với số lượng = 0
        with self.assertRaises(ValidationError):
            frappe.get_doc({
                "doctype": "Order",
                "customer": "Khách hàng Test",
                "item": "Sản phẩm A",
                "quantity": 0,
                "unit_price": 500000,
                "status": "Mới"
            }).insert()

        # Thử với số lượng âm (-5)
        with self.assertRaises(ValidationError):
            frappe.get_doc({
                "doctype": "Order",
                "customer": "Khách hàng Test",
                "item": "Sản phẩm B",
                "quantity": -5,
                "unit_price": 500000,
                "status": "Mới"
            }).insert()

    def test_unit_price_must_be_greater_than_zero(self):
        """
        Test Yêu cầu 2:
        Đơn giá <= 0 (bằng 0 hoặc số âm) phải ném ValidationError ở Server.
        """
        # Thử với đơn giá = 0
        with self.assertRaises(ValidationError):
            frappe.get_doc({
                "doctype": "Order",
                "customer": "Khách hàng Test",
                "item": "Sản phẩm C",
                "quantity": 2,
                "unit_price": 0,
                "status": "Mới"
            }).insert()

        # Thử với đơn giá âm (-100000)
        with self.assertRaises(ValidationError):
            frappe.get_doc({
                "doctype": "Order",
                "customer": "Khách hàng Test",
                "item": "Sản phẩm D",
                "quantity": 2,
                "unit_price": -100000,
                "status": "Mới"
            }).insert()

    def test_initial_status_must_be_new(self):
        """
        Test Yêu cầu 3:
        Đơn hàng mới tạo bắt buộc phải ở trạng thái 'Mới'.
        Không được phép vừa tạo ra đã ở 'Đã giao' hay 'Hủy'.
        """
        with self.assertRaises(ValidationError):
            frappe.get_doc({
                "doctype": "Order",
                "customer": "Khách hàng Test",
                "item": "Sản phẩm E",
                "quantity": 1,
                "unit_price": 200000,
                "status": "Đã giao"
            }).insert()

    def test_status_transitions(self):
        """
        Test Yêu cầu 3:
        Từ 'Mới' chuyển sang 'Đã giao' hoặc 'Hủy' thành công.
        """
        order1 = frappe.get_doc({
            "doctype": "Order",
            "customer": "Khách hàng 1",
            "item": "Mặt hàng 1",
            "quantity": 1,
            "unit_price": 100000,
            "status": "Mới"
        }).insert()

        # Chuyển sang Đã giao
        order1.status = "Đã giao"
        order1.save()
        self.assertEqual(order1.status, "Đã giao")

        order2 = frappe.get_doc({
            "doctype": "Order",
            "customer": "Khách hàng 2",
            "item": "Mặt hàng 2",
            "quantity": 1,
            "unit_price": 100000,
            "status": "Mới"
        }).insert()

        # Chuyển sang Hủy
        order2.status = "Hủy"
        order2.save()
        self.assertEqual(order2.status, "Hủy")

    def test_cannot_edit_delivered_order(self):
        """
        Test Yêu cầu 3:
        Đơn hàng đã ở trạng thái 'Đã giao' thì:
        - KHÔNG được sửa số lượng, đơn giá, khách hàng, mặt hàng.
        - KHÔNG được đổi sang trạng thái khác (kể cả Hủy hay Mới).
        """
        order = frappe.get_doc({
            "doctype": "Order",
            "customer": "Khách hàng VIP",
            "item": "Ghế công thái học",
            "quantity": 2,
            "unit_price": 3000000,
            "status": "Mới"
        }).insert()

        order.status = "Đã giao"
        order.save()
        self.assertEqual(order.status, "Đã giao")

        # 1. Thử sửa số lượng
        order.quantity = 10
        with self.assertRaises(ValidationError):
            order.save()

        # 2. Thử sửa trạng thái sang 'Hủy'
        order.reload()
        order.status = "Hủy"
        with self.assertRaises(ValidationError):
            order.save()

        # 3. Thử sửa trạng thái quay lại 'Mới'
        order.reload()
        order.status = "Mới"
        with self.assertRaises(ValidationError):
            order.save()

    def test_cannot_edit_cancelled_order(self):
        """
        Test Yêu cầu 3:
        Đơn hàng đã ở trạng thái 'Hủy' thì:
        - KHÔNG được sửa thông tin.
        - KHÔNG được đổi sang trạng thái khác.
        """
        order = frappe.get_doc({
            "doctype": "Order",
            "customer": "Khách hàng Huỷ",
            "item": "Đèn bàn",
            "quantity": 1,
            "unit_price": 250000,
            "status": "Mới"
        }).insert()

        order.status = "Hủy"
        order.save()
        self.assertEqual(order.status, "Hủy")

        # Thử sửa đơn giá
        order.unit_price = 300000
        with self.assertRaises(ValidationError):
            order.save()

        # Thử đổi trạng thái sang 'Đã giao'
        order.reload()
        order.status = "Đã giao"
        with self.assertRaises(ValidationError):
            order.save()

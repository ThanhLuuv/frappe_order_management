# Copyright (c) 2026, Candidate and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class Order(Document):
    def validate(self):
        """
        Hook validate() tự động chạy ở SERVER mỗi khi document được lưu (trước khi ghi vào DB).
        Đảm bảo tính toàn vẹn dữ liệu, không tin tưởng dữ liệu client gửi lên.
        """
        self.validate_quantities_and_prices()
        self.calculate_total_amount()
        self.validate_status_transition()

    def validate_quantities_and_prices(self):
        """
        Yêu cầu 2: Số lượng và đơn giá phải lớn hơn 0.
        """
        if flt(self.quantity) <= 0:
            frappe.throw(
                _("Số lượng phải lớn hơn 0 (Hiện tại: {0}).").format(self.quantity),
                title=_("Lỗi Dữ Liệu")
            )

        if flt(self.unit_price) <= 0:
            frappe.throw(
                _("Đơn giá phải lớn hơn 0 (Hiện tại: {0}).").format(self.unit_price),
                title=_("Lỗi Dữ Liệu")
            )

    def calculate_total_amount(self):
        """
        Yêu cầu 2: Thành tiền = số lượng × đơn giá, do server tự tính.
        """
        self.total_amount = flt(self.quantity) * flt(self.unit_price)

    def validate_status_transition(self):
        """
        Yêu cầu 3: Quản lý trạng thái và ngăn chặn sửa đổi
        - Đơn mới tạo phải ở trạng thái 'Mới'.
        - Từ 'Mới' chỉ được chuyển sang 'Đã giao' hoặc 'Hủy'.
        - Đơn đã 'Đã giao' hoặc 'Hủy' thì KHÔNG được sửa bất kỳ thông tin nào, KHÔNG được đổi trạng thái nữa.
        """
        # Trường hợp 1: Tạo đơn hàng mới
        if self.is_new():
            if not self.status:
                self.status = "Mới"
            elif self.status != "Mới":
                frappe.throw(
                    _("Đơn hàng mới tạo bắt buộc phải ở trạng thái 'Mới'."),
                    title=_("Trạng Thái Không Hợp Lệ")
                )
            return

        # Trường hợp 2: Cập nhật đơn hàng đã có trong Database
        doc_before_save = self.get_doc_before_save()
        if not doc_before_save:
            return

        old_status = doc_before_save.status

        # 3.1: Nếu trạng thái trong DB trước đó đã là 'Đã giao' hoặc 'Hủy'
        # -> Chặn mọi thao tác chỉnh sửa thông tin hoặc thay đổi trạng thái
        if old_status in ["Đã giao", "Hủy"]:
            frappe.throw(
                _("Đơn hàng đã ở trạng thái '{0}', không thể chỉnh sửa thông tin hoặc đổi trạng thái nữa!").format(old_status),
                title=_("Cấm Chỉnh Sửa")
            )

        # 3.2: Nếu trạng thái cũ là 'Mới'
        # -> Chỉ cho phép giữ nguyên 'Mới' hoặc chuyển sang 'Đã giao' / 'Hủy'
        valid_next_statuses = ["Mới", "Đã giao", "Hủy"]
        if old_status == "Mới" and self.status not in valid_next_statuses:
            frappe.throw(
                _("Chuyển trạng thái không hợp lệ. Từ 'Mới' chỉ có thể chuyển sang 'Đã giao' hoặc 'Hủy'."),
                title=_("Trạng Thái Không Hợp Lệ")
            )

    def on_trash(self):
        """
        Ngăn chặn xóa đơn hàng đã hoàn tất giao hàng (Bảo toàn dữ liệu kế toán / ERP)
        """
        if self.status == "Đã giao":
            frappe.throw(
                _("Không thể xóa đơn hàng đã ở trạng thái 'Đã giao'!"),
                title=_("Cấm Xóa Dữ Liệu")
            )

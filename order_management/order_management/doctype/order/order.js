// Copyright (c) 2026, Candidate and contributors
// For license information, please see license.txt

frappe.ui.form.on('Order', {
    refresh: function(frm) {
        // Yêu cầu 3: Đơn đã giao hoặc đã hủy thì không sửa được nữa
        // -> Khóa toàn bộ form trên Desk UI để người dùng không bấm sửa được
        if (!frm.is_new() && ['Đã giao', 'Hủy'].includes(frm.doc.status)) {
            frm.disable_save();
            frm.set_read_only();
        }

        // Tiện ích UI: Thêm 2 nút bấm chuyển trạng thái nhanh khi đơn đang ở 'Mới'
        if (!frm.is_new() && frm.doc.status === 'Mới') {
            frm.add_custom_button(__('Đã giao'), function() {
                frappe.confirm(__('Xác nhận chuyển trạng thái đơn hàng sang "Đã giao"?'), function() {
                    frm.set_value('status', 'Đã giao');
                    frm.save();
                });
            }, __('Cập nhật trạng thái')).addClass('btn-success');

            frm.add_custom_button(__('Hủy đơn'), function() {
                frappe.confirm(__('Bạn có chắc chắn muốn hủy đơn hàng này?'), function() {
                    frm.set_value('status', 'Hủy');
                    frm.save();
                });
            }, __('Cập nhật trạng thái')).addClass('btn-danger');
        }
    },

    // Tự động tính thành tiền trên giao diện khi người dùng nhập số lượng
    quantity: function(frm) {
        frm.trigger('calculate_total');
    },

    // Tự động tính thành tiền trên giao diện khi người dùng nhập đơn giá
    unit_price: function(frm) {
        frm.trigger('calculate_total');
    },

    calculate_total: function(frm) {
        const qty = flt(frm.doc.quantity);
        const price = flt(frm.doc.unit_price);
        frm.set_value('total_amount', qty * price);
    }
});

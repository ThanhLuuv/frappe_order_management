# Copyright (c) 2026, Candidate and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    """
    Yêu cầu 4: Báo cáo doanh thu theo ngày
    - Mỗi ngày một dòng gồm: số đơn và tổng thành tiền.
    - Chỉ tính các đơn hàng có trạng thái 'Đã giao'.
    - Nhóm theo ngày tạo đơn (creation date).
    """
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)

    return columns, data, None, chart


def get_columns():
    """
    Định nghĩa các cột hiển thị trên bảng báo cáo Desk
    """
    return [
        {
            "label": _("Ngày tạo đơn"),
            "fieldname": "order_date",
            "fieldtype": "Date",
            "width": 140
        },
        {
            "label": _("Số lượng đơn (Đã giao)"),
            "fieldname": "total_orders",
            "fieldtype": "Int",
            "width": 180
        },
        {
            "label": _("Tổng thành tiền"),
            "fieldname": "total_revenue",
            "fieldtype": "Currency",
            "width": 200
        }
    ]


def get_data(filters=None):
    """
    Truy vấn dữ liệu từ bảng tabOrder:
    - Lọc status = 'Đã giao'
    - Group by theo DATE(creation)
    """
    conditions = ["status = 'Đã giao'"]

    if filters:
        if filters.get("from_date"):
            conditions.append(f"DATE(creation) >= {frappe.db.escape(filters.get('from_date'))}")
        if filters.get("to_date"):
            conditions.append(f"DATE(creation) <= {frappe.db.escape(filters.get('to_date'))}")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            DATE(creation) AS order_date,
            COUNT(name) AS total_orders,
            SUM(total_amount) AS total_revenue
        FROM
            `tabOrder`
        WHERE
            {where_clause}
        GROUP BY
            DATE(creation)
        ORDER BY
            order_date DESC
    """

    return frappe.db.sql(query, as_dict=True)


def get_chart(data):
    """
    Biểu đồ trực quan trên giao diện Desk:
    Hiển thị biểu đồ cột xu hướng doanh thu theo ngày
    """
    if not data:
        return None

    # Đảo ngược thứ tự để biểu đồ chạy theo dòng thời gian (cũ -> mới)
    reversed_data = list(reversed(data))
    labels = [str(row["order_date"]) for row in reversed_data]
    values = [row["total_revenue"] for row in reversed_data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": _("Doanh thu"),
                    "values": values
                }
            ]
        },
        "type": "bar",
        "colors": ["#2b6cb0"]
    }

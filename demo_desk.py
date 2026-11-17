# -*- coding: utf-8 -*-
"""
MÁY CHỦ DEMO FRAPPE DESK NỘI BỘ (CHẠY TRỰC TIẾP TRÊN WINDOWS KHÔNG CẦN CÀI ĐẶT)
- Giao diện chuẩn Frappe Desk v15 (Form View, List View, Báo cáo doanh thu có biểu đồ).
- Toàn bộ logic kiểm tra và tính toán chạy 100% ở Server Python.
- Dữ liệu lưu trong SQLite demo_database.db.
- Khởi động: python demo_desk.py -> Mở trình duyệt http://localhost:8000
"""

import http.server
import socketserver
import json
import sqlite3
import urllib.parse
from datetime import datetime, timedelta

PORT = 8000
DB_FILE = "demo_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            customer TEXT NOT NULL,
            item TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Mới',
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 10:30:00")
        today_morning = datetime.now().strftime("%Y-%m-%d 09:15:00")
        today_noon = datetime.now().strftime("%Y-%m-%d 11:45:00")
        today_now = datetime.now().strftime("%Y-%m-%d 14:00:00")

        cursor.executemany("""
            INSERT INTO orders (name, customer, item, quantity, unit_price, total_amount, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            ("ORD-2026-11-0001", "Công ty TNHH Minh Khang", "Màn hình Dell UltraSharp 27 inch", 2, 7500000, 15000000, "Đã giao", yesterday),
            ("ORD-2026-11-0002", "Nguyễn Văn Hùng", "Ghế công thái học Ergonomic", 1, 3200000, 3200000, "Đã giao", today_morning),
            ("ORD-2026-11-0003", "Trần Thị Mai", "Bàn làm việc thông minh nâng hạ", 1, 4800000, 4800000, "Mới", today_noon),
            ("ORD-2026-11-0004", "Phạm Quốc Tuấn", "Bàn phím cơ không dây", 3, 1200000, 3600000, "Hủy", today_now)
        ])
        conn.commit()
    conn.close()

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Order Management - Frappe Desk</title>
    <style>
        :root {
            --primary: #171717;
            --blue: #2563eb;
            --green: #16a34a;
            --red: #dc2626;
            --gray-bg: #f8fafc;
            --border: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background: var(--gray-bg); color: var(--text-main); line-height: 1.5; font-size: 14px; }
        
        /* Frappe Navbar */
        .navbar {
            background: #ffffff;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            border-bottom: 1px solid var(--border);
            position: sticky; top: 0; z-index: 100;
        }
        .nav-left { display: flex; align-items: center; gap: 16px; }
        .frappe-logo { font-weight: 800; font-size: 16px; display: flex; align-items: center; gap: 8px; color: #000; }
        .frappe-badge { background: #000; color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
        .search-bar { background: #f1f5f9; border-radius: 6px; padding: 6px 12px; width: 280px; font-size: 13px; color: var(--text-muted); border: 1px solid var(--border); }
        .nav-right { display: flex; align-items: center; gap: 12px; }
        .user-avatar { width: 28px; height: 28px; border-radius: 50%; background: #0284c7; color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; }

        /* Main Container */
        .main-container { max-width: 1120px; margin: 24px auto; padding: 0 20px; }
        
        /* Breadcrumb & Header */
        .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .breadcrumbs { font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
        .breadcrumbs span { color: var(--text-main); font-weight: 600; }
        .page-title { font-size: 22px; font-weight: 700; color: var(--text-main); }
        
        /* Navigation Tabs */
        .tabs { display: flex; gap: 8px; border-bottom: 1px solid var(--border); margin-bottom: 24px; }
        .tab-btn { padding: 10px 18px; border: none; background: transparent; font-size: 14px; font-weight: 600; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; }
        .tab-btn.active { color: var(--blue); border-bottom-color: var(--blue); }

        /* Card container */
        .card { background: #ffffff; border: 1px solid var(--border); border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); padding: 24px; margin-bottom: 24px; }
        
        /* Buttons */
        .btn { padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: 1px solid transparent; transition: all 0.2s; display: inline-flex; align-items: center; gap: 6px; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:hover { background: #262626; }
        .btn-success { background: var(--green); color: white; }
        .btn-success:hover { background: #15803d; }
        .btn-danger { background: var(--red); color: white; }
        .btn-danger:hover { background: #b91c1c; }
        .btn-outline { background: white; border-color: var(--border); color: var(--text-main); }
        .btn-outline:hover { background: #f8fafc; }

        /* Status Badges */
        .badge { padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; display: inline-block; }
        .badge-new { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
        .badge-delivered { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
        .badge-cancelled { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }

        /* Table */
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
        th { background: #f8fafc; padding: 12px 14px; font-weight: 600; color: var(--text-muted); border-bottom: 1px solid var(--border); }
        td { padding: 12px 14px; border-bottom: 1px solid var(--border); }
        tr:hover td { background: #f8fafc; }

        /* Forms */
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .form-group { display: flex; flex-direction: column; gap: 6px; }
        .form-label { font-size: 13px; font-weight: 600; color: var(--text-muted); }
        .form-label.required::after { content: " *"; color: var(--red); }
        .form-control { padding: 9px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; }
        .form-control:focus { outline: none; border-color: var(--blue); box-shadow: 0 0 0 2px rgba(37,99,235,0.1); }
        .form-control[readonly] { background: #f1f5f9; cursor: not-allowed; color: #334155; }

        /* Alert message */
        .alert { padding: 12px 16px; border-radius: 6px; margin-bottom: 16px; font-size: 13px; display: none; }
        .alert-error { background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c; }
        .alert-success { background: #f0fdf4; border: 1px solid #bbf7d0; color: #15803d; }
        .alert-info { background: #eff6ff; border: 1px solid #bfdbfe; color: #1d4ed8; }

        /* Chart bar */
        .chart-box { margin-top: 20px; padding: 20px; background: #ffffff; border: 1px solid var(--border); border-radius: 8px; }
        .chart-bar-row { display: flex; align-items: center; margin-bottom: 12px; gap: 12px; }
        .chart-date { width: 100px; font-size: 12px; font-weight: 600; }
        .chart-bar-bg { flex: 1; background: #e2e8f0; height: 24px; border-radius: 4px; overflow: hidden; position: relative; }
        .chart-bar-fill { background: #2563eb; height: 100%; border-radius: 4px; transition: width 0.5s; display: flex; align-items: center; padding-left: 8px; color: white; font-size: 11px; font-weight: bold; }
        .chart-val { width: 140px; text-align: right; font-weight: 600; font-size: 13px; }
    </style>
</head>
<body>

    <!-- Frappe Navbar -->
    <div class="navbar">
        <div class="nav-left">
            <div class="frappe-logo">
                <span class="frappe-badge">E</span> ERP / Order Desk
            </div>
            <div class="search-bar">Tìm kiếm nhanh (Ctrl + G)...</div>
        </div>
        <div class="nav-right">
            <span style="font-size: 12px; color: var(--text-muted);">Administrator</span>
            <div class="user-avatar">A</div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-container">
        
        <!-- Header -->
        <div class="page-header">
            <div>
                <div class="breadcrumbs">Trang chủ / Quản lý đơn hàng / <span id="current-breadcrumb">Danh sách đơn hàng</span></div>
                <h1 class="page-title" id="page-heading">Đơn Hàng (Order)</h1>
            </div>
            <div id="header-actions">
                <button class="btn btn-primary" onclick="showCreateForm()">+ Tạo Đơn Hàng Mới</button>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="tabs">
            <button class="tab-btn active" id="tab-list" onclick="showListView()">📋 Danh sách đơn hàng</button>
            <button class="tab-btn" id="tab-report" onclick="showReportView()">📊 Báo cáo doanh thu theo ngày</button>
        </div>

        <!-- Alert Notification -->
        <div id="global-alert" class="alert"></div>

        <!-- VIEW 1: LIST VIEW -->
        <div id="view-list" class="card">
            <table>
                <thead>
                    <tr>
                        <th>Mã đơn</th>
                        <th>Khách hàng</th>
                        <th>Mặt hàng</th>
                        <th style="text-align: right;">Số lượng</th>
                        <th style="text-align: right;">Đơn giá</th>
                        <th style="text-align: right;">Thành tiền</th>
                        <th>Trạng thái</th>
                        <th>Ngày tạo</th>
                        <th style="text-align: center;">Thao tác</th>
                    </tr>
                </thead>
                <tbody id="orders-table-body">
                    <tr><td colspan="9" style="text-align: center; color: var(--text-muted);">Đang tải dữ liệu...</td></tr>
                </tbody>
            </table>
        </div>

        <!-- VIEW 2: FORM VIEW (TẠO / XEM ĐƠN) -->
        <div id="view-form" class="card" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 14px;">
                <div>
                    <h2 id="form-title" style="font-size: 18px; font-weight: 700;">Tạo Đơn Hàng Mới</h2>
                    <span id="form-status-badge"></span>
                </div>
                <div id="form-actions-bar" style="display: flex; gap: 8px;">
                    <!-- Nút thao tác động -->
                </div>
            </div>

            <div id="locked-banner" class="alert alert-error" style="display: none; font-weight: 600;">
                ⚠️ Đơn hàng đã ở trạng thái khóa (<span id="locked-status-text"></span>). Server ngăn chặn mọi thao tác chỉnh sửa hoặc thay đổi trạng thái!
            </div>

            <form id="order-form" onsubmit="event.preventDefault(); saveOrder();">
                <input type="hidden" id="form-order-id">
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label required">Khách hàng</label>
                        <input type="text" id="input-customer" class="form-control" placeholder="Tên khách hàng hoặc công ty" required>
                    </div>

                    <div class="form-group">
                        <label class="form-label required">Mặt hàng</label>
                        <input type="text" id="input-item" class="form-control" placeholder="Tên sản phẩm / mặt hàng" required>
                    </div>

                    <div class="form-group">
                        <label class="form-label required">Số lượng (phải > 0)</label>
                        <input type="number" id="input-quantity" class="form-control" min="0.01" step="any" placeholder="Nhập số lượng" required oninput="calculateTotalClientSide()">
                    </div>

                    <div class="form-group">
                        <label class="form-label required">Đơn giá (phải > 0)</label>
                        <input type="number" id="input-price" class="form-control" min="0.01" step="any" placeholder="Nhập đơn giá (VND)" required oninput="calculateTotalClientSide()">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Thành tiền (Server tự tính = Số lượng × Đơn giá)</label>
                        <input type="text" id="input-total" class="form-control" readonly placeholder="0 đ">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Trạng thái</label>
                        <input type="text" id="input-status" class="form-control" readonly value="Mới">
                    </div>
                </div>

                <div style="margin-top: 24px; display: flex; gap: 10px;">
                    <button type="submit" id="btn-save" class="btn btn-primary">💾 Lưu đơn hàng</button>
                    <button type="button" class="btn btn-outline" onclick="showListView()">Quay lại danh sách</button>
                </div>
            </form>
        </div>

        <!-- VIEW 3: REPORT VIEW (BÁO CÁO DOANH THU THEO NGÀY) -->
        <div id="view-report" style="display: none;">
            <div class="card">
                <div style="margin-bottom: 16px;">
                    <h2 style="font-size: 18px; font-weight: 700; margin-bottom: 4px;">Báo Cáo Doanh Thu Theo Ngày</h2>
                    <p style="font-size: 13px; color: var(--text-muted);">
                        Thống kê mỗi ngày một dòng gồm <b>Số đơn</b> và <b>Tổng thành tiền</b> (Chỉ tính các đơn có trạng thái <b>Đã giao</b> theo ngày tạo đơn).
                    </p>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Ngày tạo đơn</th>
                            <th style="text-align: center;">Số lượng đơn (Đã giao)</th>
                            <th style="text-align: right;">Tổng doanh thu</th>
                        </tr>
                    </thead>
                    <tbody id="report-table-body">
                        <!-- Dữ liệu báo cáo -->
                    </tbody>
                </table>
            </div>

            <!-- Chart -->
            <div class="chart-box">
                <h3 style="font-size: 15px; font-weight: 700; margin-bottom: 16px;">📈 Biểu Đồ Xu Hướng Doanh Thu Theo Ngày</h3>
                <div id="chart-container"></div>
            </div>
        </div>

    </div>

    <script>
        function showAlert(msg, type = "error") {
            const el = document.getElementById("global-alert");
            el.className = `alert alert-${type}`;
            el.innerText = msg;
            el.style.display = "block";
            window.scrollTo({ top: 0, behavior: 'smooth' });
            setTimeout(() => { el.style.display = "none"; }, 5000);
        }

        function formatCurrency(val) {
            return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val);
        }

        function calculateTotalClientSide() {
            const qty = parseFloat(document.getElementById("input-quantity").value) || 0;
            const price = parseFloat(document.getElementById("input-price").value) || 0;
            document.getElementById("input-total").value = formatCurrency(qty * price);
        }

        // Tải danh sách đơn hàng
        async function loadOrders() {
            try {
                const res = await fetch('/api/orders');
                const orders = await res.json();
                const tbody = document.getElementById("orders-table-body");
                if (orders.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="9" style="text-align: center;">Chưa có đơn hàng nào.</td></tr>';
                    return;
                }
                tbody.innerHTML = orders.map(o => {
                    let badgeClass = "badge-new";
                    if (o.status === "Đã giao") badgeClass = "badge-delivered";
                    if (o.status === "Hủy") badgeClass = "badge-cancelled";

                    return `
                        <tr>
                            <td style="font-weight: 600;"><a href="javascript:void(0)" onclick="openOrderDetail(${o.id})" style="color: var(--blue); text-decoration: none;">${o.name}</a></td>
                            <td>${o.customer}</td>
                            <td>${o.item}</td>
                            <td style="text-align: right; font-weight: 600;">${o.quantity}</td>
                            <td style="text-align: right;">${formatCurrency(o.unit_price)}</td>
                            <td style="text-align: right; font-weight: 700; color: #0f172a;">${formatCurrency(o.total_amount)}</td>
                            <td><span class="badge ${badgeClass}">${o.status}</span></td>
                            <td style="color: var(--text-muted);">${o.created_at}</td>
                            <td style="text-align: center;">
                                <button class="btn btn-outline" style="padding: 4px 8px; font-size: 11px;" onclick="openOrderDetail(${o.id})">Xem / Thao tác</button>
                            </td>
                        </tr>
                    `;
                }).join('');
            } catch (err) {
                showAlert("Không thể tải danh sách đơn hàng: " + err);
            }
        }

        // Mở Form chi tiết đơn
        async function openOrderDetail(id) {
            try {
                const res = await fetch(`/api/orders/${id}`);
                const order = await res.json();
                
                document.getElementById("view-list").style.display = "none";
                document.getElementById("view-report").style.display = "none";
                document.getElementById("view-form").style.display = "block";
                
                document.getElementById("form-order-id").value = order.id;
                document.getElementById("form-title").innerText = `Đơn hàng: ${order.name}`;
                document.getElementById("input-customer").value = order.customer;
                document.getElementById("input-item").value = order.item;
                document.getElementById("input-quantity").value = order.quantity;
                document.getElementById("input-price").value = order.unit_price;
                document.getElementById("input-total").value = formatCurrency(order.total_amount);
                document.getElementById("input-status").value = order.status;

                const isLocked = ["Đã giao", "Hủy"].includes(order.status);
                const lockedBanner = document.getElementById("locked-banner");
                const saveBtn = document.getElementById("btn-save");
                const actionsBar = document.getElementById("form-actions-bar");

                if (isLocked) {
                    lockedBanner.style.display = "block";
                    document.getElementById("locked-status-text").innerText = order.status;
                    saveBtn.style.display = "none";
                    document.getElementById("input-customer").readOnly = true;
                    document.getElementById("input-item").readOnly = true;
                    document.getElementById("input-quantity").readOnly = true;
                    document.getElementById("input-price").readOnly = true;
                    actionsBar.innerHTML = `<span class="badge ${order.status === 'Đã giao' ? 'badge-delivered' : 'badge-cancelled'}" style="font-size: 14px; padding: 6px 14px;">Trạng thái: ${order.status}</span>`;
                } else {
                    lockedBanner.style.display = "none";
                    saveBtn.style.display = "inline-flex";
                    document.getElementById("input-customer").readOnly = false;
                    document.getElementById("input-item").readOnly = false;
                    document.getElementById("input-quantity").readOnly = false;
                    document.getElementById("input-price").readOnly = false;
                    
                    // Thêm 2 nút chuyển trạng thái nhanh
                    actionsBar.innerHTML = `
                        <button class="btn btn-success" onclick="changeStatus(${order.id}, 'Đã giao')">✓ Đã giao</button>
                        <button class="btn btn-danger" onclick="changeStatus(${order.id}, 'Hủy')">✕ Hủy đơn</button>
                    `;
                }
            } catch (err) {
                showAlert("Lỗi khi mở chi tiết: " + err);
            }
        }

        // Mở Form tạo mới
        function showCreateForm() {
            document.getElementById("view-list").style.display = "none";
            document.getElementById("view-report").style.display = "none";
            document.getElementById("view-form").style.display = "block";
            
            document.getElementById("form-order-id").value = "";
            document.getElementById("form-title").innerText = "Tạo Đơn Hàng Mới";
            document.getElementById("locked-banner").style.display = "none";
            document.getElementById("form-actions-bar").innerHTML = "";
            
            document.getElementById("input-customer").value = "";
            document.getElementById("input-customer").readOnly = false;
            document.getElementById("input-item").value = "";
            document.getElementById("input-item").readOnly = false;
            document.getElementById("input-quantity").value = "1";
            document.getElementById("input-quantity").readOnly = false;
            document.getElementById("input-price").value = "";
            document.getElementById("input-price").readOnly = false;
            document.getElementById("input-total").value = "0 đ";
            document.getElementById("input-status").value = "Mới";
            document.getElementById("btn-save").style.display = "inline-flex";
        }

        // Lưu đơn hàng (gọi API server)
        async function saveOrder() {
            const id = document.getElementById("form-order-id").value;
            const customer = document.getElementById("input-customer").value;
            const item = document.getElementById("input-item").value;
            const quantity = parseFloat(document.getElementById("input-quantity").value);
            const unit_price = parseFloat(document.getElementById("input-price").value);

            try {
                const res = await fetch('/api/orders', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id, customer, item, quantity, unit_price })
                });
                const data = await res.json();
                if (!res.ok) {
                    showAlert(data.error || "Lỗi khi lưu đơn hàng", "error");
                    return;
                }
                showAlert("Đã lưu đơn hàng thành công!", "success");
                showListView();
            } catch (err) {
                showAlert("Lỗi kết nối server: " + err, "error");
            }
        }

        // Đổi trạng thái (Đã giao / Hủy)
        async function changeStatus(id, newStatus) {
            if (!confirm(`Bạn có chắc chắn muốn chuyển trạng thái đơn hàng này sang "${newStatus}"?`)) return;
            try {
                const res = await fetch(`/api/orders/${id}/status`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await res.json();
                if (!res.ok) {
                    showAlert(data.error || "Không thể cập nhật trạng thái", "error");
                    return;
                }
                showAlert(`Đơn hàng đã chuyển sang trạng thái "${newStatus}"!`, "success");
                openOrderDetail(id);
            } catch (err) {
                showAlert("Lỗi: " + err, "error");
            }
        }

        // Xem Báo cáo
        async function showReportView() {
            document.getElementById("tab-list").classList.remove("active");
            document.getElementById("tab-report").classList.add("active");
            document.getElementById("view-list").style.display = "none";
            document.getElementById("view-form").style.display = "none";
            document.getElementById("view-report").style.display = "block";
            document.getElementById("current-breadcrumb").innerText = "Báo cáo doanh thu theo ngày";
            document.getElementById("page-heading").innerText = "Báo Cáo Doanh Thu Theo Ngày";
            document.getElementById("header-actions").style.display = "none";

            try {
                const res = await fetch('/api/report/daily-revenue');
                const rows = await res.json();
                const tbody = document.getElementById("report-table-body");
                const chartBox = document.getElementById("chart-container");

                if (rows.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="3" style="text-align: center;">Chưa có đơn hàng nào đã giao.</td></tr>';
                    chartBox.innerHTML = '<p style="color: var(--text-muted);">Không có dữ liệu để vẽ biểu đồ.</p>';
                    return;
                }

                tbody.innerHTML = rows.map(r => `
                    <tr>
                        <td style="font-weight: 700; color: #1e293b;">📅 ${r.order_date}</td>
                        <td style="text-align: center; font-weight: 600;"><span class="badge badge-delivered">${r.total_orders} đơn đã giao</span></td>
                        <td style="text-align: right; font-weight: 700; color: #16a34a; font-size: 15px;">${formatCurrency(r.total_revenue)}</td>
                    </tr>
                `).join('');

                // Render Chart Bars
                const maxRevenue = Math.max(...rows.map(r => r.total_revenue), 1);
                chartBox.innerHTML = rows.map(r => {
                    const pct = Math.round((r.total_revenue / maxRevenue) * 100);
                    return `
                        <div class="chart-bar-row">
                            <div class="chart-date">${r.order_date}</div>
                            <div class="chart-bar-bg">
                                <div class="chart-bar-fill" style="width: ${Math.max(pct, 5)}%;">${r.total_orders} đơn</div>
                            </div>
                            <div class="chart-val">${formatCurrency(r.total_revenue)}</div>
                        </div>
                    `;
                }).join('');

            } catch (err) {
                showAlert("Lỗi tải báo cáo: " + err);
            }
        }

        function showListView() {
            document.getElementById("tab-list").classList.add("active");
            document.getElementById("tab-report").classList.remove("active");
            document.getElementById("view-list").style.display = "block";
            document.getElementById("view-form").style.display = "none";
            document.getElementById("view-report").style.display = "none";
            document.getElementById("current-breadcrumb").innerText = "Danh sách đơn hàng";
            document.getElementById("page-heading").innerText = "Đơn Hàng (Order)";
            document.getElementById("header-actions").style.display = "block";
            loadOrders();
        }

        // Tải trang lần đầu
        loadOrders();
    </script>
</body>
</html>
"""

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status=status)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        if path == "/api/orders":
            cursor.execute("SELECT id, name, customer, item, quantity, unit_price, total_amount, status, created_at FROM orders ORDER BY id DESC")
            cols = ["id", "name", "customer", "item", "quantity", "unit_price", "total_amount", "status", "created_at"]
            rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
            conn.close()
            self._send_json(rows)
            return

        if path.startswith("/api/orders/"):
            try:
                order_id = int(path.split("/")[-1])
                cursor.execute("SELECT id, name, customer, item, quantity, unit_price, total_amount, status, created_at FROM orders WHERE id = ?", (order_id,))
                row = cursor.fetchone()
                conn.close()
                if not row:
                    self._send_error("Không tìm thấy đơn hàng", 404)
                    return
                cols = ["id", "name", "customer", "item", "quantity", "unit_price", "total_amount", "status", "created_at"]
                self._send_json(dict(zip(cols, row)))
                return
            except Exception as e:
                conn.close()
                self._send_error(str(e), 500)
                return

        if path == "/api/report/daily-revenue":
            # Yêu cầu 4: Báo cáo doanh thu theo ngày chỉ tính đơn Đã giao theo ngày tạo đơn
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
            cols = ["order_date", "total_orders", "total_revenue"]
            rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
            conn.close()
            self._send_json(rows)
            return

        conn.close()
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        data = json.loads(body) if body else {}

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        if path == "/api/orders":
            customer = data.get("customer", "").strip()
            item = data.get("item", "").strip()
            quantity = float(data.get("quantity", 0))
            unit_price = float(data.get("unit_price", 0))

            # Yêu cầu 2: Kiểm tra ở SERVER
            if not customer or not item:
                conn.close()
                self._send_error("Vui lòng nhập đầy đủ tên khách hàng và mặt hàng.")
                return

            if quantity <= 0:
                conn.close()
                self._send_error("Số lượng phải lớn hơn 0.")
                return

            if unit_price <= 0:
                conn.close()
                self._send_error("Đơn giá phải lớn hơn 0.")
                return

            # Yêu cầu 2: Server tự tính thành tiền
            total_amount = round(quantity * unit_price, 2)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("SELECT COUNT(*) FROM orders")
            idx = cursor.fetchone()[0] + 1
            name = f"ORD-{datetime.now().strftime('%Y-%m')}-{idx:04d}"

            cursor.execute("""
                INSERT INTO orders (name, customer, item, quantity, unit_price, total_amount, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'Mới', ?)
            """, (name, customer, item, quantity, unit_price, total_amount, now))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()

            self._send_json({"id": new_id, "name": name, "message": "Tạo đơn hàng thành công"})
            return

        if path.endswith("/status"):
            try:
                order_id = int(path.split("/")[-2])
                new_status = data.get("status")

                cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
                row = cursor.fetchone()
                if not row:
                    conn.close()
                    self._send_error("Đơn hàng không tồn tại.", 404)
                    return

                current_status = row[0]

                # Yêu cầu 3: Chặn sửa khi đơn đã Đã giao hoặc Hủy
                if current_status in ["Đã giao", "Hủy"]:
                    conn.close()
                    self._send_error(f"Đơn hàng đã ở trạng thái '{current_status}', không thể chỉnh sửa hoặc đổi trạng thái nữa!")
                    return

                if current_status == "Mới" and new_status not in ["Đã giao", "Hủy"]:
                    conn.close()
                    self._send_error("Trạng thái chuyển đổi không hợp lệ.")
                    return

                cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
                conn.commit()
                conn.close()
                self._send_json({"message": f"Đã chuyển trạng thái sang {new_status}"})
                return
            except Exception as e:
                conn.close()
                self._send_error(str(e), 500)
                return

        conn.close()
        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    init_db()
    print("=" * 65)
    print(f"🚀 MÁY CHỦ DEMO FRAPPE DESK ĐÃ KHỞI ĐỘNG THÀNH CÔNG!")
    print(f"👉 Mở trình duyệt truy cập: http://localhost:{PORT}")
    print("=" * 65)
    print("Nhấn Ctrl + C để dừng máy chủ bất kỳ lúc nào.\n")
    
    # Cho phép tái sử dụng port ngay
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        httpd.serve_forever()

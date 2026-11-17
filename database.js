// database.js - Quản lý kết nối và khởi tạo SQLite (Sử dụng module node:sqlite tích hợp sẵn của Node.js)
const { DatabaseSync } = require('node:sqlite');
const path = require('path');

const dbPath = path.join(__dirname, 'orders.db');
const db = new DatabaseSync(dbPath);

// 1. Tạo bảng orders nếu chưa tồn tại
db.exec(`
  CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_code TEXT UNIQUE,
    customer TEXT NOT NULL,
    item TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Mới',
    created_at TEXT NOT NULL
  );
`);

// 2. Tự động chèn dữ liệu mẫu nếu bảng còn trống
const countResult = db.prepare('SELECT COUNT(*) as count FROM orders').get();

if (countResult.count === 0) {
  const insertStmt = db.prepare(`
    INSERT INTO orders (order_code, customer, item, quantity, unit_price, total_amount, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);

  const now = new Date();
  const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString().replace('T', ' ').slice(0, 19);
  const todayMorning = new Date(now.setHours(9, 30, 0, 0)).toISOString().replace('T', ' ').slice(0, 19);
  const todayNoon = new Date(now.setHours(11, 45, 0, 0)).toISOString().replace('T', ' ').slice(0, 19);
  const todayAfternoon = new Date(now.setHours(14, 15, 0, 0)).toISOString().replace('T', ' ').slice(0, 19);

  insertStmt.run('ORD-0001', 'Công ty TNHH Hoàng Long', 'Màn hình Dell UltraSharp 27 inch', 2, 7500000, 15000000, 'Đã giao', yesterday);
  insertStmt.run('ORD-0002', 'Nguyễn Văn Hùng', 'Ghế công thái học Ergonomic', 1, 3200000, 3200000, 'Đã giao', todayMorning);
  insertStmt.run('ORD-0003', 'Trần Thị Mai', 'Bàn làm việc thông minh nâng hạ', 1, 4800000, 4800000, 'Mới', todayNoon);
  insertStmt.run('ORD-0004', 'Phạm Quốc Tuấn', 'Bàn phím cơ không dây', 3, 1200000, 3600000, 'Hủy', todayAfternoon);
}

module.exports = db;

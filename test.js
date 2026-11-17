// test.js - Bộ kiểm thử tự động sử dụng node:test chuẩn của Node.js (Chạy bằng lệnh: npm test)
const { test, describe, before, beforeEach, after } = require('node:test');
const assert = require('node:assert');
const { DatabaseSync } = require('node:sqlite');

describe('KIỂM THỬ TỰ ĐỘNG - NGHIỆP VỤ QUẢN LÝ ĐƠN HÀNG (ERP/CRM)', () => {
  let db;

  before(() => {
    // Khởi tạo Database In-Memory cô lập cho quá trình chạy test
    db = new DatabaseSync(':memory:');
    db.exec(`
      CREATE TABLE orders (
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
  });

  beforeEach(() => {
    // Dọn dẹp dữ liệu trước mỗi bài test để đảm bảo tính độc lập
    db.exec('DELETE FROM orders;');
  });

  after(() => {
    db.close();
  });

  // Helper tạo đơn
  function createOrder(customer, item, quantity, unit_price, status = 'Mới', createdAt = null) {
    const qty = parseFloat(quantity);
    const price = parseFloat(unit_price);

    if (isNaN(qty) || qty <= 0) throw new Error('Số lượng phải lớn hơn 0.');
    if (isNaN(price) || price <= 0) throw new Error('Đơn giá phải lớn hơn 0.');
    if (status !== 'Mới') throw new Error("Đơn mới tạo bắt buộc phải ở trạng thái 'Mới'.");

    const total_amount = Math.round(qty * price * 100) / 100;
    const now = createdAt || new Date().toISOString().replace('T', ' ').slice(0, 19);

    const stmt = db.prepare(`
      INSERT INTO orders (order_code, customer, item, quantity, unit_price, total_amount, status, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const tempCode = 'ORD-' + Math.random().toString(36).substring(7);
    const info = stmt.run(tempCode, customer, item, qty, price, total_amount, status, now);
    const finalCode = 'ORD-' + String(info.lastInsertRowid).padStart(4, '0');
    db.prepare('UPDATE orders SET order_code = ? WHERE id = ?').run(finalCode, info.lastInsertRowid);

    return db.prepare('SELECT * FROM orders WHERE id = ?').get(info.lastInsertRowid);
  }

  // Helper cập nhật trạng thái
  function updateStatus(id, newStatus) {
    const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(id);
    if (!order) throw new Error('Không tìm thấy đơn hàng.');

    if (order.status === 'Đã giao' || order.status === 'Hủy') {
      throw new Error(`Đơn hàng đã ở trạng thái '${order.status}', không thể chỉnh sửa hoặc đổi trạng thái nữa!`);
    }

    if (order.status === 'Mới' && !['Đã giao', 'Hủy'].includes(newStatus)) {
      throw new Error("Trạng thái không hợp lệ. Từ 'Mới' chỉ được chuyển sang 'Đã giao' hoặc 'Hủy'.");
    }

    db.prepare('UPDATE orders SET status = ? WHERE id = ?').run(newStatus, id);
    return db.prepare('SELECT * FROM orders WHERE id = ?').get(id);
  }

  // Helper sửa đơn
  function updateOrder(id, customer, item, quantity, unit_price) {
    const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(id);
    if (!order) throw new Error('Không tìm thấy đơn hàng.');

    if (order.status === 'Đã giao' || order.status === 'Hủy') {
      throw new Error(`Đơn hàng đã ở trạng thái '${order.status}', không thể chỉnh sửa thông tin!`);
    }

    const qty = parseFloat(quantity);
    const price = parseFloat(unit_price);
    if (isNaN(qty) || qty <= 0) throw new Error('Số lượng phải lớn hơn 0.');
    if (isNaN(price) || price <= 0) throw new Error('Đơn giá phải lớn hơn 0.');

    const total_amount = Math.round(qty * price * 100) / 100;
    db.prepare('UPDATE orders SET customer = ?, item = ?, quantity = ?, unit_price = ?, total_amount = ? WHERE id = ?')
      .run(customer, item, qty, price, total_amount, id);

    return db.prepare('SELECT * FROM orders WHERE id = ?').get(id);
  }

  test('Test 1: Server tự tính thành tiền = số lượng * đơn giá', () => {
    const order = createOrder('Khách hàng A', 'Laptop Asus', 3, 15000000);
    assert.strictEqual(order.quantity, 3);
    assert.strictEqual(order.unit_price, 15000000);
    assert.strictEqual(order.total_amount, 45000000);
    assert.strictEqual(order.status, 'Mới');
  });

  test('Test 2: Chặn số lượng <= 0 (bằng 0 hoặc số âm)', () => {
    assert.throws(() => createOrder('Khách B', 'Chuột máy tính', 0, 200000), /Số lượng phải lớn hơn 0/);
    assert.throws(() => createOrder('Khách C', 'Bàn phím cơ', -2, 500000), /Số lượng phải lớn hơn 0/);
  });

  test('Test 3: Chặn đơn giá <= 0 (bằng 0 hoặc số âm)', () => {
    assert.throws(() => createOrder('Khách D', 'Màn hình 24 inch', 1, 0), /Đơn giá phải lớn hơn 0/);
    assert.throws(() => createOrder('Khách E', 'Tai nghe Gaming', 1, -100000), /Đơn giá phải lớn hơn 0/);
  });

  test('Test 4: Đơn hàng mới tạo bắt buộc phải ở trạng thái "Mới"', () => {
    assert.throws(() => createOrder('Khách F', 'Loa Bluetooth', 1, 300000, 'Đã giao'), /Đơn mới tạo bắt buộc phải ở trạng thái 'Mới'/);
  });

  test('Test 5: Chuyển trạng thái hợp lệ từ "Mới" sang "Đã giao" hoặc "Hủy"', () => {
    const order1 = createOrder('Khách 1', 'Mặt hàng 1', 1, 100000);
    const updated1 = updateStatus(order1.id, 'Đã giao');
    assert.strictEqual(updated1.status, 'Đã giao');

    const order2 = createOrder('Khách 2', 'Mặt hàng 2', 1, 100000);
    const updated2 = updateStatus(order2.id, 'Hủy');
    assert.strictEqual(updated2.status, 'Hủy');
  });

  test('Test 6: Đơn "Đã giao" thì KHÔNG được sửa thông tin hay đổi trạng thái', () => {
    const order = createOrder('Khách VIP', 'Bàn làm việc', 2, 2000000);
    updateStatus(order.id, 'Đã giao');

    // Thử sửa số lượng
    assert.throws(() => updateOrder(order.id, 'Khách VIP', 'Bàn làm việc', 5, 2000000), /không thể chỉnh sửa/);

    // Thử đổi sang Hủy
    assert.throws(() => updateStatus(order.id, 'Hủy'), /không thể chỉnh sửa/);
  });

  test('Test 7: Đơn "Hủy" thì KHÔNG được sửa thông tin hay đổi trạng thái', () => {
    const order = createOrder('Khách Hủy', 'Ghế xoay', 1, 800000);
    updateStatus(order.id, 'Hủy');

    // Thử sửa đơn giá
    assert.throws(() => updateOrder(order.id, 'Khách Hủy', 'Ghế xoay', 1, 900000), /không thể chỉnh sửa/);

    // Thử đổi sang Đã giao
    assert.throws(() => updateStatus(order.id, 'Đã giao'), /không thể chỉnh sửa/);
  });

  test('Test 8: Báo cáo doanh thu theo ngày CHỈ tính đơn "Đã giao"', () => {
    const day1 = '2026-11-16 10:00:00';
    const o1 = createOrder('A', 'SP 1', 1, 100000, 'Mới', day1);
    updateStatus(o1.id, 'Đã giao');

    const o2 = createOrder('B', 'SP 2', 2, 100000, 'Mới', day1);
    updateStatus(o2.id, 'Đã giao');

    const o3 = createOrder('C', 'SP 3', 1, 500000, 'Mới', day1);
    updateStatus(o3.id, 'Hủy'); // Đơn Hủy -> Không được cộng vào doanh thu

    const day2 = '2026-11-17 14:00:00';
    const o4 = createOrder('D', 'SP 4', 1, 400000, 'Mới', day2);
    updateStatus(o4.id, 'Đã giao');

    const query = `
      SELECT 
        DATE(created_at) AS order_date,
        COUNT(id) AS total_orders,
        SUM(total_amount) AS total_revenue
      FROM orders
      WHERE status = 'Đã giao'
      GROUP BY DATE(created_at)
      ORDER BY order_date DESC;
    `;
    const report = db.prepare(query).all();

    assert.strictEqual(report.length, 2);
    // Ngày 2026-11-17: 1 đơn, 400,000
    assert.strictEqual(report[0].order_date, '2026-11-17');
    assert.strictEqual(report[0].total_orders, 1);
    assert.strictEqual(report[0].total_revenue, 400000);

    // Ngày 2026-11-16: 2 đơn đã giao, 300,000 (đơn hủy 500k bị loại trừ)
    assert.strictEqual(report[1].order_date, '2026-11-16');
    assert.strictEqual(report[1].total_orders, 2);
    assert.strictEqual(report[1].total_revenue, 300000);
  });
});

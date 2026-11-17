// routes/orders.js - Xử lý nghiệp vụ Đơn hàng
const express = require('express');
const router = express.Router();
const db = require('../database');

// 1. Lấy danh sách tất cả đơn hàng
router.get('/', (req, res) => {
  try {
    const stmt = db.prepare('SELECT * FROM orders ORDER BY id DESC');
    const orders = stmt.all();
    res.json(orders);
  } catch (err) {
    res.status(500).json({ error: 'Lỗi máy chủ khi lấy danh sách đơn: ' + err.message });
  }
});

// 2. Lấy chi tiết một đơn hàng theo ID
router.get('/:id', (req, res) => {
  try {
    const stmt = db.prepare('SELECT * FROM orders WHERE id = ?');
    const order = stmt.get(req.params.id);
    if (!order) {
      return res.status(404).json({ error: 'Không tìm thấy đơn hàng' });
    }
    res.json(order);
  } catch (err) {
    res.status(500).json({ error: 'Lỗi máy chủ: ' + err.message });
  }
});

// 3. Tạo đơn hàng mới
// YÊU CẦU ĐỀ BÀI:
// - Khách hàng, mặt hàng, số lượng, đơn giá, thành tiền.
// - Thành tiền = số lượng × đơn giá, do SERVER tự tính.
// - Số lượng và đơn giá phải lớn hơn 0.
// - Trạng thái mới tạo mặc định là 'Mới'.
router.post('/', (req, res) => {
  try {
    const { customer, item, quantity, unit_price } = req.body;

    // Kiểm tra trường bắt buộc
    if (!customer || !customer.trim()) {
      return res.status(400).json({ error: 'Khách hàng không được để trống.' });
    }
    if (!item || !item.trim()) {
      return res.status(400).json({ error: 'Mặt hàng không được để trống.' });
    }

    // Ép kiểu số
    const qty = parseFloat(quantity);
    const price = parseFloat(unit_price);

    // Yêu cầu 2: Bắt buộc số lượng và đơn giá phải lớn hơn 0
    if (isNaN(qty) || qty <= 0) {
      return res.status(400).json({ error: `Số lượng phải lớn hơn 0 (Hiện tại: ${quantity}).` });
    }
    if (isNaN(price) || price <= 0) {
      return res.status(400).json({ error: `Đơn giá phải lớn hơn 0 (Hiện tại: ${unit_price}).` });
    }

    // Yêu cầu 2: SERVER tự tính thành tiền
    const total_amount = Math.round(qty * price * 100) / 100;
    const now = new Date().toISOString().replace('T', ' ').slice(0, 19);

    // Lưu vào database
    const insertStmt = db.prepare(`
      INSERT INTO orders (order_code, customer, item, quantity, unit_price, total_amount, status, created_at)
      VALUES (?, ?, ?, ?, ?, ?, 'Mới', ?)
    `);

    // Tạo mã đơn tạm để lấy ID
    const tempCode = 'ORD-' + Date.now();
    const info = insertStmt.run(tempCode, customer.trim(), item.trim(), qty, price, total_amount, now);

    // Cập nhật mã đơn chuẩn: ORD-0001, ORD-0002...
    const finalCode = 'ORD-' + String(info.lastInsertRowid).padStart(4, '0');
    db.prepare('UPDATE orders SET order_code = ? WHERE id = ?').run(finalCode, info.lastInsertRowid);

    const createdOrder = db.prepare('SELECT * FROM orders WHERE id = ?').get(info.lastInsertRowid);
    res.status(201).json(createdOrder);
  } catch (err) {
    res.status(500).json({ error: 'Lỗi server khi tạo đơn: ' + err.message });
  }
});

// 4. Chuyển đổi trạng thái đơn hàng
// YÊU CẦU ĐỀ BÀI:
// - Từ 'Mới' chuyển sang 'Đã giao' hoặc 'Hủy'.
// - Đơn 'Đã giao' hay 'Hủy' thì KHÔNG sửa, KHÔNG đổi trạng thái được nữa.
router.patch('/:id/status', (req, res) => {
  try {
    const { status } = req.body;
    const orderId = req.params.id;

    // Lấy thông tin đơn hàng hiện tại trong DB
    const existing = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId);
    if (!existing) {
      return res.status(404).json({ error: 'Đơn hàng không tồn tại.' });
    }

    // Yêu cầu 3: Chặn nếu đơn hiện tại đã là 'Đã giao' hoặc 'Hủy'
    if (existing.status === 'Đã giao' || existing.status === 'Hủy') {
      return res.status(400).json({
        error: `Đơn hàng đã ở trạng thái '${existing.status}', không thể chỉnh sửa hoặc thay đổi trạng thái nữa!`
      });
    }

    // Yêu cầu 3: Chỉ cho phép chuyển từ 'Mới' sang 'Đã giao' hoặc 'Hủy'
    const validStatuses = ['Đã giao', 'Hủy'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({
        error: "Trạng thái không hợp lệ. Từ 'Mới' chỉ được chuyển sang 'Đã giao' hoặc 'Hủy'."
      });
    }

    db.prepare('UPDATE orders SET status = ? WHERE id = ?').run(status, orderId);
    const updated = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId);
    res.json(updated);
  } catch (err) {
    res.status(500).json({ error: 'Lỗi server khi đổi trạng thái: ' + err.message });
  }
});

// 5. Chỉnh sửa thông tin đơn hàng (Chặn nếu đơn đã giao / hủy)
router.put('/:id', (req, res) => {
  try {
    const orderId = req.params.id;
    const { customer, item, quantity, unit_price } = req.body;

    const existing = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId);
    if (!existing) {
      return res.status(404).json({ error: 'Đơn hàng không tồn tại.' });
    }

    // Yêu cầu 3: Đơn đã giao hay hủy thì không được sửa
    if (existing.status === 'Đã giao' || existing.status === 'Hủy') {
      return res.status(400).json({
        error: `Đơn hàng đã ở trạng thái '${existing.status}', không thể chỉnh sửa thông tin!`
      });
    }

    const qty = parseFloat(quantity);
    const price = parseFloat(unit_price);

    if (isNaN(qty) || qty <= 0) {
      return res.status(400).json({ error: 'Số lượng phải lớn hơn 0.' });
    }
    if (isNaN(price) || price <= 0) {
      return res.status(400).json({ error: 'Đơn giá phải lớn hơn 0.' });
    }

    const total_amount = Math.round(qty * price * 100) / 100;

    db.prepare(`
      UPDATE orders
      SET customer = ?, item = ?, quantity = ?, unit_price = ?, total_amount = ?
      WHERE id = ?
    `).run(customer.trim(), item.trim(), qty, price, total_amount, orderId);

    const updated = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId);
    res.json(updated);
  } catch (err) {
    res.status(500).json({ error: 'Lỗi server khi sửa đơn: ' + err.message });
  }
});

module.exports = router;

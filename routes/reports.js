// routes/reports.js - Xử lý Báo cáo Doanh thu theo Ngày
const express = require('express');
const router = express.Router();
const db = require('../database');

// YÊU CẦU ĐỀ BÀI:
// 4. Báo cáo doanh thu theo ngày: mỗi ngày một dòng gồm số đơn và tổng thành tiền,
//    chỉ tính đơn 'Đã giao', theo ngày tạo đơn.
router.get('/daily-revenue', (req, res) => {
  try {
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

    const reportRows = db.prepare(query).all();
    res.json(reportRows);
  } catch (err) {
    res.status(500).json({ error: 'Lỗi máy chủ khi truy vấn báo cáo: ' + err.message });
  }
});

module.exports = router;

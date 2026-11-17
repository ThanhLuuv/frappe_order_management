// server.js - Khởi động máy chủ Express
const express = require('express');
const path = require('path');

const ordersRoute = require('./routes/orders');
const reportsRoute = require('./routes/reports');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware parse JSON và URL-encoded
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Phục vụ giao diện web tĩnh từ thư mục public/
app.use(express.static(path.join(__dirname, 'public')));

// Gắn các API routes
app.use('/api/orders', ordersRoute);
app.use('/api/reports', reportsRoute);

// Fallback: Mọi request khác đều trả về trang index.html
app.use((req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Khởi chạy server
app.listen(PORT, () => {
  console.log('='.repeat(65));
  console.log(`🚀 ỨNG DỤNG QUẢN LÝ ĐƠN HÀNG (NODE.JS EXPRESS) ĐÃ KHỞI CHẠY!`);
  console.log(`👉 Mở trình duyệt truy cập: http://localhost:${PORT}`);
  console.log('='.repeat(65));
});

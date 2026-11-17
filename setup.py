from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# Lấy version từ package chính
from order_management import __version__ as version

setup(
    name="order_management",
    version=version,
    description="Ứng dụng quản lý đơn hàng cho bài test lập trình viên ERP/CRM",
    author="Candidate",
    author_email="candidate@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[req for req in install_requires if req and not req.startswith("#")]
)

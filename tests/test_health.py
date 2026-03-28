import os
import sys
from fastapi.testclient import TestClient
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.main import app
client = TestClient(app)

"""
测试指令
虚拟环境 安装 uv add --dev pytest

项目根目录下终端 pytest tests.test_info -v 或 pytest tests -v 测试所有

"""

def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 0
    assert data["message"] == "success"
    assert data["data"]["status"] == "ok"
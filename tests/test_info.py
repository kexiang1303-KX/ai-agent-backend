import os
import sys
from fastapi.testclient import TestClient
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.main import app
client = TestClient(app)

"""
测试指令
虚拟环境 安装 uv add --dev pytest

项目根目录下终端 pytest tests.test_health -v 或 pytest tests -v 测试所有

"""

def test_info():
    response = client.get("/info")

    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 0
    assert data["message"] == "success"

    info = data["data"]
    assert info["service_name"] == "ai-agent-ios-backend"
    assert info["version"] == "0.1.0"
    assert isinstance(info["default_model"], str)

    assert isinstance(info["endpoints"], list)
    assert "/health" in info["endpoints"]
    assert "/info" in info["endpoints"]
    assert "/api/v1/summary" in info["endpoints"]


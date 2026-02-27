from fastapi.testclient import TestClient
import pytest
from wifi_scanner.web import app
from wifi_scanner.main import WiFiScanner


client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_api_scan(mocker):
    # Mock the scanner.scan method inside the web module
    mock_scan = mocker.patch("wifi_scanner.web.scanner.scan")
    mock_data = [{"ssid": "Test-WiFi", "rssi": -50, "band": "5 GHz", "channel": 44, "security": "WPA2"}]
    mock_scan.return_value = mock_data
    
    response = client.get("/api/scan")
    assert response.status_code == 200
    assert response.json() == mock_data

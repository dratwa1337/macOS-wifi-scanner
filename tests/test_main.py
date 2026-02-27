import pytest
from rich.table import Table
from wifi_scanner.main import WiFiScanner


def test_generate_table_with_networks(mocker):
    scanner = WiFiScanner()
    mock_networks = [
        {"ssid": "Home-WiFi", "rssi": -40, "band": "5 GHz", "channel": 36, "security": "WPA2 Personal"},
        {"ssid": "[Redacted/Hidden]", "rssi": -80, "band": "2.4 GHz", "channel": 6, "security": "WPA2 Personal"}
    ]
    
    table = scanner.generate_table(mock_networks)
    
    assert isinstance(table, Table)
    assert table.title == "WiFi Networks Nearby"
    # Check if SSIDs are in the table (Rich tables aren't easily inspectable for contents, 
    # but we can check if the caption contains the redaction note)
    assert "Some SSIDs are [Redacted/Hidden]" in str(table.caption)


def test_generate_table_empty():
    scanner = WiFiScanner()
    table = scanner.generate_table([])
    assert "No WiFi networks found" in str(table.caption)


def test_scan_compilation_failure(mocker):
    scanner = WiFiScanner()
    mocker.patch.object(scanner, 'compile_swift', return_value=False)
    
    networks = scanner.scan()
    assert networks == []

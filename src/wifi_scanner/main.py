import subprocess
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict

from rich.console import Console
from rich.table import Table
from rich import box
from rich.live import Live

class WiFiScanner:
    def __init__(self):
        self.package_dir = Path(__file__).parent
        self.scanner_src = self.package_dir / "scanner.swift"
        self.scanner_bin = self.package_dir / "scanner"
        self.console = Console()

    def compile_swift(self) -> bool:
        if not self.scanner_bin.exists():
            self.console.print(f"Compiling Swift scanner to {self.scanner_bin}...")
            try:
                subprocess.run(["swiftc", str(self.scanner_src), "-o", str(self.scanner_bin)], check=True)
            except subprocess.CalledProcessError:
                return False
        return True

    def scan(self) -> List[Dict]:
        if not self.compile_swift():
            return []
        
        try:
            result = subprocess.run([str(self.scanner_bin)], capture_output=True, text=True, check=True)
            output = result.stdout
            if not output:
                return []
            return json.loads(output)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []

    def generate_table(self, networks: List[Dict]) -> Table:
        if not networks:
            return Table(title="WiFi Networks Nearby", caption="[yellow]No WiFi networks found or scanning...[/yellow]")

        # Sort networks by RSSI (signal strength) descending
        networks.sort(key=lambda x: x['rssi'], reverse=True)

        table = Table(title="WiFi Networks Nearby", box=box.ROUNDED, header_style="bold cyan")
        table.add_column("SSID", style="white", min_width=15)
        table.add_column("Signal", justify="right", min_width=10)
        table.add_column("Band", justify="center", style="green")
        table.add_column("Channel", justify="right", min_width=8)
        table.add_column("Security", style="magenta", min_width=15)

        for net in networks:
            rssi = net['rssi']
            # Convert RSSI to percentage (approximate)
            # -100 dBm is 0%, -50 dBm is 100%
            percentage = min(100, max(0, 2 * (rssi + 100)))
            
            # Colorize signal strength
            if percentage >= 80:
                signal_color = "green"
            elif percentage >= 50:
                signal_color = "yellow"
            else:
                signal_color = "red"
            
            table.add_row(
                net['ssid'],
                f"[{signal_color}]{percentage}%[/{signal_color}]",
                net['band'],
                str(net['channel']),
                net['security']
            )
        
        # Check for redacted SSIDs
        redacted_count = sum(1 for n in networks if "[Redacted" in n['ssid'])
        footer = f"\n[dim]Found {len(networks)} networks.[/dim]"
        if redacted_count > 0:
            footer += "\n\n[bold yellow]Note: Some SSIDs are [Redacted/Hidden].[/bold yellow]\n"
            footer += "Check Location Services permissions for your Terminal."
        
        table.caption = footer
        return table

def start_web_server(host: str, port: int):
    try:
        import uvicorn
        from .web import app
        uvicorn.run(app, host=host, port=port)
    except ImportError:
        print("[red]Error: fastapi and uvicorn are required for the web UI.[/red]")

def main():
    parser = argparse.ArgumentParser(description="MacOS WiFi Scanner")
    parser.add_argument("-w", "--watch", action="store_true", help="Enable continuous scanning")
    parser.add_argument("-i", "--interval", type=int, default=10, help="Refresh interval in seconds (default: 10)")
    parser.add_argument("--web", action="store_true", help="Start the Web UI dashboard")
    parser.add_argument("--port", type=int, default=8000, help="Web UI port (default: 8000)")
    args = parser.parse_args()

    scanner = WiFiScanner()
    console = Console()

    if args.web:
        start_web_server("127.0.0.1", args.port)
        return

    if not scanner.compile_swift():
        console.print("[red]Critical Error: Could not find or compile the scanner utility.[/red]")
        return

    if not args.watch:
        with console.status("[bold green]Scanning for WiFi networks...", spinner="dots"):
            networks = scanner.scan()
        
        if not networks:
            console.print("[yellow]No WiFi networks found.[/yellow]")
            return
            
        console.print(scanner.generate_table(networks))
    else:
        try:
            with Live(scanner.generate_table([]), console=console, refresh_per_second=1) as live:
                while True:
                    networks = scanner.scan()
                    live.update(scanner.generate_table(networks))
                    time.sleep(args.interval)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopping scanner...[/yellow]")

if __name__ == "__main__":
    main()

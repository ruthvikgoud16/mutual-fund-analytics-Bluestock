"""Generate 4 PNG page screenshots and Dashboard.pdf for the Bluestock MF Dashboard.

Navigates to the live React dashboard app using Headless Chrome,
captures high-resolution 1600x1200 screenshots for Pages 1-4,
and compiles them into Dashboard.pdf.
"""

import http.server
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "dashboard" / "frontend" / ".output" / "public"
EXPORTS_DIR = PROJECT_ROOT / "dashboard" / "exports"
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class SinglePageHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler supporting Single Page Application routing (fallback to index.html)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        url_path = self.path.split("?")[0].lstrip("/")
        local_file = STATIC_DIR / url_path
        if not local_file.exists() or local_file.is_dir():
            self.path = "/index.html"
        return super().do_GET()


def start_server(port=3000):
    handler = SinglePageHTTPRequestHandler
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    httpd.allow_reuse_address = True
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return httpd


def capture_screenshots(port=3000):
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    pages = [
        ("/", EXPORTS_DIR / "page1_industry_overview.png"),
        ("/fund-performance", EXPORTS_DIR / "page2_fund_performance.png"),
        ("/investor-analytics", EXPORTS_DIR / "page3_investor_analytics.png"),
        ("/sip-market-trends", EXPORTS_DIR / "page4_sip_market_trends.png"),
    ]

    print("Capturing high-resolution PNG page screenshots via Headless Chrome...")
    for route, out_png in pages:
        url = f"http://127.0.0.1:{port}{route}"
        cmd = [
            CHROME_PATH,
            "--headless",
            "--disable-gpu",
            "--window-size=1600,1200",
            "--virtual-time-budget=5000",
            f"--screenshot={out_png}",
            url,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if out_png.exists() and out_png.stat().st_size > 0:
            print(f"Captured {out_png.name} ({out_png.stat().st_size} bytes)")
        else:
            print(f"Failed to capture {out_png.name}: {res.stderr}")

    # Duplicate to root/reports exports for convenience
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    images = []
    for route, out_png in pages:
        if out_png.exists():
            img = Image.open(out_png).convert("RGB")
            images.append(img)

    if images:
        pdf_path = EXPORTS_DIR / "Dashboard.pdf"
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        print(f"Compiled {pdf_path.name} ({pdf_path.stat().st_size} bytes)")

        # Save copy in reports/
        reports_pdf = reports_dir / "Dashboard.pdf"
        images[0].save(reports_pdf, save_all=True, append_images=images[1:])
        print(f"Saved copy to {reports_pdf}")


def main():
    if not STATIC_DIR.exists():
        print(
            f"Error: Static directory {STATIC_DIR} does not exist. Run npm run build first."
        )
        sys.exit(1)

    port = 3010
    httpd = start_server(port)
    time.sleep(1.0)
    try:
        capture_screenshots(port)
    finally:
        httpd.shutdown()
        print("Export server stopped.")


if __name__ == "__main__":
    main()

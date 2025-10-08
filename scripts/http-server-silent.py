#!/usr/bin/env -S uv run --script --with click
import http.server
import socketserver
import click
import webbrowser
import time
import threading


class quietServer(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


@click.command()
@click.argument("port", type=int, default=8080)
@click.option("--open", "open_path", help="Open a file in the browser after starting the server")
def main(port, open_path):
    """Start a silent HTTP server on the specified PORT (default: 8080)"""
    print(f"listening on http://0.0.0.0:{port}")

    def start_server():
        with socketserver.TCPServer(("", port), quietServer) as httpd:
            httpd.serve_forever()

    # Start server in a separate thread if we need to open a browser
    if open_path:
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        time.sleep(0.5)  # Give server time to start
        webbrowser.open(f"http://localhost:{port}/{open_path}")
        # Keep main thread alive
        try:
            server_thread.join()
        except KeyboardInterrupt:
            pass
    else:
        start_server()


if __name__ == "__main__":
    main()

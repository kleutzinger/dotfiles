#!/usr/bin/env -S uv run --with pywebview,PyGObject

# get arguments from the command line
import sys
import subprocess
import platform

import webview


def desktop_notify(
    message: str, title: str = "Notification"
) -> None:
    """Send a desktop notification."""
    try:
        if platform.system() == "Linux":
            subprocess.run(["notify-send", title, message])
        elif platform.system() == "Darwin":
            subprocess.run(
                [
                    "terminal-notifier",
                    "-title",
                    title,
                    "-message",
                    message,
                ]
            )
    except:
        # If the notification fails, we can ignore it
        pass


image_links = sys.argv[1:]

# turn images into html
image_html = ""
_id = 0
for image_link in image_links:
    image_html += f"<img id={_id} src='{image_link}' onClick='window.pywebview.api.log(this.src); window.pywebview.api.quit()'/>"
    _id += 1


class Api:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def log(self, value):
        import subprocess

        # notify-send the output

        desktop_notify(value, "Image Selected")
        print(value, flush=True)

    def quit(self):
        self._window.destroy()
        exit()


html = f"""
  <html>
    <head></head>
    <body>
      <h2>Links</h2>
        {image_html}
    </body>
    <style>
        body {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            align-content: center;
        }}
        img {{
            max-height: 256px;
            margin: 10px;
            cursor: pointer;
        }}
    </style>
  </html>
"""

if __name__ == "__main__":
    api = Api()
    window = webview.create_window(
        "Link types", html=html, fullscreen=True, js_api=api, on_top=True
    )
    api.set_window(window)
    webview.start()

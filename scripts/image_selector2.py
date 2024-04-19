#!/usr/bin/env python3
import webview

# get arguments from the command line
import sys

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
        print(value)
        exit()

    def quit(self):
        self._window.destroy()


html = f"""
  <html>
    <head></head>
    <body>
      <h2>Links</h2>
        {image_html}
    </body>
  </html>
"""

if __name__ == "__main__":
    api = Api()
    window = webview.create_window(
        "Link types", html=html, fullscreen=True, js_api=api, on_top=True
    )
    api.set_window(window)
    webview.start()

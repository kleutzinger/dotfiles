import subprocess
import webbrowser


def play_youtube_music_url(url):
    try:
        subprocess.run(
            ["playerctl", "--player", "YoutubeMusic", "open", url], check=True
        )
    except subprocess.CalledProcessError:
        webbrowser.open(url)

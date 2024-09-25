#!/usr/bin/env python3
"""

### Media Controls for Youtube Music
~/scripts ❯ playerctl status YoutubeMusic
Playing
~/scripts ❯ playerctl status YoutubeMusic
Paused
~/scripts ❯ playerctl status YoutubeMusic
No players found

playerctl --player YoutubeMusic play-pause


### radiotray-ng
https://github.com/ebruck/radiotray-ng?tab=readme-ov-file#dbus-interface
play:
qdbus com.github.radiotray_ng /com/github/radiotray_ng com.github.radiotray_ng.play
stop:
qdbus com.github.radiotray_ng /com/github/radiotray_ng com.github.radiotray_ng.stop
"""

import subprocess
import click
from abc import ABC


# make an abc class that abstracts players and their has
# play, pause, stop, next, previous, status, is_running


class Player(ABC):
    def __init__(self):
        pass

    def play(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass

    def is_playing(self) -> bool:
        pass

    def next(self):
        pass

    def previous(self):
        pass

    def is_running(self) -> bool:
        return False

    def interactive_choose_song(self):
        pass


class YoutubeMusicPlayer(Player):
    def __init__(self):
        self.player = "YoutubeMusic"

    def play(self):
        subprocess.run(["playerctl", "--player", self.player, "play"])

    def pause(self):
        subprocess.run(["playerctl", "--player", self.player, "pause"])

    def stop(self):
        subprocess.run(["playerctl", "--player", self.player, "stop"])

    def is_playing(self) -> bool:
        if not self.is_running():
            return False
        if subprocess.run(
            ["playerctl", "--player", self.player, "status"], capture_output=True
        ).stdout == "Playing":
            print("WE ARE PLAYING")
            return True
        print("we are not playing")
        return False

    def next(self):
        pass

    def previous(self):
        subprocess.run(["playerctl", "--player", self.player, "previous"])

    def is_running(self) -> bool:
        return (
            subprocess.run(
                ["playerctl", "--player", self.player, "status"], capture_output=True
            ).returncode
            == 0
        )

    def interactive_choose_song(self):
        pass


def playpause():
    player = YoutubeMusicPlayer()
    print(player.is_running())
    print(player.is_playing())
    if player.is_playing():
        print("pausing")
        player.pause()
    elif not player.is_playing():
        print("playing")
        player.play()
    else:
        print("No players found")


playpause()

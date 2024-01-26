Hi, this is my computer's config. I use the <a href="https://colemak.com/">colemak</a> keyboard layout  
I'm using [yadm](https://yadm.io/) to manage my dotfiles and I like it because it doesn't make a bunch of symlinks everywhere.

```
kevin@think0
------------
OS: ArcoLinux
Host: 20FAS4EG00 ThinkPad T460s
Kernel: 6.5.6-arch2-1
Packages: 1939 (pacman), 7 (nix-user)
Shell: fish 3.6.1
Resolution: 2560x1440
DE: Xfce 4.18
WM: Xfwm4
WM Theme: Arc-Dark
Theme: Adwaita-dark [GTK2], Arc-Dark [GTK3]
Icons: Adwaita [GTK2], Sardi-Arc [GTK3]
Terminal: kitty
CPU: Intel i7-6600U (4) @ 3.400GHz
GPU: Intel Skylake GT2 [HD Graphics 520]
Memory: 19745MiB
Editor: neovim
```

## Keybindings (OS)

All keybindings are defined in [config/sxhkd/sxhkdrc](.config/sxhkd/sxhkdrc)

- `F1`: dropdown terminal
- `super + enter`: floating terminal
- `super + space`: dmenu_run
- `super + w`: open browser
- `super + m`: maximize
- `super + q`: quit application
- `shift + super + b`: disconnect bluetooth controller
- `super + b`: edit [blog](https://blog.kevbot.xyz)
- `super + o`: video game launcher

## TODO:

[] separate commands on different window managers
[] make `grid_overlay.py` able to click the screen (xdotool)

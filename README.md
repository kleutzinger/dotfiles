Hi, this is my computer's config. I use the <a href="https://colemak.com/">colemak</a> keyboard layout  
I'm using [yadm](https://yadm.io/) to manage my dotfiles and I like it because it doesn't make a bunch of symlinks everywhere.

```
kevin@kb-think
--------------
OS: EndeavourOS Linux x86_64
Host: 20FAS4EG00 ThinkPad T460s
Kernel: 5.11.8-arch1-1
Packages: 1974 (pacman)
Shell: fish 3.2.1
Resolution: 2560x1440
DE: Plasma 5.21.3
WM: KWin
WM Theme: Ant-Dark
Theme: Breeze Dark [Plasma], Adwaita-dark [GTK2/3]
Icons: Arc-X-D [Plasma], Arc-X-D [GTK2/3]
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
- `super + space`: dmenu\_run
- `super + w`: open browser
- `super + m`: maximize
- `super + q`: quit application
- `shift + super + b`: disconnect bluetooth controller
- `super + b`: edit [blog](https://blog.kevbot.xyz)
- `super + o`: video game launcher


## TODO:

[] separate commands on different window managers
[] auto run CocInstall

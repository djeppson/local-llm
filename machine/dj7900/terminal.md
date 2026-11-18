# Cargo Applications

See [rust-cargo.md](./rust-cargo.md) for quick restore/sync notes

- bat: alternative to cat
- eza: alternative to ls https://github.com/eza-community/eza
- bottom: alternative to top (command is `btm`)
- procs: alternative to ps

After install, setup terminal aliases and such

```
scp remotehost:~/.zprofile ~
source .zprofile
```

# Starship

## Debian

Download: https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/BitstreamVeraSansMono.zip

```
mkdir -p ~/.fonts/b
unzip ~/BitstreamVeraSansMono.zip -d ~/.fonts/b/
fc-list | grep BitstromWeraNerdFont
fc-cache -fv
```

## Mac

```
brew tap homebrew/cask-fonts &&
brew install --cask font-bitstream-vera
brew install starship
```

# Terminal

Consider Wez (because Rust):

```
cd ~/Downloads
curl -LO https://github.com/wez/wezterm/releases/download/20240203-110809-5046fc22/wezterm-20240203-110809-5046fc22.Debian12.deb
sudo apt install -y ./wezterm-20240203-110809-5046fc22.Debian12.deb
```

Consider foot (because Reddit) https://codeberg.org/dnkl/foot

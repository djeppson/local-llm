# Terminal

## Starship

- Make sure you are running zsh (e.g., `sudo pacman -Syu zsh`)
- Install Starship `curl -sS https://starship.rs/install.sh | sh`
- If pyenv is missing: `pamac install pyenv`

# Boot

## systemd-boot (EndeavorOs)

To enable management of AMD GPU settings:

- Temporarily: At the boot screen, type `e` on the entry you wish to modify and options like those below
- Permanently: Edit `/etc/kernel/cmdline` (see below) and run `sudo reinstall-kernels`
  - `amdgpu.ppfeaturemask=0xffffffff` (that is 8-f's) Allows control of the graphics card's lighting and fans and stuff [CoreCtrl](https://gitlab.com/corectrl/corectrl/-/wikis/Setup)
  - `acpi_enforce_resources=lax` Allows control of the RAM LEDs (future Darren: don't buy RGB stuff again plz, thx). Some Aorus motherboards have an ACPI conflict with the SMBus controller. See the [Kernel Parameters](https://gitlab.com/CalcProgrammer1/OpenRGB/-/blob/master/Documentation/KernelParameters.md)
  3. Reboot as necessary to confirm operation

Note: For the EndeavorOS setup, I only modified the newest kernel non-fallback option to keep the other options as 'vanilla' as possible

## Wake on LAN

The motherboard/NIC must support (seems like with new Gigabyte Aorus the option is enabled by default now - not in BIOS settings) Install wol-systemd: `yay -S wol-systemd` Enable for adapter (e.g., enp13s0): `systemctl enable wol@enp13s0`

## GRUB (Manjaro, Debian, etc.)

To recognize new OSes:

```
sudo os-prober
sudo update-grub 
```

General procedure:

- Edit the GRUB config `sudo vi /etc/default/grub`
- Modify GRUB_CMDLINE_LINUX_DEFAULT (see above systemd-boot for options)
- Regenerate: `sudo grub-mkconfig -o /boot/grub/grub.cfg`
- Validate result of `cat /proc/cmdline` ("Vanilla" Manjaro: `BOOT_IMAGE=/boot/vmlinuz-6.11-x86_64 root=UUID=060c8a65-7251-428f-b631-8cd2778dde21 rw quiet splash udev.log_priority=3`)

## OpenRGB - GSkill RAM

Install:

- Manjaro: `pamac install openrgb`

Pay attention to [Enable SMBus access](https://gitlab.com/CalcProgrammer1/OpenRGB#smbus-access-1)

- `pamac install i2c-tools`
- `sudo modprobe i2c-dev`
- `sudo modprobe i2c-piix4` (AMD chipset)
- Confirm RAM controls are available, setup to run at boot
  - `sudo touch /etc/modules-load.d/i2c.conf`
  - `sudo sh -c 'echo "i2c-dev" >> /etc/modules-load.d/i2c.conf'`
  - `sudo sh -c 'echo "i2c-piix4" >> /etc/modules-load.d/i2c.conf'`

FYI pretty blue color for RAM:

- R: 0 G: 19 B: 35
- H: 207 S: 255 V: 35

## CoolerControl

https://gitlab.com/coolercontrol/coolercontrol

Install

- Arch: https://docs.coolercontrol.org/installation/arch.html

Setup:

- NZXT Kraken Z: https://github.com/liquidctl/liquidctl/blob/main/docs/kraken-x3-z3-guide.md
- Put a nice image on the screen in `~/.config/coolercontrol`

![Diversity](https://www.debian.org/logos/diversity-2019.png)

# Devices

## CoreCtrl - AMD GPU (e.g., undervolting)

See: https://gitlab.com/corectrl/corectrl/-/wikis/Setup Current voltage set to `-70`

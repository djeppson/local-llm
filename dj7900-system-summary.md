# DJ7900
- CPU: AMD Ryzen 9 7900 12-Core Processor
- GPU: Radeon RX 7900 XTX 24GB RAM
- RAM: 32GB DDR5 6000MHz


## Motherboard

### Baseboard Information
- **Manufacturer**: Gigabyte Technology Co., Ltd.
- **Model**: B650 AORUS ELITE AX
- **Version**: x.x
- **UUID**: 03560274-043c-0538-b906-e40700080009
- **Family**: B650 MB

### Command
```bash
sudo dmidecode -t baseboard
sudo dmidecode -t system
```

## GPU Details

### `lspci -k | grep -EA3 'VGA|3D|Display'`
```
03:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Navi 31 [Radeon RX 7900 XT/7900 XTX] (rev c8)
       Subsystem: Sapphire Technology Limited NITRO+ RX 7900 XTX Vapor-X
       Kernel driver in use: amdgpu
       Kernel modules: amdgpu
-- 
12:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Raphael (rev c4)
       Subsystem: Gigabyte Technology Co., Ltd Raphael
       Kernel driver in use: amdgpu
       Kernel modules: amdgpu
```
- Detailed outputs:
    - [rocm-smi.md](./rocm-smi.md)
    - [rocminfo.md](./rocminfo.md)

### Do not attempt to disable power management
```bash
# ⚠️ WARNING: This solution rendered the system inoperable - it would freeze at boot
# ⚠️ DO NOT ATTEMPT THIS SOLUTION AGAIN - IT WILL FREEZE THE SYSTEM AT BOOT
# ⚠️ This solution has been marked as dangerous and should not be retried
# sudo nano /etc/modprobe.d/amdgpu-disable-igpu.conf
# Add to the file:
#   options amdgpu runpm=0
#   options amdgpu dpm=0
```

## Operating System

### System Information
- **Hostname**: `endeavor-7900`
- **Distribution**: EndeavourOS (Arch-based)
- **Kernel**: `6.18.25-1-lts`
- **Architecture**: `x86_64`
- **Desktop Environment**: `XFCE`
- **Shell**: `/usr/bin/zsh`
- **Uptime**: ~39 minutes
- **Memory**: 30Gi total (6.8Gi used, 9.0Gi free)
- **Swap**: 0B
- **Root Disk**: `/dev/nvme1n1p2` (1.8T, 916G used, 823G free)
- **CPU**: AMD Ryzen 9 7900 12-Core Processor (12 threads)

### Commands
```bash
# Kernel and architecture
uname -r
uname -m

# OS information
cat /etc/os-release | grep -E "PRETTY_NAME|NAME"

# Desktop environment
echo $XDG_CURRENT_DESKTOP
echo $DESKTOP_SESSION

# Shell
echo $SHELL

# Memory and disk
free -h
df -h /

# CPU information
lscpu | grep -E "Model name|CPU(s)|Thread(s)"

# Hostname
hostname

# Uptime
uptime
```

## Storage

### Disk Hardware

#### nvme1n1 (Main System Drive)
- **Model**: Samsung SSD 990 EVO 2TB
- **Revision**: 0B2QKXJ7
- **Serial**: S7M4NL0X906706J
- **WWN**: eui.0025382941a07efe
- **Capacity**: 1.8TB (raw)

#### nvme0n1 (Secondary Drive)
- **Model**: Samsung SSD 980 PRO 2TB
- **Revision**: 5B2QGXA7
- **Serial**: S6B0NL0W136572M
- **Capacity**: 1.8TB (raw)

#### sda (USB Drive)
- **Model**: Samsung SSD 840 EVO 250GB
- **Revision**: EXT0BB6Q
- **Serial**: S1DBNSCF305637H
- **Capacity**: 232.9GB (raw)

### Filesystem Layout

#### nvme1n1
| Partition | Filesystem | UUID | Mountpoint |
|-----------|------------|------|------------|
| nvme1n1p1 | vfat | 5A3D-8E2E | /efi |
| nvme1n1p2 | ext4 | bfe3af79-b071-44cc-8cba-791efb6450e1 | / |

#### nvme0n1
| Partition | Filesystem | UUID | Mountpoint |
|-----------|------------|------|------------|
| nvme0n1p1 | vfat | 85F5-6C68 | (boot) |
| nvme0n1p2 | ext4 | 10b459d6-e9b8-4a04-a4f4-0b74c1720c9b | (data) |

### Commands
```bash
# List all disks with filesystem info
lsblk -f

# Get detailed disk information
lsblk -no MODEL,REV,SERIAL,WWN /dev/disk

# Get filesystem details
lsblk -no FSTYPE,UUID,MOUNTPOINT /dev/disk

# SMART status (if available)
sudo smartctl -i /dev/nvme1n1
```

## Boot Manager

### systemd-boot (UEFI Boot Manager)

**Boot Loader**: systemd-boot (located at `/EFI/systemd/systemd-bootx64.efi`)

**EFI Boot Order** (from `efibootmgr -v`):
| Boot Entry | Name | Path | Status |
|--|--|--|--|
| Boot0000 | Windows Boot Manager | `\EFI\Microsoft\Boot\bootmgfw.efi` | - |
| Boot0001 | Debian | `\EFI\Debian\shimx64.efi` | - |
| Boot0002 | Linux Boot Manager | `\EFI\systemd\systemd-bootx64.efi` | - |
| Boot0005 | UEFI OS | `\EFI\BOOT\BOOTX64.EFI` | **Current** |
| Boot0006-000D | Network Boot (PXE/HTTP) | - | - |

**Boot Configuration**:
- **Timeout**: 1 second
- **BootOrder**: 0005,0001,0002,0006,0007,0008,0009,000A,000B,000C,000D,0000
- **Current Boot**: Boot0005 (UEFI OS)

### Boot Process

1. **UEFI Firmware** initializes hardware and reads NVRAM boot order
2. **EFI Boot Manager** loads the first boot entry (currently `\EFI\BOOT\BOOTX64.EFI`)
3. **systemd-boot** loads the kernel and initramfs from `/efi`
4. **Linux Kernel** initializes and starts systemd
5. **Systemd** starts services and user session

### EFI System Partition

- **Mountpoint**: `/efi`
- **Filesystem**: vfat
- **UUID**: 5A3D-8E2E
- **Purpose**: Stores EFI bootloaders and boot configuration

### Commands
```bash
# View EFI boot order
efibootmgr -v

# View current boot entry
efibootmgr -v | grep BootCurrent

# Change boot order
efibootmgr -o <new_order>

# List boot entries
efibootmgr -v | grep -E "Boot[0-9A-F]"

# Reset NVRAM (removes all custom boot entries)
sudo efibootmgr -c -d /dev/nvme1n1 -p 1 -w /dev/nvme1n1p1 -L "Ubuntu" -U "UUID=..." -D

# View systemd-boot configuration
cat /boot/loader/loader.conf
cat /boot/loader/entries/*.conf
```

## Keyboard (KBDFans)

### `/etc/udev/rules.d/99-hidraw.rules` 
`KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="4b42", ATTRS{idProduct}=="1226", MODE="0660", GROUP="jeppson", TAG+="uaccess", TAG+="udev-acl"`

Restart udev after a rule change:
```
udevadm control --reload-rules
udevadm trigger
```


## Peripherals

### lsusb
```
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 002: ID 0bda:5411 Realtek Semiconductor Corp. RTS5411 Hub
Bus 001 Device 003: ID 048d:5702 Integrated Technology Express, Inc. RGB LED Controller
Bus 001 Device 004: ID 0e8d:0616 MediaTek Inc. Wireless_Device
Bus 001 Device 005: ID 1e71:3008 NZXT NZXT KrakenZ Device
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 002 Device 002: ID 0bda:0411 Realtek Semiconductor Corp. Hub
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 005 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 005 Device 002: ID 2188:0034 No brand Element USB 2.0 Hub
Bus 005 Device 003: ID 2188:0031 No brand USB2.0 Hub
Bus 005 Device 004: ID 05ac:12ab Apple, Inc. iPad
Bus 005 Device 005: ID 2188:0035 No brand Element Hub
Bus 005 Device 006: ID 0bda:5483 Realtek Semiconductor Corp. 4-Port USB 2.0 Hub
Bus 005 Device 007: ID 0bda:5483 Realtek Semiconductor Corp. 4-Port USB 2.0 Hub
Bus 005 Device 008: ID 1235:8211 Focusrite-Novation Scarlett Solo (3rd Gen.)
Bus 005 Device 009: ID 1050:0407 Yubico.com Yubikey 4/5 OTP+U2F+CCID
Bus 005 Device 010: ID 4b42:1226 KBDFANS KBD67MKIIRGBV3
Bus 005 Device 011: ID 0bda:8153 Realtek Semiconductor Corp. RTL8153 Gigabit Ethernet Adapter
Bus 005 Device 012: ID 046d:c548 Logitech, Inc. Logi Bolt Receiver
Bus 005 Device 013: ID 046d:0892 Logitech, Inc. C920 HD Pro Webcam
Bus 005 Device 014: ID 0bda:1100 Realtek Semiconductor Corp. USB2.0 HID
Bus 006 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 007 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 007 Device 002: ID 05e3:0608 Genesys Logic, Inc. Hub
Bus 007 Device 003: ID 051d:0002 American Power Conversion Uninterruptible Power Supply
```

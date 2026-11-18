# Hardware and Install (as of 2025-05-15)

## EFI Boot

```
❯ efibootmgr
BootCurrent: 0005
Timeout: 1 seconds
BootOrder: 0005,0001,0002,0006,0007,0008,0009,000A,000B,000C,000D,0000
Boot0000  Windows Boot Manager	HD(1,GPT,ac517fa6-f0a5-4c1f-8702-6c28ac416223,0x800,0x32000)/\EFI\Microsoft\Boot\bootmgfw.efi57494e444f5753000100000088000000780000004200430044004f0042004a004500430054003d007b00390064006500610038003600320063002d0035006300640064002d0034006500370030002d0061006300630031002d006600330032006200330034003400640034003700390035007d00000074000100000010000000040000007fff0400
Boot0001* Debian	HD(1,GPT,2a4788db-a6fb-4400-a55a-443c5aa55d40,0x1000,0x96000)/\EFI\Debian\shimx64.efi
Boot0002* Linux Boot Manager	HD(1,GPT,8a5cb04d-6b31-4227-abeb-69ab8f0c4aa6,0x1000,0x400000)/\EFI\systemd\systemd-bootx64.efi
Boot0005* UEFI OS	HD(1,GPT,8a5cb04d-6b31-4227-abeb-69ab8f0c4aa6,0x1000,0x400000)/\EFI\BOOT\BOOTX64.EFI0000424f
Boot0006* UEFI: HTTP IPv4 Realtek PCIe 2.5GBE Family Controller	PciRoot(0x0)/Pci(0x2,0x1)/Pci(0x0,0x0)/Pci(0xa,0x0)/Pci(0x0,0x0)/MAC(74563c38b9e4,0)/IPv4(0.0.0.0,0,DHCP,0.0.0.0,0.0.0.0,0.0.0.0)/Uri()0000424f
Boot0007* UEFI: PXE IPv4 Realtek PCIe 2.5GBE Family Controller	PciRoot(0x0)/Pci(0x2,0x1)/Pci(0x0,0x0)/Pci(0xa,0x0)/Pci(0x0,0x0)/MAC(74563c38b9e4,0)/IPv4(0.0.0.0,0,DHCP,0.0.0.0,0.0.0.0,0.0.0.0)0000424f
Boot0008* UEFI: HTTP IPv6 Realtek PCIe 2.5GBE Family Controller	PciRoot(0x0)/Pci(0x2,0x1)/Pci(0x0,0x0)/Pci(0xa,0x0)/Pci(0x0,0x0)/MAC(74563c38b9e4,0)/IPv6([::],0,Static,[::],[::],64)/Uri()0000424f
Boot0009* UEFI: PXE IPv6 Realtek PCIe 2.5GBE Family Controller	PciRoot(0x0)/Pci(0x2,0x1)/Pci(0x0,0x0)/Pci(0xa,0x0)/Pci(0x0,0x0)/MAC(74563c38b9e4,0)/IPv6([::],0,Static,[::],[::],64)0000424f
Boot000A* Samsung SSD 840 EVO 250GB	BBS(HD,,0x0)0000424f
Boot000B* Samsung SSD 990 EVO 2TB	BBS(HD,,0x0)0000424f
Boot000C* Samsung SSD 980 PRO 2TB	BBS(HD,,0x0)0000424f
Boot000D* Realtek PXE B0D D00	BBS(Network,,0x0)0000424f
```

Note: 'UEFI OS HD' is Endeavor - an Arch distribution. Renaming it from 'UEFI OS' requires deleting and then recreating the boot setup.

## bootctl

```
System:
      Firmware: UEFI 2.90 (American Megatrends 5.35)
 Firmware Arch: x64
   Secure Boot: disabled (setup)
  TPM2 Support: yes
  Measured UKI: no
  Boot into FW: supported

Current Boot Loader:
       Product: systemd-boot 260.1-2-arch
     Features: ✓ Boot counting
               ✓ Menu timeout control
               ✓ One-shot menu timeout control
               ✓ Default entry control
               ✓ One-shot entry control
               ✓ Support for XBOOTLDR partition
               ✓ Support for passing random seed to OS
               ✓ Load drop-in drivers
               ✓ Support Type #1 sort-key field
               ✓ Support @saved pseudo-entry
               ✓ Support Type #1 devicetree field
               ✓ Enroll SecureBoot keys
               ✓ Retain SHIM protocols
               ✓ Menu can be disabled
               ✓ Multi-Profile UKIs are supported
               ✓ Loader reports network boot URL
               ✓ Support Type #1 uki field
               ✓ Support Type #1 uki-url field
               ✓ Loader reports active TPM2 PCR banks
     Partition: /dev/disk/by-partuuid/8a5cb04d-6b31-4227-abeb-69ab8f0c4aa6
        Loader: └─/efi//EFI/BOOT/BOOTX64.EFI
 Current Entry: 914f579d51a94b01a741a8ae5a094160-6.18.25-1-lts.conf

Random Seed:
 System Token: set
       Exists: yes

Available Boot Loaders on ESP:
          ESP: /efi (/dev/disk/by-partuuid/8a5cb04d-6b31-4227-abeb-69ab8f0c4aa6)
         File: ├─/efi//EFI/systemd/systemd-bootx64.efi (systemd-boot 260.1-2-arch)
               └─/efi//EFI/BOOT/BOOTX64.EFI (systemd-boot 260.1-2-arch)

Boot Loaders Listed in EFI Variables:
        Title: UEFI OS
           ID: 0x0005
       Status: active, boot-order
    Partition: /dev/disk/by-partuuid/8a5cb04d-6b31-4227-abeb-69ab8f0c4aa6
         File: └─/efi//EFI/BOOT/BOOTX64.EFI

        Title: Debian
           ID: 0x0001
       Status: active, boot-order
    Partition: /dev/disk/by-partuuid/2a4788db-a6fb-4400-a55a-443c5aa55d40
         File: └─/efi//EFI/Debian/shimx64.efi

        Title: Linux Boot Manager
           ID: 0x0002
       Status: active, boot-order
    Partition: /dev/disk/by-partuuid/8a5cb04d-6b31-4227-abeb-69ab8f0c4aa6
         File: └─/efi//EFI/systemd/systemd-bootx64.efi

        Title: Windows Boot Manager
           ID: 0x0000
       Status: inactive, boot-order
    Partition: /dev/disk/by-partuuid/ac517fa6-f0a5-4c1f-8702-6c28ac416223
         File: └─/efi//EFI/Microsoft/Boot/bootmgfw.efi

Boot Loader Entry Locations:
          ESP: /efi (/dev/disk/by-partuuid/8a5cb04d-6b31-4227-abeb-69ab8f0c4aa6, $BOOT)
       config: /efi//loader/loader.conf
        token: endeavouros

Default Boot Loader Entry:
         type: Boot Loader Specification Type #1 (.conf)
        title: EndeavourOS (6.18.25-1-lts)
           id: 914f579d51a94b01a741a8ae5a094160-6.18.25-1-lts.conf
       source: /efi//loader/entries/914f579d51a94b01a741a8ae5a094160-6.18.25-1-lts.conf (on the EFI System Partition)
     sort-key: endeavouros-6.18.25-1-lts
      version: 6.18.25-1-lts
   machine-id: 914f579d51a94b01a741a8ae5a094160
        linux: /efi//914f579d51a94b01a741a8ae5a094160/6.18.25-1-lts/linux
       initrd: /efi//914f579d51a94b01a741a8ae5a094160/6.18.25-1-lts/initrd
      options: nvme_load=YES nowatchdog rw root=UUID=bfe3af79-b071-44cc-8cba-791efb6450e1 amdgpu.ppfeaturemask=0xffffffff acpi_enforce_resources=lax systemd.machine_id=914f579d51a94b01a741a8ae5a094160
```

## Disks: `sudo fdisk -l`

```
Disk /dev/sda: 232.89 GiB, 250059350016 bytes, 488397168 sectors
Disk model: Samsung SSD 840 
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: AFF6AC94-D185-47CC-973A-3AF99FC59E6F

Device         Start       End   Sectors   Size Type
/dev/sda1       2048    206847    204800   100M EFI System
/dev/sda2     206848    239615     32768    16M Microsoft reserved
/dev/sda3     239616 487079935 486840320 232.1G Microsoft basic data
/dev/sda4  487079936 488394751   1314816   642M Windows recovery environment


Disk /dev/nvme0n1: 1.82 TiB, 2000398934016 bytes, 3907029168 sectors
Disk model: Samsung SSD 980 PRO 2TB                 
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: 5484798B-C4D6-4DAC-B88E-AE4B977D63BE

Device              Start        End    Sectors  Size Type
/dev/nvme0n1p1       4096     618495     614400  300M EFI System
/dev/nvme0n1p2     618496 3836740702 3836122207  1.8T Linux filesystem
/dev/nvme0n1p3 3836740703 3907029101   70288399 33.5G Linux swap


Disk /dev/nvme1n1: 1.82 TiB, 2000398934016 bytes, 3907029168 sectors
Disk model: Samsung SSD 990 EVO 2TB                 
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: 745FBAA6-79D5-4CDD-98EE-B67691CC0DAC

Device           Start        End    Sectors  Size Type
/dev/nvme1n1p1    4096    4198399    4194304    2G EFI System
/dev/nvme1n1p2 4198400 3907029101 3902830702  1.8T Linux filesystem
```

# Getting a new linux box up and running

## Dev Environment

- Mac: type `git` at command line to prompt developer tools install
- Arch (generic): TODO
- Manjaro: `pamac install base-devel`
- Debian:
  - update /etc/apt/sources.list - add 'contrib'
  - ```
    sudo apt update
    sudo apt upgrade
    sudo apt-get install build-essentials
    ```
- Rust: Install via script, see: https://www.rust-lang.org/learn/get-started
  - Linux/Mac to Windows: `rustup target add x86_64-pc-windows-gnu`
    - If on linux you may need: `sudo apt-get install gcc-mingw-w64`
  - Linux to Mac: TBD - not great support
  - Linux/Mac to WASM: `rustup target add wasm32-unknown-unknown`
- Ollama setup moved to `~/projects/local-llm/docs/ollama.md` (see [ollama.md](../../docs/ollama.md))

## Sync System Files

- see code in [src](../src/main.rs) - `cargo run`
- sensitive files stored in s3
- s3sync
  - in XFCE, session and startup, application autostart: `/usr/local/bin/s3sync --config /home/jeppson/.config/sync.yaml` triggered on login

## Integration

### SSH

- Install and enable SSH server
  - `sudo pacman -S openssh`
  - `sudo systemctl enable --now sshd`
- Copy/download existing key pairs or generate key `ssh-keygen -t ed25519`
- Upload public key to s3://darrenjeppson.com/static/clients/{hostname}.pub
- Download public keys for systems that will login to this one (to ~/.ssh)
  - https://static.darrenjeppson.com/clients/jeppmini.pub
  - https://static.darrenjeppson.com/clients/jeppair.pub
  - https://static.darrenjeppson.com/clients/dj7900.pub
- Add the public keys to `~/.ssh/authorized_keys`

### Streaming Audio

- Mac: server running and listening on port
- Linux:
  - See if setup should be based on pipewire, otherwise
  - See [Linux Audio](./audio.md) setup
  - then config default-server to point to mac, reboot, test audio

### Steam

- Install Steam
- Install, play, quit, re-play Valheim see [linux-gpu.md](linux-gpu.md) for GPU issues

### AWS

- Install awscli
- Create/verify IAM user (hostname)
- Create/rotate and upload AWS credentials
- Get config and credentials from `s3://djeppson/secrets/.aws/` or Configure profile with `aws configure`

### Homebrew

- Install [homebrew](https://brew.sh/)
- Follow instructions to set in path
- `brew install gcc`

## [cargo backup](https://crates.io/crates/cargo-backup/0.4.1)

- prereq: `sudo pacman -Sy gcc` or `sudo apt-get install build-essential`
- install: `cargo install cargo-backup`
- restore: `cargo restore --backup ~/projects/notes/config/.cargo/backup.json`
- update backup file: `cargo backup --out ~/projects/notes/config/.cargo/backup.json`
- Get a listing of installed crate names (`jq '[.[].name]' ~/.cargo/backup.json `)

## DarDNS

Compile from source

```
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:djeppson/dardns-client.git
cd dardns-client
cargo build --release

mkdir -p ~/.dardns
cp target/release/dardns-client ~/.dardns/dardns-client
```

Setup environment file ~/.dardns/env with credentials for user named the same as the DNS entry (e.g., `foo.darrenjeppson.com`)

```
AWS_ACCESS_KEY_ID="AKIAEXAMPLE..."
AWS_SECRET_ACCESS_KEY="..."
AWS_REGION="us-west-2"
HEARTBEAT_DOMAIN_NAME="api.dardns.darrenjeppson.com"
```

Add schedule to crontab: `* * * * * /home/jeppson/.dardns/dardns-client`

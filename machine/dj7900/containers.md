# Podman

Excellent write-up: https://betterstack.com/community/guides/scaling-docker/podman-vs-docker/

Arch:

- Install: `sudo pacman -Syu podman` (Manjaro: `pamac install podman podman-docker crun`)
- Configure: see https://podman.io/docs/installation#configuration-files
- Setup and run cockpit: `pamac install cockpit-podman`

## Run at startup

- Guided by [quadlets](https://mo8it.com/blog/quadlet/)
- Using https://github.com/containers/podlet
- Reference: https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html#container-units-container

### Misc:

May not be necessary but had issues with "port already assigned" kinds of errors with the current default "pasta" network manager.

- install slirp4netns
- modify `sudo vi /etc/containers/containers.conf`
- change default_rootless_network_cmd to "slirp4netns"

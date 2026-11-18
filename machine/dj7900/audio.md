Linux Audio
============================================
* Apple Music via [Cider](https://cider.sh/) (or fallback to [Web player](https://music.apple.com/us/new))
* Stream from Mac to linux (WIP)
  * What does *not* work: headphones from mac to line-in on PC (awful feedback, super loud, even using USB audio out) `pactl load-module module-loopback`
  * What sorta worked at least once: [SonoBus](https://github.com/sonosaurus/sonobus): very quiet sound, req. blackhole on mac, not ideal for direct network connections


Scarlett Solo
--------------------------------------------
Loads and seems to allow control (turn on/off features) not sure how to "route" sound

See: https://github.com/geoffreybennett/alsa-scarlett-gui 
* Dependencies: `sudo pacman -S gtk4`
* Install from source:
  ```
  git clone https://github.com/geoffreybennett/alsa-scarlett-gui
  cd alsa-scarlett-gui/src
  make -j4
  ```

Troubleshooting
--------------------------------------------
When client is playing at high-speed via eqMac
1. On the server: `pactl exit`
2. On the client: make sure the right output is selected/active (may need to toggle between it and another source for some reason)
3. On the client: play some audio to test output

If the high-speed issue isn't getting better, switch to the non-eqMac modified output

Streaming linux audio to mac
--------------------------------------------

### Listener/Receiver Setup

Installation via Homebrew
```
brew install pulseaudio
brew services restart pulseaudio
```

listen for connections from local addresses:
* determine the correct 'sink' (where audio should be played on server):
    * `pactl list sinks` (Note: Sink numbers may not be consistent, use name instead)
* one-time run commands using pactl: 
    * `pactl load-module module-native-protocol-tcp auth-ip-acl=192.168.7.0/24`
    * `pactl set-default-sink Channel_1__Channel_2.2` 
* permanent: include commands in `/opt/homebrew/etc/pulse/default.pa`

Verify listening and on which port
`lsof -i -P | grep -i "pulse"`

see:
* `~/.config/pulse/` for install files
* `/opt/homebrew/etc/pulse` for config


### Streamer/Player Setup

One time test: 
`export PULSE_SERVER={ipaddress of listener}`
`speaker-test`

Durable at boot: /etc/pulse/client.conf
`default-server = {ipaddress of listener}`


References
--------------------------------------------

* https://medium.com/@cristianduguet/play-remote-audio-over-an-ssh-connection-with-a-mac-client-9b7135dfe129
* https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/Modules/#module-native-protocol-unixtcp
* https://gist.github.com/xarinatan/c415341ff34eab445cfb073988dcf6c1
* https://wiki.archlinux.org/title/PulseAudio/Examples



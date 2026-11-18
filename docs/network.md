## Secure/Private DNS

- Setup Quad9 on the Unifi controller (https://docs.quad9.net/) - CyberSecure > Protection > Encrypted DNS:
  - Quad9-dnscrypt-{ipv4|ipv6}-filter-pri
  - Quad9-doh-{ipv4|ipv6}-port443-filter-pri
- Verify use of Quad9 DNS: https://on.quad9.net/
- Verify use of DNS over HTTPS/TLS: `dig +short txt proto.on.quad9.net.`

## Site-to-site VPN (Fox/Starlight)

- The gateway requires a WAN IP address and shows a warning since the address is via DHCP
- Created a "custom" DDNS entry on both Fox and Starlight pointing to an "echo" function (dardns repo/mgmt account)
- **TODO:** Determine how the API is expected to work (what does Unifi send in and expect back?)
  - There is no traffic to the function yet
  - I assume the gateway does not send an update until the address changes (may be weeks, months ...)
- Why not use Unifi Official Hosting
  - Costs $17.75/mo more than my current AWS hosting ($12.25/mo vs. $30+/mo)
  - More "lock-in" to their roadmap (e.g., required upgrades, shifting costs)
  - Prevents me from being able to turn-off the controller (if I want to save more money)
- Why not use Cloud Gateways
  - Requires giving their cloud "remote access" to our network/home otherwise ...
    - VPN maintenance/changes/issues would block my access to remote sites
    - I would not get notifications when the Gateway/Internet goes down
  - More likely to eventually require forced upgrades/planned obsolescence
  - I am most comfortable with securing AWS resources (and it is practice/nerd-fun)
  - No significant need for LAN-only management access when the Internet is down
  - Can't return the UXGs (Fox: 11/2025, Starlight: 1/2026) and "just-in-case" backup hardware is wasteful

## Remote access to unifi

- Using WireGuard client on iOS to Fox or Starlight

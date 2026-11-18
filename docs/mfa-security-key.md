# Yubikey setup

These hardware tokens augment (or replace) other MFA/2FA methods like authenticator apps (see [mfa-totp.md](./mfa-totp.md)).

Keys:

- Home: Yubikey 5C Nano
- Mobile: Yubikey Security Key C-NFC
- Recovery/Off-site: Yubikey Security Key C-NFC

| Account          | Token                                 | Notes                   |
| ---------------- | ------------------------------------- | ----------------------- |
| DJ7900 Linux     | \* home<br/>\* mobile<br/>\* off-site | Login                   |
| AWS main account | \* home<br/>\* mobile<br/>\* off-site | Root and main user MFA  |
| Google           | \* home<br/>\* mobile<br/>\* off-site |                         |
| iCloud           | \* home<br/>\* mobile<br/>\* off-site |                         |
| GitHub           | \* home<br/>\* mobile<br/>\* off-site |                         |
| Unifi            | \* home<br/>\* mobile<br/>\* off-site |                         |
| Discord          | \* home                               |                         |
| ID.me            | \* home                               | keith.jeppson@gmail.com |

## Test

- Yubico: https://demo.yubico.com/webauthn-technical/registration
- Mozilla: https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API#examples

## Manjaro

- Refs:
  - Details on PAM: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/6/html/managing_smart_cards/pam_configuration_files#pam-modules
  - https://developers.yubico.com/Developer_Program/Guides/Touch_triggered_OTP.html
  - As of 2024-11-18 you cannot use u2f keys for AWS CLI access: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa_configure-api-require.html#MFAProtectedAPI-important-points
- Guides
  - I wish I saw earlier: https://github.com/adambhun/yubikey-setup-on-manjaro-kde
  - Setting up MFA in AWS CLI (Not fully setup): https://medium.com/@sergiu.savva/simplify-your-aws-cli-experience-with-mfa-a-handy-bash-script-940d8517ad4d
  - Initial blog, most of the sudo setup: https://credibledev.com/easy-setup-yubikey-on-manjaro-linux/
  - Useful for setting up system-auth: https://devblog.jpcaparas.com/use-your-yubikey-as-a-system-level-authentication-pam-module-on-fedora-40-457ae7375254

### Login/Sudo Instructions

- In window 1 (backup window): `sudo -s` (get in as root in case of weirdness)
- Leave the backup window open in case of issues
- In window 2:

(note: seems like the folder _must_ use a capital Y)

```
sudo pacman -S autoconf automake libtool pkg-config libfido2 pam-u2f
mkdir -p ~/.config/Yubico
pamu2fcfg >> ~/.config/Yubico/u2f_keys
# key should be blinking, touch it for the command to finish
# do this for each key if you have multiple

sudo vi /etc/pam.d/sudo
# add the line to the beginning (sufficient makes order dependent)
#   auth sufficient pam_u2f.so cue [cue_prompt=Tap your Yubikey]
```

To use system-wide (i.e., in GUI windows and such)

```
sudo vi /etc/pam.d/system-auth
# add to the beginning
#   auth       required                    pam_env.so
#   auth       required                    pam_faildelay.so delay=2000000
#   auth       sufficient                  pam_u2f.so cue
#   auth       sufficient                  pam_unix.so nullok
#   auth       required                    pam_deny.so
```

### Authenticator App

- Home page: https://developers.yubico.com/yubioath-flutter/
- Linux Permission Info: https://developers.yubico.com/yubikey-manager/Device_Permissions.html
  - Detail on permissions: https://github.com/Yubico/yubikey-personalization/tree/master?tab=readme-ov-file#using

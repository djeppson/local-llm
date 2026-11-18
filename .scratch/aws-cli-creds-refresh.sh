#!/usr/bin/env bash
#
# aws-cli-creds-refresh.sh — refresh AWS SSO creds for the session host
# (dj7900) by completing the browser sign-in from this Mac.
#
#   Run this from a terminal ON THE MAC (a Zed terminal or iTerm).
#
# Flow
#   1. Start `aws sso login --no-browser --profile $PROFILE` in the
#      background on dj7900 (over ssh). It prints an auth URL and listens
#      on 127.0.0.1:<random-port> for the OAuth callback.
#   2. Open an ssh tunnel from the Mac:
#         127.0.0.1:<port>  --ssh-->  dj7900:127.0.0.1:<port>
#   3. You open the auth URL in the Mac's browser and complete sign-in
#      (incl. MFA). The browser's final redirect to 127.0.0.1:<port> then
#      reaches dj7900's callback server through the tunnel, and the token
#      is cached on dj7900 (~/.aws sso cache + cli cache).
#
# Security model (deliberate)
#   The unattended host can never mint credentials on its own: the OAuth
#   loop only completes when a human, physically at this Mac, does the
#   browser sign-in. Same reasoning as the hardware key gating privileged
#   remote execution — local presence is the credential.
#
# Usage
#   aws-cli-creds-refresh.sh            # opens the auth URL in the default browser
#   aws-cli-creds-refresh.sh --no-open  # print the URL only; open it yourself
#
# Prereqs: key-based ssh from the Mac to SSH_TARGET; macOS `open`
# (optional — the URL is always printed). No other dependencies.

set -euo pipefail

SSH_TARGET="jeppson@dj7900-local.darrenjeppson.com"  # TODO confirm ssh user
PROFILE="djeppson"
WAIT_SECS=600                       # SSO budget for the pending auth
HOSTNAME_HINT="dj7900"              # refuse to run ON the session host
WORK_FILE="/tmp/aws-cli-creds-refresh.out"  # on dj7900

OPEN_BROWSER=1
if [ "${1:-}" = "--no-open" ]; then OPEN_BROWSER=0; fi

say() { printf '\n\033[1m==> %s\033[0m\n' "$*" >&2; }
die() { say "ERROR: $*"; exit 1; }

# ssh options shared by every leg: non-interactive, bounded connect timeout
REMOTE="ssh -n -o BatchMode=yes -o ConnectTimeout=10 $SSH_TARGET"

# --- sanity ---------------------------------------------------------------
case "$(hostname 2>/dev/null)" in
  *"$HOSTNAME_HINT"*)
    die "this looks like the session host ($HOSTNAME_HINT) — run this script on the MAC"
    ;;
esac
command -v ssh >/dev/null 2>&1 || die "ssh not found in PATH"

# --- cleanup: kill tunnel, drop the remote work file -----------------------
TUNNEL_PID=""
cleanup() {
  if [ -n "$TUNNEL_PID" ]; then
    kill "$TUNNEL_PID" 2>/dev/null || true
    wait "$TUNNEL_PID" 2>/dev/null || true
  fi
  ssh -n -o BatchMode=yes -o ConnectTimeout=5 "$SSH_TARGET" \
      "rm -f '$WORK_FILE'" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# --- 1. start the login on dj7900, wait for the auth URL -------------------
say "starting 'aws sso login --no-browser --profile $PROFILE' on $SSH_TARGET..."
$REMOTE "rm -f '$WORK_FILE'
  pkill -f '[a]ws sso login' 2>/dev/null
  nohup aws sso login --no-browser --profile '$PROFILE' >'$WORK_FILE' 2>&1 &
  echo ok" >/dev/null

URL_LOG=""
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do   # ~20 s grace
  URL_LOG="$($REMOTE "cat '$WORK_FILE' 2>/dev/null" || true)"
  case "$URL_LOG" in *"https://"*) break ;; esac
  sleep 1
done

AUTH_URL="$(printf '%s\n' "$URL_LOG" | grep -oE 'https://[^ ]+' | head -n1)"
PORT="$(printf '%s\n' "$URL_LOG" \
  | grep -oE '127\.0\.0\.1(%3A|:)[0-9]+' | head -n1 | grep -oE '[0-9]+$' || true)"
if [ -z "$AUTH_URL" ] || [ -z "$PORT" ]; then
  say "could not find the auth URL / callback port; remote log so far:"
  printf '%s\n' "$URL_LOG" >&2
  exit 1
fi

# --- 2. tunnel: Mac 127.0.0.1:$PORT -> dj7900 127.0.0.1:$PORT ---------------
say "tunnel: Mac 127.0.0.1:$PORT -> $SSH_TARGET:127.0.0.1:$PORT"
ssh -N -o BatchMode=yes -o ExitOnForwardFailure=yes -o ConnectTimeout=10 \
    -L "$PORT:127.0.0.1:$PORT" "$SSH_TARGET" >/dev/null 2>&1 &
TUNNEL_PID=$!
sleep 1
kill -0 "$TUNNEL_PID" 2>/dev/null \
  || die "tunnel failed to start (port $PORT busy on the Mac? old tunnel still up?)"

# --- 3. browser step (you, on the Mac) -------------------------------------
say "complete sign-in (incl. MFA) in the browser at:"
printf '%s\n' "$AUTH_URL"
if [ "$OPEN_BROWSER" = 1 ] && command -v open >/dev/null 2>&1; then
  open "$AUTH_URL" 2>/dev/null || true   # best effort; URL was printed above
fi
say "waiting up to ${WAIT_SECS}s for the login to complete on dj7900..."

# --- 4. wait for the remote login process to finish --------------------------
end=$(( $(date +%s) + WAIT_SECS ))
timed_out=0
while :; do
  if ! $REMOTE "pgrep -f '[a]ws sso login' >/dev/null 2>&1"; then
    break
  fi
  if [ "$(date +%s)" -ge "$end" ]; then timed_out=1; break; fi
  sleep 2
done
[ "$timed_out" = 0 ] \
  || die "timed out after ${WAIT_SECS}s (the pending auth likely expired) — just re-run this script"

# --- 5. verify ---------------------------------------------------------------
say "verifying credentials on dj7900..."
id_json="$($REMOTE "aws sts get-caller-identity --profile '$PROFILE' --output json 2>&1" || true)"
if printf '%s' "$id_json" | grep -q '"Account"'; then
  account="$(printf '%s' "$id_json" | grep -oE '"Account": ?"[0-9]+"' | grep -oE '[0-9]+' | head -n1)"
  say "OK — profile '$PROFILE' is live on $SSH_TARGET (account $account)"
  say "the AWS MCP proxy on dj7900 picks up the refreshed credentials automatically — carry on in Zed"
else
  say "sts check failed; tail of the remote login log:"
  $REMOTE "tail -n 8 '$WORK_FILE'" 2>/dev/null || true
  exit 1
fi

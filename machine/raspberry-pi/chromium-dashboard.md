# These are prior directions

1. SSH into the remote system (e.g., Raspberry Pi connected to monitor)
1. (optional) Create a file with the URL you want to connect to
1. `DISPLAY=:0 chromium --kiosk --app=$(cat ~/Desktop/dashboard-link.txt) &` (end ampersand to run in background)
1. Logout

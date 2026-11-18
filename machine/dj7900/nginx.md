Setup a proxy to send `http://localhost` to `http://localhost:9000/lambda-url/web` (for example) to simplify serving things with cargo lambda

* Install: `sudo install apt-get nginx` or `pamac install nginx`
* Enable: `systemctl enable nginx`
* Status: `systemctl status nginx`
* Reload: `sudo nginx -s reload` (detect config changes)



Default setup:

* Static files served in `/var/www/html`

Cargo Lambda setup (default port, assume binary named 'web'):

* **/etc/nginx/sites-enabled/default**
    ```
    server {
        listen 80 default_server;
        listen [::]:80 default_server;

        location / {
            proxy_pass http://127.0.0.1:9000/lambda-url/web/;
        }

        location /assets/ {
            # First attempt to serve request as file, then
            # as directory, then fall back to displaying a 404.
            try_files $uri $uri/ =404;
        }
    }
    ```
* Create the assets directory (e.g., `sudo mkdir -p /var/www/html/assets`)
* Hard-link to the desired files (e.g., `ln ~/projects/valheim/assets/site.css .`)

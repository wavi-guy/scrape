curl http://127.0.0.1:5000
curl  http://127.0.0.1:9000
source venv/bin/activate
curl  http://127.0.0.1:9000
curl http://127.0.0.1:5000
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y nginx git curl ufw
python3 --version
pip3 --version
nginx -v
ls
mv flask-pole-app/ helps/
ls
cd /home/ubuntu/helps
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-prod.txt 
pip list | grep Flask
source venv/bin/activate
python3 app.py
source venv/bin/activate
pip install gunicorn
mkdir -p logs
cat > gunicorn.conf.py << 'EOF'

# Gunicorn configuration file

import multiprocessing



# Server socket

bind = "127.0.0.1:5000"

backlog = 2048



# Worker processes

workers = multiprocessing.cpu_count() * 2 + 1

worker_class = "sync"

worker_connections = 1000

timeout = 30

keepalive = 2



# Logging

errorlog = "/home/ubuntu/helps/logs/gunicorn_error.log"

accesslog = "/home/ubuntu/helps/logs/gunicorn_access.log"

loglevel = "info"



# Process naming

proc_name = "flask_helps_app"



# Server mechanics

daemon = False

pidfile = "/home/ubuntu/helps/gunicorn.pid"

user = "ubuntu"

group = "ubuntu"



# Restart workers after handling this many requests

max_requests = 1000

max_requests_jitter = 100

EOF

more gunicorn.conf.py 
gunicorn --config gunicorn.conf.py wsgi:application
sudo tee /etc/systemd/system/flask-helps.service > /dev/null << 'EOF'

[Unit]

Description=Gunicorn instance to serve Flask Helps App

After=network.target



[Service]

User=ubuntu

Group=ubuntu

WorkingDirectory=/home/ubuntu/helps

Environment="PATH=/home/ubuntu/helps/venv/bin"

Environment="FLASK_ENV=production"

Environment="SECRET_KEY=f35429ec195e970156e1f71cff768828bfce18042d4d172a1522c1098f8a319e"

ExecStart=/home/ubuntu/helps/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application

ExecReload=/bin/kill -s HUP $MAINPID

KillMode=mixed

TimeoutStopSec=5

PrivateTmp=true

Restart=always

RestartSec=3



[Install]

WantedBy=multi-user.target

EOF

sudo systemctl daemon-reload
sudo systemctl enable flask-helps
sudo systemctl start flask-helps
sudo systemctl status flask-helps
curl http://127.0.0.1:5000
sudo tee /etc/nginx/sites-available/flask-helps > /dev/null << 'EOF'

server {

    listen 80 default_server;

    listen [::]:80 default_server;

    

    server_name _;

    

    location / {

        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Proto $scheme;

        

        # Connection settings

        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;

        proxy_set_header Connection "upgrade";

        

        # Timeouts

        proxy_connect_timeout 60s;

        proxy_send_timeout 60s;

        proxy_read_timeout 60s;

        proxy_buffering off;

    }

    

    # Static files (if you have any)

    location /static/ {

        alias /home/ubuntu/helps/static/;

        expires 1y;

        add_header Cache-Control "public, immutable";

    }

    

    # Basic security headers

    add_header X-Frame-Options "SAMEORIGIN" always;

    add_header X-XSS-Protection "1; mode=block" always;

    add_header X-Content-Type-Options "nosniff" always;

}

EOF

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/flask-helps /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx
curl http://localhost
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
curl -s ifconfig.me
echo
sudo systemctl status flask-helps nginx --no-pager
curl http://localhost
curl -X POST -H "Content-Type: application/json" http://localhost/create_pole
curl -X POST -H "Content-Type: application/json" http://localhost/
curl -X POST -H "Content-Type: application/json" http://localhost/helps
curl -X POST -H "Content-Type: application/json" http://localhost/helps/
sudo systemctl status flask-helps nginx
sudo journalctl -u flask-helps -n 20
curl -s ifconfig.me
echo
sudo tee /etc/nginx/sites-available/flask-helps > /dev/null << 'EOF'

server {

    listen 80 default_server;

    listen [::]:80 default_server ipv6only=on;

    

    server_name _;

    

    location / {

        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Proto $scheme;

        

        # Connection settings

        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;

        proxy_set_header Connection "upgrade";

        

        # Timeouts

        proxy_connect_timeout 60s;

        proxy_send_timeout 60s;

        proxy_read_timeout 60s;

        proxy_buffering off;

    }

    

    # Static files (if you have any)

    location /static/ {

        alias /home/ubuntu/helps/static/;

        expires 1y;

        add_header Cache-Control "public, immutable";

    }

    

    # Basic security headers

    add_header X-Frame-Options "SAMEORIGIN" always;

    add_header X-XSS-Protection "1; mode=block" always;

    add_header X-Content-Type-Options "nosniff" always;

}

EOF

sudo nginx -t
sudo systemctl reload nginx
sudo ufw --force enable
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw status verbose
curl http://localhost
curl -g "http://[2406:da14:1d0f:9400:10a5:b902:8ddc:71df]"
curl -4 ifconfig.me
ip addr show | grep "inet " | grep -v "127.0.0.1"
curl -4 ipinfo.io/ip
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
certbot --version
sudo tee /etc/nginx/sites-available/flask-helps > /dev/null << 'EOF'

server {

    listen 80;

    listen [::]:80;

    

    server_name helps.team www.helps.team;

    

    location / {

        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Proto $scheme;

        

        # Connection settings

        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;

        proxy_set_header Connection "upgrade";

        

        # Timeouts

        proxy_connect_timeout 60s;

        proxy_send_timeout 60s;

        proxy_read_timeout 60s;

        proxy_buffering off;

    }

    

    # Static files

    location /static/ {

        alias /home/ubuntu/helps/static/;

        expires 1y;

        add_header Cache-Control "public, immutable";

    }

    

    # Security headers

    add_header X-Frame-Options "SAMEORIGIN" always;

    add_header X-XSS-Protection "1; mode=block" always;

    add_header X-Content-Type-Options "nosniff" always;

}

EOF

sudo nginx -t
sudo systemctl reload nginx
nslookup helps.team
dig helps.team A
dig helps.team AAAA
curl http://helps.team
sudo ufw allow 443
sudo certbot --nginx -d helps.team -d www.helps.team
sudo certbot renew --dry-run
sudo systemctl status certbot.timer
sudo systemctl list-timers | grep certbot
curl https://helps.team
curl https://www.helps.team
curl -I http://helps.team
openssl s_client -connect helps.team:443 -servername helps.team
curl -I https://www.ssllabs.com/ssltest/analyze.html?d=helps.team
sudo ufw allow 443
sudo certbot --nginx -d helps.team -d www.helps.team
curl https://helps.team
curl -I http://helps.team
sudo tee /etc/nginx/sites-available/flask-helps > /dev/null << 'EOF'

server {

    listen 80;

    listen [::]:80;

    

    # Accept both domain names AND IP address

    server_name helps.team www.helps.team 54.95.1.0 _;

    

    location / {

        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Proto $scheme;

        

        # Connection settings

        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;

        proxy_set_header Connection "upgrade";

        

        # Timeouts

        proxy_connect_timeout 60s;

        proxy_send_timeout 60s;

        proxy_read_timeout 60s;

        proxy_buffering off;

    }

    

    # Static files

    location /static/ {

        alias /home/ubuntu/helps/static/;

        expires 1y;

        add_header Cache-Control "public, immutable";

    }

    

    # Security headers

    add_header X-Frame-Options "SAMEORIGIN" always;

    add_header X-XSS-Protection "1; mode=block" always;

    add_header X-Content-Type-Options "nosniff" always;

}

EOF

sudo nginx -t
sudo systemctl reload nginx
curl http://54.95.1.0/
curl https://54.95.1.0/
curl -k https://54.95.1.0/
curl --insecure https://54.95.1.0/
sudo tee /etc/nginx/sites-available/flask-helps > /dev/null << 'EOF'

# HTTP server for both domain and IP

server {

    listen 80;

    listen [::]:80;

    

    server_name helps.team www.helps.team 54.95.1.0 _;

    

    # Redirect domain HTTP to HTTPS, but allow IP HTTP

    if ($host ~ ^(helps\.team|www\.helps\.team)$) {

        return 301 https://$host$request_uri;

    }

    

    location / {

        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Proto $scheme;

        

        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;

        proxy_set_header Connection "upgrade";

        

        proxy_connect_timeout 60s;

        proxy_send_timeout 60s;

        proxy_read_timeout 60s;

        proxy_buffering off;

    }

}



# HTTPS server for domain only

server {

    listen 443 ssl http2;

    listen [::]:443 ssl http2;

    

    server_name helps.team www.helps.team;

    

    # SSL certificate paths (will be added by Certbot)

    # ssl_certificate /etc/letsencrypt/live/helps.team/fullchain.pem;

    # ssl_certificate_key /etc/letsencrypt/live/helps.team/privkey.pem;

    

    location / {

        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Proto $scheme;

        

        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;

        proxy_set_header Connection "upgrade";

        

        proxy_connect_timeout 60s;

        proxy_send_timeout 60s;

        proxy_read_timeout 60s;

        proxy_buffering off;

    }

}

EOF

sudo nginx -t
sudo tee /etc/nginx/sites-available/flask-helps > /dev/null << 'EOF'

server {

    listen 80;

    listen [::]:80;

    

    server_name helps.team www.helps.team 54.95.1.0 _;

    

    location / {

        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Proto $scheme;

        

        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;

        proxy_set_header Connection "upgrade";

        

        proxy_connect_timeout 60s;

        proxy_send_timeout 60s;

        proxy_read_timeout 60s;

        proxy_buffering off;

    }

    

    # Static files

    location /static/ {

        alias /home/ubuntu/helps/static/;

        expires 1y;

        add_header Cache-Control "public, immutable";

    }

    

    # Security headers

    add_header X-Frame-Options "SAMEORIGIN" always;

    add_header X-XSS-Protection "1; mode=block" always;

    add_header X-Content-Type-Options "nosniff" always;

}

EOF

sudo tee /etc/nginx/sites-available/flask-helps > /dev/null << 'EOF'

server {

    listen 80;

    listen [::]:80;

    

    server_name helps.team www.helps.team 54.95.1.0 _;

    

    location / {

        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Proto $scheme;

        

        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;

        proxy_set_header Connection "upgrade";

        

        proxy_connect_timeout 60s;

        proxy_send_timeout 60s;

        proxy_read_timeout 60s;

        proxy_buffering off;

    }

    

    # Static files

    location /static/ {

        alias /home/ubuntu/helps/static/;

        expires 1y;

        add_header Cache-Control "public, immutable";

    }

    

    # Security headers

    add_header X-Frame-Options "SAMEORIGIN" always;

    add_header X-XSS-Protection "1; mode=block" always;

    add_header X-Content-Type-Options "nosniff" always;

}

EOF

sudo tee /etc/nginx/sites-available/flask-helps > /dev/null << 'EOF'

server {

    listen 80;

    listen [::]:80;

    

    server_name helps.team www.helps.team 54.95.1.0 _;

    

    location / {

        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Proto $scheme;

        

        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;

        proxy_set_header Connection "upgrade";

        

        proxy_connect_timeout 60s;

        proxy_send_timeout 60s;

        proxy_read_timeout 60s;

        proxy_buffering off;

    }

    

    # Static files

    location /static/ {

        alias /home/ubuntu/helps/static/;

        expires 1y;

        add_header Cache-Control "public, immutable";

    }

    

    # Security headers

    add_header X-Frame-Options "SAMEORIGIN" always;

    add_header X-XSS-Protection "1; mode=block" always;

    add_header X-Content-Type-Options "nosniff" always;

}

EOF

sudo tee /etc/nginx/sites-available/flask-helps > /dev/null << 'EOF'

server {

    listen 80;

    listen [::]:80;

    

    server_name helps.team www.helps.team 54.95.1.0 _;

    

    location / {

        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Proto $scheme;

        

        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;

        proxy_set_header Connection "upgrade";

        

        proxy_connect_timeout 60s;

        proxy_send_timeout 60s;

        proxy_read_timeout 60s;

        proxy_buffering off;

    }

    

    # Static files

    location /static/ {

        alias /home/ubuntu/helps/static/;

        expires 1y;

        add_header Cache-Control "public, immutable";

    }

    

    # Security headers

    add_header X-Frame-Options "SAMEORIGIN" always;

    add_header X-XSS-Protection "1; mode=block" always;

    add_header X-Content-Type-Options "nosniff" always;

}

EOF

sudo nginx -t
sudo systemctl reload nginx
curl http://helps.team/
curl http://54.95.1.0/
sudo certbot --nginx -d helps.team -d www.helps.team
curl http://helps.team/  
curl https://helps.team/ 
sudo cat /etc/nginx/sites-available/flask-helps
curl https://helps.team/ 
sudo systemctl restart flask-helps
ls
gzip
tar -czf flask-pole-app-backup-$(Get-Date -Format 'yyyy-MM-dd').tar.gz -C c:\ flask-pole-app
cd ..
ks
ls
tar -czf flask-pole-app-backup-$(Get-Date -Format 'yyyy-MM-dd').tar.gz -C helps/
tar -czf helps-backup-$(date +%Y-%m-%d).tar.gz helps/
ls
sudo systemctl restart flask-helps
history
more /etc/nginx/sites-available/flask-helps
cd helps/
ls
pip install -r requirements.txt
sudo pip install -r requirements.txt
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart flask-helps
sudo pkill -f gunicorn
gunicorn --config gunicorn_config.py wsgi:application
sudo systemctl restart helps-team.service
sudo systemctl restart flask-helps
sudo systemctl reload nginx
sudo systemctl restart flask-helps
curl http://helps.team/
curl -I https://helps.team/
sudo nginx -t
sudo systemctl reload nginx
curl http://helps.team/
sudo systemctl status flask-helps
sudo systemctl daemon-reload
sudo systemctl enable flask-helps
sudo systemctl start flask-helps
sudo systemctl status flask-helps
curl http://127.0.0.1:5000
ls /etc/nginx/sites-available
cat /etc/nginx/sites-available/flask-helps 
sudo nano /etc/nginx/sites-available/flask-helps
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl restart flask-app.service
sudo systemctl restart flask.helps
sudo systemctl restart flask-helps
curl http://localhost:9000/
curl -I https://helps.team/
systemctl enable flask-helps
sudo systemctl enable flask-helps
sudo sudo systemctl status flask-helps
sudo systemctl status flask-helps
sudo journalctl -u flask-helps --no-pager -n 50
pip install -r requirements.txt
sudo systemctl restart flask-helps
cd ~/helps
source venv/bin/activate
python -c "import flask_socketio; print('SocketIO OK')"
sudo systemctl cat flask-helps
python app.py
sudo ss -tlnp | grep python
sudo journalctl -u flask-helps -f
sudo systemctl stop flask-helps
nano wsgi.py
sudo systemctl stop flask-helps
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl start flask-helps
sudo systemctl status flask-helps
curl http://localhost:9000/
sudo journalctl -u flask-helps --no-pager -n 20
sudo journalctl -u flask-helps --no-pager -n 50 | grep -A 10 -B 10 "App failed to load"
sudo systemctl stop flask-helps
python -c "from flask_socketio import SocketIO; print('SocketIO OK')"
python -c "from app import app, socketio; print('App imports OK')"
python app.py
source venv/bin/activate
cd helps/
source venv/bin/activate
pip install -r requirements.txt
python app.py
cat ~/helps/gunicorn_config.py
nano gunicorn_config.py
grep -E "(bind|worker_class)" gunicorn_config.py
source venv/bin/activate
gunicorn --config gunicorn_config.py wsgi:application
ls
sudo lsof -i :9000
curl http://localhost:9000/
cd helps/
source venv/bin/activate
curl http://127.0.0.1:9000
n
Error: class uri 'eventlet' invalid or not found: 
[Traceback (most recent call last):
7, in <module>
e 4, in <module>
4, in <module>
in <module>
n <module>
ine 7, in <module>
, line 6, in <module>
ModuleNotFoundError: No module named 'distutils'
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
in load_class
pip install --upgrade eventlet>=0.33.3
pip install gevent
source venv/bin/activate
pip install -r requirements.txt
sed -i 's/worker_class = "sync"/worker_class = "gevent"/' gunicorn_config.py
grep worker_class gunicorn_config.py
nano gunicorn_config.py 
grep worker_class gunicorn_config.py
gunicorn --config gunicorn_config.py wsgi:application
source venv/bin/activate
gunicorn --config gunicorn_config.py wsgi:application
sudo systemctl restart flask-helps
curl http://localhost:9000/
gunicorn --config gunicorn_config.py wsgi:application
sudo systemctl stop flask-helps
sudo pkill -f gunicorn
rm -f /home/ubuntu/helps/gunicorn.pid
sudo ss -tlnp | grep :9000
sudo systemctl stop flask-helps
sudo pkill -f gunicorn
source venv/bin/activate
gunicorn --config gunicorn_config.py wsgi:application
sudo systemctl start flask-helps
sudo systemctl status flask-helps
sudo ss -tlnp | grep :9000
source venv/bin/activate
gunicorn --bind 127.0.0.1:9000 --workers 1 wsgi:application
sudo systemctl stop flask-helps
sudo pkill -f gunicorn
sudo systemctl start flask-helps
sudo systemctl status flask-helps
grep -n "proxy_pass" /etc/nginx/sites-available/flask-helps
python app.py
source venv/bin/activate
pip install gevent-websocket
sudo systemctl stop flask-helps
sudo pkill -f gunicorn
rm -f /home/ubuntu/helps/gunicorn.pid
sudo systemctl start flask-helps
sudo systemctl status flask-helps
curl http://localhost:9000/
sudo journalctl -u flask-helps --no-pager -n 20
clear
sudo journalctl -u flask-helps --no-pager -n 20
sudo journalctl -u flask-helps --no-pager -n 40
source venv/bin/activate
gunicorn --log-level debug --bind 127.0.0.1:9000 wsgi:application
cat requirements.txt | grep gevent
python app.py
sudo systemctl cat flask-helps
ls gun*
more gun
more gunicorn.conf.py 
more gunicorn_config.py 
mv gunicorn_config.py gunicorn.conf.py
ls gun*
ls -la gunicorn.conf.py
sudo systemctl start flask-helps
sudo systemctl status flask-helps
curl http://localhost:9000/
sudo ss -tlnp | grep :9000
ls
ls logs/
ls
cat gunicorn.conf.py 
pip list | grep gevent
ls -la /home/ubuntu/helps/logs/
sudo systemctl status flask-helps
sudo journalctl -u flask-helps --no-pager -n 10
cat /home/ubuntu/helps/logs/gunicorn_error.log
gunicorn --config gunicorn.conf.py wsgi:application
sudo systemctl stop flask-helps
sudo pkill -f gunicorn
rm -f /home/ubuntu/helps/gunicorn.pid
sudo ss -tlnp | grep :9000
ps aux | grep gunicorn
sudo ss -tlnp | grep :9000
source venv/bin/activate
gunicorn --config gunicorn.conf.py wsgi:application
sudo systemctl start flask-helps
sudo ss -tlnp | grep :9000
histort
history
sudo systemctl restart flask-helps
ps aux | grep gunicorn
cd helps/
source venv/bin/activate
pip list | grep gevent
sudo systemctl stop flask-helps
source venv/bin/activate
gunicorn --worker-class gevent --bind 127.0.0.1:9000 --workers 1 wsgi:application
ls /etc/nginx/sites-available
cat /etc/nginx/sites-available/flask-helps 
sudo systemctl restart flask-helps
sudo systemctl restart flask-pole-app
sudo systemctl restart flask-helps
sudo systemctl status flask-helps
sudo netstat -tlnp | grep 9000
sudo journalctl -u flask-helps -n 50
cat /home/ubuntu/helps/wsgi.py
sudo systemctl restart flask-helps
sudo systemctl status flask-helps
sudo systemctl stop flask-helps
/home/ubuntu/helps/venv/bin/gunicorn -c gunicorn.conf.py wsgi:application --log-level debug
gunicorn -c gunicorn.conf.py wsgi:application -
gunicorn -c gunicorn.conf.py wsgi:application --log-level debug
python3 -c "from wsgi import application; print('Application loaded successfully:', type(application))"
python3 -c "import gevent; print('Gevent version:', gevent.__version__)"
/home/ubuntu/helps/venv/bin/gunicorn --bind 127.0.0.1:9000 --worker-class eventlet --workers 1 wsgi:application --log-level debug
sudo apt update
sudo apt install net-tools
sudo netstat -tlnp | grep 9000
sudo systemctl status flask-helps
curl https://helps.team
/home/ubuntu/helps/venv/bin/gunicorn -c gunicorn.conf.py wsgi:application
python3 -c "

from wsgi import application

print('Application type:', type(application))

print('Application callable:', callable(application))

"
cat /home/ubuntu/helps/wsgi.py
python3 -c "

from wsgi import application

print('Application type:', type(application))

print('Application callable:', callable(application))

"
python3 -c "

from wsgi import application

print('Application type:', type(application))

print('Application callable:', callable(application))

"
clear
python3 -c "

from wsgi import application

print('Application type:', type(application))

print('Application callable:', callable(application))

"
source venv/bin/activate
python3 -c "

from wsgi import application

print('Application type:', type(application))

print('Application callable:', callable(application))

"
/home/ubuntu/helps/venv/bin/gunicorn -c gunicorn.conf.py wsgi:application --log-level debug
sudo systemctl restart flask-helps
curl -v "https://helps.team/socket.io/?EIO=4&transport=polling"
sudo systemctl restart flask-helps
history
ls
cd helps
ls
ls -l
ls /etc/systemd/system/help*
ls /etc/systemd/system/
cat /etc/systemd/system/flask-helps.service 
cat gunicorn.conf.py
gunicorn.conf.py cat /etc/nginx/sites-available/flask-helps 
cat /etc/nginx/sites-available/flask-helps 
ls
more =\=0.33.3 
more '=0.33.3'
history
sudo systemctl restart flask-helps
ls
cd helps/
sudo systemctl restart flask-helps
ls
cd ..
mkdir help-back
cd helps
cp -R . ..//help-back/
ls ../help-back/
sudo apt update
sudo apt install git
git config --global user.name "wavi-guy"
git config --global user.email "waviguy@gmail.com"
ssh-keygen -t ed25519 -C "waviguy@gmail.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ls .ssh/
ssh-keygen -t ed25519 -C "waviguy@gmail.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
git init
git remote add origin git@github.com:wavi-guy/helps.team.git
git branch -M master
git fetch origin
git reset --hard origin/master 
ls
ls -l
ls -?
ls --help
ls -lt
cat Install_notes.txt 
sudo systemctl restart flask-helps
chmod +x update.sh
git pull origin master
sudo systemctl restart flask-app.service
sudo systemctl restart flask-helps
git pull origin master
sudo systemctl restart flask-helps
git pull origin master
sudo systemctl restart flask-helps
curl https://www.cryptocraft.com/
clear
nano scrape.sh
ls
chmod +x scrape_table.sh
chmod +x scrape.sh 
./scrape.sh https://www.cryptocraft.com/
pip install selenium beautifulsoup4 webdriver-manager
sudo pip install selenium beautifulsoup4 webdriver-manager
python3 -m venv scraper_env
source scraper_env/bin/activate
pip install playwright beautifulsoup4
playwright install chromium
sudo playwright install-deps 
pip install playwright
playwright install chromium
sudo playwright install-deps
sudo apt-get install libatk-bridge2.0-0t64libcups2t64libatspi2.0-0t64libxcomposite1libxdamage1libxfixes3libxrandr2libgbm1libcairo2libpango-1.0-0libasound2t64
sudo apt-get install libatk-bridge2.0-0t64 libcups2t64 libatspi2.0-0t64 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libcairo2 libpango-1.0-0 libasound2t64
playwright install chromium
pip install selenium beautifulsoup4 webdriver-manager
python -c "
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import sys

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(sys.argv[1])
driver.implicitly_wait(5)
soup = BeautifulSoup(driver.page_source, 'html.parser')
table = soup.find('table', class_='calendar__table calendar__table--no-currency')
print(table if table else 'Table not found')
driver.quit()
" https://www.cryptocraft.com/
python 
sudo apt update
sudo apt install chromium-browser
pip install selenium beautifulsoup4 webdriver-manager
python -c "
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import sys

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(sys.argv[1])
driver.implicitly_wait(5)
soup = BeautifulSoup(driver.page_source, 'html.parser')
table = soup.find('table', class_='calendar__table calendar__table--no-currency')
print(table if table else 'Table not found')
driver.quit()
" https://www.cryptocraft.com/
python -c "
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import sys

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(sys.argv[1])
driver.implicitly_wait(5)
soup = BeautifulSoup(driver.page_source, 'html.parser')
table = soup.find('table', class_='calendar__table calendar__table--no-currency')
print(table if table else 'Table not found')
driver.quit()
" https://www.cryptocraft.com/
ls /snap/bin/ch*
neon scrape.py
nano scrape.py
python scrape.py 
Error: Message: session not created: This version of ChromeDriver only supports Chrome vers                   ion 114
Current browser version is 140.0.7339.185 with binary path /snap/bin/chromium; For document                   ation on this error, please visit: https://www.selenium.dev/documentation/webdriver/trouble                   shooting/errors#sessionnotcreatedexception
pip uninstall selenium webdriver-manager
pip install playwright beautifulsoup4
playwright install chromium
ls
rm scrape.sh
rm scrape.py
mkdir scrape
cd scrape
nano scrape.py
python scrape.py 
rm scrape.py 
nano scrape.py
python scrape.py 
rm scrape.py 
nano scrape.py
python scrape.py 
rm scrape.py 
nano scrape.py
python scrape.py 
rm scrape.py 
nano s.py
python s.py 
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/wavi-guy/scrape.git
git push -u origin main
git remote add origin https://github.com/wavi-guy/scrape.git
git push -u origin main
ls -l
git pull origin main
git branch -a
git push origin master
git remote add origin https://github.com/wavi-guy/scrape.git
git push -u origin main
rm -al .
rm .
ls
ls -l
rm s.py 
ls
git clone https://github.com/wavi-guy/scrape.git
ls
cd scrape/
ls
cd ..
rm -f scrape/
rm -fr scrape/
ls
cd ..
ls
git clone https://github.com/wavi-guy/scrape.git
rm -fr scrape
git clone https://github.com/wavi-guy/scrape.git
cd scrapeq
cd scrape
ls
git pull origin main
ls
python s.py 
more structured_text_20250925_230204.txt 
git pull origin main
python s.py 
git pull origin main
python s.py 
ls
ls -l
git pull origin main
python s.py 
ls
ls -l 
rm structured_text_20250925_230204.txt 
more scraping_error_20250925_231139.txt 
cat scraping_error_20250925_231139.txt 
git pull origin main
python s.py 
ls
echo "alias ll='ls -l'" >> ~/.bashrc
source ~/.bashrc
ll
rm *.txt
ll
python s.py 
ll
cat cryptocraft_content_20250925_231812.txt 
git pull origin main
rm *.txt
python s.py 
ll
more cryptocraft_content_20250925_232310.txt 
add .
git add *.txt
git git commit -m "Update"
git commit -m "Update"
git push
git push -u origin main
ssh -T git@github.com
git remote -v
git remote set-url origin git@github.com:wavi-guy/scrape.git
git push
ll
more cryptocraft_content_20250925_232310.txt 
git add .
git commit 
git status
ls
git push origin
git pull origin
python s.py 
git pull origin
python s.py 
git pull origin
python s.py 
git pull origin
python s.py 
git add .
git commit -m "Update s.py"
git push
ll

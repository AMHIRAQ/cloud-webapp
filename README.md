# Cloud Services & Web App Deployment

## Live Website
http://54.152.121.226

## Architecture

Client (Browser)
│
Internet
│
AWS Security Group (port 22 SSH from my IP only, port 80 HTTP open)
│
Ubuntu 26.04 EC2 Instance (t3.micro) — IP: 54.152.121.226
│
UFW Firewall (allows OpenSSH + Nginx Full)
│
Nginx (reverse proxy, port 80)
│
Gunicorn (WSGI server, port 8000 internal only)
│
Flask App (Python)
│
PostgreSQL (port 5432 — localhost only, not exposed to internet)


## What I Built
A cloud-hosted notes web application where users can add and view notes, backed by a PostgreSQL database running on the same server.

## Tech Stack
| Layer | Technology |
|---|---|
| Application Code | Python 3.14 + Flask |
| WSGI Server | Gunicorn |
| Reverse Proxy | Nginx |
| Database | PostgreSQL 18 |
| Cloud Provider | AWS EC2 |
| OS | Ubuntu 26.04 LTS |
| Process Manager | systemd |

## Deployment Steps

### 1. Cloud Compute — Create the VM
- Launched AWS EC2 instance (Ubuntu 26.04, t3.micro)
- Created and downloaded SSH key pair (.pem)
- Configured Security Group: SSH (22) from my IP only, HTTP (80) open to all
- Connected via SSH:
```bash
chmod 400 ~/.ssh/my-key.pem
ssh -i ~/.ssh/my-key.pem ubuntu@54.152.121.226
```

### 2. Server Configuration
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git nginx postgresql
```

### 3. Database Setup
```bash
sudo systemctl enable --now postgresql
sudo -u postgres psql
```
```sql
CREATE USER appuser WITH PASSWORD '...';
CREATE DATABASE appdb OWNER appuser;
```
Verified PostgreSQL is private (localhost only):
```bash
ss -tulpn | grep 5432
# tcp LISTEN 127.0.0.1:5432  ← not exposed to internet
```

### 4. Application Deployment
```bash
git clone https://github.com/AMHIRAQ/cloud-webapp.git webapp
cd webapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Credentials stored in environment file, never in code:
```bash
sudo nano /etc/webapp.env
sudo chmod 600 /etc/webapp.env
```

### 5. Systemd Service
App runs as a system service, restarts automatically on failure or reboot:
```bash
sudo systemctl enable --now webapp
systemctl status webapp
```
See: `deploy/webapp.service`

### 6. Networking — Nginx Reverse Proxy
```bash
sudo nano /etc/nginx/sites-available/webapp
sudo ln -s /etc/nginx/sites-available/webapp /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
```
See: `deploy/nginx-webapp.conf`

## Connectivity Tests

### App is reachable publicly
```bash
curl http://54.152.121.226/health
# → OK
```

### Database port is blocked from internet
```bash
nc -zv 54.152.121.226 5432
# → timeout (connection refused) ✅
```

### Persistence test
```bash
sudo systemctl restart webapp
# reload the page → notes still there (stored in PostgreSQL) ✅
```

## Security Practices Applied
- SSH key-based authentication only (password auth disabled)
- Root login disabled
- Database not exposed to the internet
- Credentials stored in `/etc/webapp.env` (chmod 600), never in Git
- Systemd auto-restart
- UFW firewall + AWS Security Group (defense in depth)

## Project Structure

cloud-webapp/
├── app.py # Flask application
├── requirements.txt # Python dependencies
├── .gitignore # excludes .env, venv, pem files
├── README.md
├── deploy/
│ ├── webapp.service # systemd service file
│ └── nginx-webapp.conf # Nginx reverse proxy config
└── screenshots/
├── 01-ec2-instance.png
├── 02-ssh-connection.png
├── 03-app-running-browser.png
├── 04-note-added.png
├── 05-persistence-test.png
└── 06-port-5432-blocked.png


## What I Learned
- How to provision and secure a Linux server in the cloud from scratch
- The difference between AWS Security Groups (cloud-level firewall) and UFW (OS-level firewall) and why both matter
- How Nginx acts as a reverse proxy in front of Gunicorn
- Why secrets must never be committed to Git (environment variables instead)
- How systemd manages services and ensures automatic restarts
- How to verify network security with `ss`, `nc`, and `curl`

## Challenges Faced
- `chmod 400` on a .pem file in `/mnt/c/` (Windows filesystem via WSL) had no effect — solved by moving the key to `~/.ssh/` in the Linux filesystem
- `python3-venv` package not found initially — solved by running `sudo apt update` first
- Certbot HTTPS setup requires a real domain name — tested the concept but deployed on IP for this project

## Author
AMHIRAQ
GitHub: https://github.com/AMHIRAQ/cloud-webapp
<img width="1918" height="823" alt="{7FAE7A80-2E29-46AE-A5DB-A65F4199B420}" src="https://github.com/user-attachments/assets/912c2f78-4ced-4318-b77c-847e99131827" />
<img width="1137" height="716" alt="{890D702E-FF5E-4E2B-A8D7-6D4D030BD47D}" src="https://github.com/user-attachments/assets/713fe104-bd04-4be2-87da-3f530e953b47" />
<img width="1744" height="280" alt="{7F9E32BF-08C3-4364-9054-0CC225F5C2B5}" src="https://github.com/user-attachments/assets/a654cf5e-4b38-40d0-a6ae-753943fe5a99" />
<img width="1540" height="398" alt="{B606E6F8-5FB3-41B4-BAA0-2B2C1243C02B}" src="https://github.com/user-attachments/assets/00f5905f-c6dd-49b5-9ed9-36401d78b227" />
<img width="936" height="79" alt="{6F14BA43-A164-4819-936B-DBB00432D3CE}" src="https://github.com/user-attachments/assets/4eef32c2-046b-47f9-8321-06b8aa3a75ac" />
<img width="1920" height="643" alt="{74B19CD7-028C-4E32-BC02-C1CED712FFC5}" src="https://github.com/user-attachments/assets/7857923a-1242-4802-beca-64f75066102b" />
<img width="1850" height="200" alt="{1DA01E67-5D8B-4797-8FC3-1739A4D54320}" src="https://github.com/user-attachments/assets/c3ed6b68-6faa-48c3-925c-d04680d816c5" />



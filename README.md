# it-infrastructure-devops-trainee
Overview
This project is a practical implementation of an IT Infrastructure and DevOps environment running on an AWS EC2 Ubuntu server.

The project demonstrates:
 Linux server administration
 SSH hardening and key-based authentication
 UFW firewall configuration
 Docker and Docker Compose
 Nginx reverse proxy
 Python Flask application
 PostgreSQL database with persistent storage
 Bash automation
 Cron-based health monitoring
 Database backup and restore
 Prometheus and Node Exporter monitoring
 Git branching and documentation

 # Architecture
 
                         Internet
                            │
                            │ HTTP :80
                            ▼
                  ┌──────────────────┐
                  │      Nginx       │
                  │ Reverse Proxy    │
                  │      :80         │
                  └────────┬─────────┘
                           │
                           │ :5000
                           ▼
                  ┌──────────────────┐
                  │   Flask App      │
                  │   Python         │
                  │   :5000          │
                  └────────┬─────────┘
                           │
                           │ PostgreSQL
                           ▼
                  ┌──────────────────┐
                  │   PostgreSQL     │
                  │     :5432        │
                  │ Persistent Data  │
                  └──────────────────┘


        Monitoring
             │
             ├──────────────► Node Exporter :9100
             │
             └──────────────► Prometheus :9090
                                │
                                │ SSH Tunnel
                                ▼
                         Local Browser
                         localhost:9090
# Infrastructure

AWS EC2
The application is deployed on an AWS EC2 Ubuntu instance.

Server configuration
Component	Configuration
Cloud Provider--AWS
Service--EC2
Operating System--Ubuntu 24.04 LTS
Instance Type--t3.micro
Storage--20 GB
SSH Port--2222
HTTP Port--80
HTTPS Port--443
Application Port--5000
PostgreSQL Port--5432
Prometheus--9090
Node Exporter--9100

# Project Structure

devops-trainee-assignment/
│
├── app/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── nginx/
│   ├── nginx.conf
│   └── Dockerfile
│
├── monitoring/
│   └── prometheus/
│       └── prometheus.yml
│
├── scripts/
│   ├── infra_health_check.sh
│   └── db_backup.sh
│
├── screenshots/
│   ├── ufw-status.png
│   ├── docker-ps.png
│   ├── application-browser.png
│   ├── health-check.png
│   ├── health-log.png
│   └── prometheus.png
│
├── docker-compose.yml
├── .gitignore
└── README.md

# 1. Linux & SSH Security
Create trainee user

A dedicated trainee user was created and granted sudo privileges.

sudo adduser trainee
sudo usermod -aG sudo trainee

Verify:
id trainee
Expected:
uid=1001(trainee) gid=1001(trainee) groups=1001(trainee),27(sudo)
# Configure SSH key authentication
SSH was configured to:
Disable direct root login
Disable password authentication
Enable public-key authentication
Use port 2222

# SSH configuration:

Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

Validate the configuration:

sudo sshd -t

Check the effective configuration:

sudo sshd -T | grep -E 'port|permitrootlogin|passwordauthentication|pubkeyauthentication'

Expected:

port 2222
permitrootlogin no
pubkeyauthentication yes
passwordauthentication no

Restart SSH:

sudo systemctl restart ssh

Verify:

sudo systemctl status ssh --no-pager

Important: The original SSH connection on port 22 was kept open until the new trainee connection on port 2222 was successfully tested.

# 2. UFW Firewall

UFW was configured to allow only the required ports.

sudo ufw default deny incoming
sudo ufw default allow outgoing

sudo ufw allow 2222/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

sudo ufw enable

Check firewall status:

sudo ufw status verbose

Expected rules:

2222/tcp    ALLOW
80/tcp      ALLOW
443/tcp     ALLOW

# 3. Docker Installation

Docker was installed on the Ubuntu server.

sudo apt update
sudo apt install -y docker.io docker-compose-v2

Enable Docker:

sudo systemctl enable --now docker

Add the trainee user to the Docker group:

sudo usermod -aG docker trainee

After reconnecting, verify:

docker --version
docker compose version
# 4. Docker Compose Application Stack

The application consists of four main services:

Nginx
Flask application
PostgreSQL
Monitoring services

Start the stack:

docker compose up -d --build

Check containers:
docker ps

# 5. Nginx Reverse Proxy

Nginx is used as the reverse proxy.

The external request flow is:

Client
  ↓
EC2 Port 80
  ↓
Nginx
  ↓
Flask Application :5000

The Flask application is not directly exposed to the internet.

Nginx forwards requests to:

http://app:5000

Test Nginx configuration:

docker exec devops-nginx nginx -t

Expected:
syntax is ok
test is successful

# 6.  Flask Application

The Python Flask application runs inside its own Docker container.

The application provides:

Home endpoint
/
Health endpoint
/health
Database test endpoint
/db-test

Test from the EC2 server:

curl http://localhost/
curl http://localhost/health
curl http://localhost/db-test
# 7.  PostgreSQL Database

PostgreSQL runs in a dedicated Docker container.

The database uses a named Docker volume:

postgres-data

This provides persistent database storage.

Check the volume:

docker volume ls

Check the database container:

docker ps
# 8. Database Persistence Test

Database persistence was tested by:

Creating data
Restarting the PostgreSQL container
Checking the data again

Restart database:

docker restart devops-db

Verify:

docker ps

The data should remain available after the restart because PostgreSQL uses a persistent Docker volume.

# 9.  Infrastructure Health Check

The health-check script is located at:

/opt/scripts/infra_health_check.sh

The script checks:

CPU usage
RAM usage
Root filesystem usage
Docker service status
Application container status

Run manually:

sudo /opt/scripts/infra_health_check.sh

The script generates a warning when:

Disk usage > 85%

or when:

Application container is stopped

Warnings are printed using:

[WARNING]

and written to:

/var/log/infra_health.log
# 10. Health Check Verification

Run:

sudo /opt/scripts/infra_health_check.sh

Check the log:

sudo cat /var/log/infra_health.log

To test the warning condition, stop the application:

docker stop devops-app

Run the health check:

sudo /opt/scripts/infra_health_check.sh

Check:

sudo tail -n 20 /var/log/infra_health.log

Restart the application:

docker start devops-app

# 11.  Cron Automation

The health-check script is scheduled to run every 15 minutes.

Edit the root crontab:

sudo crontab -e

Add:

*/15 * * * * /opt/scripts/infra_health_check.sh

Verify:

sudo crontab -l

Expected:

*/15 * * * * /opt/scripts/infra_health_check.sh
12. Database Backup

The backup script is located at:

/opt/scripts/db_backup.sh

Backup location:

/var/backups/db/

Run the backup:

sudo /opt/scripts/db_backup.sh

Check generated backups:

sudo ls -lh /var/backups/db/

Example:

db_backup_20260913_031500.sql.gz

Verify the gzip archive:

sudo gzip -t /var/backups/db/db_backup_YYYYMMDD_HHMMSS.sql.gz

A successful command produces no output and returns exit code 0.

# 12. Database Restore

A backup can be restored into PostgreSQL using the following process.

Copy the backup into the PostgreSQL container:

docker cp /var/backups/db/db_backup_YYYYMMDD_HHMMSS.sql.gz devops-db:/tmp/restore.sql.gz

Restore:

docker exec -i devops-db sh -c 'gunzip -c /tmp/restore.sql.gz | psql -U devopsuser -d devopsdb'

Verify the restored database:

docker exec -it devops-db psql -U devopsuser -d devopsdb 

# 13. Prometheus Monitoring

Prometheus is used for infrastructure monitoring.

Prometheus runs on:

localhost:9090

It is intentionally bound to localhost and is accessed through an SSH tunnel.

Node Exporter provides system metrics.

SSH Tunnel

From the local MobaXterm terminal:

ssh -i your-key.pem -p 2222 -L 9090:localhost:9090 trainee@YOUR_EC2_PUBLIC_IP

Keep the SSH session open.

Then open in the local browser:

http://localhost:9090

Check:

Status → Targets

The Prometheus and Node Exporter targets should be available.

# 14. Browser Verification

The application can be accessed through the Nginx reverse proxy using:

http://YOUR_EC2_PUBLIC_IP/

The request path is:

Browser
   ↓
EC2 :80
   ↓
Nginx
   ↓
Flask :5000

The backend application port is not directly exposed to the internet.

# 15. Verification Commands
Check UFW
sudo ufw status verbose
Check SSH
sudo ss -tlnp | grep ssh
Check Docker
docker ps
Check Nginx
docker exec devops-nginx nginx -t
Check application
curl http://localhost/
Check application health
curl http://localhost/health
Check database
curl http://localhost/db-test
Check health script
sudo /opt/scripts/infra_health_check.sh
Check health log
sudo tail -n 20 /var/log/infra_health.log
Check backups
sudo ls -lh /var/backups/db/
Check Docker Compose
docker compose ps
# 16. Git Branching Strategy

The project uses separate branches for major configuration tasks.

Example branches:

main
│
├── feature/docker-setup
│
└── feature/scripts

Branches were created for:

Docker/application infrastructure
Automation and backup scripts

Example commands:

git checkout -b feature/docker-setup

Commit:

git add app/ nginx/ docker-compose.yml monitoring/
git commit -m "feat: add containerized web stack"

Create scripts branch:

git checkout main
git checkout -b feature/scripts

Commit:

git add scripts/
git commit -m "feat: add health check and database backup scripts"

Merge into main:

git checkout main

git merge feature/docker-setup --no-ff -m "merge: docker infrastructure setup"

git merge feature/scripts --no-ff -m "merge: automation and backup scripts"

Check history:

git log --oneline --graph --all

# 17. Setup Instructions
Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd devops-trainee-assignment
Build and start services
docker compose up -d --build
Verify
docker ps

Test:
curl http://localhost/
# 18. Teardown

Stop the containers:

docker compose down

To stop and remove containers and the project network:

docker compose down

The PostgreSQL named volume is intentionally preserved unless explicitly removed.

To remove the database volume:

docker compose down -v
Warning: Removing the volume deletes the PostgreSQL persistent data.

# 19. Troubleshooting
--Check container logs
--docker logs devops-nginx
--docker logs devops-app
--docker logs devops-db
--Check all containers
--docker compose ps
--Restart the stack
--docker compose restart
--Rebuild the application
--docker compose up -d --build
--Check Nginx configuration
--docker exec devops-nginx nginx -t
--Check SSH configuration
--sudo sshd -t
--Check listening ports
--sudo ss -tlnp

# 20.  Conclusion

This project demonstrates a complete basic DevOps infrastructure workflow on AWS, including Linux administration, SSH hardening, firewall configuration, containerized application deployment, reverse proxying, database persistence, automation, backup and recovery, monitoring, and Git-based project management.

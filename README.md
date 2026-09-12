# ☁️ Cloud Notes App

A simple Notes app (create / view / edit / delete) built with **FastAPI**
(backend + CRUD API) and **vanilla HTML/CSS/JS** (frontend), storing data
in **SQLite**. Everything runs as a single process on one port, which
keeps deployment on a free-tier EC2 instance simple.

---

## 1. Run it locally

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in your browser.

---

## 2. Push this project to GitHub

```bash
git init
git add .
git commit -m "Cloud notes app"
git branch -M main
git remote add origin https://github.com/<your-username>/cloud-notes-app.git
git push -u origin main
```

---

## 3. Deploy on AWS EC2

### Step A — Launch the instance
1. Log into the [AWS Console](https://console.aws.amazon.com/) → **EC2** → **Launch instance**.
2. Name: `cloud-notes-app`.
3. AMI: **Ubuntu Server 24.04 LTS** (or 22.04), free-tier eligible.
4. Instance type: **t2.micro** (free-tier eligible).
5. Key pair: create a new one, e.g. `notes-app-key`, download the `.pem` file and keep it safe — you can't re-download it later.
6. Network settings → create a new security group and allow:
   - **SSH (22)** — source: *My IP*
   - **Custom TCP (8000)** — source: *Anywhere (0.0.0.0/0)* — this is what makes the app reachable from the internet
7. Launch the instance. Wait until **Instance state = Running** and note its **Public IPv4 address**.

### Step B — Connect over SSH (from Windows PowerShell)
Modern Windows ships with an SSH client, so PowerShell works directly:

```powershell
cd path\to\folder\with\your\key
icacls notes-app-key.pem /inheritance:r /grant:r "$($env:USERNAME):(R)"
ssh -i notes-app-key.pem ubuntu@<EC2_PUBLIC_IP>
```

Type `yes` when asked about the host fingerprint. You're now inside the Ubuntu machine.

### Step C — Set up the server (run these on the EC2 instance)
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip git

git clone https://github.com/<your-username>/cloud-notes-app.git notes-app
cd notes-app

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step D — Run the app
Quick test run (stops when you close SSH):
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

To keep it running permanently (recommended — survives SSH disconnects and reboots), use the included `systemd` service:
```bash
sudo cp notes-app.service /etc/systemd/system/notes-app.service
sudo systemctl daemon-reload
sudo systemctl enable notes-app
sudo systemctl start notes-app
sudo systemctl status notes-app     # should show "active (running)"
```

### Step E — Verify from the internet
Open a browser (on your own laptop, not the EC2 instance) and go to:
```
http://<EC2_PUBLIC_IP>:8000
```
You should see the Cloud Notes app. Try adding, editing, and deleting a note.

---

## 4. Security Group recap
| Rule | Port | Source | Purpose |
|---|---|---|---|
| SSH | 22 | My IP | Lets you connect from your own machine |
| Custom TCP | 8000 | 0.0.0.0/0 | Lets anyone on the internet load the app |

---

## 5. Cleanup
Once your submission is evaluated, **stop or terminate the instance** from the EC2 console to avoid charges.

---

## What I learned
- **EC2**: a virtual machine you rent by the hour (or free-tier for 750 hrs/month); you pick the OS image (AMI) and hardware size (instance type), and it boots up with a public IP you control.
- **SSH**: a secure, key-based way to get a remote terminal on the instance — the `.pem` key proves your identity instead of a password.
- **Security Groups**: a virtual firewall attached to the instance; nothing is reachable from outside until you explicitly open a port (22 for SSH, 8000 for the app here), and you should scope each rule to only what's needed.

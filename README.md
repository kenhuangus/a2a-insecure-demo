# A2A Vulnerable Server & Red Team Attack Client

## Quick Start: Clone and Enter the Project Directory

1. **Clone this repository:**
   ```sh
   git clone https://github.com/kenhuangus/a2a-insecure-demo.git
   ```
2. **Change into the project directory:**
   ```sh
   cd a2a-insecure-demo
   ```
   *(All following steps assume you are in this directory!)*

## Overview
This project demonstrates how SQL injection (SQLi) vulnerabilities can be exploited using a purposely insecure server (A2A Server) and an automated attack client. It is designed for absolute beginners—even if you are new to Python or security!

---

## 1. Key Aspects of the A2A Server and A2A Client

### **A2A Vulnerable Server (`a2a-vulnerable-server.py`)**
- **What it is:** A small web server (using Flask) that stores contact info in a database.
- **Purpose:** It is intentionally insecure so you can practice and observe real SQL injection attacks.
- **What it does:**
  - Creates a database with a `contacts` table (names and phone numbers).
  - Accepts commands to insert, delete, drop, or show records **without any protection**—making it easy to hack!
  - Resets the database every time the server starts.
  - **New:** Exposes a `/debug/reset` endpoint (POST) to reset the database from the client or API.
  - **New:** The server advertises a `reset_db` capability in its agent card at `/.well-known/agent.json`.

### **A2A Attack Client (`a2a-attack-client.py`)**
- **What it is:** A Python script that acts like a red team attacker.
- **Purpose:** Automatically sends both normal and malicious (SQLi) commands to the server and prints the results.
- **What it does:**
  - Shows records, inserts data, deletes data, and tries SQL injection attacks.
  - **No longer attempts to drop tables or destroy data structure.**
  - Tells you if an attack succeeded or failed and prints a detailed attack report.
  - Resets the database before each test using the `/debug/reset` endpoint.

---

## 2. The Vulnerability Exposed by the Server
- **SQL Injection (SQLi):** The server takes whatever you send and puts it directly into its database commands, without checking if it's safe. This means an attacker can:
  - Add extra SQL commands (like `DROP TABLE contacts;`) to delete all data.
  - Insert, modify, or expose data using crafted payloads.

---

## 3. Additional Features
- **/debug/reset Endpoint:**
  - POST to `/debug/reset` to restore the contacts table to its default state (Alice, Bob, Charlie).
  - Used by the attack client to ensure a consistent starting point for tests.
- **reset_db Capability:**
  - The server advertises this capability in its agent card (see `/.well-known/agent.json`).
- **Safe Testing:**
  - The attack client avoids destructive actions (like dropping tables) and focuses on demonstrating SQLi for learning and reporting.

---

## 4. Running the Demo
- Follow the instructions above to clone the repo.

### (Recommended) Use a Python Virtual Environment
1. **Create a virtual environment:**
   - On Windows:
     ```sh
     python -m venv venv
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     python3 -m venv venv
     source venv/bin/activate
     ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

- Start the server with:
  ```sh
  python a2a-vulnerable-server.py
  ```
- In another terminal, run the attack client:
  ```sh
  python a2a-attack-client.py
  ```
- Review the detailed SQLi attack report printed by the client.

---

## 5. More Info
- GitHub repo: https://github.com/kenhuangus/a2a-insecure-demo
- For questions or to contribute, please open an issue or pull request on GitHub.

---


## 3. The Attack Client
- **Automates attacks** so you don’t have to type them manually.
- **Tests normal and malicious payloads** (e.g., tries to insert a record, then tries to drop the table with a SQLi payload).
- **Prints easy-to-read output** so you can see what happened for each attack step.

---

## 4. Step-by-Step: How to Run Everything (for Absolute Beginners)

### **A. Setup**
1. **Open a terminal** (Command Prompt or PowerShell).
2. **Go to your project folder (or the directory you just cloned):**
   ```sh
   cd current directory
   ```
3. **Create a virtual environment:**
   ```sh
   python -m venv venv
   ```
4. **Activate the virtual environment:**
   ```sh
   venv\Scripts\activate
   ```
   (Your prompt will now start with (venv))
5. **Install needed Python packages (for BOTH server and client):**
   ```sh
   pip install -r requirements.txt
   ```
   - All required dependencies are listed in `requirements.txt`.
   - This will install everything needed for both the server and the attack client.

### **B. Start the Vulnerable Server**
1. **In your terminal (with venv activated):**
   ```sh
   python a2a-vulnerable-server.py
   ```
2. **You should see a debug message like:**
   ```
   [DEBUG] SERVER START | VERSION=SQLI-REDTEAM-3 | FILE=...a2a-vulnerable-server.py | PYTHON=...
   ```
3. **Leave this terminal window open and running.**

### **C. Run the Attack Client**
1. **Open a new terminal window.**
2. **Go to your project folder (current directory) and activate the venv again:**
   ```sh
   cd current directory
   venv\Scripts\activate
   ```
3. **Install the required packages (if you haven't already):**
   ```sh
   pip install requests
   ```
   *(If you already did this in the previous terminal, you can skip this step!)*
4. **Run the attack client:**
   ```sh
   python a2a-attack-client.py
   ```
5. **You will see output for each attack step, such as:**
   ```
   [SHOW] Initial records:
   [RESPONSE] show: {'records': [[1, 'Alice', '555-0101'], [2, 'Bob', '555-0202'], ...]}
   ```
   - If you see errors like `no such table: contacts`, it means the table was dropped by a previous attack (which is expected for a successful SQLi attack!).

---

## 5. How to Clean Up and Re-Run Tests

If you want to reset everything and start fresh (for example, after dropping the table):

1. **Stop all Python processes** (close all terminals running the server or client, or run this in a terminal):
   ```sh
   taskkill /F /IM python.exe
   ```
2. **Delete the database file:**
   ```sh
   del a2a_vuln.db
   ```
3. **Restart the server:**
   ```sh
   python a2a-vulnerable-server.py
   ```
4. **Re-run the attack client in a new terminal:**
   ```sh
   python a2a-attack-client.py
   ```

---


## 6. Learning More
- Try changing the attack payloads in `a2a-attack-client.py` to see what else you can do!
- Read the server code to understand how SQL injection works—and why it's dangerous.

---

## 7. Credits
- This project is for educational use only. Do not use these techniques on real systems!
- Inspired by classic red team/blue team training exercises.

---

**Have fun hacking (safely)!**

import os
import sqlite3
from flask import Flask, request, jsonify
import sys
print(f"[DEBUG] SERVER START | VERSION=SQLI-REDTEAM-3 | FILE={os.path.abspath(__file__)} | PYTHON={sys.version}")

app = Flask(__name__)
DB_PATH = "a2a_vuln.db"

# --- Setup vulnerable database ---
def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE contacts (id INTEGER PRIMARY KEY, name TEXT, phone TEXT)")
    c.execute("INSERT INTO contacts (name, phone) VALUES ('Alice', '555-0101')")
    c.execute("INSERT INTO contacts (name, phone) VALUES ('Bob', '555-0202')")
    c.execute("INSERT INTO contacts (name, phone) VALUES ('Charlie', '555-0303')")
    conn.commit()
    conn.close()

reset_db()

@app.route("/.well-known/agent.json", methods=["GET"])
def agent_card():
    card = {
        "name": "VulnerableA2AAgent",
        "description": "A vulnerable A2A agent for SQLi and data exposure demos.",
        "url": "http://localhost:5050",
        "version": "2.0",
        "capabilities": {
            "sql_insert": True,
            "sql_delete": True,
            "sql_drop": True,
            "sql_show": True,
            "env_exposure": True,
            "reset_db": True
        }
    }
    return jsonify(card)
@app.route("/debug/reset", methods=["POST"])
def debug_reset():
    reset_db()
    return jsonify({"status": "reset", "records": [
        [1, 'Alice', '555-0101'],
        [2, 'Bob', '555-0202'],
        [3, 'Charlie', '555-0303']
    ]})


@app.route("/tasks/send", methods=["POST"])
def handle_task():
    data = request.get_json()
    task_id = data.get("id")
    user_message = ""
    try:
        user_message = data["message"]["parts"][0]["text"]
    except Exception:
        return jsonify({"error": "Invalid request format"}), 400
    print(f"[DEBUG] /tasks/send called | VERSION=SQLI-REDTEAM-2 | user_message='{user_message}'")

    # Secure SQL Insert
    if user_message.lower().startswith("insert"):
        # e.g. insert 'Mallory', '555-9999'
        try:
            values = user_message[len("insert"):].strip()
            # Expecting format: 'Name', 'Phone'
            import re
            match = re.match(r"'([^']+)',\s*'([^']+)'", values)
            if not match:
                return jsonify({"error": "Invalid insert format. Use: insert 'Name', 'Phone'"}), 400
            name, phone = match.groups()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))
            conn.commit()
            c.execute("SELECT id, name, phone FROM contacts")
            records = c.fetchall()
            conn.close()
            return jsonify({"status": "inserted", "records": records})
        except Exception as e:
            return jsonify({"error": str(e)})
        return

    # Secure SQL Delete
    elif user_message.lower().startswith("delete"):
        # e.g. delete name='Alice'
        try:
            where = user_message[len("delete"):].strip()
            # Only allow deleting by name or phone
            import re
            match = re.match(r"name='([^']+)'", where)
            if match:
                name = match.group(1)
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM contacts WHERE name = ?", (name,))
            else:
                match = re.match(r"phone='([^']+)'", where)
                if match:
                    phone = match.group(1)
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("DELETE FROM contacts WHERE phone = ?", (phone,))
                else:
                    return jsonify({"error": "Invalid delete format. Use: delete name='Name' or delete phone='Phone'"}), 400
            conn.commit()
            c.execute("SELECT id, name, phone FROM contacts")
            records = c.fetchall()
            conn.close()
            return jsonify({"status": "deleted", "records": records})
        except Exception as e:
            return jsonify({"error": str(e)})
        return

    # Vulnerable SQL Drop
    elif user_message.lower().startswith("drop"):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            sql = "DROP TABLE contacts"
            c.executescript(sql)
            conn.commit()
            conn.close()
            return jsonify({"status": "dropped"})
        except Exception as e:
            return jsonify({"error": str(e)})
        return

    # Show all records
    elif user_message.lower().startswith("show"):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, name, phone FROM contacts")
            records = c.fetchall()
            conn.close()
            return jsonify({"status": "ok", "records": records})
        except Exception as e:
            return jsonify({"error": str(e)})
        return

    # Env var exposure
    elif user_message.lower().startswith("attack env"):
        envs = {k: v for k, v in os.environ.items() if "key" in k.lower() or "secret" in k.lower() or "pass" in k.lower()}
        reply = f"Env exposure: {envs if envs else '[no sensitive env vars found]'}"
        response_task = {
            "id": task_id,
            "status": {"state": "completed"},
            "messages": [
                data.get("message", {}),
                {"role": "agent", "parts": [{"text": reply}]}
            ]
        }
        return jsonify(response_task)
    else:
        reply = "Unknown or unsupported attack. Use 'insert', 'delete', 'drop', 'show', 'attack env'."
        response_task = {
            "id": task_id,
            "status": {"state": "completed"},
            "messages": [
                data.get("message", {}),
                {"role": "agent", "parts": [{"text": reply}]}
            ]
        }
        return jsonify(response_task)

@app.route("/debug/sqli", methods=["GET"])
def debug_sqli():
    reset_db()
    forced_payload = "('attacker', 'hacked'); DROP TABLE users;--"
    debug_result = {}
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        sql = f"INSERT INTO users (name, address) VALUES {forced_payload}"
        print(f"[DEBUG] /debug/sqli Executing: {sql}")
        try:
            c.executescript(sql)
            conn.commit()
            try:
                c.execute("SELECT name, address FROM users")
                users = c.fetchall()
                debug_result["result"] = users
            except Exception as e:
                debug_result["error"] = str(e)
        except Exception as e:
            debug_result["error"] = str(e)
        conn.close()
    except Exception as e:
        debug_result["error"] = str(e)
    return jsonify(debug_result)

if __name__ == "__main__":
    print("A2A Vulnerable Agent running at http://localhost:5050")
    app.run(host="0.0.0.0", port=5050)

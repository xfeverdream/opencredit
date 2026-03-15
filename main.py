import json
import os
import hashlib
import getpass
from datetime import datetime
import base64
import re

SETTINGS_FILE = "settings.json"
DATA_FILE = "credit_log.json"


def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()


def setup_password():
    print("No settings file found. Create a new password.")
    password = getpass.getpass("New password: ")

    salt = os.urandom(16).hex()
    password_hash = hash_password(password, salt)

    settings = {
        "salt": salt,
        "password_hash": password_hash
    }

    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

    print("Password created.\n")


def authenticate():
    if not os.path.exists(SETTINGS_FILE):
        setup_password()

    with open(SETTINGS_FILE) as f:
        settings = json.load(f)

    salt = settings["salt"]
    stored_hash = settings["password_hash"]

    password = getpass.getpass("Enter password: ")

    if hash_password(password, salt) != stored_hash:
        print("Incorrect password.")
        exit()

    print("Access granted.\n")


def encrypt_text(text, key):
    key_bytes = key.encode()
    text_bytes = text.encode()

    encrypted = bytes([text_bytes[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(text_bytes))])
    return base64.b64encode(encrypted).decode()


def decrypt_text(text, key):
    key_bytes = key.encode()
    encrypted = base64.b64decode(text)

    decrypted = bytes([encrypted[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(encrypted))])
    return decrypted.decode()


def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_entry(data):
    description = input("Description: ")
    try:
        amount = float(input("Amount (positive for credit, negative for debit): "))
    except ValueError:
        print("Invalid amount\n")
        return

    # Allow custom date
    date_input = input("Date (YYYY-MM-DD HH:MM) [leave blank for now]: ")
    if date_input.strip():
        try:
            date = datetime.strptime(date_input, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid date format, using current time.")
            date = datetime.now().strftime("%Y-%m-%d %H:%M")
    else:
        date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Calculate running total
    total = data[-1]["total"] + amount if data else amount

    entry_id = 1 if not data else max(e["id"] for e in data) + 1

    entry = {
        "id": entry_id,
        "description": description,
        "delta": amount,
        "total": total,
        "date": date,
        "type": "add"
    }

    data.append(entry)
    save_data(data)

    print(f"Entry added with ID {entry_id}\n")


def remove_entry(data):
    try:
        entry_id = int(input("Entry ID to remove: "))
    except ValueError:
        print("Invalid ID\n")
        return

    # Find entry
    entry_to_remove = next((e for e in data if e["id"] == entry_id), None)
    if not entry_to_remove:
        print("ID not found\n")
        return

    # Subtract its delta from running total
    total_before = data[-1]["total"] if data else 0
    new_total = total_before - entry_to_remove["delta"]

    remove_entry_log = {
        "id": entry_id,
        "description": entry_to_remove["description"],
        "delta": -entry_to_remove["delta"],  # log as negative
        "total": new_total,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": "remove"
    }

    data.append(remove_entry_log)
    save_data(data)

    print(f"Entry {entry_id} removed (logged)\n")



def list_entries(data):
    if not data:
        print("No entries\n")
        return

    for e in data:
        print(f'{e["id"]}: {e["description"]} | {e["delta"]} | {e["date"]}     | {e["total"]}')
    print()

def setup_personal_data():
    with open(SETTINGS_FILE) as f:
        settings = json.load(f)

    key = settings["password_hash"]

    print("\nEnter personal/account details (leave blank to skip)\n")

    personal_data = {
        "bank_provider": input("Bank Provider: "),
        "iban": input("IBAN: "),
        "swift": input("SWIFT/BIC: "),
    }

    encrypted_data = {}

    for k, v in personal_data.items():
        encrypted_data[k] = encrypt_text(v, key)

    settings["personal_data"] = encrypted_data

    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

    print("\nPersonal data updated.\n")


def load_personal_data():
    with open(SETTINGS_FILE) as f:
        settings = json.load(f)

    key = settings["password_hash"]

    if "personal_data" not in settings:
        return {}

    decrypted = {}
    for k, v in settings["personal_data"].items():
        decrypted[k] = decrypt_text(v, key)

    return decrypted

def is_valid_format(s):
    # ^ = start of string, \d = digit, {n} = exactly n times, - = literal dash, $ = end of string
    pattern = r"^\d{2}-\d{4}$"
    return bool(re.match(pattern, s))

def export_ascii(data):

    if not data:
        print("No data to export\n")
        return

    # warning + numbering input
    warning_text = """
NOTE: You are exporting a document containing confidential information. Before proceeding,
      verify this transaction and enter the following information:
                - Document ID (XX-XXXX)
                - Statement Nr.
"""
    print(warning_text)
    doc_id = input("DOCUMENT ID   >      ")
    statement_id = input("STATEMENT Nr. >      ")

    if not is_valid_format(doc_id):
        print("error: Invalid document ID")
        return

    personal = load_personal_data()

    statement_title = "VAULT CASH STATEMENT"
    export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    confidential = "This document is classified as: CONFIDENTIAL - FINANCIAL INFORMATION"
    confidential2 = "Unauthorized access, duplication or distribution is strictly prohibited."

    note = ""

    lines = []

    lines.append(confidential)
    lines.append(confidential2)
    lines.append("*" * 80)
    lines.append(statement_title.center(80))
    lines.append(f"Generated: {export_time}".center(80))
    lines.append("*" * 80)
    lines.append("")

    # Account holder info
    lines.append(" " * 60 + "        " + doc_id)
    lines.append(" " * 60 + "Statement Nr. " + statement_id)
    lines.append(f"Provider:        {personal.get('bank_provider','')}")
    lines.append(f"IBAN:            {personal.get('iban','')}")
    lines.append(f"SWIFT/BIC:       {personal.get('swift','')}")
    lines.append("")

    lines.append("")
    lines.append("")

    # Table header
    lines.append(f"{'ID':<4} {'Description':<30} {'Delta':>10} {'Total':>10} {'Date':<16} {'Type':<6}")
    lines.append("-" * 80)

    for e in data:
        desc = e["description"][:30]
        lines.append(
            f"{e['id']:<4} "
            f"{desc:<30} "
            f"{e['delta']:>10.2f} "
            f"{e['total']:>10.2f} "
            f"{e['date']:<16} "
            f"{e['type']:<6}"
        )

    lines.append("")

    final_total = data[-1]["total"] if data else 0
    lines.append(f"{'TOTAL BALANCE:':<47}{final_total:>10.2f}")
    lines.append("")

    # Signature area
    lines.append("")
    lines.append("Date ........................   Signature .....................................")

    with open("credit_export.txt", "w") as f:
        f.write("\n".join(lines))

    print("DONE: Exported to credit_export.txt\n")


def print_help():
    help_text = """
Available commands:

add      - Add a new credit/debit entry (you can backdate the entry)
remove   - Remove an entry by its ID (logs it instead of deleting)
list     - List all entries in the database
export   - Export all entries to a formatted ASCII statement (credit_export.txt)
setup    - Set or overwrite your personal/account data
help     - Show this help message
exit     - Exit the program
"""
    print(help_text)


def startup_msg():
    text = """
opencredit 0.1.0.release-rev0
developed by: Kian Schmalzl (xfeverdream)
"""
    print(text)


def main():
    startup_msg()
    authenticate()

    print("commands: add, remove, setup, list, export, help, exit")
    data = load_data()

    while True:
        cmd = input("> ").lower()

        if cmd == "add":
            data = load_data()
            add_entry(data)

        elif cmd == "remove":
            data = load_data()
            remove_entry(data)

        elif cmd == "list":
            data = load_data()
            list_entries(data)

        elif cmd == "export":
            data = load_data()
            export_ascii(data)

        elif cmd == "exit":
            break

        elif cmd == "setup":
            setup_personal_data()

        else:
            print("error: unknown command\n")


if __name__ == "__main__":
    main()
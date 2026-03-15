# opencredit

### Overview

opencredit is a secure, text-based Python program for managing and tracking financial credit/debit transactions. It allows users to maintain a detailed log of entries, including descriptions, amounts, running totals, and timestamps. Personal and banking data are securely encrypted, and the program can generate professional ASCII-formatted account statements suitable for printing.

Key features include:

- Encrypted password protection and personal data storage.
- Add, remove, and list transactions with running totals.
- Export a professional-looking account statement as a text file.
- Backdate entries to maintain historical accuracy.
- Setup and update personal information and banking details.
- Confidential notices and signature lines for printed statements.
- Command-line interface (CLI) with a built-in help system.

---

### How it Works

1. **Authentication**:  
   Upon startup, the program prompts the user for a password. This password is securely hashed and stored in an encrypted settings file (`settings.json`).

2. **Data Storage**:  
   Transaction entries are stored in a separate JSON file (`credit_log.json`) to ensure that sensitive password data is not mixed with user financial data. Each entry contains:

   - `ID`: Unique identifier
   - `Description`: Details of the transaction
   - `Delta`: Amount added or subtracted
   - `Total`: Running total after the transaction
   - `Date`: Timestamp of the entry
   - `Type`: `add` or `remove`

   Removing an entry does **not delete it** but logs it as a reversal to preserve a full audit trail.

3. **Personal Data**:  
   Users can securely store personal information such as name, address, banking details, and account numbers. These are encrypted in the settings file and included in the exported statement.

4. **Export**:  
   The program generates a clean ASCII table showing all transactions, running totals, and account information. The statement includes a **confidential warning**, date, signature line, and total balance.

---

### Usage

After launching the program:

1. **Login**:  
   Enter your password to access the system.

2. **Commands**:

| Command  | Description |
|----------|-------------|
| `add`    | Add a new credit or debit entry. You can optionally backdate entries. |
| `remove` | Log a removal of an existing entry by its ID. Preserves audit trail. |
| `list`   | Display all entries in a simple table. |
| `export` | Export a professional ASCII-formatted account statement (`credit_export.txt`). |
| `setup`  | Enter or update personal/account details such as name, address, and bank info. |
| `help`   | Display a list of commands and their explanations. |
| `exit`   | Exit the program. |

3. **Notes**:

- The program enforces limits: `Description` is truncated at 30 characters; amounts are limited to ±10000.
- Running totals are automatically updated with each transaction.
- The exported statement is print-ready with a signature line and date placeholder.

---

### Installation

1. **Requirements**:

- Python 3.7+  
- No external dependencies are required; the program uses standard Python libraries.

2. **Setup**:

```bash
# Clone the repository
git clone https://github.com/xfeverdream/opencredit.git
cd credit-log-system

# Run the program
python credit_log.py
```

### Credits
developed by Kian Schmalzl (xfeverdream)

### License
opencredit is licensed under the MIT License.
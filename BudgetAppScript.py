import csv
import hashlib
import sqlite3
from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

# File Paths
ROOT_DIR = "./input/"
DB_FILE = "./cache/BudgetApp.db"
OUTPUT_FILE = "./output.csv"

# Enriched Transaction Column Names
SOURCE_COL_NM = "trans_source"
DATE_COL_NM = "trans_date"
DESCRIPTION_COL_NM = "trans_description"
AMOUNT_COL_NM = "trans_amount"
HASH_COL_NM = "trans_hash"

# Transaction Reading Configurations
BOA_TRANS_CFG = {
    "BOA_CC": {
        DATE_COL_NM: "Posted Date",
        DESCRIPTION_COL_NM: "Payee",
        AMOUNT_COL_NM: "Amount",
    },
    "BOA_Checking": {
        DATE_COL_NM: "Date",
        DESCRIPTION_COL_NM: "Description",
        AMOUNT_COL_NM: "Amount",
    },
}

# Budget Categories
BUDGET_CATEGORIES = {
    "Income": ["HCA Salary", "HCA Bonus", "Inheritance", "Gifts", "Other"],
    "House": ["Mortgage", "Utilities", "Discretionary"],
    "Transportation": ["Gasoline", "Insurance", "Car Payments"],
    "Vacation": None,
    "Food": ["Groceries", "Eating Out"],
    "Health": ["Perscriptions", "Doctors Visits", "Discretionary"],
    "Digital": ["Subscriptions", "Discretionary"],
    "Starting Checking Balance": None,
    "Investment": None,
    "Other": None,
    "Ignore": None,
}


# SQLite Table Definitions
KEY_WORD_RULES_DB_COLS = """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_words TEXT NOT NULL,
    primary_cat TEXT NOT NULL,
    secondary_cat TEXT 
"""


def main_menu():
    while True:
        menu_selection = inquirer.select(
            message="Select an action:",
            choices=[
                Choice(
                    value="Update Transaction History",
                    name="Update Transaction History",
                ),
                "Key Word Rules",
                "Exit",
            ],
            default=None,
        ).execute()

        if menu_selection == "Update Transaction History":
            enriched_transactions = update_transactions()

            write_to_csv(enriched_transactions)
        elif menu_selection == "Key Word Rules":
            key_word_rules_menu()

        else:
            return
    print("Welcome to the Ficcadenti Budget App")


def write_to_csv(enriched_transactions):
    with open(OUTPUT_FILE, mode="w", newline="") as file:
        csv_writer = csv.DictWriter(file, fieldnames=enriched_transactions[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(enriched_transactions)
    print(len(enriched_transactions))


def update_transactions():
    transactions_by_source = read_transactions_from_file()

    enriched_transactions = []
    for source_nm in transactions_by_source.keys():
        if source_nm == "AmazonPurchases":
            enriched_transactions += enrich_amazon_purchases(
                transactions_by_source, source_nm
            )
        elif "BOA" in source_nm:
            enriched_transactions += enrich_boa_transactions(
                transactions_by_source, source_nm
            )
        elif source_nm == "ValleyHYS_8300":
            enriched_transactions += enrich_valley_transactions(
                transactions_by_source, source_nm
            )

    return enriched_transactions


def enrich_boa_transactions(transactions_by_source, source_nm):
    for key in BOA_TRANS_CFG.keys():
        if key in source_nm:
            boa_config = BOA_TRANS_CFG[key]

    enriched_boa_transactions = []
    for boa_trans in transactions_by_source[source_nm]:
        # boa config returns the corresponding bank statement col name for each enriched
        # transaction col name

        if boa_trans[boa_config[DESCRIPTION_COL_NM]] == "Beginning balance as of":
            amount = boa_trans["Running Bal."]
        else:
            amount = boa_trans[boa_config[AMOUNT_COL_NM]]
        amount = amount.replace(",", "")  # Remove Commas
        amount = amount if amount != "" else "0.00"  # Set to 0.00 if entry is blank
        amount = round(float(amount), 2)

        trans_enriched = {
            SOURCE_COL_NM: source_nm,
            DATE_COL_NM: boa_trans[boa_config[DATE_COL_NM]],
            DESCRIPTION_COL_NM: boa_trans[boa_config[DESCRIPTION_COL_NM]],
            AMOUNT_COL_NM: amount,
            HASH_COL_NM: hash_transaction(boa_trans),
        }

        enriched_boa_transactions.append(trans_enriched)

    return enriched_boa_transactions


def enrich_valley_transactions(transactions_by_source, source_nm):
    enriched_valley_transactions = []
    for valley_trans in transactions_by_source[source_nm]:
        if "DEBIT" in valley_trans["Description"]:
            amount = valley_trans["Amount Debit"]
        else:
            amount = valley_trans["Amount Credit"]

        amount = round(float(amount), 2)

        trans_enriched = {
            SOURCE_COL_NM: source_nm,
            DATE_COL_NM: valley_trans["Date"],
            DESCRIPTION_COL_NM: valley_trans["Memo"],
            AMOUNT_COL_NM: amount,
            HASH_COL_NM: hash_transaction(valley_trans),
        }

        enriched_valley_transactions.append(trans_enriched)
    return enriched_valley_transactions


def enrich_amazon_purchases(transactions_by_source, source_nm):
    # last row is the headers repeated
    enriched_amazon_transactions = []
    for amazon_transaction in transactions_by_source[source_nm][:-1]:
        order_no = amazon_transaction["order id"]  # Amazon Order Identifier
        item_no = amazon_transaction["ASIN"]  # Amazon Item Identifer
        description = amazon_transaction["description"][:75]  # cut off at 75 characters
        amazon_cat = amazon_transaction["category"].split("›")[0]  # highest level cat

        price = amazon_transaction["price"][1:]
        price = float(price if price[1:] != "" else 0.0)
        price = round(price, 2) * -1  # amazon purchases are expenses

        trans_enriched = {
            SOURCE_COL_NM: source_nm,
            DATE_COL_NM: amazon_transaction["order date"],
            DESCRIPTION_COL_NM: amazon_cat + "|" + description,
            AMOUNT_COL_NM: price,
            HASH_COL_NM: hash_str(order_no + item_no),
        }

        enriched_amazon_transactions.append(trans_enriched)
    return enriched_amazon_transactions


def hash_transaction(transaction: dict):
    hash_src = "".join([transaction[key] for key in transaction.keys()])
    hash = hash_str(hash_src)
    return hash


def hash_str(hash_src: str):
    hash_bytes = hash_src.encode("utf-8")
    hash_hex = hashlib.sha256(hash_bytes).hexdigest()
    return hash_hex


def read_transactions_from_file():
    root_dir = Path(ROOT_DIR)
    all_transactions = {}
    for path in root_dir.rglob("*"):
        if not path.is_dir() and str(path) != "input\\.gitignore":
            table_name, transactions = read_statement(path)
            if table_name in all_transactions.keys():
                all_transactions[table_name] += transactions
            else:
                all_transactions.update({table_name: transactions})

    return all_transactions


def read_statement(statement_csv_path: Path):
    with open(statement_csv_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)

        report_width = max([len(row) for row in csv_reader])
        file.seek(0)

        transactions = []
        headers = None
        for csv_row in csv_reader:
            # clean rows of sloppy csv writing
            csv_row_cln = [cell.replace("\ufeff", "") for cell in csv_row]

            if headers is not None:
                # if the headers have been found, append the row of data to transactions
                transactions.append(dict(zip(headers, csv_row_cln)))
            elif len(csv_row_cln) == report_width:
                # if headers are not found, and if the row matches the report width,
                # the loop has reached the header row and needs to be captured
                headers = csv_row_cln

    # Use statement directory names as names for the SQL tables
    table_name = statement_csv_path.as_posix().split("/")[-2]

    return table_name, transactions


def key_word_rules_menu():
    while True:
        menu_selection = inquirer.select(
            message="Select an action:",
            choices=[
                Choice(name="View Keyword Rules", value="View Keyword Rules"),
                "Add Key Word Rule",
                "Remove Key Word Rule",
                "Exit",
            ],
            default=None,
        ).execute()

        if menu_selection == "View Keyword Rules":
            view_key_word_rules()
        elif menu_selection == "Add Key Word Rule":
            add_key_word_rules()
        elif menu_selection == "Remove Key Word Rule":
            remove_key_word_rules()
        else:
            return


def view_key_word_rules():
    rows = get_key_word_rules_from_db()

    if len(rows) == 0:
        print("No Keyword Rules Saved")
    else:
        for row in rows:
            print(row)


def remove_key_word_rules():

    while True:
        rows = get_key_word_rules_from_db()

        if len(rows) == 0:
            print("No key word rules saved.")
            return

        key_word_rules = []
        for row in rows:
            key_word_rule = row[1] + "->" + row[2] + "+" + row[3]
            key_word_rules.append(key_word_rule)

        key_word_rules.append("Exit")

        delete_selection = inquirer.select(
            message="Select an action:",
            choices=key_word_rules,
            default=None,
        ).execute()

        key_word_to_delete = delete_selection.split("->")[0]

        if delete_selection == "Exit":
            return
        elif delete_selection is not None:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            delete_query = "DELETE FROM key_word_rules WHERE key_words = ?;"

            cursor.execute(delete_query, (key_word_to_delete,))
            conn.commit()
            conn.close()


def add_key_word_rules():
    create_key_word_db()
    while True:
        new_key_words = get_key_word_from_user()
        new_key_words = new_key_words.strip()

        primary_cat = None
        secondary_cat = None

        print("'" + new_key_words + "'")
        if new_key_words == "Cancel":
            return
        if new_key_words is not None and new_key_words != "":
            primary_cat, secondary_cat = get_categories_from_user()

            if primary_cat != "Cancel" and secondary_cat != "Cancel":
                key_word_rules = get_key_word_rules_from_db()
                if new_key_words in (kwrd[1] for kwrd in key_word_rules):
                    print("Key Words already in DB")
                else:
                    add_key_word_rule_to_db(new_key_words, primary_cat, secondary_cat)


def get_key_word_rules_from_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    select_key_words_query = """
            SELECT * FROM key_word_rules
        """
    cursor.execute(select_key_words_query)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows


def add_key_word_rule_to_db(new_key_words, primary_cat, secondary_cat):
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    insert_key_words_query = (
        "INSERT INTO key_word_rules (key_words, primary_cat, secondary_cat)"
    )
    insert_key_words_query = (
        insert_key_words_query
        + "VALUES ('"
        + new_key_words
        + "','"
        + primary_cat
        + "','"
        + secondary_cat
        + "');"
    )

    cursor.execute(insert_key_words_query)

    conn.commit()

    conn.close()


def get_key_word_from_user():
    new_key_word = inquirer.text(
        message="Enter new key word phrase:", completer={"Cancel": None}
    ).execute()

    return new_key_word


def get_categories_from_user():
    prim_choices = list(BUDGET_CATEGORIES.keys()).copy()
    prim_choices.append("Cancel")
    primary_cat = inquirer.select(
        message="Select a Primary Category",
        choices=prim_choices,
    ).execute()

    if primary_cat != "Cancel" and BUDGET_CATEGORIES[primary_cat] is not None:
        sec_choices = BUDGET_CATEGORIES[primary_cat].copy()
        sec_choices.append("Cancel")
        secondary_cat = inquirer.select(
            message="Select a Primary Category",
            choices=sec_choices,
        ).execute()
    else:
        secondary_cat = "N/A"
    return primary_cat, secondary_cat


def create_key_word_db():
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    create_db_query = (
        "CREATE TABLE IF NOT EXISTS key_word_rules (" + KEY_WORD_RULES_DB_COLS + ")"
    )

    cursor.execute(create_db_query)

    conn.commit()

    conn.close()


def main():
    main_menu()


if __name__ == "__main__":
    main()

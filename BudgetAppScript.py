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
    "House": ["Essential", "Discretionary"],
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
KEY_WORD_RULES = """
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


def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS 

    """)


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
                Choice(
                    name="View Keyword Rules",
                ),
                "Add Key Word Rule",
                "Exit",
            ],
            default=None,
        ).execute()

        if menu_selection == "View Keyword Rules":
            return
        elif menu_selection == "Add Key Word Rule":
            return
        else:
            return


def add_key_word_rules():
    while True:
        new_key_word = inquirer.text(
            message="Enter new key word phrase:", completer={"Exit"}
        ).execute()

        if new_key_word == "Exit":
            return
        else:
            primary_key = inquirer.select(
                message="Select a Primary Category", choices=BUDGET_CATEGORIES.keys()
            ).execute()

            # if BUDGET_CATEGORIES[primary_key] is not None:
            #     secondary_key = inquirer.select(
            #         message=""
            #     )


def main():
    main_menu()


if __name__ == "__main__":
    main()

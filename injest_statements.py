import csv
import hashlib
from pathlib import Path

# test_path = "./input/BOABlueCard5511/currentTransaction_5511.csv"
# test_path = "./input/BOAChecking3236/Checking_2026_06_28.csv"
# test_path = "./input/ValleyHYS8300/Valley_2026_06_28.csv"
# test_path = "./input/AmazonChase4147/chase_transactions.csv"
# test_path = "./input/AmazonOrders/amazon_items.csv"

# Transaction schema:
#     "Date"
#     "Payee"
#     "Amount"
#     "Category" (Amazon items only)


def hash_row(row: dict):
    values_orderby_keys = [str(row[key]) for key in sorted(row.keys())]
    values_str = "|".join(values_orderby_keys)
    row_hash = hashlib.sha256(values_str.encode("utf-8")).hexdigest()

    return row_hash


def get_transactions(statement_csv_path: str):
    folder_name = statement_csv_path.split("/")[-2]

    with open(statement_csv_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)

        if folder_name in ("BOABlueCard5511", "BOARedCard3924"):
            transactions = read_boa_cc_stmt(csv_reader)
        elif folder_name == "BOAChecking3236":
            transactions = read_boa_checking(csv_reader)
        elif folder_name == "ValleyHYS8300":
            transactions = read_valley_hys(csv_reader)
        elif folder_name == "AmazonChase4147":
            transactions = read_chase_card(csv_reader)
        elif folder_name == "AmazonOrders":
            transactions = read_amazon_purchases(csv_reader)
        else:
            raise RuntimeError("Folder Not Recognized")

        return transactions

    return None


def read_boa_cc_stmt(csv_reader):
    result_arr = []

    headers = next(csv_reader)

    for row in csv_reader:
        row_dict = dict(zip(headers, row))

        transaction = {
            "Date": row_dict["Posted Date"],
            "Payee": row_dict["Payee"],
            "Amount": row_dict["Amount"],
        }

        result_arr.append(transaction)
    return result_arr


def read_boa_checking(csv_reader):
    result_arr = []

    headers = next(csv_reader)
    while len(headers) == 0 or headers[0] != "Date":
        headers = next(csv_reader)

    for row in csv_reader:
        row_dict = dict(zip(headers, row))

        transaction = {
            "Date": row_dict["Date"],
            "Payee": row_dict["Description"],
            "Amount": row_dict["Amount"],
        }

        result_arr.append(transaction)

    return result_arr


def read_valley_hys(csv_reader):
    result_arr = []

    headers = next(csv_reader)
    while len(headers) == 0 or headers[0] != "Transaction Number":
        headers = next(csv_reader)

    for row in csv_reader:
        row_dict = dict(zip(headers, row))

        transaction = {
            "Date": row_dict["Date"],
            "Payee": row_dict["Description"],
            "Amount": row_dict["Amount Credit"]
            if "CREDIT" in row_dict["Description"]
            else row_dict["Amount Debit"],
        }

        result_arr.append(transaction)

    return result_arr


def read_chase_card(csv_reader):
    result_arr = []

    headers = next(csv_reader)

    for row in csv_reader:
        row_dict = dict(zip(headers, row))

        transaction = {
            "Date": row_dict["Transaction Date"],
            "Payee": row_dict["Description"],
            "Amount": row_dict["Amount"],
        }

        result_arr.append(transaction)
    return result_arr


# amazon purchases generated with "Amazon Order History Reporter" Chrome extension
def read_amazon_purchases(csv_reader):
    result_arr = []

    headers = next(csv_reader)

    for row in csv_reader:
        row_dict = dict(zip(headers, row))

        if row_dict["\ufefforder id"] != "order id":
            if row_dict["price"][1:] == "":
                price = 0.0
            else:
                price = float(row_dict["price"][1:])

            item_category = (
                "BLANK"
                if row_dict["category"].split("›")[0] == ""
                else row_dict["category"].split("›")[0]
            )

            item_name = row_dict["description"].split(",")[0]
            if len(item_name) > 100:
                item_name = item_name[:101]

            transaction = {
                "Date": row_dict["order date"],
                "Payee": item_category + "|" + item_name,
                "Amount": float(row_dict["quantity"]) * price,
            }

            result_arr.append(transaction)
    return result_arr


# transactions = get_transactions(test_path)
# for transaction in transactions:
#     print(transaction)

root_dir = Path("./input/")

all_transactions = []
for path in root_dir.rglob("*"):
    if (
        not path.is_dir()
        and str(path) != "input\\.gitignore"
        and str(path) != "input\\output.csv"
    ):
        print(path.as_posix())
        all_transactions += get_transactions(path.as_posix())


with open("./output.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=list(all_transactions[0].keys()))
    writer.writeheader()
    writer.writerows(all_transactions)

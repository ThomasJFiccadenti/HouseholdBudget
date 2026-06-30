import csv
import hashlib

# test_path = "./input/BOABlueCard5511/currentTransaction_5511.csv"
# test_path = "./input/BOAChecking3236/Checking_2026_06_28.csv"
# test_path = "./input/ValleyHYS8300/Valley_2026_06_28.csv"
# test_path = "./input/AmazonChase4147/chase_transactions.csv"
test_path = "./input/AmazonOrders/amazon_items.csv"

# Transaction schema:
#     "Posted Date"
#     "Payee"
#     "Amount"
#     "Hash"


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
        row_hash = hash_row(row_dict)

        transaction = {
            "Date": row_dict["Posted Date"],
            "Payee": row_dict["Payee"],
            "Amount": row_dict["Amount"],
            "Hash": row_hash,
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
        row_hash = hash_row(row_dict)

        transaction = {
            "Date": row_dict["Date"],
            "Payee": row_dict["Description"],
            "Amount": row_dict["Amount"],
            "Hash": row_hash,
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
        row_hash = hash_row(row_dict)
        print(row_dict)
        transaction = {
            "Date": row_dict["Date"],
            "Payee": row_dict["Description"],
            "Amount": row_dict["Amount Credit"]
            if "CREDIT" in row_dict["Description"]
            else row_dict["Amount Debit"],
            "Hash": row_hash,
        }

        result_arr.append(transaction)

    return result_arr


def read_chase_card(csv_reader):
    result_arr = []

    headers = next(csv_reader)

    for row in csv_reader:
        row_dict = dict(zip(headers, row))
        row_hash = hash_row(row_dict)

        transaction = {
            "Date": row_dict["Transaction Date"],
            "Payee": row_dict["Description"],
            "Amount": row_dict["Amount"],
            "Hash": row_hash,
        }

        result_arr.append(transaction)
    return result_arr


# amazon purchases generated with "Amazon Order History Reporter" Chrome extension
def read_amazon_purchases(csv_reader):
    result_arr = []

    headers = next(csv_reader)

    for row in csv_reader:
        row_dict = dict(zip(headers, row))
        row_hash = hash_row(row_dict)

        if row_dict["\ufefforder id"] != "order id":
            if row_dict["price"][1:] == "":
                price = 0.0
            else:
                print(row_dict["price"][1:])
                print(row_dict["price"])
                price = float(row_dict["price"][1:])

            transaction = {
                "Date": row_dict["order date"],
                "Payee": row_dict["description"],
                "Amount": float(row_dict["quantity"]) * price,
                "Hash": row_hash,
                "Category": row_dict["category"],
            }

            result_arr.append(transaction)
    return result_arr


transactions = get_transactions(test_path)
for transaction in transactions:
    print(transaction)

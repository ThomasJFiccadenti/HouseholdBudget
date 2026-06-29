import csv
import hashlib

test_path = "./input/BOABlueCard5511/currentTransaction_5511.csv"

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


def load_statement(statement_csv_path: str):
    folder = statement_csv_path.split("/")[-2]

    with open(statement_csv_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)

        if folder in ("BOABlueCard5511", "BOARedCard3924"):
            transactions = read_boa_cc_stmt(csv_reader)

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


transactions = load_statement(test_path)
for transaction in transactions:
    print(transaction)

import csv
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


def read_statement(statement_csv_path: Path):
    with open(statement_csv_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)

        report_width = max([len(row) for row in csv_reader])
        file.seek(0)

        transactions = []
        headers = None
        for csv_row in csv_reader:
            #clean rows of sloppy csv writing
            csv_row_cln = [cell.replace("\ufeff", "") for cell in csv_row]

            if headers is not None:
                # if the headers have been found, append the row of data to transactions
                transactions.append(csv_row_cln)
            elif len(csv_row_cln) == report_width:
                # if headers are not found, and if the row matches the report width,
                # the loop has reached the header row and needs to be captured
                headers = csv_row_cln

    # Use statement directory names as names for the SQL tables
    table_name = statement_csv_path.as_posix().split("/")[-2]

    return {
        "TableName": table_name,
        "Rows": transactions,
    }


root_dir = Path("./input/")
all_transactions = []
for path in root_dir.rglob("*"):
    if not path.is_dir() and str(path) != "input\\.gitignore":
        print(path.as_posix())
        transactions = read_statement(path)
        print(transactions["TableName"])
        print(len(transactions["Rows"]))

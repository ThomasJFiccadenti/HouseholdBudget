import csv
import tkinter as tk
import sqlite3
from pathlib import Path
from tkinter import filedialog

DB_PATH = "./cache/BudgetApp.py"

class Model:
    DEFAULT_DIR = Path("./input/")

    def __init__(self):
        self.bank_stmt_directory = Model.DEFAULT_DIR

        bank_reader = Bankreader(self.bank_stmt_directory)
        test = bank_reader.load_transactions()
        print(len(test))


class View(tk.Tk):
    BROWSE_FIELD_PLACEHOLDER = "Bank Statement Directory Path"
    BROWSE_FIELD_CHAR_LEN = 50

    def __init__(self):
        super().__init__()
        self.title("Budget App")
        # self.minsize(1000, 300)
        # self.maxsize(1000, 300)
        self.geometry("1000x300+50+50")

        self._init_ui()

    def _init_ui(self):
        # define window grid
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._init_browse_page()

    def _init_browse_page(self):
        # define browse page structure (center content in window)
        self.browse_page = tk.Frame(self)
        self.browse_page.grid(row=0, column=0)

        # define 2 space frames and 1 content frame in browse page
        upper_frame = tk.Frame(self.browse_page)
        self.content_frame = tk.Frame(self.browse_page)
        lower_frame = tk.Frame(self.browse_page)

        # enter space and content frames onto browse page grid
        upper_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid(row=1, column=0)
        lower_frame.grid(row=2, column=0, sticky="nsew")

        # define title
        title = tk.Label(
            self.content_frame,
            text="Tom & Hilda Budget App",
            font=("Arial", 18, "bold"),
        )
        title.grid(row=0, column=0, pady=(0, 20))

        # define path entry field
        self.browse_field = tk.Entry(
            self.content_frame,
            width=View.BROWSE_FIELD_CHAR_LEN,
            font=("Segoe UI", 14),
        )
        self.browse_field.grid(row=1, column=0)
        self.browse_field.bind("<FocusIn>", self.browse_field_clear_placeholder)
        self.browse_field.bind("<FocusOut>", self.browse_field_escape)
        self.browse_field.bind("<Escape>", self.browse_field_escape)
        self.browse_field.insert(0, View.BROWSE_FIELD_PLACEHOLDER)
        self.browse_field.config(fg="gray")

        # define file system browse button
        self.browse_button = tk.Button(
            self.content_frame, text="Browse", font=("Segoe UI", 14)
        )
        self.browse_button.grid(row=1, column=1)

        # define browse page grid - rows
        self.browse_page.rowconfigure(0, weight=1)
        self.browse_page.rowconfigure(1, weight=0, minsize=100)
        self.browse_page.rowconfigure(2, weight=1)

        # define browse page grid = cols
        self.browse_page.columnconfigure(0, weight=1)

    def browse_field_clear_placeholder(self, event):
        # Only clear if the text is exactly the placeholder
        if event.widget.get() == View.BROWSE_FIELD_PLACEHOLDER:
            event.widget.delete(0, tk.END)
            self.browse_field.config(fg="black")

    def update_browse_field(self, new_directory: str):
        if new_directory != "":
            self.browse_field.delete(0, tk.END)
            self.browse_field.insert(0, new_directory)
            self.browse_field.config(fg="black")

    def browse_field_escape(self, event):
        if self.browse_field.get() == "":
            self.browse_field.insert(0, View.BROWSE_FIELD_PLACEHOLDER)
            self.browse_field.config(fg="gray")
        else:
            if len(self.browse_field.get()) > View.BROWSE_FIELD_CHAR_LEN:
                self.browse_field.xview(tk.END)

        self.focus_set()


class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view

        self._bind_events()

    def _bind_events(self):
        self.view.browse_button.config(command=self._handle_browse_btn)

    def _handle_browse_btn(self):
        seleced_path = filedialog.askdirectory(
            title="Select a Folder", initialdir="./", mustexist=True
        )
        self.model.bank_stmt_directory = seleced_path
        self.view.update_browse_field(self.model.bank_stmt_directory)
        self.view.browse_field.xview(tk.END)

    def extract_foldername(dir_path: str):
        return


class Bankreader:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def load_transactions(self):
        all_transactions = []
        for path in self.root_dir.rglob("*"):
            if (
                not path.is_dir()
                and str(path) != "input\\.gitignore"
                and str(path) != "input\\output.csv"
            ):
                print(path.as_posix())
                all_transactions += Bankreader._get_transactions(path.as_posix())

        return all_transactions

    def _get_transactions(statement_csv_path: str):
        folder_name = statement_csv_path.split("/")[-2]

        with open(statement_csv_path, mode="r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)

            if folder_name in ("BOABlueCard5511", "BOARedCard3924"):
                transactions = Bankreader._read_boa_cc_stmt(csv_reader)
            elif folder_name == "BOAChecking3236":
                transactions = Bankreader._read_boa_checking(csv_reader)
            elif folder_name == "ValleyHYS8300":
                transactions = Bankreader._read_valley_hys(csv_reader)
            elif folder_name == "AmazonChase4147":
                transactions = Bankreader._read_chase_card(csv_reader)
            elif folder_name == "AmazonOrders":
                transactions = Bankreader._read_amazon_purchases(csv_reader)
            else:
                raise RuntimeError("Folder Not Recognized")

            return transactions

        return None

    def _read_boa_cc_stmt(csv_reader):
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

    def _read_boa_checking(csv_reader):
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

    def _read_valley_hys(csv_reader):
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

    def _read_chase_card(csv_reader):
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
    def _read_amazon_purchases(csv_reader):
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

class sqliteDB:
    def __init__(self, db_path:str):
        self.conn = sqlite3.connect(db_path)
app_model = Model()
app_view = View()
app_controller = Controller(app_model, app_view)

app_view.mainloop()

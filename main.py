import tkinter as tk

root = tk.Tk()

root.title("Budget App")
root.minsize(200, 200)
root.maxsize(500, 500)
root.geometry("300x300+50+50")

tk.Label(root, text="Nothing will work unless you do.").pack()
tk.Label(root, text="- Maya Angelou").pack()

root.mainloop()
# CARDS_CSV = "./input/cards.csv"
# STATEMENT_DIR = "./input/"


# def get_cards(cards_csv_path: str):
#     out = []
#     with open(cards_csv_path) as config_file:
#         config_reader = csv.reader(config_file)
#         next(config_reader)  # skip header
#         for row in config_reader:
#             out.append({"card_no": row[0], "card_name": row[1]})

#     return out

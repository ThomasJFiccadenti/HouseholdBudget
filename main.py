import tkinter as tk
from tkinter import filedialog


class Model:
    DEFAULT_DIR = "./input/"

    def __init__(self):
        self._bank_stmt_directory = Model.DEFAULT_DIR

    @property
    def bank_stmt_directory(self):
        return self._directory

    @bank_stmt_directory.setter
    def bank_stmt_directory(self, new_directory):
        self._bank_stmt_directory = new_directory


class View(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Budget App")
        self.minsize(200, 200)
        self.maxsize(500, 500)
        self.geometry("300x300+50+50")

        self._init_ui()

    def _init_ui(self):
        browse_frame = tk.Frame(self)
        browse_frame.pack(expand=True, fill="x", padx=20, pady=10)

        self.browse_btn = tk.Button(browse_frame, text="Browse")
        self.browse_btn.pack(side="left", expand=True, fill="x")

        self.browse_result_label = tk.Label(self, text="Value: 0", font=("Arial", 16))
        self.browse_result_label.pack(expand=True, pady=10)

    def update_browse_label(self, new_directory: str):
        self.browse_result_label.config(text=new_directory)


class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view

        self.view.browse_result_label.config(text=self.model._bank_stmt_directory)
        self._bind_events()

    def _bind_events(self):
        self.view.browse_btn.config(command=self._handle_browse_btn)

    def _handle_browse_btn(self):
        seleced_path = filedialog.askdirectory(
            title="Select a Folder", initialdir="./", mustexist=True
        )
        self.model._bank_stmt_directory = seleced_path
        self.view.update_browse_label(self.model._bank_stmt_directory)


app_model = Model()
app_view = View()
app_controller = Controller(app_model, app_view)

app_view.mainloop()

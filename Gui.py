import tkinter as tk
from pathlib import Path
from tkinter import filedialog


class Model:
    DEFAULT_DIR = Path("./input/").resolve()

    def __init__(self):
        self.bank_stmt_directory = Model.DEFAULT_DIR


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


app_model = Model()
app_view = View()
app_controller = Controller(app_model, app_view)

app_view.mainloop()

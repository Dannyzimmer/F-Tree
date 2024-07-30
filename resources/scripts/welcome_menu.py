import customtkinter as ctk
from tkinter import filedialog, messagebox

# Initialize customtkinter
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class WelcomeMenu(ctk.CTk):
    def __init__(self, launch_data):
        super().__init__()

        self.launch_data = launch_data
        self.title("Database Menu")
        self.geometry("400x300")

        self.label = ctk.CTkLabel(self, text="Welcome to the Database Manager", font=("Arial", 16))
        self.label.pack(pady=20)

        self.create_button = ctk.CTkButton(self, text="Create New Database", command=self.create_database)
        self.create_button.pack(pady=10)

        self.import_button = ctk.CTkButton(self, text="Import Existing Database", command=self.import_database_menu)
        self.import_button.pack(pady=10)

        self.exit_button = ctk.CTkButton(self, text="Exit", command=self.quit)
        self.exit_button.pack(pady=10)

    def create_database(self):
        # Function to handle creating a new database
        messagebox.showinfo("Info", "Creating a new database...")

    def import_database_menu(self):
        # Function to open the import database options
        import_menu = ImportMenu(self)
        # import_menu.grab_set()
        import_menu.lift()  # Bring the import menu to the top

class ImportMenu(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Import Database")
        self.geometry("400x300")
        self.transient(parent)  # Ensure this window is always on top of the parent

        self.label = ctk.CTkLabel(self, text="Import Database from:", font=("Arial", 14))
        self.label.pack(pady=20)

        self.sqlite_button = ctk.CTkButton(self, text="SQLite File", command=self.import_sqlite)
        self.sqlite_button.pack(pady=10)

        self.tsv_button = ctk.CTkButton(self, text="TSV File", command=self.import_tsv)
        self.tsv_button.pack(pady=10)

        self.fdata_button = ctk.CTkButton(self, text="FData File", command=self.import_fdata)
        self.fdata_button.pack(pady=10)

    def import_sqlite(self):
        file_path = filedialog.askopenfilename(parent=self, filetypes=[("SQLite Files", "*.sqlite"), ("All Files", "*.*")])
        if file_path:
            messagebox.showinfo("Info", f"Importing SQLite database from {file_path}")

    def import_tsv(self):
        file_path = filedialog.askopenfilename(parent=self, filetypes=[("TSV Files", "*.tsv"), ("All Files", "*.*")])
        if file_path:
            messagebox.showinfo("Info", f"Importing TSV database from {file_path}")

    def import_fdata(self):
        file_path = filedialog.askopenfilename(parent=self, filetypes=[("FData Files", "*.fdata *.txt"), ("All Files", "*.*")])
        if file_path:
            messagebox.showinfo("Info", f"Importing FData database from {file_path}")


def launch(launch_data):
    app = WelcomeMenu(launch_data)
    app.mainloop()

if __name__ == "__main__":
    launch()

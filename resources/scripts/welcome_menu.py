import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

# Initialize customtkinter
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class WelcomeMenu(ctk.CTk):
    def __init__(self, launch_data):
        super().__init__()
        self.launch_data = launch_data
        self.title("Database Menu")
        self.current_width = 400
        self.current_height = 280
        self.geometry(f"{self.current_width}x{self.current_height}")

        self.label = ctk.CTkLabel(self, text=self.launch_data.params.software_name, font=("Arial", 16))
        self.label.pack(pady=20)

        # New
        self.create_button = ctk.CTkButton(self, text=self.launch_data.lang_manager.new_family_btn, command=self.create_database)
        self.create_button.pack(pady=10)

        # Import
        self.import_button = ctk.CTkButton(self, text=self.launch_data.lang_manager.import_family_btn, command=self.import_family_menu)
        self.import_button.pack(pady=10)

        # Exit
        self.exit_button = ctk.CTkButton(self, text=self.launch_data.lang_manager.exit, command=self.quit)
        self.exit_button.pack(pady=10)

        # Language
        icon_size = 27
        icon_dark = self.launch_data.image_manager.get_image("lang_icon_dark", height = icon_size, width = icon_size)
        self.language_button = ctk.CTkLabel(self, image=icon_dark, text="", height=icon_size, width=icon_size, bg_color='transparent', fg_color='transparent')
        self.language_combobox = ctk.CTkComboBox(self, values=self.launch_data.lang_manager.get_available_languages(), command=self.on_language_selection)
        self.language_button.pack(pady=10, padx=(40, 10), side='left')
        self.language_combobox.pack(pady=0, side='left')
        self.language_combobox.set(self.launch_data.params.language)

    def on_language_selection(self, selected_language):
        self.launch_data.params.write_param("language", selected_language)
        print(self.launch_data.params.language)

    def create_database(self):
        # Function to handle creating a new database
        messagebox.showinfo("Info", "Creating a new database...")

    # def import_database_menu(self):
    #     # Function to open the import database options
    #     import_menu = ImportMenu(self)
    #     # import_menu.grab_set()
    #     import_menu.lift()  # Bring the import menu to the top

    def import_family_menu(self):
        file_path = filedialog.askopenfilename(parent=self, 
                        filetypes=[
                            (self.launch_data.lang_manager.sqlite_file, "*.db"),
                            (self.launch_data.lang_manager.fdata_file, "*.fdata"),
                            (self.launch_data.lang_manager.tsv_file, "*.tsv"),
                            (self.launch_data.lang_manager.all_files, "*.*")
                            ])
        if file_path:
            self.launch_data.params.write_param("database", file_path)
            self.destroy()
            import GUI
            GUI.launch(self.launch_data)
    

# class ImportMenu(ctk.CTkToplevel):
#     def __init__(self, parent):
#         super().__init__(parent)
        
#         self.title("Import Database")
#         self.geometry("400x300")
#         self.transient(parent)  # Ensure this window is always on top of the parent

#         self.label = ctk.CTkLabel(self, text="Import Database from:", font=("Arial", 14))
#         self.label.pack(pady=20)

#         self.sqlite_button = ctk.CTkButton(self, text="SQLite File", command=self.import_sqlite)
#         self.sqlite_button.pack(pady=10)

#         self.tsv_button = ctk.CTkButton(self, text="TSV File", command=self.import_tsv)
#         self.tsv_button.pack(pady=10)

#         self.fdata_button = ctk.CTkButton(self, text="FData File", command=self.import_fdata)
#         self.fdata_button.pack(pady=10)

#     def import_sqlite(self):
#         file_path = filedialog.askopenfilename(parent=self, filetypes=[("SQLite Files", "*.sqlite"), ("All Files", "*.*")])
#         if file_path:
#             messagebox.showinfo("Info", f"Importing SQLite database from {file_path}")

#     def import_tsv(self):
#         file_path = filedialog.askopenfilename(parent=self, filetypes=[("TSV Files", "*.tsv"), ("All Files", "*.*")])
#         if file_path:
#             messagebox.showinfo("Info", f"Importing TSV database from {file_path}")

#     def import_fdata(self):
#         file_path = filedialog.askopenfilename(parent=self, filetypes=[("FData Files", "*.fdata *.txt"), ("All Files", "*.*")])
#         if file_path:
#             messagebox.showinfo("Info", f"Importing FData database from {file_path}")


def launch(launch_data):
    app = WelcomeMenu(launch_data)
    app.mainloop()

if __name__ == "__main__":
    launch()

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from resources.scripts.JsonManager import LaunchData
from resources.scripts.Database import Database, DatabaseTSV
from resources.scripts.widgets import TSVNewNameDialog, FileSavedInDialog, RecentDBTable

# Initialize customtkinter
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class WelcomeMenu(ctk.CTk):
    def __init__(self, launch_data: LaunchData):
        super().__init__()
        self.launch_data = launch_data
        self.title(self.launch_data.params.software_name)
        self.current_width = 600
        self.current_height = 400
        self.geometry(f"{self.current_width}x{self.current_height}")

        # Frames
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.pack(expand=0, fill='both', side='left')
        self.right_frame = ctk.CTkFrame(self, fg_color=self.launch_data.color_manager.bright_black)
        self.right_frame.pack(expand=1, fill='both', side='left')

        # Open
        self.open_button = ctk.CTkButton(self.left_frame, text=self.launch_data.lang_manager.open_family_btn, command=self.open_family_menu, width=180)
        self.open_button.pack(pady=(30, 10), padx = (30,30), anchor='w')

        # New
        self.create_button = ctk.CTkButton(self.left_frame, text=self.launch_data.lang_manager.new_family_btn, command=self.create_database, width=180)
        self.create_button.pack(pady=10, padx = (30,30), anchor='w')

        # Import
        self.import_button = ctk.CTkButton(self.left_frame, text=self.launch_data.lang_manager.import_family_btn, command=self.import_family_menu, width=180)
        self.import_button.pack(pady=(10, 0), padx = (30,30), anchor='w')

        # Exit
        self.exit_button = ctk.CTkButton(self.left_frame, text=self.launch_data.lang_manager.exit, command=self.quit, fg_color=self.launch_data.color_manager.soft_red, width=80)
        self.exit_button.pack(pady=(30, 30), padx=(30,0), anchor='sw')
        
        # Language
        icon_size = 27
        icon_dark = self.launch_data.image_manager.get_image("lang_icon_dark", height = icon_size, width = icon_size)
        self.language_icon = ctk.CTkLabel(self.left_frame, image=icon_dark, text="", height=icon_size, width=icon_size, bg_color='transparent', fg_color='transparent')
        self.language_combobox = ctk.CTkComboBox(self.left_frame, values=self.launch_data.lang_manager.get_available_languages(), command=self.on_language_selection)
        self.language_icon.pack(pady=(10, 30), padx=(30, 10), side='left', anchor='se')
        self.language_combobox.pack(pady=(10, 30), side='left', anchor='se')
        self.language_combobox.set(self.launch_data.params.language)

        # Recent files
        self.recent_table = RecentDBTable(self.right_frame, self.launch_data)
        self.recent_table.pack(anchor='center', expand=True, fill='both', pady=10, padx=10)
        self.recent_table.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, _):
        selection = self.recent_table.get_selection()
        self.launch_data.recent_manager.refresh()
        path = self.launch_data.recent_manager.get_path_from_file(selection)
        if path != 'NA':
            self.launch_data.params.write_param("database", self.launch_data.recent_manager.get_path_from_file(selection))
        # db_path = self.launch_data.recent_manager.get_path_from_file(selection)
        # self.launch_data.params.write_param("database", db_path)
            self.launch_gui(write_params=False)
    
    def launch_gui(self, write_params = True):
        database = Database(self.launch_data.params.database)
        if write_params:
            self.launch_data.params.write_param("database", self.launch_data.params.database)
        self.launch_data.recent_manager.add_file_to_recent_file(self.launch_data.params.database)
        self.destroy()
        self.launch_data.refresh()
        import GUI
        GUI.launch(self.launch_data, database)
        
    def on_language_selection(self, selected_language):
        self.launch_data.params.write_param("language", selected_language)
        self.refresh()

    def create_database(self):
        # Function to handle creating a new database
        messagebox.showinfo("Info", "Creating a new database...")

    def open_family_menu(self):
        file_path = filedialog.askopenfilename(parent=self, 
                        filetypes=[
                            (self.launch_data.lang_manager.sqlite_file, "*.db")
                            ])
        if file_path:
            if os.path.splitext(file_path)[1] in ['.db', '.DB']:
                print(file_path)
                self.launch_data.params.write_param("database", file_path)
                self.launch_data.refresh()
                self.launch_gui()
                # self.launch_data.recent_manager.add_file_to_recent_file(file_path)
                # database = Database(file_path)
                # self.destroy()
                # self.launch_data.refresh()
                # import GUI
                # GUI.launch(self.launch_data, database)

    def import_family_menu(self):
        file_path = filedialog.askopenfilename(parent=self, 
                        filetypes=[
                            (self.launch_data.lang_manager.fdata_file, "*.fdata"),
                            (self.launch_data.lang_manager.tsv_file, "*.tsv"),
                            (self.launch_data.lang_manager.all_files, "*.*")
                            ])
        if file_path:
            old_filename = os.path.basename(file_path)
            # TSV
            if os.path.splitext(file_path)[1] in ['.tsv', '.TSV']:
                filename = TSVNewNameDialog(old_filename, self.launch_data).get_input()
                database = DatabaseTSV(file_path, self.launch_data.params, database_filename=filename)
                FileSavedInDialog(self.launch_data.params.database, self.launch_data)
                self.launch_data.recent_manager.add_file_to_recent_file(self.launch_data.params.database)
                self.destroy()
                import GUI
                GUI.launch(self.launch_data, database)
            # DB (SQLite)
            elif os.path.splitext(file_path)[1] in ['.db', '.DB']:
                self.launch_data.params.write_param("database", file_path)
                database = Database(file_path)
                self.destroy()
                import GUI
                GUI.launch(self.launch_data, database)
            # FDATA
            elif os.path.splitext(file_path)[1] in ['.fdata', '.FDATA']:
                print('Selected FDATA file.')
            # Unknown
            else:
                print('Unknown file format.')
        else:
            pass

    
    def refresh(self):
        self.launch_data.lang_manager.refresh()
        self.launch_data.refresh()
        self.destroy()
        self.__init__(self.launch_data)

def launch(launch_data):
    app = WelcomeMenu(launch_data)
    app.mainloop()

if __name__ == "__main__":
    launch()

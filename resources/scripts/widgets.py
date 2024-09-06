import customtkinter as tk
from resources.scripts.JsonManager import LaunchData

class NewNameDialog(tk.CTkInputDialog):
    def __init__(
            self, old_filename, **kwargs):
        super().__init__(**kwargs)
        self.old_filename = old_filename

class TSVNewNameDialog(NewNameDialog):
    def __init__(
            self, old_filename: str, launch_data: LaunchData, **kwargs):
        self.launch_data = launch_data
        self.old_filename = old_filename
        title = self.get_title()
        message = self.get_message()
        super().__init__(self.old_filename, text=message, title=title, **kwargs)

    def get_message(self):
        raw_message : str = self.launch_data.lang_manager.import_filename_msg
        return raw_message.replace('@1', self.old_filename)
    
    def get_title(self):
        return self.launch_data.lang_manager.save_as

class FileSavedInDialog(tk.CTk):
    def __init__(self, save_path, launch_data: LaunchData, **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path
        self.launch_data = launch_data
        self.title(self.launch_data.lang_manager.info)
        self.current_width = 250
        self.current_height = 100
        self.geometry(f"{self.current_width}x{self.current_height}")

        tk.CTkLabel(self, text=self.get_message()).pack()
        tk.CTkLabel(self, text=self.save_path, font=self.launch_data.font_manager.medium).pack()
        tk.CTkButton(self, text=self.launch_data.lang_manager.ok, command=self.on_ok).pack()

    def get_message(self):
        return self.launch_data.lang_manager.file_saved_in_msg
    
    def on_ok(self):
        self.destroy()
    
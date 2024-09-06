import customtkinter as tk
from resources.scripts.JsonManager import LaunchData
from resources.scripts.tkinterClasses import Tableview
import pandas as pd

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
    
class RecentDBTable(Tableview):
    def __init__(self, parent, launch_data: LaunchData):
        self.launch_data = launch_data
        colname = self.launch_data.lang_manager.recent_files
        self.data = pd.DataFrame(self.launch_data.recent_manager.recent_files, columns=[colname])
        if len(self.data) == 0:
            self.data = pd.DataFrame(['...'], columns=[colname])
        super().__init__(parent, self.data)

    def get_selection(self)-> dict:
        selected_items = self.selection()
        if not selected_items:
            return ""
        selected_item = selected_items[0]
        values = self.item(selected_item, 'values')
        columns = self["columns"]
        dic = {columns[i]: values[i] for i in range(len(columns))}
        return str(list(dic.values())[0])
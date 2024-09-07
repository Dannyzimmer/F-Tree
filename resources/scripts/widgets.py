import customtkinter as tk
import tkinter as ttk
from resources.scripts.JsonManager import LaunchData
from resources.scripts.tkinterClasses import Tableview
import pandas as pd
import os

class NewNameDialog(tk.CTkInputDialog):
    def __init__(self, old_filename, **kwargs):
        super().__init__(**kwargs)
        self.old_filename = old_filename

# class ImportNewNameDialog(NewNameDialog):
#     def __init__(
#             self, old_filename: str, launch_data: LaunchData, **kwargs):
#         self.launch_data = launch_data
#         self.old_filename = old_filename
#         title = self.get_title()
#         message = self.get_message()
#         super().__init__(self.old_filename, text=message, title=title, **kwargs)

#     def get_message(self):
#         raw_message : str = self.launch_data.lang_manager.import_filename_msg
#         return raw_message.replace('@1', self.old_filename)
    
#     def get_title(self):
#         return self.launch_data.lang_manager.save_as

class ImportNewNameDialog(tk.CTkInputDialog):
    def __init__(self, old_filename: str, launch_data: LaunchData, **kwargs):
        self.launch_data = launch_data
        self.old_filename = old_filename
        title = self.get_title()
        message = self.get_message()
        super().__init__(text=message, title=title, **kwargs)
        self._create_widgets()

        # Event to detect changes in the Entry widget
        # self._entry.bind("<KeyRelease>", self.on_text_change, add=True)

    def get_message(self):
        raw_message: str = self.launch_data.lang_manager.import_filename_msg
        return raw_message.replace('@1', self.old_filename)

    def get_title(self):
        return self.launch_data.lang_manager.save_as

    def on_text_change(self, event=None):
        current_text = self._entry.get()
        bright_red = self.launch_data.color_manager.bright_red
        dark_red = self.launch_data.color_manager.dark_red
        # File already exists
        if self.is_filename_exists(current_text + ".db"):
            self._entry.configure(text_color=(dark_red, bright_red))  
            self._ok_button.configure(state=tk.DISABLED)  
            self._entry.unbind("<Return>", None)
        # File do not exists
        else:
            self._entry.configure(text_color=("black", "white") )  
            self._ok_button.configure(state=tk.NORMAL)
            self._entry.bind("<Return>", self._ok_event) 

    def is_filename_exists(self, filename):
        database_dir = self.launch_data.params.default_database_dir
        file_path = os.path.join(database_dir, filename)
        return os.path.exists(file_path)
    
    def _create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self._label = tk.CTkLabel(master=self,
                               width=300,
                               wraplength=300,
                               fg_color="transparent",
                               text_color=self._text_color,
                               text=self._text,
                               font=self._font)
        self._label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self._entry = tk.CTkEntry(master=self,
                               width=230,
                               fg_color=self._entry_fg_color,
                               border_color=self._entry_border_color,
                               text_color=self._entry_text_color,
                               font=self._font)
        self._entry.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        self._ok_button = tk.CTkButton(master=self,
                                    width=100,
                                    border_width=0,
                                    fg_color=self._button_fg_color,
                                    hover_color=self._button_hover_color,
                                    text_color=self._button_text_color,
                                    text='Ok',
                                    font=self._font,
                                    command=self._ok_event)
        self._ok_button.grid(row=2, column=0, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew")

        self._cancel_button = tk.CTkButton(master=self,
                                        width=100,
                                        border_width=0,
                                        fg_color=self._button_fg_color,
                                        hover_color=self._button_hover_color,
                                        text_color=self._button_text_color,
                                        text='Cancel',
                                        font=self._font,
                                        command=self._cancel_event)
        self._cancel_button.grid(row=2, column=1, columnspan=1, padx=(10, 20), pady=(0, 20), sticky="ew")

        self.after(150, lambda: self._entry.focus())  # set focus to entry with slight delay, otherwise it won't work
        self._entry.bind("<Return>", self._ok_event)
        self._entry.bind("<KeyRelease>", self.on_text_change, add=True)

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
import customtkinter as tk
from tkinter import ttk
import re
import pandas as pd

class LabelWidget:
    def __init__(self, root, label_text, row, col, label_width=10, show_label=True, **kwargs):
        self.root = root
        self.label_text = label_text
        self.row = row
        self.col = col
        self.label_width = label_width
        self.show_label = show_label
        # Frame
        self.frame = tk.CTkFrame(self.root)
        self.frame.grid(sticky='NWES', row=row, column=col, columnspan=2, padx=10, pady=5)
        if self.show_label == True:
            # Label
            self.label = tk.CTkLabel(self.frame, text=self.label_text, width=self.label_width, **kwargs)
            self.label.grid(sticky='NW', row=0, column=0, padx=10, pady=5)

class LabelEntry(LabelWidget):
    def __init__(self, root, label_text, row, col, label_width=10, show_label=True, **kwargs):
        super().__init__(root, label_text, row, col, label_width, show_label, **kwargs)
        # Widget
        self.entry = tk.CTkEntry(self.frame, **kwargs)
        self.entry.grid(sticky='E', row=0, column=2, padx=5, pady=5)

class LabelSlider(LabelWidget):
    def __init__(self, root, label_text, row, col, label_width=10, show_label=True, **kwargs):
        super().__init__(root, label_text, row, col, label_width, show_label, **kwargs)
        # Widget
        self.slider = tk.CTkSlider(self.frame, **kwargs)
        self.slider.grid(sticky='E', row=0, column=2, padx=5, pady=5)

class LabelDropdown(LabelWidget):
    def __init__(self, root, label_text, row, col, options, label_width=10, show_label=True, **kwargs):
        super().__init__(root, label_text, row, col, label_width, show_label, **kwargs)
        # Widget
        self.dropdown = tk.CTkOptionMenu(self.frame, values=options, **kwargs)
        self.dropdown.grid(sticky='E', row=0, column=2, padx=5, pady=5)

class LabelTable(LabelWidget):
    def __init__(self, root, label_text, row, col, columns, data, label_width=10, show_label=True, **kwargs):
        super().__init__(root, label_text, row, col, label_width, show_label, **kwargs)
        # Create Treeview widget
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        self.tree.grid(sticky='NEWS', row=1, column=0, columnspan=3, padx=10, pady=5)
        self.data = data

        # Define columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.W)

        # Insert data
        for row_data in data:
            self.tree.insert('', tk.END, values=row_data)

        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(sticky='NS', row=1, column=4)

    def clear(self, _=""):
        """Clears all items of the table.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def subset_table(self, pattern, column):
        self.clear()
        search = f'.*{pattern}.*'
        for row_data in self.data:
            if re.search(pattern=search, string=row_data[column]) != None:
                self.tree.insert('', tk.END, values=row_data)
    
    def select_first_item(self):
        """
        Selects the first item in the table.
        """
        items = self.tree.get_children()
        if items:
            first_item = items[0]
            self.tree.selection_set(first_item)
            self.refresh_selection()
    
    def get_focus(self):
        self.tree.get_focus()

class LabelTextbox(LabelWidget):
    def __init__(self, root, label_text, row, col, label_width=10, show_label=True, **kwargs):
        super().__init__(root, label_text, row, col, label_width, show_label, **kwargs)
        # Widget
        self.textbox = tk.CTkTextbox(self.frame, **kwargs)
        self.textbox.grid(sticky='NWES', row=1, column=0, columnspan=3, padx=10, pady=5)

class LabelButton(LabelWidget):
    def __init__(self, root, label_text, row, col, button_text, command, label_width=10, **kwargs):
        super().__init__(root, label_text, row, col, label_width, show_label, **kwargs)
        # Widget
        self.button = tk.CTkButton(self.frame, text=button_text, command=command, **kwargs)
        self.button.grid(sticky='E', row=0, column=2, padx=5, pady=5)

class Tableview(ttk.Treeview):
    def __init__(self, parent, pandasDF: pd.DataFrame):
        super().__init__(parent, show='headings')  # Oculta la columna #0
        self.data = pandasDF
        self.refresh()
        self.get_selection()

    def _add_data_rows(self):
        for _, row in self.data.iterrows():
            values = [row[col] for col in self["columns"]]
            self.insert("", tk.END, values=values)

    def _remove_all_rows(self):
        for item in self.get_children():
            self.delete(item)

    def _add_columns(self):
        self["columns"] = list(self.data.columns)
        for col in self["columns"]:
            col_width = max(self.data[col].astype(str).map(len).max(), len(col)) + 2
            self.heading(col, text=col)
            self.column(col, width=col_width * 8, stretch=True)

    def refresh(self)-> None:
        self._remove_all_rows()
        self._add_columns()
        self._add_data_rows()

    def focus_first_row(self)-> None:
        self.focus_set()
        children = self.get_children()
        if children:
            self.focus(children[0])
            self.selection_set(children[0])

    def get_selection(self)-> dict:
        selected_items = self.selection()
        if not selected_items:
            return {}

        selected_item = selected_items[0]
        values = self.item(selected_item, 'values')
        columns = self["columns"]
        return {columns[i]: values[i] for i in range(len(columns))}

def get_column_values(treeview, column):
    """
    Get all values from a specific column in a Treeview widget.

    Args:
        treeview (ttk.Treeview): The Treeview widget to extract values from.
        column (int): The column number (0 for the first column, 1 for the second, etc.).

    Returns:
        list: List of values from the specified column.
    """
    values = []
    for item in treeview.get_children():
        values.append(treeview.item(item)['values'][column])
    return values

# if __name__ == "__main__":
#     def on_button_click():
#         print("Button clicked!")

#     root = tk.CTk()
#     entry = LabelEntry(root, "Hello", 0, 0)
#     slider = LabelSlider(root, "Adjust", 1, 0)
#     dropdown = LabelDropdown(root, "Options", 2, 0, options=["Option 1", "Option 2", "Option 3"])
#     table_columns = ["Column 1", "Column 2", "Column 3"]
#     table_data = [
#         ("Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"),
#         ("Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"),
#         ("Row 3 Col 1", "Row 3 Col 2", "Row 3 Col 3")
#     ]
#     table = LabelTable(root, "Table", 3, 0, columns=table_columns, data=table_data)
#     textbox = LabelTextbox(root, "Notes", 4, 0)
#     button = LabelButton(root, "Action", 5, 0, button_text="Click Me", command=on_button_click)
#     root.resizable(False, False)
#     root.mainloop()
#!/usr/bin/env python3﻿
import customtkinter as tk
from tkinter import messagebox
from resources.scripts.Database import create_table_from_tsv, load_data_from_tsv, convert_tsv_to_sqlite
from resources.scripts.Database import Database
from resources.scripts.tkinterClasses import LabelEntry, LabelDropdown, LabelTextbox, LabelTable, get_column_values
from resources.libs.fcodes.fcodes.libs.classes.Fcode import FcodeManager
from resources.scripts.autocombobox import AutocompleteCombobox
from resources.scripts.autoentry import AutocompleteEntry
from resources.scripts.JsonManager import LangManager, ColorManager, FontManager, ParameterManager
import os
import json

parameter_path = 'resources/parameters.json'
parameter = ParameterManager(parameter_path)
db_path = parameter.database
lang = LangManager(parameter.language, parameter_path)
color = ColorManager(parameter.color_file)
font = FontManager(parameter.font_file)

class App:
    def __init__(self, root, db_path):
        self.root = root
        self.db_path = db_path
        # self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.db = Database(self.db_path)

        # Style parameters
        self.biography_height = 500
        self.biography_width = 500

        # Tab view
        self.tabview = tk.CTkTabview(self.root, width=600)
        self.tabview.grid(sticky='NEWS', row = 0, column = 1, padx = (2, 10), pady = 5)
        edit_tab = lang.tab_edit
        add_tab = lang.tab_add
        info_tab = lang.tab_info
        db_tab = lang.database
        self.tabview.add(info_tab)
        self.tabview.add(edit_tab)
        self.tabview.add(add_tab)
        self.tabview.add(db_tab)

        # Frames
        self.left_frame = tk.CTkFrame(self.root)
        self.tabview.tab(edit_tab).grid(sticky='NEWS', row = 0, column = 1, padx = (2, 10), pady = 5)
        self.left_frame.grid(sticky='NEWS', row=0, column=0, padx = 10, pady = 5)
        self.edit_tab_button_frame = tk.CTkFrame(self.tabview.tab(edit_tab))
        self.edit_tab_button_frame.grid(sticky = 'NE', row = 4, column = 0, padx = 10, pady = 10)
        
        self.table = None
        self.refresh = True
        self.select_first_row_bool = True
        if self.refresh:
            self.load_table()
            if self.select_first_row_bool:
                self.select_first_row()
                self.select_first_row_bool = False

        # Selections (Edit tab)
        self.selected_fcode = None
        self.selected_name = None
        self.selected_nickname = None
        self.selected_biography = None
        self.selected_year = None

        # Widgets Edit Tab
        self.name_entry = LabelEntry(self.tabview.tab(edit_tab), lang.name, 0, 0)
        self.name_entry.entry.configure(width = 250, placeholder_text = lang.name)
        self.nickname = LabelEntry(self.tabview.tab(edit_tab), lang.nickname, 1, 0)
        self.year = LabelEntry(self.tabview.tab(edit_tab), lang.year, 2, 0)
        self.biography = LabelTextbox(self.tabview.tab(edit_tab), lang.biography, 3, 0)
        self.biography.textbox.configure(width = self.biography_width, height = self.biography_height)
        self.table_focus = self.table.tree.item(self.table.tree.selection())
        self.save_button = tk.CTkButton(self.edit_tab_button_frame, text=lang.save, command = self.save_entries_edit)
        self.del_button = tk.CTkButton(self.edit_tab_button_frame, text=lang.delete, command=self.delete_row_edit, fg_color='#D55B5B')
        self.save_button.grid(sticky = 'NE', row = 4, column = 0, padx = 10, pady = 10)
        self.del_button.grid(sticky = 'NE', row = 4, column = 1, padx = 10, pady = 10)

        # Widgets Add Tab
        self.name_fcode_addt_frame = tk.CTkFrame(self.tabview.tab(add_tab))
        self.name_fcode_addt_frame.grid_columnconfigure(0, weight=2)
        self.name_fcode_addt_frame.grid(sticky='NEWS', row=0, column=0, columnspan=2)
        self.name_entry_addt = LabelEntry(self.name_fcode_addt_frame, lang.name, 0, 0)
        self.name_entry_addt.entry.configure(width = 200)
        self.fcode_entry_addt = LabelEntry(self.name_fcode_addt_frame, "Fcode", 0, 1)
        self.nickname_addt = LabelEntry(self.tabview.tab(add_tab), lang.nickname, 2, 0)
        self.year_addt = LabelEntry(self.tabview.tab(add_tab), lang.year, 3, 0)
        self.biography_addt = LabelTextbox(self.tabview.tab(add_tab), lang.biography, 4, 0)
        self.biography_addt.textbox.configure(width = self.biography_width, height = self.biography_height - 30)
        self.save_button = tk.CTkButton(self.tabview.tab(add_tab), text=lang.save, command = self.save_entries_add)
        self.save_button.grid(sticky = 'NE', row = 5, column = 0, padx = 10, pady = 10)

        # Widgets Information Tab
        self.info_header_frame = tk.CTkFrame(self.tabview.tab(info_tab), fg_color='gray20')
        self.info_self_label = tk.CTkLabel(self.info_header_frame, text="NA", font=font.name, text_color=color.blue_gray)
        self.info_header_frame.grid(sticky='NEWS', row=0, column=0, padx = 5, pady = (10, 10))
        self.info_self_label.grid(sticky='NWS', row=0, column=0, padx=10, pady=(10,0))

        self.year_fcode_frame = tk.CTkFrame(self.info_header_frame, fg_color='gray20')
        self.info_fcode_label = tk.CTkLabel(self.year_fcode_frame, text="", font=font.fcode, text_color='gray60')
        self.info_year_label = tk.CTkLabel(self.year_fcode_frame, text="NA", font=font.year, text_color='gray80')
        self.year_fcode_frame.grid(sticky='NEWS', row=1, column=0, padx = 10, pady = (0, 10))
        self.info_year_label.grid(sticky='NWS', row=0, column=0, padx=(0,10), pady=1)
        self.info_fcode_label.grid(sticky='NSE', row=0, column=1, padx=10, pady=1)

        self.info_spouse_label = tk.CTkLabel(self.tabview.tab(info_tab), text = lang.spouse.capitalize())
        self.info_spouse_entry = tk.CTkEntry(self.tabview.tab(info_tab))
        self.info_spouse_label.grid(sticky='NWS', row=2, column=0, padx=10, pady=(0,5))
        self.info_spouse_entry.grid(sticky='NWS', row=3, column=0, padx=15, pady=(0,5))        

        self.info_parents_label = tk.CTkLabel(self.tabview.tab(info_tab), text = lang.parents.capitalize())
        self.info_mother_entry = LabelEntry(self.tabview.tab(info_tab), "", 6, 0, show_label=False)
        self.info_father_entry = LabelEntry(self.tabview.tab(info_tab), "", 7, 0, show_label=False)
        self.info_parents_label.grid(sticky='W', row=4, column=0, padx = 10, pady = (12,0), columnspan = 2)
        self.info_mother_entry.entry.configure(placeholder_text=lang.mother, width = 250)
        self.info_father_entry.entry.configure(placeholder_text=lang.father, width = 250)
        self.info_father_entry.frame.grid(pady=0)
        self.info_spouse_entry.configure(placeholder_text=lang.spouse, width = 250)

        columns = [lang.name, lang.sibling_number]
        siblings = ()
        self.info_siblings_tree = LabelTable(self.tabview.tab(info_tab), lang.siblings, 8, 0, columns=columns, data=siblings, show_label = True)
        self.info_siblings_tree.label.grid(sticky='W')
        self.info_siblings_tree.tree.column(lang.name, width=250)
        self.info_siblings_tree.tree.configure(height=8)
        self.info_siblings_tree.frame.grid(padx=0)
        self.info_siblings_tree.tree.grid(padx=15)
        self.info_siblings_tree.label.grid(pady=(12,0))

        columns_off = [lang.name, lang.offspring_number]
        siblings_off = ()
        self.info_offspring_tree = LabelTable(self.tabview.tab(info_tab), lang.offspring, 9, 0, 
            columns=columns_off, data=siblings_off, show_label = True)
        self.info_offspring_tree.label.grid(sticky='W')
        self.info_offspring_tree.tree.column(lang.name, width=250)
        self.info_offspring_tree.tree.configure(height=8)
        self.info_offspring_tree.frame.grid(padx=0)
        self.info_offspring_tree.tree.grid(padx=15)
        self.info_offspring_tree.label.grid(pady=(10,0))

        # Database tab
        self.db_tab_frame = tk.CTkFrame(self.tabview.tab(db_tab))
        self.db_tab_frame.grid(sticky='NEWS', row=0, column=0, padx=10, pady=5)
            # import
        self.db_import_frame = tk.CTkFrame(self.db_tab_frame)
        self.db_import_frame.grid(sticky='NEWS', row=0, column=0, padx=10, pady=5)
        self.db_import_menu = tk.CTkOptionMenu(self.db_import_frame, values=[lang.from_sqlite, lang.from_tsv], width=180)
        self.db_import_label = tk.CTkLabel(self.db_import_frame, text=lang._import)
        self.db_import_button = tk.CTkButton(self.db_import_frame, text=lang._import, command=self.import_button)
        self.db_import_label.grid(sticky='NWS', row=0, column=0, padx=10, pady=5)
        self.db_import_menu.grid(sticky='NWS', row=0, column=1, padx=10, pady=5)
        self.db_import_button.grid(sticky='NWS', row=0, column=2, padx=10, pady=5)
            # export
        self.db_export_frame = tk.CTkFrame(self.db_tab_frame)
        self.db_export_frame.grid(sticky='NEWS', row=1, column=0, padx=10, pady=5)
        self.db_export_menu = tk.CTkOptionMenu(self.db_export_frame, values=[lang.to_sqlite, lang.to_tsv], width=180)
        self.db_export_label = tk.CTkLabel(self.db_export_frame, text=lang.export)
        self.db_export_button = tk.CTkButton(self.db_export_frame, text=lang.export, command=self.export_button)
        self.db_export_label.grid(sticky='NWS', row=0, column=0, padx=10, pady=5)
        self.db_export_menu.grid(sticky='NWS', row=0, column=1, padx=10, pady=5)
        self.db_export_button.grid(sticky='NWS', row=0, column=2, padx=10, pady=5)

        # self.info_siblings_label.grid(sticky='W', row=3, column=0, padx = 10, pady = 5, columnspan = 2)
        # self.name_entry_infot = LabelEntry(self.tabview.tab(info_tab), lang.father, 0, 0)
        
        self.tabview.set(info_tab)
    
    def select_first_row(self):
        self.table.tree.selection_set(self.table.tree.get_children()[0])

    def refresh_selection(self, event=''):
        self.table_focus = self.table.tree.item(self.table.tree.selection())
        self.selected_fcode = self.table_focus.get('values')[0]
        self.selected_name = self.table_focus.get('values')[1]
        self.selected_nickname = self.table_focus.get('values')[2]
        self.selected_biography = self.table_focus.get('values')[3].strip()
        self.selected_year = self.table_focus.get('values')[4]
        self.name_entry.entry.delete(0, tk.END)
        self.nickname.entry.delete(0, tk.END)
        self.year.entry.delete(0, tk.END)
        self.biography.textbox.delete(1.0, tk.END)
        # Refresh info tab
        self.info_self_label.configure(text=f'{self.selected_name}')
        self.info_fcode_label.configure(text=f'({self.selected_fcode})')
        self.info_year_label.configure(text=f'{self.selected_year}')
        self.info_father_entry.entry.delete(0, tk.END)
        self.info_father_entry.entry.insert(0,
            self.db.fbook.get_father_name(self.selected_fcode))
        self.info_mother_entry.entry.delete(0, tk.END)
        self.info_mother_entry.entry.insert(0,
            self.db.fbook.get_mother_name(self.selected_fcode))
        self.info_spouse_entry.delete(0, tk.END)
        self.info_spouse_entry.insert(0,
            self.db.fbook.get_partner_name(self.selected_fcode))

        self.current_siblings = self.db.fbook.get_siblings_name(self.selected_fcode)
        self.current_siblings_fcodes = self.db.fbook.get_siblings_code(self.selected_fcode)
        self.current_offspring = self.db.fbook.get_offspring_names(self.selected_fcode)
        self.current_offspring_fcodes = self.db.fbook.get_offspring_code(self.selected_fcode)
        # self.current_siblings_fnumbers_tmp = self.db.fbook.get_siblings_code(self.current_siblings_fcodes)
        self.current_siblings_fnumbers = [FcodeManager(i).number for i in self.current_siblings_fcodes]
        self.current_offspring_fnumbers = [FcodeManager(i).number for i in self.current_offspring_fcodes]

        rows_siblings = list(zip(self.current_siblings, self.current_siblings_fnumbers))
        rows_siblings.sort(key=lambda x: x[1])
        rows_offspring = list(zip(self.current_offspring, self.current_offspring_fnumbers))
        rows_offspring.sort(key=lambda x: x[1])

        for i in self.info_siblings_tree.tree.get_children():
            self.info_siblings_tree.tree.delete(i)
        for i in self.info_offspring_tree.tree.get_children():
            self.info_offspring_tree.tree.delete(i)

        # Insert data
        for row_data, fnumber in rows_siblings:
            self.info_siblings_tree.tree.insert('', tk.END, values=(row_data, fnumber))
        for row_data, fnumber in rows_offspring:
            self.info_offspring_tree.tree.insert('', tk.END, values=(row_data, fnumber))
        
        if self.selected_name != "None":
            self.name_entry.entry.insert(0, self.selected_name)
        if self.selected_nickname != "None":
            self.nickname.entry.insert(0, self.selected_nickname)
        if self.selected_year != "None":
            self.year.entry.insert(0, self.selected_year)
        if self.selected_biography != "None":
            self.biography.textbox.insert(1.0, self.selected_biography)
    
    def get_row_from_add_tab(self):
        """Return a row to insert in the SQLite DB from the data
        introduced in the add tab.
        """
        fcode = self.fcode_entry_addt.entry.get()
        name = self.name_entry_addt.entry.get()
        nickname = self.nickname_addt.entry.get()
        biography = self.biography_addt.textbox.get(1.0, tk.END).strip()
        year = self.year_addt.entry.get()
        result = (fcode, name, nickname, biography, year, "")
        if result[0:3] == ("", "", "", ""):
            return ("", "", "", "", "")
        return result

    def load_table(self):
        table_columns = ["Fcode", "Name", "Nickname", "Biography", "Year Born", "Notes"]
        table_data = self.db.table_shown
        self.table = LabelTable(self.left_frame, lang.table, 0, 0, columns=table_columns, data=table_data)
        self.table.tree.bind('<<TreeviewSelect>>', self.refresh_selection)
        # self.table.tree.selection_set(self.table.tree.get_children()[0])
        self.table.tree.configure(height=40)
        self.table.tree.column("Name", width=250)
        self.refresh = False
        self.table.tree.grid(columnspan=4)

        # Search frame
        column_values = get_column_values(self.table.tree, 1)
        self.search_frame = tk.CTkFrame(self.table.frame, fg_color=color.frame_background)
        self.search_frame.grid(sticky='E', row=0, column = 1, columnspan=3)
        
        # Search box
        self.search_autocom = AutocompleteEntry(self.search_frame, completevalues=column_values, width=30)
        self.search_autocom.grid(sticky='E', row=0, column=0, columnspan=3)
        self.search_button = tk.CTkButton(self.search_frame, text=lang.search, width=12, command=self.go_search_button)
        self.search_button.grid(sticky='E', row=0, column=4, padx = 10, pady = 5)
        # self.search_autocom.bind('<<ComboboxSelected>>', self.go_search_button)
        self.search_autocom.bind("<Return>", self.go_search_button)

    def select_tree_by_fcode(self, fcode):
        for item in self.table.tree.get_children():
            # Get first column value
            value = self.table.tree.item(item, 'values')[0]
            if value == fcode:
                # Select and set focus to the row
                self.table.tree.selection_set(item)
                self.table.tree.focus(item)
                self.table.tree.see(item)  # Ensure the row is visible
                break
    
    def refresh_table(self):
        self.db.update_table_shown()
        self.load_table()
        self.select_tree_by_fcode(self.selected_fcode)

    def save_entries_edit(self):
        new_biography = self.biography.textbox.get('1.0', 'end')
        new_name = self.name_entry.entry.get()
        new_year = self.year.entry.get()
        new_nickname = self.nickname.entry.get()
        self.db.update_biography(self.selected_fcode, new_biography)
        self.db.update_name(self.selected_fcode, new_name)
        self.db.update_year_born(self.selected_fcode, new_year)
        self.db.update_nickname(self.selected_fcode, new_nickname)
        # for i in self.table.tree.get_children():
        #     self.table.tree.delete(i)
        self.refresh_table()

    def clear_widgets_add(self):
        self.fcode_entry_addt.entry.delete(0, tk.END)
        self.name_entry_addt.entry.delete(0, tk.END)
        self.nickname_addt.entry.delete(0, tk.END)
        self.biography_addt.textbox.delete(1.0, tk.END)
        self.year_addt.entry.delete(0, tk.END)
    
    def save_entries_add(self):
        print('save_entries_add')
        row = self.get_row_from_add_tab()
        if row != ('','','','','',''):
            if row[0] == "":
                messagebox.showwarning(self.root, message = lang.empty_fcode_error)
            else:
                self.selected_fcode = row[0]
                self.db.insert_row(row)
                self.refresh_table()
        self.clear_widgets_add()
    
    def delete_row_edit(self):
        answer = messagebox.askokcancel(message=lang.del_confirmation)
        if answer:
            self.db.delete_row(self.selected_fcode)
            self.refresh_table()
            self.select_first_row()
            self.refresh_selection()
            print('row deleted')

    def get_selected_row(self):
        self.table_focus = self.table.tree.item(self.table.tree.selection())
        if self.table_focus != ('','','','',0,''):
            return self.table_focus
        else:
            return {'value':["NA","NA","NA","NA","NA","NA"]}

    def go_search_button(self, _=''):
        pattern = self.search_autocom.get()
        self.table.subset_table(pattern=pattern, column=1)
        self.select_first_row()
        self.refresh_selection()
        
    def import_button(self):
        option = self.db_import_menu.get()
        if option == lang.from_sqlite:
            db_file = tk.filedialog.askopenfile(mode ='r', filetypes =[('SQLite DB', '*.db')]).name
            self.db_path = db_file
            self.db = Database(self.db_path)
            self.refresh_table()
            self.refresh_selection()
        elif option == lang.from_tsv:
            self.db.close()
            db_file = tk.filedialog.askopenfile(mode ='r', filetypes =[('SQLite DB', '*.tsv')]).name
            filename = os.path.splitext(os.path.basename(db_file))[0] + '_auto.db'
            dirname = os.path.join(os.path.dirname(db_file))
            sqlite_output_file = os.path.join(dirname, filename)
            #'/private/tmp'
            convert_tsv_to_sqlite(db_file, sqlite_output_file, 'family')
            self.db_path = sqlite_output_file
            self.db = Database(self.db_path)
            self.load_table()
            self.refresh_selection()
            

    def export_button(self):
        option = self.db_export_menu.get()
        if option == lang.to_sqlite:
            db_file = tk.filedialog.asksaveasfilename(defaultextension=".db", filetypes=[('SQLite DB', '*.db')])
            if db_file:
                self.db.export_to_sqlite(db_file)
                print(f'Database exported to {db_file}')
        elif option == lang.to_tsv:
            tsv_file = tk.filedialog.asksaveasfilename(defaultextension=".tsv", filetypes=[('TSV files', '*.tsv')])
            if tsv_file:
                self.db.export_to_tsv(tsv_file)
                print(f'Database exported to {tsv_file}')
        else:
            print('No valid export option selected')
        

    # def on_closing(self):
    #     print('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    #     self.db.close()
    #     self.root.destroy()

if __name__ == "__main__":
    root = tk.CTk()
    root.title("Fcode Tools")
    root.resizable(True, True)
    app = App(root, db_path)
    root.mainloop()

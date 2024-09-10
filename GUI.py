#!/usr/bin/env python3
import customtkinter as tk
from tkinter import messagebox
from resources.scripts.Database import create_table_from_tsv, load_data_from_tsv, convert_tsv_to_sqlite
from resources.scripts.Database import Database, DatabaseTSV
from resources.scripts.tkinterClasses import LabelEntry, LabelDropdown, LabelTextbox, LabelTable, get_column_values
from resources.scripts.fcodesClasses import FamilyTreeTreeview
from resources.libs.fcodes.fcodes.libs.classes.Fcode import FcodeManager
from resources.scripts.html_report import HTMLReport
# from resources.scripts.autocombobox import AutocompleteCombobox
from resources.scripts.autoentry import AutocompleteEntry
from resources.scripts.JsonManager import LaunchData
from PIL import Image
from tkinter import filedialog
import os

class App:
    def __init__(self, root, launch_data: LaunchData, database: Database | DatabaseTSV):
        self.root = root
        self.db_path = launch_data.params.database
        self.db_filename = os.path.basename(self.db_path)
        self.launch_data = launch_data
        self.lang = launch_data.lang_manager
        self.font = launch_data.font_manager
        # self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.db = database #Database(self.db_path)

        # Style parameters
        self.biography_height = 500
        self.biography_width = 500

        # Tab view
        self.tabview = tk.CTkTabview(self.root, width=600)
        self.tabview.grid(sticky='NEWS', row = 0, column = 1, padx = (2, 10), pady = 5)
        edit_tab = self.lang.tab_edit
        add_tab = self.lang.tab_add
        info_tab = self.lang.tab_info
        db_tab = self.lang.database
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
        self.name_entry = LabelEntry(self.tabview.tab(edit_tab), self.lang.name, 0, 0)
        self.name_entry.entry.configure(width = 250, placeholder_text = self.lang.name)
        self.nickname = LabelEntry(self.tabview.tab(edit_tab), self.lang.nickname, 1, 0)
        self.year = LabelEntry(self.tabview.tab(edit_tab), self.lang.year, 2, 0)
        self.biography = LabelTextbox(self.tabview.tab(edit_tab), self.lang.biography, 3, 0)
        self.biography.textbox.configure(width = self.biography_width, height = self.biography_height)
        self.table_focus = self.table.tree.item(self.table.tree.selection())
        self.save_button = tk.CTkButton(self.edit_tab_button_frame, text=self.lang.save, command = self.save_entries_edit)
        self.del_button = tk.CTkButton(self.edit_tab_button_frame, text=self.lang.delete, command=self.delete_row_edit, fg_color='#D55B5B')
        self.save_button.grid(sticky = 'NE', row = 4, column = 0, padx = 10, pady = 10)
        self.del_button.grid(sticky = 'NE', row = 4, column = 1, padx = 10, pady = 10)

        # Widgets Add Tab
        self.name_fcode_addt_frame = tk.CTkFrame(self.tabview.tab(add_tab))
        self.name_fcode_addt_frame.grid_columnconfigure(0, weight=2)
        self.name_fcode_addt_frame.grid(sticky='NEWS', row=0, column=0, columnspan=2)
        self.name_entry_addt = LabelEntry(self.name_fcode_addt_frame, self.lang.name, 0, 0)
        self.name_entry_addt.entry.configure(width = 200)
        self.fcode_entry_addt = LabelEntry(self.name_fcode_addt_frame, "Fcode", 0, 1)
        self.nickname_addt = LabelEntry(self.tabview.tab(add_tab), self.lang.nickname, 2, 0)
        self.year_addt = LabelEntry(self.tabview.tab(add_tab), self.lang.year, 3, 0)
        self.biography_addt = LabelTextbox(self.tabview.tab(add_tab), self.lang.biography, 4, 0)
        self.biography_addt.textbox.configure(width = self.biography_width, height = self.biography_height - 30)
        self.save_button = tk.CTkButton(self.tabview.tab(add_tab), text=self.lang.save, command = self.save_entries_add)
        self.save_button.grid(sticky = 'NE', row = 5, column = 0, padx = 10, pady = 10)

        # Widgets Information Tab
        self.info_header_frame = tk.CTkFrame(self.tabview.tab(info_tab), fg_color='gray20')
        self.info_self_label = tk.CTkLabel(self.info_header_frame, text="NA", font=self.font.name, text_color=self.launch_data.color_manager.blue_gray)
        self.info_header_frame.grid(sticky='NEWS', row=0, column=0, padx = 5, pady = (10, 10))
        self.info_self_label.grid(sticky='NWS', row=0, column=0, padx=10, pady=(10,0))

        self.year_fcode_frame = tk.CTkFrame(self.info_header_frame, fg_color='gray20')
        self.info_fcode_label = tk.CTkLabel(self.year_fcode_frame, text="", font=self.font.fcode, text_color='gray60')
        self.info_year_label = tk.CTkLabel(self.year_fcode_frame, text="NA", font=self.font.year, text_color='gray80')
        self.year_fcode_frame.grid(sticky='NEWS', row=1, column=0, padx = 10, pady = (0, 10))
        self.info_year_label.grid(sticky='NWS', row=0, column=0, padx=(0,10), pady=1)
        self.info_fcode_label.grid(sticky='NSE', row=0, column=1, padx=10, pady=1)

        self.info_spouse_label = tk.CTkLabel(self.tabview.tab(info_tab), text = self.lang.spouse.capitalize())
        self.info_spouse_entry = tk.CTkEntry(self.tabview.tab(info_tab))
        self.info_spouse_label.grid(sticky='NWS', row=2, column=0, padx=10, pady=(0,5))
        self.info_spouse_entry.grid(sticky='NWS', row=3, column=0, padx=15, pady=(0,5))        

        self.info_parents_label = tk.CTkLabel(self.tabview.tab(info_tab), text = self.lang.parents.capitalize())
        self.info_mother_entry = LabelEntry(self.tabview.tab(info_tab), "", 6, 0, show_label=False)
        self.info_father_entry = LabelEntry(self.tabview.tab(info_tab), "", 7, 0, show_label=False)
        self.info_parents_label.grid(sticky='W', row=4, column=0, padx = 10, pady = (12,0), columnspan = 2)
        self.info_mother_entry.entry.configure(placeholder_text=self.lang.mother, width = 250)
        self.info_father_entry.entry.configure(placeholder_text=self.lang.father, width = 250)
        self.info_father_entry.frame.grid(pady=0)
        self.info_spouse_entry.configure(placeholder_text=self.lang.spouse, width = 250)

        columns = [self.lang.name, self.lang.sibling_number]
        siblings = ()
        self.info_siblings_tree = LabelTable(self.tabview.tab(info_tab), self.lang.siblings, 8, 0, columns=columns, data=siblings, show_label = True)
        self.info_siblings_tree.label.grid(sticky='W')
        self.info_siblings_tree.tree.column(self.lang.name, width=250)
        self.info_siblings_tree.tree.configure(height=8)
        self.info_siblings_tree.frame.grid(padx=0)
        self.info_siblings_tree.tree.grid(padx=15)
        self.info_siblings_tree.label.grid(pady=(12,0))

        columns_off = [self.lang.name, self.lang.offspring_number]
        siblings_off = ()
        self.info_offspring_tree = LabelTable(self.tabview.tab(info_tab), self.lang.offspring, 9, 0, 
            columns=columns_off, data=siblings_off, show_label = True)
        self.info_offspring_tree.label.grid(sticky='W')
        self.info_offspring_tree.tree.column(self.lang.name, width=250)
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
        self.db_import_menu = tk.CTkOptionMenu(self.db_import_frame, values=[self.lang.from_sqlite, self.lang.from_tsv], width=180)
        self.db_import_label = tk.CTkLabel(self.db_import_frame, text=self.lang._import)
        self.db_import_button = tk.CTkButton(self.db_import_frame, text=self.lang._import, command=self.import_button)
        self.db_import_label.grid(sticky='NWS', row=0, column=0, padx=10, pady=5)
        self.db_import_menu.grid(sticky='NWS', row=0, column=1, padx=10, pady=5)
        self.db_import_button.grid(sticky='NWS', row=0, column=2, padx=10, pady=5)
            # export
        self.db_export_frame = tk.CTkFrame(self.db_tab_frame)
        self.db_export_frame.grid(sticky='NEWS', row=1, column=0, padx=10, pady=5)
        self.db_export_menu = tk.CTkOptionMenu(self.db_export_frame, values=[self.lang.to_sqlite, self.lang.to_tsv], width=180)
        self.db_export_label = tk.CTkLabel(self.db_export_frame, text=self.lang.export)
        self.db_export_button = tk.CTkButton(self.db_export_frame, text=self.lang.export, command=self.export_button)
        self.db_export_label.grid(sticky='NWS', row=0, column=0, padx=10, pady=5)
        self.db_export_menu.grid(sticky='NWS', row=0, column=1, padx=10, pady=5)
        self.db_export_button.grid(sticky='NWS', row=0, column=2, padx=10, pady=5)
            # generate tree
        self.generate_tree_frame = tk.CTkFrame(self.db_tab_frame)
        self.generate_tree_frame.grid(sticky='NEWS', row=2, column=0, padx=10, pady=(20,10))
        self.generate_tree_button = tk.CTkButton(self.generate_tree_frame, text=self.lang.generate_tree, command=self.on_generate_tree)
        self.generate_tree_button.grid(sticky='NWS', row=0, column=1, padx=10, pady=5)
            # generate report
        self.generate_report_frame = tk.CTkFrame(self.db_tab_frame)
        self.generate_report_frame.grid(sticky='NEWS', row=3, column=0, padx=10, pady=5)
        self.generate_report_button = tk.CTkButton(self.generate_report_frame, text=self.lang.generate_report, command=self.on_generate_report)
        self.generate_report_button.grid(sticky='NWS', row=0, column=1, padx=10, pady=5)

        # self.info_siblings_label.grid(sticky='W', row=3, column=0, padx = 10, pady = 5, columnspan = 2)
        # self.name_entry_infot = LabelEntry(self.tabview.tab(info_tab), self.lang.father, 0, 0)
        
        self.tabview.set(info_tab)

    def on_generate_report(self):
        output_report = filedialog.asksaveasfile(mode='w', filetypes=[('PDF', '*.pdf')]).name
        HTMLReport(self.table.tree).save_report_to_pdf(output_report)
    
    def on_generate_tree(self):
        output_tree = filedialog.asksaveasfile(mode ='w', filetypes =[('PDF', '*.pdf')]).name
        FamilyTreeTreeview(self.table.tree).render_tree(filepath = output_tree)

    def select_first_row(self):
        try:
            self.table.tree.selection_set(self.table.tree.get_children()[0])
        except IndexError:
            print('No results')

    def refresh_selection(self, event=''):
        self.table_focus = self.table.tree.item(self.table.tree.selection())
        try:
            self.selected_fcode = self.table_focus.get('values')[0]
            self.selected_name = self.table_focus.get('values')[1]
            self.selected_nickname = self.table_focus.get('values')[2]
            self.selected_biography = self.table_focus.get('values')[3].strip()
            self.selected_year = self.table_focus.get('values')[4]
        except IndexError:
            # No results
            pass
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
        table_name = f'   {self.db_filename}'
        icon = tk.CTkImage(
            light_image=Image.open(self.launch_data.image_manager.database_icon),
            size=(15, 15)
            )
        self.table = LabelTable(self.left_frame, table_name, 0, 0,
                                columns=table_columns, data=table_data,
                                image=icon, compound='left')
        self.table.tree.bind('<<TreeviewSelect>>', self.refresh_selection)
        # self.table.tree.selection_set(self.table.tree.get_children()[0])
        self.table.tree.configure(height=40)
        self.table.tree.column("Name", width=250)
        self.refresh = False
        self.table.tree.grid(columnspan=4)

        # Search frame
        self.search_frame = tk.CTkFrame(self.table.frame,
                                        fg_color=(
                                            self.launch_data.color_manager.frame_foreground,
                                            self.launch_data.color_manager.frame_background)   
                                        )
        self.search_frame.grid(sticky='E', row=0, column = 1, columnspan=3, padx=10)
        
        # Column selector
        self._column_names_colnames_dict = {k:v for v, k in enumerate(self.table.tree.cget("columns"))}
        self._column_names_index_dict = {k:v for k, v in enumerate(self.table.tree.cget("columns"))}
        self.selected_column = 1
        self.column_selector = tk.CTkComboBox(self.search_frame, values=list(self._column_names_colnames_dict.keys()), command = self.on_column_selection)
        self.column_selector.grid(sticky='W', row=0, column=0, padx=10, pady=10)
        self.column_selector.set(self._column_names_index_dict[self.selected_column])

        # Search box
        self._column_values = [str(i) for i in get_column_values(self.table.tree, self.selected_column)]
        self.search_autocom = AutocompleteEntry(self.search_frame, completevalues=self._column_values, width=30)
        self.search_autocom.grid(sticky='E', row=0, column=1, columnspan=3)
        self.search_button = tk.CTkButton(self.search_frame, text=self.lang.search, width=12, command=self.go_search_button)
        self.search_button.grid(sticky='E', row=0, column=5, padx = 10, pady = 5)
        # self.search_autocom.bind('<<ComboboxSelected>>', self.go_search_button)
        self.search_autocom.bind("<Return>", self.go_search_button)

    def on_column_selection(self, event=None)-> None:
        self.selected_column = self._column_names_colnames_dict[self.column_selector.get()]
        self._column_values = [str(i) for i in get_column_values(self.table.tree, self.selected_column)]
        self.search_autocom.set_completion_list(self._column_values)

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
        self.launch_data.params.write_param('database', self.db_path)
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
                messagebox.showwarning(self.root, message = self.lang.empty_fcode_error)
            else:
                self.selected_fcode = row[0]
                self.db.insert_row(row)
                self.refresh_table()
        self.clear_widgets_add()
    
    def delete_row_edit(self):
        answer = messagebox.askokcancel(message=self.lang.del_confirmation)
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
        # Escapes the first asterisk (OC)
        if self.selected_column == 0:
            pattern = '\\' + pattern
        self.table.subset_table(pattern=pattern, column=self.selected_column)
        self.select_first_row()
        self.refresh_selection()
    
    def _refresh_db_filename(self):
        self.db_filename = os.path.basename(self.db_path)

    def import_button(self):
        option = self.db_import_menu.get()
        if option == self.lang.from_sqlite:
            db_file = tk.filedialog.askopenfile(mode ='r', filetypes =[('SQLite DB', '*.db')]).name
            self.db_path = db_file
            self._refresh_db_filename()
            self.db = Database(self.db_path)
            self.refresh_table()
            self.refresh_selection()
        elif option == self.lang.from_tsv:
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
        if option == self.lang.to_sqlite:
            db_file = tk.filedialog.asksaveasfilename(defaultextension=".db", filetypes=[('SQLite DB', '*.db')])
            if db_file:
                self.db.export_to_sqlite(db_file)
                print(f'Database exported to {db_file}')
        elif option == self.lang.to_tsv:
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

def launch(launch_data, database):
    root = tk.CTk()
    root.title(launch_data.params.software_name)
    root.resizable(False, False)
    app = App(root, launch_data, database)
    root.mainloop()

if __name__ == "__main__":
    launch()

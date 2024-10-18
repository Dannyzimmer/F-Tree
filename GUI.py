#!/usr/bin/env python3
import customtkinter as tk
from tkinter import messagebox
from resources.scripts.Database import create_table_from_tsv, load_data_from_tsv, convert_tsv_to_sqlite
from resources.scripts.Database import Database, DatabaseTSV
from resources.scripts.tkinterClasses import LabelEntry, LabelDropdown, LabelTextbox, LabelTable, get_column_values
from resources.scripts.fcodesClasses import FamilyTreeTreeview
from resources.libs.fcodes.fcodes.libs.classes.Fcode import FcodeManager
from resources.scripts.html_report import HTMLReport
# from resources.scripts.widgets import CloseOnEditingWarning# from resources.scripts.autocombobox import AutocompleteCombobox
from resources.scripts.autoentry import AutocompleteEntry
from resources.scripts.Managers import LaunchData
from PIL import Image, ImageTk
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

        self.editing_a_field = False

        # Style parameters
        self.biography_height = 500
        self.biography_width = 430

        # Tab view
        self.tabview = tk.CTkTabview(self.root, width=485, command=self.on_tab_change)
        self.tabview.grid(sticky='NEWS', row = 0, column = 1, padx = (0, 10), pady = 5)
        edit_tab = self.lang.tab_edit
        add_tab = self.lang.tab_add
        info_tab = self.lang.tab_info
        db_tab = self.lang.export
        self.tabview.add(info_tab)
        self.tabview.add(edit_tab)
        self.tabview.add(add_tab)
        self.tabview.add(db_tab)
        # self.tabview.set(add_tab)
        self.tabview.set(info_tab)

        self.active_tab = 'info_tab'

        # Frames
        self.left_frame = tk.CTkFrame(self.root)
        self.tabview.tab(edit_tab).grid(sticky='NEWS', row = 0, column = 1, padx = (2, 10), pady = 5)
        self.left_frame.grid(sticky='NEWS', row=0, column=0, padx = 10, pady = 5)
        
        self.table = None
        self.refresh = True
        self.select_first_row_bool = True
        if self.refresh:
            self.load_table()
            if self.select_first_row_bool:
                self.select_first_row()
                self.select_first_row_bool = False
        
        # Edit tab
        #-----------------------------------------------------------------------
        # Selections (Edit tab)
        self.selected_fcode = None
        self.selected_name = None
        self.selected_nickname = None
        self.selected_biography = None
        self.selected_year = None

        # Widgets Edit Tab
        tab_elements_style = {"sticky":'NWS', "padx":(15, 10), "pady": 5}
        edt_fcode_frame_elements_style = {"sticky": "NES", "padx":10, "pady": 5}

        self.edit_tab_button_frame = tk.CTkFrame(self.tabview.tab(edit_tab))
        self.edit_tab_button_frame.grid(sticky = 'NE', row = 4, column = 0, padx = 10, pady = 10)

        self.edt_fcode_frame = tk.CTkFrame(self.tabview.tab(edit_tab), fg_color=('#b0b0b0', '#3b3b3b'))
        self.edt_fcode_frame.grid(sticky='NEWS', row=0, column=0, columnspan=2, padx=10, pady=10)
        self.edt_fcode_frame.grid_columnconfigure(0, weight=2)

        self.edt_title_label = tk.CTkLabel(self.edt_fcode_frame, text=self.launch_data.lang_manager.tab_edit.upper(), **self.launch_data.widget_style_manager.edit_tab['section_title'])
        self.edt_fcode_label = tk.CTkLabel(self.edt_fcode_frame, text = 'Fcode')
        self.edt_fcode_entry = tk.CTkEntry(self.edt_fcode_frame)
        self.edt_title_label.grid(sticky='NWS', row=0, column=0, padx=(15, 10), pady=5)
        self.edt_fcode_label.grid(row=0, column=1, **edt_fcode_frame_elements_style)
        self.edt_fcode_entry.grid(row=0, column=2, **edt_fcode_frame_elements_style)

        self.edt_middle_frame = tk.CTkFrame(self.tabview.tab(edit_tab))
        self.edt_middle_frame.grid(sticky='NEWS', row=1, column=0, columnspan=2, padx=10, pady=10)

        self.edt_name_label = tk.CTkLabel(self.edt_middle_frame, text = self.lang.name)
        self.edt_nickname_label = tk.CTkLabel(self.edt_middle_frame, text = self.lang.nickname)
        self.edt_year_label = tk.CTkLabel(self.edt_middle_frame, text = self.lang.year)
        self.edt_name_label.grid(row=0, column=0, **tab_elements_style)
        self.edt_nickname_label.grid(row=1, column=0, **tab_elements_style)
        self.edt_year_label.grid(row=2, column=0, **tab_elements_style)

        self.edt_name_entry = tk.CTkEntry(self.edt_middle_frame, width=300)
        self.edt_nickname_entry = tk.CTkEntry(self.edt_middle_frame, width=300)
        self.edt_year_entry = tk.CTkEntry(self.edt_middle_frame)
        self.edt_name_entry.grid(row=0, column=1, **tab_elements_style)
        self.edt_nickname_entry.grid(row=1, column=1, **tab_elements_style)
        self.edt_year_entry.grid(row=2, column=1, **tab_elements_style)

        self.edt_biography = LabelTextbox(self.tabview.tab(edit_tab), self.lang.biography, 3, 0)
        self.edt_biography.textbox.configure(width = self.biography_width, height = self.biography_height)
        self.table_focus = self.table.tree.item(self.table.tree.selection())
        self.save_button = tk.CTkButton(self.edit_tab_button_frame, text=self.lang.save, command = self.save_entries_edit)
        self.del_button = tk.CTkButton(self.edit_tab_button_frame, text=self.lang.delete, command=self.delete_row_edit, fg_color='#D55B5B')
        self.save_button.grid(sticky = 'NE', row = 4, column = 0, padx = 10, pady = 10)
        self.del_button.grid(sticky = 'NE', row = 4, column = 1, padx = 10, pady = 10)

        # Edition detection
        self.edt_fcode_entry.bind('<Key>', command=self.on_edition)
        self.edt_name_entry.bind('<Key>', command=self.on_edition)
        self.edt_nickname_entry.bind('<Key>', command=self.on_edition)
        self.edt_year_entry.bind('<Key>', command=self.on_edition)
        self.edt_biography.textbox.bind('<Key>', command=self.on_edition)

        # Widgets Add Tab
        #-----------------------------------------------------------------------
        addt_fcode_frame_elements_style = {"padx":10, "pady": 5}

        self.addt_fcode_frame = tk.CTkFrame(self.tabview.tab(add_tab), fg_color=('#b0b0b0', '#3b3b3b'))
        self.addt_fcode_frame.grid_columnconfigure(0, weight=2)
        self.addt_fcode_frame.grid(sticky='NEWS', row=0, column=0, columnspan=2, padx=10, pady=10)

        self.addt_title_label = tk.CTkLabel(self.addt_fcode_frame, text=self.launch_data.lang_manager.tab_add.upper(), **self.launch_data.widget_style_manager.add_tab['section_title'])
        self.addt_fcode_label = tk.CTkLabel(self.addt_fcode_frame, text = 'Fcode')
        self.addt_fcode_entry = tk.CTkEntry(self.addt_fcode_frame)
        self.addt_title_label.grid(sticky='NWS', row=0, column=0, padx=(15, 10), pady=5)
        self.addt_fcode_label.grid(sticky='NES', row=0, column=0, **addt_fcode_frame_elements_style)
        self.addt_fcode_entry.grid(sticky='NWS',row=0, column=1, **addt_fcode_frame_elements_style)

        self.addt_middle_frame = tk.CTkFrame(self.tabview.tab(add_tab))
        self.addt_middle_frame.grid(sticky='NEWS', row=1, column=0, columnspan=2, padx=10, pady=10)

        self.addt_name_label = tk.CTkLabel(self.addt_middle_frame, text=self.lang.name)
        self.addt_name_entry = tk.CTkEntry(self.addt_middle_frame, width = 300)
        self.addt_name_label.grid(row = 1, column = 0, **tab_elements_style)
        self.addt_name_entry.grid(row = 1, column = 1, **tab_elements_style)

        self.addt_nickname_label = tk.CTkLabel(self.addt_middle_frame, text = self.lang.nickname)
        self.addt_nickname_entry = tk.CTkEntry(self.addt_middle_frame, width=300)
        self.addt_nickname_label.grid(row = 3, column = 0, **tab_elements_style)
        self.addt_nickname_entry.grid(row = 3, column = 1, **tab_elements_style)
        
        self.addt_year_label = tk.CTkLabel(self.addt_middle_frame, text = self.lang.year)
        self.addt_year_entry = tk.CTkEntry(self.addt_middle_frame)
        self.addt_year_label.grid(row=4, column=0, **tab_elements_style)
        self.addt_year_entry.grid(row=4, column=1, **tab_elements_style)

        self.addt_biography = LabelTextbox(self.tabview.tab(add_tab), self.lang.biography, 5, 0)
        self.addt_biography.textbox.configure(width = self.biography_width, height = self.biography_height)
        self.save_button = tk.CTkButton(self.tabview.tab(add_tab), text=self.lang.save, command = self.save_entries_add)
        self.save_button.grid(sticky = 'NE', row = 6, column = 0, padx = 10, pady = 10)

        # Edition detection
        self.addt_fcode_entry.bind('<Key>', command=self.on_edition)
        self.addt_name_entry.bind('<Key>', command=self.on_edition)
        self.addt_nickname_entry.bind('<Key>', command=self.on_edition)
        self.addt_year_entry.bind('<Key>', command=self.on_edition)
        self.addt_biography.textbox.bind('<Key>', command=self.on_edition)

        # Widgets Information Tab
        #-----------------------------------------------------------------------
        info_style_data_grid = self.launch_data.widget_style_manager.info_data['data_labels_grid']
        info_style_data_style = self.launch_data.widget_style_manager.info_data['data_labels_style']
        info_style_section = self.launch_data.widget_style_manager.info_data['section_labels_style']
        info_style_section_frames = self.launch_data.widget_style_manager.info_data['main_frame_grid']
        info_style_header_frame = self.launch_data.widget_style_manager.info_data['header_frame']
        info_style_header_title_style = self.launch_data.widget_style_manager.info_data['main_frame_title_style']
        
        # Main frame
        self.info_main_frame = tk.CTkFrame(self.tabview.tab(info_tab))
        self.info_main_frame.grid(**info_style_section_frames)
        
        # Header
        self.info_header_frame = tk.CTkFrame(self.info_main_frame, **info_style_header_frame)
        self.info_self_label = tk.CTkLabel(self.info_header_frame, **info_style_header_title_style)
        self.info_header_frame.grid(sticky='NEWS', row=0, column=0, padx = 5, pady = (10, 10), columnspan=3)
        self.info_self_label.grid(sticky='NWS', row=0, column=0, padx=10, pady=(10,0))

        self.year_fcode_frame = tk.CTkFrame(self.info_header_frame, fg_color='transparent')
        self.info_fcode_label = tk.CTkLabel(self.year_fcode_frame, text="", font=self.font.fcode, text_color=('#7a7a7a', 'gray60'))
        self.info_year_label = tk.CTkLabel(self.year_fcode_frame, text="NA", font=self.font.year, text_color=('#575757', 'gray80'))
        self.year_fcode_frame.grid(sticky='NEWS', row=1, column=0, padx = 10, pady = (0, 10))
        self.info_year_label.grid(sticky='NWS', row=0, column=0, padx=(0,10), pady=1)
        self.info_fcode_label.grid(sticky='NSE', row=0, column=1, padx=10, pady=1)

        # Spouse
        self.info_spouse_label = tk.CTkLabel(self.info_main_frame, text = self.lang.spouse.capitalize(), **info_style_section)
        self.info_spouse_data_label = tk.CTkLabel(self.info_main_frame, **info_style_data_style)
        self.info_spouse_label.grid(sticky='NWS', row=2, column=0, padx=10, pady=(0,5))
        self.info_spouse_data_label.grid(row=3, **info_style_data_grid)        

        # Parents
        self.info_mother_data_label = tk.CTkLabel(self.info_main_frame, **info_style_data_style)
        self.info_father_data_label = tk.CTkLabel(self.info_main_frame, **info_style_data_style)
        self.info_mother_data_label.grid(row=5, **info_style_data_grid)
        self.info_father_data_label.grid(row=6, **info_style_data_grid)
        
        self.info_parents_label = tk.CTkLabel(self.info_main_frame, text = self.lang.parents.capitalize(), **info_style_section)
        self.info_parents_label.grid(sticky='W', row=4, column=0, padx = 10, pady = (12,0), columnspan = 2)

        # Siblings
        columns = [self.lang.name, self.lang.sibling_number]
        siblings = ()
        self.info_siblings_tree = LabelTable(
            self.info_main_frame, 
            self.lang.siblings, 8, 0,
            columns=columns, data=siblings, 
            launch_data=self.launch_data,
            show_label = True, 
            **info_style_section
            )
        self.info_siblings_tree.label.grid(sticky='W')
        self.info_siblings_tree.tree.column(self.lang.name, width=250)
        self.info_siblings_tree.tree.configure(height=8)
        self.info_siblings_tree.frame.grid(padx=0)
        self.info_siblings_tree.tree.grid(padx=15)
        self.info_siblings_tree.label.grid(pady=(12,0))

        # Offspring
        columns_off = [self.lang.name, self.lang.offspring_number]
        siblings_off = ()
        self.info_offspring_tree = LabelTable(
            self.info_main_frame, self.lang.offspring, 9, 0, 
            columns=columns_off, launch_data=self.launch_data,
            data=siblings_off, show_label = True, 
            **info_style_section
            )
        self.info_offspring_tree.label.grid(sticky='W')
        self.info_offspring_tree.tree.column(self.lang.name, width=250)
        self.info_offspring_tree.tree.configure(height=8)
        self.info_offspring_tree.frame.grid(padx=0)
        self.info_offspring_tree.tree.grid(padx=15)
        self.info_offspring_tree.label.grid(pady=(10,0))

        # Database tab
        #-----------------------------------------------------------------------
        self.db_tab_frame = tk.CTkFrame(self.tabview.tab(db_tab))
        self.db_tab_frame.grid(sticky='NEWS', row=0, column=0, padx=10, pady=5)

            # export
        self.db_export_frame = tk.CTkFrame(self.db_tab_frame)
        self.db_export_frame.grid(sticky='NEWS', row=1, column=0, padx=10, pady=5)
        self.db_export_label = tk.CTkLabel(self.db_export_frame, text=self.lang.export)
        self.db_export_menu = tk.CTkOptionMenu(self.db_export_frame, values=[self.lang.to_sqlite, self.lang.to_tsv], width=180)
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

    def on_tab_change(self):
        self.active_tab = self.tabview.get()
        self.update_initial_fcode()

    def update_initial_fcode(self):
        tabs = [self.launch_data.lang_manager.tab_edit, 
                self.launch_data.lang_manager.tab_add]
        if self.active_tab == tabs[0]:
            fcode = self.edt_fcode_entry.get()
            if fcode not in ['', None]:
                self.initial_fcode = self.edt_fcode_entry.get()
        elif self.active_tab == tabs[1]:
            fcode = self.edt_fcode_entry.get()
            if fcode not in ['', None]:
                self.initial_fcode = self.addt_fcode_entry.get()

    def on_generate_report(self):
        output_report = filedialog.asksaveasfile(mode='w', filetypes=[('PDF', '*.pdf')]).name
        HTMLReport(self.table.tree).save_report_to_pdf(output_report)

        try:
            import subprocess
            if os.name == 'posix':  # Unix-like OS (Linux, macOS)
                subprocess.run(['xdg-open', output_report])
            elif os.name == 'nt':  # Windows
                subprocess.run(['start', output_report], shell=True)
            else:
                print("Unsupported OS.")
        except Exception as e:
            print(f"Failed to open PDF: {e}")
    
    def on_generate_tree(self):
        output_tree = filedialog.asksaveasfile(mode ='w', filetypes =[('PDF', '*.pdf')]).name
        FamilyTreeTreeview(self.table.tree).render_tree(filepath = output_tree)

    def on_edition(self, event=None):
        self.set_editing_on()

    def select_first_row(self):
        try:
            self.table.tree.selection_set(self.table.tree.get_children()[0])
            self.update_initial_fcode()
        except IndexError:
            print('No results')

    def refresh_selection(self, event=''):
        if self.editing_a_field == True:
            self.warning_no_save()

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
        self.edt_fcode_entry.delete(0, tk.END)
        self.edt_name_entry.delete(0, tk.END)
        self.edt_nickname_entry.delete(0, tk.END)
        self.edt_year_entry.delete(0, tk.END)
        self.edt_biography.textbox.delete(1.0, tk.END)
        # Refresh info tab
        self.info_self_label.configure(text=f'{self.selected_name}')
        self.info_fcode_label.configure(text=f'({self.selected_fcode})')
        self.info_year_label.configure(text=f'{self.selected_year}')
        self.info_father_data_label.configure(text=self.db.fbook.get_father_name(self.selected_fcode))
        self.info_mother_data_label.configure(text=self.db.fbook.get_mother_name(self.selected_fcode))
        self.info_spouse_data_label.configure(text=self.db.fbook.get_partner_name(self.selected_fcode))

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
        
        if self.selected_fcode != "None":
            self.edt_fcode_entry.insert(0, self.selected_fcode)
        if self.selected_name != "None":
            self.edt_name_entry.insert(0, self.selected_name)
        if self.selected_nickname != "None":
            self.edt_nickname_entry.insert(0, self.selected_nickname)
        if self.selected_year != "None":
            self.edt_year_entry.insert(0, self.selected_year)
        if self.selected_biography != "None":
            self.edt_biography.textbox.insert(1.0, self.selected_biography)
        self.update_initial_fcode()

    def set_editing_on(self):
        self.editing_a_field = True

    def set_editing_off(self):
        self.editing_a_field = False
    
    def get_row_from_add_tab(self):
        """Return a row to insert in the SQLite DB from the data
        introduced in the add tab.
        """
        fcode = self.addt_fcode_entry.get()
        name = self.addt_name_entry.get()
        nickname = self.addt_nickname_entry.get()
        biography = self.addt_biography.textbox.get(1.0, tk.END).strip()
        year = self.addt_year_entry.get()
        result = (fcode, name, nickname, biography, year, "")
        if result[0:3] == ("", "", "", ""):
            return ("", "", "", "", "")
        return result

    def load_table(self):
        # table_columns_ori = ["Fcode", "Name", "Nickname", "Biography", "Year Born", "Notes"]
        table_columns = [
            self.launch_data.lang_manager.fcode,
            self.launch_data.lang_manager.name,
            self.launch_data.lang_manager.nickname,
            self.launch_data.lang_manager.biography,
            self.launch_data.lang_manager.year
        ]

        table_data = self.db.table_shown
        table_name = f'   {self.db_filename}'
        icon = tk.CTkImage(
            light_image=Image.open(self.launch_data.image_manager.database_icon),
            size=(15, 15)
            )
        self.table = LabelTable(self.left_frame, table_name, 0, 0,
                                columns=table_columns, data=table_data,
                                launch_data=self.launch_data,
                                image=icon, compound='left')
        self.table.tree.bind('<<TreeviewSelect>>', self.refresh_selection)
        # self.table.tree.selection_set(self.table.tree.get_children()[0])
        self.table.tree.configure(height=40)
        self.table.tree.column(self.launch_data.lang_manager.name, width=250)
        self.table.tree.column(self.launch_data.lang_manager.nickname, width=150)
        self.table.tree.column(self.launch_data.lang_manager.year, width=120)
        self.table.tree["displaycolumns"] = table_columns[0:3] + [table_columns[-1]]
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
        self.column_selector = tk.CTkComboBox(self.search_frame, values=list(self._column_names_colnames_dict.keys()), command = self.on_column_selection, state='readonly')
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
        self.update_initial_fcode()

    def is_fcode_in_database(self, fcode: str, exclude=[])-> bool:
        database = [i.code for i in self.db.fbook.all_fcodes if i.code not in exclude]
        return fcode in database

    def show_error_fcode_exists(self, fcode: str):
        message = self.launch_data.lang_manager.error_fcode_exists.replace('@1', fcode)
        messagebox.showerror(title='', message=message)

    def save_entries_edit(self):
        new_fcode = self.edt_fcode_entry.get()
        new_biography = self.edt_biography.textbox.get('1.0', 'end')
        new_name = self.edt_name_entry.get()
        new_year = self.edt_year_entry.get()
        new_nickname = self.edt_nickname_entry.get()
        self.db.refresh()
        if self.is_fcode_in_database(new_fcode, [self.initial_fcode]):
            self.show_error_fcode_exists(new_fcode)
            self.edt_fcode_entry.delete(0, tk.END)
            self.edt_fcode_entry.insert(0, self.initial_fcode)
        else:
            self.db.update_fcode(self.initial_fcode, new_fcode)
            self.db.update_biography(self.selected_fcode, new_biography)
            self.db.update_name(self.selected_fcode, new_name)
            self.db.update_year_born(self.selected_fcode, new_year)
            self.db.update_nickname(self.selected_fcode, new_nickname)
            # for i in self.table.tree.get_children():
            #     self.table.tree.delete(i)
            self.refresh_table()
            self.db.refresh()
            self.set_editing_off()

    def clear_widgets_add(self):
        self.addt_fcode_entry.delete(0, tk.END)
        self.addt_name_entry.delete(0, tk.END)
        self.addt_nickname_entry.delete(0, tk.END)
        self.addt_biography.textbox.delete(1.0, tk.END)
        self.addt_year_entry.delete(0, tk.END)

    def save_entries_add(self):
        row = self.get_row_from_add_tab()
        if row != ('','','','','',''):
            if row[0] == "":
                messagebox.showwarning(self.root, message = self.lang.empty_fcode_error)
            else:
                if self.is_fcode_in_database(row[0]):
                    self.show_error_fcode_exists(row[0])
                    self.addt_fcode_entry.delete(0, tk.END)
                else:
                    self.db.insert_row(row)
                    self.refresh_table()
                    self.clear_widgets_add()
                    self.db.refresh()
                    self.set_editing_off()
                    self.selected_fcode = row[0]
    
    def delete_row_edit(self):
        message = f'{self.lang.del_confirmation} ({self.selected_fcode}).'
        answer = messagebox.askokcancel(message=message)
        if answer:
            self.db.delete_row(self.selected_fcode)
            self.refresh_table()
            self.select_first_row()
            self.refresh_selection()
            self.db.refresh()
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

    def warning_no_save(self):
        message = self.launch_data.lang_manager.warning_no_save
        do_i_save = messagebox.askyesnocancel(title=None, message=message)
        if do_i_save == True:
            if self.active_tab == self.launch_data.lang_manager.tab_edit:
                self.save_entries_edit()
            elif self.active_tab == self.launch_data.lang_manager.tab_add:
                self.save_entries_add()
        if do_i_save == False:
            self.clear_widgets_add()
            self.set_editing_off()


def is_darkmode_enabled(root: tk.CTk)-> bool: #FIXME
    current_theme = root._get_appearance_mode()
    return True if current_theme == 'dark' else False

def get_icon(root: tk.CTk, launch_data: LaunchData)-> ImageTk: #FIXME
    # if is_darkmode_enabled(root):
    #     icon = launch_data.image_manager.software_simple_icon_dark
    # else:
    #     icon = launch_data.image_manager.software_simple_icon_dark
    key = launch_data.params.icon
    icon = launch_data.image_manager.__dict__[key]
    return ImageTk.PhotoImage(file=icon)

def launch(launch_data, database):
    root = tk.CTk()
    root.iconpath = get_icon(root, launch_data)
    root.wm_iconbitmap()
    root.iconphoto(False, root.iconpath)

    root.title(launch_data.params.software_name)
    current_width = 1192
    current_height = 902
    root.geometry(f"{current_width}x{current_height}")
    root.resizable(False, False)
    # CloseOnEditingWarning()
    app = App(root, launch_data, database)
    root.mainloop()

if __name__ == "__main__":
    launch()

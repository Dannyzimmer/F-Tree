import sqlite3
import os
import csv
from resources.libs.fcodes.fcodes.libs.classes.FBook import FBook
from resources.scripts.JsonManager import ParameterManager

def create_table_from_tsv(tsv_file, sqlite_file, sqlite_table):
    # Connect to SQLite database (create if it doesn't exist)
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    # Remove the table if exists
    cursor.execute(f"DROP TABLE IF EXISTS {sqlite_table}")

    # Create table in SQLite
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {sqlite_table} (
            "fcode"	TEXT,
            "name"	TEXT,
            "nickname"	TEXT,
            "biography"	TEXT,
            "yearBorn"	INTEGER,
            "notes"	TEXT
        )
        ''')

    # Save changes and close connection
    conn.commit()
    conn.close()

def load_data_from_tsv(tsv_file, sqlite_file, sqlite_table):
    # Connect to SQLite database
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    # Read TSV file and load data into SQLite
    with open(tsv_file, 'r', newline='', encoding='utf-8') as file:
        tsv_reader = csv.reader(file, delimiter='\t')
        next(tsv_reader)  # Skip header row if it exists

        # Insert each row from TSV file into SQLite table
        for row in tsv_reader:
            cursor.execute(f'''
                INSERT INTO {sqlite_table} (fcode, name, nickname, biography, yearBorn, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', row)

    # Save changes and close connection
    conn.commit()
    conn.close()

def convert_tsv_to_sqlite(tsv_file, sqlite_file, sqlite_table):
    # Create table in SQLite
    create_table_from_tsv(tsv_file, sqlite_file, sqlite_table)

    # Load data from TSV file to SQLite
    load_data_from_tsv(tsv_file, sqlite_file, sqlite_table)

    print(f'Successfully converted TSV file "{tsv_file}" to SQLite "{sqlite_file}".')

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()
        self.col_filter = '*'
        self.table_shown = self.get_table_shown()
        self.current_row = ()
        self.n_fields = self.get_column_count()
        self.fbook = FBook(self.db_path)

    def get_column_count(self):
        self.cur.execute(f"SELECT * FROM family LIMIT 1")
        return len(self.cur.description)

    def get_table_shown(self):
        code = f"""SELECT {self.col_filter} FROM family"""
        result = list(self.cur.execute(code))
        return result

    def connect(self):
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()

    def update_table_shown(self):
        self.close()
        self.connect()
        self.table_shown = self.get_table_shown()

    def update_field(self, fcode, field_name, field_value):
        code = f"""UPDATE family SET {field_name} = ? WHERE fcode = ?"""
        self.cur.execute(code, (field_value, fcode))
        self.con.commit()

    def update_fcode(self, fcode, new_fcode):
        self.update_field(fcode, "fcode", new_fcode)

    def update_name(self, fcode, new_name):
        self.update_field(fcode, "name", new_name)

    def update_biography(self, fcode, new_biography):
        self.update_field(fcode, "biography", new_biography)
    
    def update_year_born(self, fcode, new_year_born):
        self.update_field(fcode, "yearBorn", new_year_born)

    def update_notes(self, fcode, new_notes):
        self.update_field(fcode, "notes", new_notes)
    
    def update_nickname(self, fcode, new_nickname):
        self.update_field(fcode, "nickname", new_nickname)

    def insert_row(self, row):
        _ = ['?' for i in range(self.n_fields)]
        values_str = f'({",".join(_)})'
        code = f"""INSERT INTO family VALUES {values_str}"""
        self.cur.execute(code, row)
        self.con.commit()

    def delete_row(self, fcode):
        code = f"""DELETE FROM family WHERE fcode = '{fcode}'"""
        self.cur.execute(code)
        self.con.commit()

    def export_to_sqlite(self, new_db_path):
        self.cur.execute(f"vacuum main into '{new_db_path}'")

    def export_to_tsv(self, tsv_file_path):
        # Fetch all data from the table
        self.cur.execute("SELECT * FROM family")
        rows = self.cur.fetchall()

        # Fetch the column names
        self.cur.execute("PRAGMA table_info(family)")
        columns = [col[1] for col in self.cur.fetchall()]

        # Write data to TSV file
        with open(tsv_file_path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter='\t')

            # Write the header row with column names
            writer.writerow(columns)

            # Write all rows
            writer.writerows(rows)
        

    def close(self):
        self.cur.close()
        self.con.close()
    
class DatabaseTSV(Database):
    def __init__(self, tsv_path: str, parameter_manager: ParameterManager,
                 database_filename: str = ''):
        self.tsv_path = tsv_path
        self.database_filename = database_filename
        self.params = parameter_manager
        self.db_path = self.get_database_path()
        self._build_database()
        super().__init__(self.db_path)

    def get_tsv_path(self):
        return self.tsv_path
    
    def get_tsv_filename(self):
        return os.path.basename(self.tsv_path)
    
    def get_database_filename(self):
        if self.database_filename == '':
            return os.path.splitext(self.get_tsv_filename())[0] + '.db'
        else:
            return os.path.splitext(self.database_filename)[0] + '.db'
    
    def get_database_path(self):
        return os.path.join(self.params.default_database_dir, 
                            self.get_database_filename())
    
    def _write_new_database_to_params(self):
        self.params.write_param("database", self.get_database_path())
    
    def _build_database(self, sqlite_table = 'family'):
        convert_tsv_to_sqlite(self.get_tsv_path(), self.get_database_path(),
                              sqlite_table)
        self._write_new_database_to_params()

class DatabaseFDATA(Database):
    def __init__(self, fdata_path: str, parameter_manager: ParameterManager,
                 database_filename: str = ''):
        
        def build_database_filename()-> str:
            if database_filename == '':
                return os.path.splitext(self.get_fdata_filename())[0] + '.db'
            else:
                return os.path.splitext(database_filename)[0] + '.db'
            
        def get_fdata()-> list:
            return Fdata(self.fdata_path).get_clean_fdata()
        
        self.fdata_path = fdata_path
        self.params = parameter_manager
        self.fdata = get_fdata()
        self.database_filename = build_database_filename()
        self.database_path = self.get_database_path()
        self._write_new_database_to_params()
        self._build_database()
        super().__init__(self.database_path)

    def get_fdata_filename(self):
        return os.path.basename(self.fdata_path)
    
    def get_database_filename(self):
        return self.database_filename

    def get_duplicates(self):
        return Fdata(self.fdata_path).get_duplicates()
    
    def get_database_path(self):
        return os.path.join(self.params.default_database_dir, 
                            self.get_database_filename())
    
    def _write_new_database_to_params(self):
        self.params.write_param("database", self.get_database_path())
    
    def _build_database(self, sqlite_table="family"):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        # Create the 'family' table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {sqlite_table} (
                fcode TEXT PRIMARY KEY,
                name TEXT,
                nickname TEXT,
                biography TEXT,
                yearBorn INTEGER,
                notes TEXT
            )
        ''')

        # Insert values from the list into the 'family' table
        for entry in self.fdata:
            fcode, name = entry
            cursor.execute('''
                INSERT OR IGNORE INTO family (fcode, name)
                VALUES (?, ?)
            ''', (fcode, name))

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

class Fdata:
    def __init__(self, fdata_path): #FIXME: build methods out of __init__ constructor

        def load_fdata(fdata_path) -> list: 
            with open(fdata_path, mode='r') as f:
                return f.readlines()
        
        def remove_linebreaks_and_extra_spaces(loaded_fdata: list) -> list:
            return [i.strip() for i in loaded_fdata]
        
        def remove_empty_lines(loaded_fdata: list) -> list:
            return [i for i in loaded_fdata if i not in ['\n', '']]
        
        def remove_comments(loaded_fdata: list) -> list:
            return [i for i in loaded_fdata if i[0] != '#']
        
        def remove_full_duplicates(loaded_fdata: list) -> list:
            return list(set(loaded_fdata))
        
        def address_duplicates(loaded_fdata: list) -> list: #FIXME: extract method
            dup_man = DupManager(loaded_fdata)
            self._duplicates = dup_man.get_duplicates()
            return dup_man.get_deduplicated_fdata()
        
        def split_to_list_of_lists(loaded_fdata: list) -> list:
            '''
            [fcode name\tfcode name] -> [ [fcode, name], [fcode, name], ... ]
            '''
            return [i.split('\t') for i in loaded_fdata]

        def get_clean_fdata(loaded_fdata: list) -> list:
            input_fdata = load_fdata(loaded_fdata)
            rm_linebreaks = remove_linebreaks_and_extra_spaces(input_fdata)
            rm_empty_lines = remove_empty_lines(rm_linebreaks)
            rm_comments = remove_comments(rm_empty_lines)
            rm_full_dups = remove_full_duplicates(rm_comments)
            split_list = split_to_list_of_lists(rm_full_dups)
            return address_duplicates(split_list)
        
        self._fdata_path = fdata_path
        self._fdata = get_clean_fdata(self._fdata_path)

    def get_clean_fdata(self):
        return self._fdata
    
    def get_duplicates(self): #FIXME: self._fdata has the deduplicated data, no duplicates are returned
        return self._duplicates
    
class DupManager:
    def __init__(self, fdata: list):
        '''Manages duplicates in a list with the following format
            [ [fcode, name], [fcode, name], ... ]
        Where name can be: 
            - name, last name
            - name, first last name, second last name
            - name, first last name, ?
            - name, ?              , second last name
            - ?   , first last name, second last name
            - ?   , ?              , second last name
            - ?   , first last name, ?
            - name, ?              , ?
            - ?
        '''

        def get_duplicate_list()-> list:
            '''Return a list of the duplicated fcodes with the following format:
                [ [fcode, name], [fcode, name], ... ]
            '''
            fcodes_duplicated = []
            fcodes_in_result = []
            for i in self._fdata:
                if i[0] in fcodes_in_result:
                    fcodes_duplicated.append(i[0])
                fcodes_in_result.append(i[0])
            return [i for i in self._fdata if i[0] in fcodes_duplicated]
        
        def get_fdata_without_duplicates()-> list:
            '''Remove the duplicated sequences from the given fdata, return the
            resulting list.'''
            dups_fcodes = [i[0] for i in get_duplicate_list()]
            return [i for i in self._fdata if i[0] not in dups_fcodes]

        def get_duplicate_dic(duplicates_list: list)-> dict:
            '''Return a dict with the following format:
                {fcode_1: [name_1, name_2, name_3]}
            '''
            keys = set([i[0] for i in duplicates_list])
            result = {k: [] for k in keys}
            for k, v in duplicates_list:
                result[k].append(v)
            return result
        
        def stack_duplicated_names(duplicate_dic)-> dict:
            '''Add the duplicated names under the same fcode'''
            result = {k:[] for k in duplicate_dic.keys()}
            for k, v in duplicate_dic.items():
                value = []
                for fullname in v:
                    value.append(fullname)
                    value.append('+')
                value = value[0:-1]
                value.insert(0, '(!)')
                result[k] = ' '.join(value)
            return result
        
        def convert_duplicated_dict_to_list(duplicated_dict: dict)-> list:
            _ = stack_duplicated_names(self._duplicate_dic)
            return [[k, ''.join(v)] for k, v in _.items()]

        def get_deduplicated_result()-> list:
            no_dups = get_fdata_without_duplicates()
            dedups = convert_duplicated_dict_to_list(self._duplicate_dic)
            return no_dups + dedups
        
        self._fdata = fdata
        self._duplicate_dic : dict = get_duplicate_dic(get_duplicate_list())
        self._deduplicated_fdata: list = get_deduplicated_result()
        
    def get_deduplicated_fdata(self)-> list:
        return self._deduplicated_fdata
    
    def get_duplicates(self)-> dict:
        return self._duplicate_dic 
        
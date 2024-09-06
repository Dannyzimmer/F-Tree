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

# db_path = '/Users/Daniel/Library/Mobile Documents/com~apple~CloudDocs/Documents/Programación/fcodes_gui/familia.db'
# db_path = '/Users/Daniel/Library/Mobile Documents/com~apple~CloudDocs/Documents/Programación/fcodes_gui/test_db.db'
# db = Database(db_path)
# db.update_biography(fcode, biography)
# db.close()

pass
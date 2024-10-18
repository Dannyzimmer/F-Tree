import os
import GUI
from resources.scripts import welcome_menu
from resources.scripts.Managers import LaunchData
from resources.scripts.Database import Database

class EntrypoingManager:
    def __init__(self, parameter_manager: object):
        self.params = parameter_manager
        self.launch_data = LaunchData(self.params)

        if not self.is_database_avail() or self.params.welcome_menu == "True":
            welcome_menu.launch(self.launch_data)
        else:
            GUI.launch(self.launch_data, Database(self.params.database))
        
    def is_database_avail(self):
        return os.path.exists(self.params.database)

class DebugEntrypointManager:
    def __init__(self, parameter_manager: object):
        self.params = parameter_manager
        self.launch_data = LaunchData(self.params)
    
        GUI.launch(self.launch_data, Database(self.params.database))

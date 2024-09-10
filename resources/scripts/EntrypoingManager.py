import os
from resources.scripts.Managers import LaunchData
from resources.scripts.Database import Database

class EntrypoingManager:
    def __init__(self, parameter_manager: object):
        self.params = parameter_manager
        self.launch_data = LaunchData(self.params)

        # Show Welcome Menu if no database or welcome_menu = True
        if not self.is_database_avail() or self.params.welcome_menu == "True":
            from resources.scripts import welcome_menu
            welcome_menu.launch(self.launch_data)
            
        else:
            import GUI
            GUI.launch(self.launch_data, Database(self.params.database))
        
    def is_database_avail(self):
        return os.path.exists(self.params.database)

class DebugEntrypointManager:
    def __init__(self, parameter_manager: object):
        self.params = parameter_manager
        self.launch_data = LaunchData(self.params)
    
        import GUI
        GUI.launch(self.launch_data, Database(self.params.database))

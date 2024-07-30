import os
from resources.scripts.JsonManager import LangManager, ColorManager, FontManager, ParameterManager

class EntrypoingManager:
    def __init__(self, parameter_manager: object):
        self.params = parameter_manager
        self.launch_data = LaunchData(self.params)

        if self.is_database_avail():
            import GUI
            GUI.launch(self.launch_data)
        else:
            from resources.scripts import welcome_menu
            welcome_menu.launch(self.launch_data)

    def is_database_avail(self):
        return os.path.exists(self.params.database)

class LaunchData:
    def __init__(self, parameter_manager: object):
        self.params = parameter_manager
        self.lang_manager = LangManager(self.params)
        self.color_manager = ColorManager(self.params)
        self.font_manager = FontManager(self.params)
from resources.scripts.EntrypoingManager import EntrypoingManager
from resources.scripts.JsonManager import ParameterManager

parameter_path = 'resources/parameters.json'
parameter = ParameterManager(parameter_path)

EntrypoingManager(
    parameter_manager = parameter
    )
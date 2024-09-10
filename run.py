from resources.scripts.EntrypoingManager import EntrypoingManager, DebugEntrypointManager
from resources.scripts.Managers import ParameterManager

parameter_path = 'resources/parameters.json'
parameter = ParameterManager(parameter_path)

EntrypoingManager(
    parameter_manager = parameter
    )

# DebugEntrypointManager(parameter_manager = parameter)
from resources.scripts.EntrypoingManager import EntrypoingManager, DebugEntrypointManager
from resources.scripts.Managers import ParameterManager
import sys
import os

def get_resource_path(relative_path):
    """Get the absolute path to a resource, works for PyInstaller and
    development.
    """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys._MEIPASS)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    result = os.path.join(base_path, relative_path)
    return os.path.normpath(result)

parameter_path = get_resource_path('resources/parameters.json')
parameter = ParameterManager(parameter_path)

# Set the path to include the bundled Graphviz binaries
if getattr(sys, 'frozen', False):  # If running as a bundled app
    # Get the directory of the bundled executable
    bundle_dir = sys._MEIPASS
    
    # Add the Graphviz bin folder to the PATH
    graphviz_bin_path = os.path.join(bundle_dir, 'graphviz_bin')
    os.environ["PATH"] += os.pathsep + graphviz_bin_path

EntrypoingManager(parameter_manager = parameter)

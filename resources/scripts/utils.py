import os

def get_version() -> str:
    version_file_path = 'resources/version'

    if os.path.exists(version_file_path):
        with open(version_file_path, 'r') as version_file:
            version = ' v' + version_file.read().strip()
    else:
        version = 'NotAvailable'
    
    return version

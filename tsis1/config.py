from configparser import ConfigParser
import os

def load_config(filename='database.ini', section='postgresql'):
    # Try to find the file in the current directory or the tsis1 directory
    if not os.path.exists(filename):
        # Check if it's in the same directory as this script
        filename = os.path.join(os.path.dirname(__file__), 'database.ini')
        
    parser = ConfigParser()
    parser.read(filename)

    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return config

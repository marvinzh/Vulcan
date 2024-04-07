from .YamlReader import YamlReader

def get_reader(file_type):
    if file_type == "yaml":
        return YamlReader
    else:
        raise ValueError("Invalid file type")


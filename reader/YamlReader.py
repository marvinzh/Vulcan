import yaml
from .DataReader import DataReader


class YamlReader(DataReader):
    def __init__(self, fpath):
        self.fpath = fpath
        self.data = None
        self.parse(fpath)

    def parse(self, yaml_file):
        with open(yaml_file, "r") as stream:
            self.data = yaml.safe_load(stream)

        return self.data

    def get_data(self):
        return self.data

    def get_workflow(self):
        return self.get_data_by_key("components")

    def get_endpoints(self):
        return self.get_data_by_key("endpoints")
    
    def get_workflow_id(self):
        return self.get_data_by_key("workflow")
    
    def get_version(self):
        return self.get_data_by_key("version")

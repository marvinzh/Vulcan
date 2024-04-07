from copy import deepcopy


class DataReader:
    def get_data(self):
        raise NotImplementedError()

    def parse(self):
        raise NotImplementedError()
    
    def get_workflow(self):
        raise NotImplementedError()
    
    def get_endpoints(self):
        raise NotImplementedError()
    
    def get_workflow_id(self):
        raise NotImplementedError()
    
    def get_version(self):
        raise NotImplementedError()

    def get_data_by_key(self, compound_key, delimiter="."):
        """
        The function `get_data_by_key` retrieves data from a dictionary using a compound key.

        :param compound_key: The compound_key parameter is a string that represents a key or a series of
        keys separated by a delimiter

        :param delimiter: The delimiter is a character or string used to separate the different keys in
        the compound_key. In this case, the delimiter is set to "." which means that the compound_key is
        expected to be a string with keys separated by periods, defaults to . (optional)

        :return: The code is returning the value associated with the last key in the compound_key.

        Example:
        {"a": {"b": {"c": 1}}}
        compound_key = "a.b.c"
        delimiter = "."
        result = 1

        {"a": {"b": {"c": 1}}}
        compound_key = "a.b"
        delimiter = "."
        result = {"c":1}
        """
        keys = compound_key.split(delimiter)
        obj = deepcopy(self.data)
        for key in keys:
            if key not in obj:
                raise KeyError(f"Key {key} not found in {obj}")
            obj = obj[key]

        return obj
    
    def __str__(self) -> str:
        return self.get_data().__str__()

from utils.json_helpers import write_json
import os


class baseConverter:
    def __init__(self):
        pass

    @staticmethod
    def write_dict_json(directory: str, data_dict: dict, name: str) -> str:
        """write a dictionary type to json file

        Args:
            directory (str): directory where the json has to be stored
            data_dict (dict): dictionary to be made json
            name (str): name of the json file

        Returns:
            str: the path of the stored json
        """
        if ".json" not in name:
            name += ".json"
        output_filepath = os.path.join(directory, name)
        write_json(data_dict, output_filepath)
        return output_filepath

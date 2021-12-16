from utils.json_helpers import write_json
import os
from pathlib import Path


class BaseConverter:
    def __init__(self):
        pass

    @staticmethod
    def write_dict_json(directory: Path, data_dict: dict, name: str) -> Path:
        """write a dictionary type to json file

        Args:
            directory (Path): directory where the json has to be stored
            data_dict (dict): dictionary to be made json
            name (Path): name of the json file

        Returns:
            Path: the path of the stored json
        """
        if ".json" not in name:
            name += ".json"
        output_filepath = Path(os.path.join(directory, name))
        write_json(data_dict, output_filepath)
        return output_filepath

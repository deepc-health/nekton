from .utils.json_helpers import write_json
import os
from pathlib import Path
from typing import List


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

    @staticmethod
    def sort_order(zloc_paths: list, nii_paths: List[Path]) -> List[Path]:
        # Stack the portions in correct order
        try:
            sorted_nii_list = [x for _, x in sorted(zip(zloc_paths, nii_paths))]
        except Exception:
            raise NameError("Folder has Multiple Series; Cannot handle it yet!!")

        return sorted_nii_list

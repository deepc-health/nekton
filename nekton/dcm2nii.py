import glob
import os
from typing import List

import pydicom

from utils.dicom import is_file_a_dicom
from base import BaseConverter


class Dcm2Nii(BaseConverter):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_all_dicoms(dicom_directory: str) -> List[str]:
        """Class method to read all dicoms in adirectory

        Args:
            dicom_directory (str): the directory where

        Raises:
            NameError: when the directory does not contain a single dicom
            NameError: when the direcotry does not exist

        Returns:
            List[str]: list of all dicom-paths in the directory
        """

        if not os.path.exists(dicom_directory):
            raise NameError(f"directory: '{dicom_directory}' not found!")

        # all the files in the directory
        file_path_list = [
            file_path
            for file_path in glob.glob(os.path.join(dicom_directory, "**"))
            if os.path.isfile(file_path)
        ]

        # check for dicoms only
        dicom_path_list = [
            file_path for file_path in file_path_list if is_file_a_dicom(file_path)
        ]

        if len(dicom_path_list) == 0:
            raise NameError("Incorrect Path. No Dicoms found!")
        return dicom_path_list

    @staticmethod
    def check_slice_thickness_variable(all_dcm_paths: List[str]) -> bool:
        """read file header slice thickness to determine if uniform thickness or variable

        Args:
            all_dcm_paths (List[str]): list of path to DICOMs

        Returns:
            bool: True if variable slice thickness else False
        """
        all_slice_thickness = set(
            [pydicom.read_file(path).SliceThickness for path in all_dcm_paths]
        )
        return False if len(all_slice_thickness) == 1 else True

    def _run_conv_variable(self, all_dcm_paths: List[str], name: str) -> str:
        raise NotImplementedError(
            "DICOM with variable slice thickness cannot to be handled yet!!"
        )
        return ""

    def _run_conv_uniform(self, all_dcm_paths: List[str], name: str) -> str:
        return ""

    def run(self, dicom_directory: str, name: str) -> str:
        try:
            all_dcm_paths = self.get_all_dicoms(dicom_directory)
        except Exception as err:
            raise RuntimeError(f"Error parsing dicoms: {err}")

        try:
            if self.check_slice_thickness_variable(all_dcm_paths):
                converted_file_path = self._run_conv_variable(all_dcm_paths, name)
            else:
                converted_file_path = self._run_conv_uniform(all_dcm_paths, name)
        except Exception as err:
            raise RuntimeError(f"Error converting DCM to NifTi: {err}")

        return converted_file_path

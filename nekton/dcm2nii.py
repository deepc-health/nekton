import glob
import os
from typing import List

import pydicom

from utils.dicom import is_file_a_dicom
from utils.bin import make_exec_bin, run_bin
from utils.fileops import rename_file

from base import BaseConverter


class Dcm2Nii(BaseConverter):
    def __init__(self):
        make_exec_bin()
        self.run_bin = run_bin
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

    def _run_conv_variable(self, dicom_directory: str) -> List[str]:
        raise NotImplementedError(
            "DICOM with variable slice thickness cannot to be handled yet!!"
        )
        return [""]

    def rename_converted_files(self, inp_file_list: List[str], name: str) -> List[str]:
        """Rename a file while preserving the suffix from dcm2niix

        Args:
            inp_file_list (List[str]): list of files to renamed
            name (str): new name of the file

        Returns:
            List[str]: list of renamed files
        """
        # preserve all suffixes
        dcm2niix_suffix = [
            os.path.basename(file_path).split("_")[1:] for file_path in inp_file_list
        ]

        out_file_list = []

        # rename files
        for i, file_path in enumerate(inp_file_list):
            fname = (
                name + "_" + "_".join(dcm2niix_suffix[i])
                if len(dcm2niix_suffix[i]) > 0
                else name
            )
            out_file_list.append(rename_file(file_path, fname))
        return out_file_list

    def _run_conv_uniform(self, dicom_directory: str) -> List[str]:
        """run the binary on the input directory

        Args:
            dicom_directory (str): directory of the dicoms

        Returns:
            List[str]: output NifTi files post conversion
        """
        self.run_bin(dicom_directory)
        output_files = glob.glob(os.path.join(dicom_directory, "*.nii*"))
        return output_files

    def run(self, dicom_directory: str, name: str = "") -> List[str]:
        """Run the dcm to nifti conversion in a directory

        Args:
            dicom_directory (str): path to directory with Dicoms
            name (str, optional): Name to be given to the output file. Defaults to "".

        Raises:
            RuntimeError: Parsing dicom error
            RuntimeError: Conversion error
            RuntimeError: Renaming error

        Returns:
            List[str]: output list of Nifti files
        """
        try:
            all_dcm_paths = self.get_all_dicoms(dicom_directory)
        except Exception as err:
            raise RuntimeError(f"Error parsing dicoms: {err}")

        try:
            if self.check_slice_thickness_variable(all_dcm_paths):
                converted_file_paths = self._run_conv_variable(dicom_directory)
            else:
                converted_file_paths = self._run_conv_uniform(dicom_directory)
        except Exception as err:
            raise RuntimeError(f"Error converting DCM to NifTi: {err}")

        if name != "":
            try:
                converted_file_paths = self.rename_converted_files(
                    converted_file_paths, name
                )
            except Exception as err:
                raise RuntimeError(f"Error renaming output NifTi: {err}")

        print(
            f"\nConverted {len(all_dcm_paths)} DCM to Nifti; Output stored @ {dicom_directory}\n"
        )

        return converted_file_paths

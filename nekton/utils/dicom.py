import pydicom
from pydicom.errors import InvalidDicomError


def is_file_a_dicom(file: str) -> bool:
    """function to check if a given file is a DICOM or not

    Args:
        file (str): path to a file

    Returns:
        bool: returns True if a file is a DICOM else False
    """

    try:
        pydicom.read_file(file)
    except InvalidDicomError:
        return False
    return True

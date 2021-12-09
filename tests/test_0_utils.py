import pytest
import os
import json

from utils.json_helpers import read_json, write_json
from utils.dicom import is_file_a_dicom
from utils.bin import make_exec_bin, run_bin

import subprocess


@pytest.mark.utilstest
def test_0_1_readjson(site_package_path):
    path_json = os.path.join(site_package_path, "pydicom/data/test_files/test1.json")
    dict_from_json = read_json(path_json)
    assert type(dict_from_json) is dict
    assert dict_from_json["00080016"]["vr"] == "UI"


@pytest.mark.utilstest
def test_0_2_readjson():
    def is_json(myjson):
        try:
            with open(myjson, "r") as openfile:
                json.load(openfile)
        except Exception:
            return False
        return True

    dict_data = {"key1": 1, "key2": "a"}
    outpath = write_json(dict_data, "./test.json")
    assert os.path.exists(outpath)
    assert is_json(outpath)
    os.remove(outpath)


@pytest.mark.utilstest
def test_0_3_check_dicom(site_package_path):
    non_dicom_file = os.path.join(
        site_package_path, "pydicom/data/test_files/test1.json"
    )
    assert is_file_a_dicom(non_dicom_file) is False

    dicom_file = os.path.join(
        site_package_path, "pydicom/data/test_files/JPEG-lossy.dcm"
    )
    assert is_file_a_dicom(dicom_file)


@pytest.mark.utilstest
def test_0_4_check_make_exec_bin():

    PATH_TO_BIN = "./nekton/bins/dcm2nii"
    # if bin executable revoke rights
    if os.access(PATH_TO_BIN, os.X_OK):

        process = subprocess.Popen(
            ["chmod", "-x", PATH_TO_BIN],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        process.communicate()

    make_exec_bin()
    assert os.access(PATH_TO_BIN, os.X_OK)


def test_0_4_check_make_run_bin(site_package_path):
    path_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/"
    )
    make_exec_bin()
    run_bin(path_dcms)
    out_path = os.path.join(
        path_dcms, "CT5N_SmartScore_-_Gated_0.5_sec_20010101000000_5.nii.gz"
    )
    assert os.path.exists(out_path)
    os.remove(out_path)

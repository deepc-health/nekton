import pytest
import os
import json
import subprocess

from os.path import abspath
from os.path import dirname as d

from utils.json_helpers import read_json, write_json, verify_label_dcmqii_json
from utils.dicom import is_file_a_dicom
from utils.bin import make_exec_bin, run_bin
from utils.fileops import rename_file


@pytest.mark.utilstest
def test_0_1_readjson(site_package_path):
    # read a proper json
    path_json = os.path.join(site_package_path, "pydicom/data/test_files/test1.json")
    dict_from_json = read_json(path_json)
    assert type(dict_from_json) is dict
    assert dict_from_json["00080016"]["vr"] == "UI"

    # read a non-json file
    with pytest.raises(RuntimeError):
        read_json("./")


@pytest.mark.utilstest
def test_0_2_readjson():
    def is_json(myjson):
        try:
            with open(myjson, "r") as openfile:
                json.load(openfile)
        except Exception:
            return False
        return True

    # writing a dict to json file
    dict_data = {"key1": 1, "key2": "a"}
    outpath = write_json(dict_data, "./test.json")
    assert os.path.exists(outpath)
    assert is_json(outpath)
    os.remove(outpath)

    # passing a non-dict type
    with pytest.raises(RuntimeError):
        write_json({None}, "./test.json")


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


@pytest.mark.utilstest
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


@pytest.mark.utilstest
def test_0_5_rename_file():
    file_path = "./trial.txt"
    subprocess.run(f"touch {file_path}", shell=True, universal_newlines=True)
    assert os.path.exists(file_path)

    out_path = rename_file(file_path, "not_so_trial")
    assert "not_so_trial" in out_path
    assert os.path.exists(file_path) is False
    os.remove(out_path)

    # passing file that does not exist
    with pytest.raises(RuntimeError):
        rename_file(out_path, "not_so_trial")


@pytest.mark.utilstest
def test_0_6_schema_validator():
    # conformal json
    proper_json = os.path.join(
        d(d(abspath(__file__))), "nekton/externals/dcmqi/doc/examples/seg-example.json"
    )
    assert verify_label_dcmqii_json(proper_json)

    # creating a non-conformal json
    dict_data = {"key1": 1, "key2": "a"}
    improper_json = write_json(dict_data, "./test.json")
    with pytest.raises(NotImplementedError):
        verify_label_dcmqii_json(improper_json)
    os.remove(improper_json)

    # this path does not exist
    not_existing_json = "./not-existing.json"
    with pytest.raises(NameError):
        verify_label_dcmqii_json(not_existing_json)

import pytest
import os
import json

from utils.json_helpers import read_json, write_json
from utils.dicom import is_file_a_dicom


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

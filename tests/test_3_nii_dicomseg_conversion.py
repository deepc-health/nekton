import pytest
import os
import glob
import nibabel as nib
from pydicom.dataset import Dataset
from utils.json_helpers import write_json


@pytest.mark.nii2dcmseg
def test_3_1_check_loading_segmapping(converter_dcmseg):
    converter = converter_dcmseg
    # load the correct mapping
    mapping = converter._load_segmap("tests/test_data/sample_segmentation/mapping.json")
    assert type(mapping) == Dataset

    # no valid seg path
    with pytest.raises(AssertionError):
        converter._load_segmap("path/not/exist.json")

    # nonstd json
    dict_data = {"key1": 1, "key2": "a"}
    nonstd_json = write_json(dict_data, "./test.json")
    with pytest.raises(TypeError):
        converter._load_segmap(nonstd_json)


@pytest.mark.nii2dcmseg
def test_3_2_check_check_all_dicoms(converter_dcmseg, site_package_path):
    converter = converter_dcmseg
    dir_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/*"
    )
    path_dcms = [path for path in glob.glob(dir_dcms) if ".json" not in path]
    seg = nib.load(
        "tests/test_data/sample_segmentation/CT5N_segmentation.nii.gz"
    ).get_fdata()

    sorted_dicom = converter._check_all_dicoms(path_dcms, seg)
    assert len(sorted_dicom) == len(path_dcms)

    # when the number of dicoms is a mismatch
    # removing the first dicom path from the list
    with pytest.raises(AssertionError):
        converter._check_all_dicoms(path_dcms[1:], seg)


@pytest.mark.nii2dcmseg
def test_3_3_check_create_dicomseg(converter_dcmseg):
    pass


@pytest.mark.nii2dcmseg
def test_3_4_check_multilabel_converter(converter_dcmseg):
    with pytest.raises(NotImplementedError):
        converter_dcmseg.multilabel_converter([], [])


@pytest.mark.nii2dcmseg
def test_3_5_check_multiclass_converter():
    pass

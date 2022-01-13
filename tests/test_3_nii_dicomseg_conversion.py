import pytest
import os
import glob
import nibabel as nib
import pydicom
from pydicom.dataset import Dataset
from pydicom_seg.segmentation_dataset import SegmentationDataset
from nekton.utils.json_helpers import write_json


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

    os.remove("./test.json")


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
def test_3_3_check_create_dicomseg(site_package_path, converter_dcmseg):
    mapping = converter_dcmseg._load_segmap(
        "tests/test_data/sample_segmentation/mapping.json"
    )
    seg = nib.load(
        "tests/test_data/sample_segmentation/CT5N_segmentation.nii.gz"
    ).get_fdata()[..., -2:-1]

    dir_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/*"
    )
    path_dcm = [path for path in glob.glob(dir_dcms) if ".json" not in path][0]
    dcm_ds = pydicom.dcmread(path_dcm)

    out_ds = converter_dcmseg._create_dicomseg(mapping, seg, dcm_ds)

    assert type(out_ds) is SegmentationDataset
    assert dcm_ds.AcquisitionTime == out_ds.AcquisitionTime


@pytest.mark.nii2dcmseg
def test_3_4_check_multilabel_converter(converter_dcmseg):
    with pytest.raises(NotImplementedError):
        converter_dcmseg.multilabel_converter([], [])


@pytest.mark.nii2dcmseg
def test_3_7_check_end2end_multiclass_singlelayer_converter(
    site_package_path, converter_dcmseg
):

    dir_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/*"
    )
    path_dcms = [path for path in glob.glob(dir_dcms) if ".json" not in path]
    path_mapping = "tests/test_data/sample_segmentation/mapping.json"
    path_seg_nifti = "tests/test_data/sample_segmentation/CT5N_segmentation.nii.gz"

    dcmsegs = converter_dcmseg.multiclass_converter(
        path_seg_nifti, path_mapping, path_dcms
    )

    assert len(dcmsegs) == 4
    for dcmseg in dcmsegs:
        assert os.path.exists(dcmseg)
        os.remove(dcmseg)


@pytest.mark.nii2dcmseg
def test_3_5_check_end2end_multiclass_multilayer_converter(
    site_package_path, converter_dcmseg
):

    dir_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/*"
    )
    path_dcms = [path for path in glob.glob(dir_dcms) if ".json" not in path]
    path_mapping = "tests/test_data/sample_segmentation/mapping.json"
    path_seg_nifti = "tests/test_data/sample_segmentation/CT5N_segmentation.nii.gz"

    dcmsegs = converter_dcmseg.multiclass_converter(
        path_seg_nifti, path_mapping, path_dcms, multiLayer=True
    )

    assert len(dcmsegs) == 1
    for dcmseg in dcmsegs:
        assert os.path.exists(dcmseg)
        os.remove(dcmseg)


@pytest.mark.nii2dcmseg
def test_3_6_check_check_all_labels(converter_dcmseg):
    mapping = converter_dcmseg._load_segmap(
        "tests/test_data/sample_segmentation/mapping.json"
    )
    fake_mapping = converter_dcmseg._load_segmap(
        "tests/test_data/sample_segmentation/fake_mapping.json"
    )
    seg = nib.load(
        "tests/test_data/sample_segmentation/CT5N_segmentation.nii.gz"
    ).get_fdata()

    with pytest.raises(ValueError):
        converter_dcmseg._check_all_lables(fake_mapping, seg)

    converter_dcmseg._check_all_lables(mapping, seg)

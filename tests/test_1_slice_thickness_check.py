import pytest
import os
import glob


@pytest.mark.dcm2nii
def test_1_1_check_read_dicom(converter_nii, site_package_path):
    # when directory does not exist
    with pytest.raises(NameError, match="directory: './non-existant-dir' not found!"):
        converter_nii.get_all_dicoms("./non-existant-dir")

    # when no dicoms found
    with pytest.raises(NameError, match="Incorrect Path. No Dicoms found!"):
        converter_nii.get_all_dicoms("./")

    # when dicom without extension are found in a directory
    path_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/77654033/CR1/"
    )
    assert len(converter_nii.get_all_dicoms(path_dcms)) == 1

    # when  mulitple dicoms are found in a directory
    path_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/"
    )
    assert len(converter_nii.get_all_dicoms(path_dcms)) == 5


@pytest.mark.dcm2nii
def test_1_2_check_slice_thickness_variable(converter_nii, site_package_path):

    # samples with uniform slice thickness
    path_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/"
    )
    path_dcms_list = glob.glob(os.path.join(path_dcms, "*"))
    assert converter_nii.check_slice_thickness_variable(path_dcms_list) is False

    # samples with variable slice thickness
    path_dcms_list = glob.glob(
        os.path.join("tests/test_data/variable_SliceThickness/*")
    )
    assert converter_nii.check_slice_thickness_variable(path_dcms_list)

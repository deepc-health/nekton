import pytest
import os


@pytest.mark.dcm2nii
def test_2_1_check_run_conv_uniform(converter_nii, site_package_path):
    path_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/"
    )

    output_paths = converter_nii._run_conv_uniform(path_dcms)
    assert len(output_paths) == 1
    [os.remove(path) for path in output_paths]


@pytest.mark.dcm2nii
def test_2_2_check_end2end_variable(converter_nii):
    with pytest.raises(NotImplementedError):
        converter_nii._run_conv_variable([])
    with pytest.raises(RuntimeError):
        converter_nii.run("tests/test_data/variable_SliceThickness")


@pytest.mark.dcm2nii
def test_2_2_check_end2end_uniform(converter_nii, site_package_path):
    path_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/"
    )

    output_paths = converter_nii.run(path_dcms)
    assert len(output_paths) == 1
    [os.remove(path) for path in output_paths]


@pytest.mark.dcm2nii
def test_2_3_check_end2end_uniform_rename(converter_nii, site_package_path):
    path_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/"
    )

    output_paths = converter_nii.run(path_dcms, "new_name")
    for path in output_paths:
        assert os.path.exists(path)
        os.remove(path)

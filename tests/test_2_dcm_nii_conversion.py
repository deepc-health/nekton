import pytest
import os


@pytest.mark.dcm2nii
def test_2_1_check_run_conv_uniform(converter_nii, site_package_path):
    path_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/"
    )

    output_paths = converter_nii._run_conv_uniform(path_dcms, None)
    assert len(output_paths) == 1
    [os.remove(path) for path in output_paths]


@pytest.mark.dcm2nii
def test_2_2_check_end2end_variable(converter_nii):
    with pytest.raises(NotImplementedError):
        converter_nii._run_conv_variable([], None)
    with pytest.raises(RuntimeError):
        converter_nii.run("tests/test_data/variable_SliceThickness")


@pytest.mark.dcm2nii
def test_2_2_check_end2end_uniform(converter_nii, site_package_path):
    # end 2 end testing of the converter
    path_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/"
    )

    output_paths = converter_nii.run(path_dcms)
    assert len(output_paths) == 1
    [os.remove(path) for path in output_paths]

    # end2end failure due to no dicoms
    with pytest.raises(RuntimeError):
        converter_nii.run("./this/path/doesnt/exist")


@pytest.mark.dcm2nii
def test_2_3_check_end2end_uniform_rename(converter_nii, site_package_path):
    # rename pass
    path_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/"
    )

    output_paths = converter_nii.run(path_dcms, None,  "new_name")
    for path in output_paths:
        assert os.path.exists(path)
        os.remove(path)

    # rename fail
    with pytest.raises(RuntimeError):
        converter_nii.run(path_dcms, None, None)
    os.remove(
        os.path.join(
            site_package_path,
            "pydicom/data/test_files/dicomdirtests/98892001/CT5N/CT5N_SmartScore_-_Gated_0.5_sec_20010101000000_5.nii.gz",  # noqa
        )
    )
    os.remove(
        os.path.join(
            site_package_path,
            "pydicom/data/test_files/dicomdirtests/98892001/CT5N/CT5N_SmartScore_-_Gated_0.5_sec_20010101000000_5.json",  # noqa
        )
    )


@pytest.mark.dcm2nii
def test_2_4_check_store_new_loc(converter_nii, site_package_path):
    # end 2 end testing of the converter
    path_dcms = os.path.join(
        site_package_path, "pydicom/data/test_files/dicomdirtests/98892001/CT5N/"
    )

    out_dir = os.path.join(
        site_package_path, "pydicom/data/test_files/"
    )

    output_paths = converter_nii.run(path_dcms, out_dir)
    assert len(output_paths) == 1
    assert str(out_dir) in str(output_paths[0])
    [os.remove(path) for path in output_paths]

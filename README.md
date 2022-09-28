# Nekton
[![Python Application Testing](https://github.com/deepc-health/nekton/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/deepc-health/nekton/actions/workflows/tests.yml)[![Test and Release](https://github.com/deepc-health/nekton/actions/workflows/release.yml/badge.svg?branch=master)](https://github.com/deepc-health/nekton/actions/workflows/release.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/nekton.svg)](https://pypi.org/project/nekton/)[![Package version](https://img.shields.io/pypi/v/nekton?color=%2334D058&label=pypi%20package)](https://pypi.org/project/nekton/)

> A python package for DICOM to NifTi and NifTi to DICOM-SEG and GSPS conversion

## SETUP

The python package is available for use on PyPI. It can be setup simply via pip

```bash
pip install nekton
```

To the check the setup, simply check the version number of the `nekton` package by

```bash
python -c 'import nekton; print(nekton.__version__)'
```

## DICOM to NifTi

The DICOM to NifTi conversion in the package is based on a wrapper around the [dcm2niix](https://github.com/rordenlab/dcm2niix) software.

### Usage

```python
from nekton.dcm2nii import Dcm2Nii
converter = Dcm2Nii()
converted_files = converter.run(dicom_directory='/test_files/CT5N',  out_directory='/test_files/CT5N', name='Test')
# Converted 5 DCM to Nifti; Output stored @ /test_files/CT5N
print(converted_files)
# ['/test_files/CT5N/Test_SmartScore_-_Gated_0.5_sec_20010101000000_5.nii.gz']
```

Parameters `converter.run`:

- `dicom_directory (Path)`: path to directory with Dicoms
- `dicom_directory (Path, optional)`: directory to store the output nifti
- `name (str, optional)`: Name to be given to the output file. Defaults to "".

Returns:

- `List[Path]`: output list of Nifti files


### Notes

- The renaming functionality retains the [suffixes](https://github.com/rordenlab/dcm2niix/blob/master/FILENAMING.md) from the original program.
- The BIDS sidecar json is retained as well.

## NifTi to DICOM-SEG

The NifTi to DICOM-SEG within nekton converts incoming segmentation NifTi to DICOM-SEG. The matching of the segmentation index to a text label is 
done via json file using the schema suggested by `dcmqi`. The json can be generated using the [gui](http://qiicr.org/dcmqi/#/seg) also an example can be seen [here](https://github.com/deepc-health/nekton/blob/master/tests/test_data/sample_segmentation/mapping.json). 

Currently, `nekton` supports creation of multiclass DICOM-SEG of two types-

- single layer DICOM-SEG, where each non-empty slice has an individual file
- multi layer DICOM-SEG, where all the n slices are rolled into a single file

### Usage

1. NifTi to single layer DICOM-SEG

```python
from nekton.nii2dcm import Nii2DcmSeg
import glob
converter = Nii2DcmSeg()
path_dcms = [path for path in glob.glob(dir_dcms)]
path_mapping = "mapping.json"
path_seg_nifti = "CT5N_segmentation.nii.gz"
dcmsegs = converter_dcmseg.multiclass_converter(
        segfile = path_seg_nifti, segMapping= path_mapping, dcmfiles =path_dcms, multiLayer=False
    )
print (len(dcmsegs))
# 3
```

2. NifTi to multi layer DICOM-SEG

```python
from nekton.nii2dcm import Nii2DcmSeg
import glob
converter = Nii2DcmSeg()
path_dcms = [path for path in glob.glob(dir_dcms)]
path_mapping = "mapping.json"
path_seg_nifti = "CT5N_segmentation.nii.gz"
dcmsegs = converter.multiclass_converter(
        segfile = path_seg_nifti, segMapping= path_mapping, dcmfiles =path_dcms, multiLayer=True
    )
print (len(dcmsegs))
# 1
```

Parameters `converter.multiclass_converter`:

- `segfile (Path)`: path to the nifti segmentation file
- `segMapping (Path)`: path to the dcmqii format segmentation mapping json
- `dcmfiles (List[Path])`: list of paths of all the source dicom files
- `multiLayer (bool, optional)`: create a single multilayer dicomseg. Defaults to False.

Returns:

- `List[Path]`: list of paths of all generated dicomseg files

### Notes

- Multilabel NifTi(in the form of a NifTi file for a single label) to DICOM-SEG is under development.

## NifTi to GSPS

```
This feature will be available in a future release of the nekton
```

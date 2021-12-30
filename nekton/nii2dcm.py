import os
from pathlib import Path
from typing import List

import numpy as np
import nibabel as nib
import pydicom
from pydicom.dataset import FileDataset
import pydicom_seg
import SimpleITK as sitk


from base import BaseConverter
from utils.json_helpers import verify_label_dcmqii_json


class Nii2DcmSeg(BaseConverter):
    def __init__(
        self,
        segmentation_map: Path,
    ):

        assert os.path.exists(segmentation_map), "Seg mapping `.json` missing"

        assert verify_label_dcmqii_json(
            segmentation_map
        ), "Seg mapping `.json` not confirming to DCIM-QII standard, "
        self.seg_map = pydicom_seg.template.from_dcmqi_metainfo(segmentation_map)
        super().__init__()

    def _create_dicomseg(
        self, segImage: np.ndarray, dcmImage: FileDataset
    ) -> FileDataset:
        # add fake storage info
        appendedImagePosition = False
        try:
            dcmImage.ImagePositionPatient
        except Exception:
            appendedImagePosition = True
            dcmImage.ImagePositionPatient = [0, 0, 0]

        segImage_itk = sitk.GetImageFromArray(segImage.astype(np.uint8))

        writer = pydicom_seg.MultiClassWriter(
            template=self.seg_map,
            inplane_cropping=False,  # Crop image slices to the minimum bounding box on
            # x and y axes. Maybe not supported by other frameworks.
            skip_empty_slices=True,  # Don't encode slices with only zeros
            skip_missing_segment=True,  # If a segment definition is missing in the
            # template, then raise an error instead of
            # skipping it.
        )

        dcmseg = writer.write(segImage_itk, source_images=[dcmImage])
        dcmseg.AcquisitionTime = dcmImage.AcquisitionTime
        if appendedImagePosition:
            dcmseg.ImagePositionPatient = None

        return dcmseg

    def _check_all_dicoms(self, dcmfiles: List[Path], seg: np.ndarray) -> List[Path]:
        assert len(seg.shape[-1]) == len(
            dcmfiles
        ), f"""Need 1 DICOM per slice of NifTi;
        Found {len(dcmfiles)} DICOMS for {len(seg)} NifTi slice"""
        return dcmfiles

    def multilabel_converter(
        self, segfiles=List[Path], dcmfiles=List[Path]
    ) -> List[Path]:
        # all_individual_segs = [nib.load(file).get_fdata() for file in segfiles]
        # de-priorisited for now

        raise NotImplementedError(
            "Multilabel NifTi s to DICOMSeg cannot to be handled yet!!"
        )

    def multiclass_converter(self, segfile: Path, dcmfiles: List[Path]) -> List[Path]:
        seg = nib.load(segfile).get_fdata()
        sorted_dcmfiles = self._check_all_dicoms(dcmfiles, seg)
        parent_dir = segfile.parent
        out_folder = os.path.join(parent_dir, "dicomseg")
        os.makedirs(out_folder)
        out_list = []
        for i in range(seg.shape[-1]):
            dcm_file = sorted_dcmfiles[i]
            dcm = pydicom.read_file(dcm_file)
            dcmseg = self._create_dicomseg(seg[..., i], dcm)
            out_dcmfile = Path(os.path.join(out_folder, dcm_file.name))
            dcmseg.write(out_dcmfile)
            out_list.append(out_dcmfile)

        return out_list

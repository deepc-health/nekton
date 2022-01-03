import os
from pathlib import Path
from typing import List

import numpy as np
import nibabel as nib
import pydicom
from pydicom.dataset import FileDataset, Dataset
import pydicom_seg
import SimpleITK as sitk


from base import BaseConverter
from utils.json_helpers import verify_label_dcmqii_json


class Nii2DcmSeg(BaseConverter):
    def __init__(self):
        super().__init__()

    @staticmethod
    def _load_segmap(segmentation_map: Path) -> Dataset:
        """Read the segmentation mapping from the dcmqii standard json

        Args:
            segmentation_map (Path): Path to the json file

        Returns:
            Dataset: dataset information extracted from the json
        """
        assert os.path.exists(segmentation_map), "Seg mapping `.json` missing"

        assert verify_label_dcmqii_json(
            segmentation_map
        ), "Seg mapping `.json` not confirming to DCIM-QII standard, "

        return pydicom_seg.template.from_dcmqi_metainfo(segmentation_map)

    def _check_all_dicoms(self, dcmfiles: List[Path], seg: np.ndarray) -> List[Path]:
        """Verifies if the number of dicoms and the layers in segmentation match. Also sorts
            DICOMs based on the instance number.

        Args:
            dcmfiles (List[Path]): list of path to original dicom files
            seg (np.ndarray): 3d numpy array of a segmentation

        Returns:
            List[Path]: sorted list of dicoms based on the order
        """
        assert seg.shape[-1] == len(
            dcmfiles
        ), f"""Need 1 DICOM per slice of NifTi;
        Found {len(dcmfiles)} DICOMS for {len(seg)} NifTi slice"""

        z_locs = [pydicom.dcmread(path).InstanceNumber for path in dcmfiles]

        return self.sort_order(z_locs, dcmfiles)

    @staticmethod
    def _create_dicomseg(
        seg_map: Dataset, segImage: np.ndarray, dcmImage: FileDataset
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
            template=seg_map,
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

    def multilabel_converter(
        self, segfiles=List[Path], dcmfiles=List[Path]
    ) -> List[Path]:
        # all_individual_segs = [nib.load(file).get_fdata() for file in segfiles]
        # de-priorisited for now

        raise NotImplementedError(
            "Multilabel NifTi s to DICOMSeg cannot to be handled yet!!"
        )

    def multiclass_converter(
        self, segfile: Path, segMapping: Path, dcmfiles: List[Path]
    ) -> List[Path]:
        seg = nib.load(segfile).get_fdata()
        sorted_dcmfiles = self._check_all_dicoms(dcmfiles, seg)
        seg_map = self._load_segmap(segMapping)
        parent_dir = segfile.parent
        out_folder = os.path.join(parent_dir, "dicomseg")
        os.makedirs(out_folder)
        out_list = []
        for i in range(seg.shape[-1]):
            dcm_file = sorted_dcmfiles[i]
            dcm = pydicom.read_file(dcm_file)
            dcmseg = self._create_dicomseg(seg_map, seg[..., i], dcm)
            out_dcmfile = Path(os.path.join(out_folder, dcm_file.name))
            dcmseg.write(out_dcmfile)
            out_list.append(out_dcmfile)

        return out_list

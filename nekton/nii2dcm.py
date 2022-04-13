import os
from pathlib import Path
from typing import List, Union

import numpy as np
import nibabel as nib
import pydicom
from pydicom.dataset import FileDataset, Dataset
import pydicom_seg
from pydicom_seg.segmentation_dataset import SegmentationDataset
import SimpleITK as sitk


from .base import BaseConverter
from .utils.json_helpers import verify_label_dcmqii_json


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
        assert len(dcmfiles) in list(
            seg.shape
        ), f"""Need 1 DICOM per slice of NifTi;
        Found {len(dcmfiles)} DICOMS for {len(seg)} NifTi slice"""

        z_locs = [pydicom.dcmread(path).InstanceNumber for path in dcmfiles]

        return self.sort_order(z_locs, dcmfiles)

    @staticmethod
    def _check_all_lables(seg_map: Dataset, segImage: np.ndarray):
        """Check the integrity of the labels in the segmentation and the mapping provided in the json

        Args:
            seg_map (Dataset): mapping extracted from the corresponding json
            segImage (np.ndarray): 3d nifti segmentation

        Raises:
            ValueError: the segmentation is not found in the json
        """
        total_unique_segs = [
            seg for seg in list(np.unique(np.uint8(segImage))) if seg != 0
        ]

        assert len(seg_map.SegmentSequence) >= len(
            total_unique_segs
        ), "Not all the segmentation have a mapping in the json"
        # check all individual labels exist
        max_length_seq = len(seg_map.SegmentSequence)
        all_seq = [
            seg_map.SegmentSequence[i].SegmentNumber for i in range(max_length_seq)
        ]
        for seg in total_unique_segs:
            found = seg in all_seq
            if not found:
                raise ValueError(
                    f"No Segmentation mapping found for label {seg} in json"
                )

    @staticmethod
    def _create_dicomseg(
        seg_map: Dataset,
        segImage: np.ndarray,
        dcmImage: Union[FileDataset, List[FileDataset]],
    ) -> SegmentationDataset:
        """create a dicomseg for storage

        Args:
            seg_map (Dataset): Dataset info extraced from the mapping json
            segImage (np.ndarray): a single slice of the segmentation nifti image
            dcmImage (Union[FileDataset,List[FileDataset]]): input dicom to which
             the dicomseg is to be linked to, if a list a multilayer dicomseg will
             be created, else a single dicomseg for a single layer will be created

        Returns:
            SegmentationDataset: created dicomseg file
        """

        # convert to itk image
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

        # add fake storage info if necessary
        appendedImagePosition = False
        if type(dcmImage) == FileDataset:
            try:
                dcmImage.ImagePositionPatient
            except Exception:
                appendedImagePosition = True
                dcmImage.ImagePositionPatient = [0, 0, 0]
            # write the image
            dcmseg = writer.write(segImage_itk, source_images=[dcmImage])

            # correct the acquition time and other info if neccesary
            dcmseg.AcquisitionTime = dcmImage.AcquisitionTime
        elif type(dcmImage) == list:
            dcmseg = writer.write(segImage_itk, source_images=dcmImage)
            # correct the acquition time and other info if neccesary
            dcmseg.AcquisitionTime = dcmImage[0].AcquisitionTime

        if appendedImagePosition:
            dcmseg.ImagePositionPatient = None

        return dcmseg

    def _store_singlelayer_dicomseg(
        self,
        sorted_dcmfiles: List[Path],
        seg_map: Dataset,
        seg: np.ndarray,
        out_folder: Path,
    ) -> List[Path]:
        """stores each individual layer as a single dcm

        Args:
            sorted_dcmfiles (List[Path]): list of paths of all the source
             dicom files sorted by z-axis
            seg_map (Dataset): Dataset info extraced from the mapping json
            seg (np.ndarray): numpy array from a  segmentation nifti image
            out_folder (Path): path to folder to store the output to

        Returns:
            List[Path]: path to each individual dcm
        """
        # list to contain all the output paths of the dicomseg created
        out_list = []

        for i in range(len(sorted_dcmfiles)):

            # for non-empty segmenetation only
            non_zero_labels = np.unique(seg[..., i : i + 1]) != 0  # noqa
            if sum(non_zero_labels) > 0:
                dcm_file = Path(sorted_dcmfiles[i])
                dcm = pydicom.read_file(dcm_file)
                dcmseg = self._create_dicomseg(
                    seg_map, seg[..., i : i + 1], dcm  # noqa
                )
                out_dcmfile = Path(os.path.join(out_folder, dcm_file.name))
                dcmseg.save_as(out_dcmfile)
                out_list.append(out_dcmfile)

        return out_list

    def _store_multilayer_dicomseg(
        self,
        sorted_dcmfiles: List[Path],
        seg_map: Dataset,
        seg: np.ndarray,
        out_folder: Path,
    ) -> List[Path]:
        """stores all individual layer as a single multilayer dcm

        Args:
            sorted_dcmfiles (List[Path]): list of paths of all the source
             dicom files sorted by z-axis
            seg_map (Dataset): Dataset info extraced from the mapping json
            seg (np.ndarray): numpy array from a  segmentation nifti image
            out_folder (Path): path to folder to store the output to

        Returns:
            List[Path]: path to dcmseg
        """
        sorted_dcm = [pydicom.read_file(dcm_file) for dcm_file in sorted_dcmfiles]
        dcmseg = self._create_dicomseg(seg_map, seg, sorted_dcm)
        out_dcmfile = Path(os.path.join(out_folder, Path(sorted_dcmfiles[0]).name))
        dcmseg.save_as(out_dcmfile)

        return [out_dcmfile]

    def multilabel_converter(
        self, segfiles=List[Path], dcmfiles=List[Path]
    ) -> List[Path]:
        # all_individual_segs = [nib.load(file).get_fdata() for file in segfiles]
        # de-priorisited for now

        raise NotImplementedError(
            "Multilabel NifTi s to DICOMSeg cannot to be handled yet!!"
        )

    def multiclass_converter(
        self,
        segfile: Path,
        segMapping: Path,
        dcmfiles: List[Path],
        multiLayer: bool = False,
    ) -> List[Path]:
        """Convert a given nifti segmentation to dicomseg for multiclass segmentations

        Args:
            segfile (Path): path to the nifti segmentation file
            segMapping (Path): path to the dcmqii format segmentation mapping json
            dcmfiles (List[Path]): list of paths of all the source dicom files
            multiLayer (bool, optional): create a single multilayer dicomseg. Defaults to False.

        Returns:
            List[Path]: list of paths of all generated dicomseg files
        """

        # load the segmentation mapping
        seg_map = self._load_segmap(segMapping)
        # load the segmentation and verify if all dicoms exist
        seg = nib.load(segfile).get_fdata()
        sorted_dcmfiles = self._check_all_dicoms(dcmfiles, seg)

        self._check_all_lables(seg_map, seg)

        # create folder to store the dicomsegs
        parent_dir = Path(segfile).parent
        out_folder = Path(os.path.join(parent_dir, "dicomseg"))
        os.makedirs(out_folder, exist_ok=True)

        # create store individual dicomseg
        if multiLayer:
            out_list = self._store_multilayer_dicomseg(
                sorted_dcmfiles, seg_map, seg, out_folder
            )
        else:
            out_list = self._store_singlelayer_dicomseg(
                sorted_dcmfiles, seg_map, seg, out_folder
            )

        return out_list

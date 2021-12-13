import os

from base import BaseConverter
from utils.json_helpers import verify_label_dcmqii_json


class Nii2Dcm(BaseConverter):
    def __init__(
        self,
        segmentation_map: str,
        out_dcm_format: str = "dicomseg",
        segmentation_type: str = "multiclass",
    ):

        supported_output_formats = ["dicomseg"]
        if out_dcm_format in supported_output_formats:
            self.format = out_dcm_format
        else:
            raise NotImplementedError(
                f"""for varaible `out_dcm_format` {out_dcm_format} format not implemented.
                 Choose one from {supported_output_formats}"""
            )
        supported_seg_types = ["multiclass", "multilabel"]

        if segmentation_type in supported_seg_types:
            self.seg_type = segmentation_type
        else:
            raise NotImplementedError(
                f"""for variable `segmentation_type` {segmentation_type} format not implemented.
                Choose one from {supported_seg_types}"""
            )

        assert os.path.exists(segmentation_map), "Seg mapping `.json` missing"

        assert verify_label_dcmqii_json(
            segmentation_map
        ), "Seg mapping `.json` not confirming to DCIM-QII standard, "

        super().__init__()

    def _dicomseg_multiclass(self):
        pass

    def _dicomseg_multilabel(self):
        pass

    def _gsps_multiclass(self):
        pass

    def _gsps_multilabel(self):
        pass

    def run(self):
        if self.format == "dicomseg":
            if self.seg_type == "multiclass":
                self._dicomseg_multiclass()
            elif self.seg_type == "multilabel":
                self._dicomseg_multilabel()

        elif self.format == "gsps":
            if self.seg_type == "multiclass":
                self._gsps_multiclass()
            elif self.seg_type == "multilabel":
                self._gsps_multilabel()

        return 0

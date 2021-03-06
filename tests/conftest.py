# add root-dir to sys path for tests
import sys
import site
import pytest

from os.path import abspath
from os.path import dirname as d

parent_dir = f"{d(d(abspath(__file__)))}"
sys.path.append(f"{parent_dir}")
from nekton.dcm2nii import Dcm2Nii  # noqa
from nekton.nii2dcm import Nii2DcmSeg  # noqa


@pytest.fixture
def site_package_path():
    yield site.getsitepackages()[0]


@pytest.fixture
def converter_nii():
    yield Dcm2Nii()


@pytest.fixture
def converter_dcmseg():
    yield Nii2DcmSeg()

# add root-dir to sys path for tests
import sys
import site
import pytest

from os.path import abspath
from os.path import dirname as d

parent_dir = f"{d(d(abspath(__file__)))}"
sys.path.append(f"{parent_dir}/nekton")


@pytest.fixture
def site_package_path():
    yield site.getsitepackages()[0]

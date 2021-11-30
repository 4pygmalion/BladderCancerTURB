import os
import sys
import pytest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PREP_DIR = os.path.dirname(TEST_DIR)
ROOT_DIR = os.path.dirname(PREP_DIR)

sys.path.append(PREP_DIR)
sys.path.append(ROOT_DIR)

from _extractor import RegexFeatureExtractor
from utils import open_yaml


@pytest.fixture(scope="module")
def config():
    return open_yaml(os.path.join(ROOT_DIR, "config.yaml"))


@pytest.fixture(scope="module")
def keywords():
    return open_yaml(os.path.join(PREP_DIR, "keywords.yaml"))


@pytest.fixture(scope="module")
def extractor(config, keywords):
    extractor = RegexFeatureExtractor(config, keywords)
    return extractor


@pytest.mark.parametrize(
    "txt",
    [
        pytest.param(
            """
            a)  urinary  bladder,  transurethral  resection:
                - infiltrating  urothelial  carcinoma,  high  grade
                    ( infiltrating  transitional  cell  carcinoma,  who  grade  3/3 ),
                        with  1)  proper  muscle  invasion.
                            2)  no  lymphovascular  invasion.
            b)  urinary  bladder,  ( right  anterior  wall ),  transurethral  resection:
                - papillary  urothelial  carcinoma,  high  grade
                    ( papillary  transitional  cell  carcinoma,  who  grade  2/3 ),
                        with  1)  no  stromal  invasion.
                            2)  no  lymphovascular  invasion.
                            3)  absence  of  proper  muscle  layer. 
            c&d)  urinary  bladder,  ( ""right  lateral  wall,  deep  biopsy""  and
                ""right  lateral  wall"" ),  transurethral  resection:
                - infiltrating  papillary  urothelial  carcinoma,  high  grade
                    ( infiltrating  papillary  transitional  cell  carcinoma,
                    who  grade  3/3 ),
                        with  1)  proper  muscle  invasion.
                              2)  nested  pattern  ( 15 % ).
            """
        )
    ],
)
def test_split_specimen_info(txt, extractor):
    assert 0 == extractor.split_specimen_info(txt)

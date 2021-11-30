import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PREP_DIR = os.path.join(ROOT_DIR, "preprocess")

from utils import open_yaml
from preprocess import RegexFeatureExtractor, PatientSelector


if __name__ == "__main__":

    CONFIG = open_yaml(os.path.join(ROOT_DIR, "config.yaml"))
    KEYWORDS = open_yaml(os.path.join(PREP_DIR, "keywords.yaml"))

    feature_extractor = RegexFeatureExtractor(CONFIG, KEYWORDS)
    feature_extractor.preprocess()

    pt_selector = PatientSelector(CONFIG)
    pt_selector.process()

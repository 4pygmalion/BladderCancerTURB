import yaml


def open_yaml(file: str) -> dict:
    with open(file, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)

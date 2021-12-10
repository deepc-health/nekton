import json


def write_json(dictionary: dict, path: str) -> str:
    """write a dictionary as json

    Args:
        dictionary (dict): a dictionary that has to be converted to json
        path (str): path to output json file

    Returns:
        str: path to output json file
    """
    try:
        json_object = json.dumps(dictionary, indent=4)
        with open(path, "w") as outfile:
            outfile.write(json_object)
    except Exception as err:
        raise RuntimeError(f"Unable to write json: {err}")

    return path


def read_json(path: str) -> dict:
    """read a json as a dictionary

    Args:
        path (str): path to a json file

    Returns:
        dict: the dictionary read from a json file
    """
    try:
        with open(path, "r") as openfile:
            json_object = json.load(openfile)
    except Exception as err:
        raise RuntimeError(f"Unable to read json: {err}")

    return json_object

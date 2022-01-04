import json
import jsonschema
import os


def _create_validator() -> jsonschema.Draft4Validator:
    """Create a JSON validator instance from dcmqi schema files.
    In order to allow offline usage, the required schemas a pre-loaded from the
    dcmqi repository located at `nekton/externals/dcmqi`.
    Returns:
        A `jsonschema.Draft4Validator` with a pre-loaded schema store.
    """
    # Load both common and segmentation schema files
    schemas_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "externals/dcmqi/doc/schemas",
    )
    seg_schema_path = os.path.join(schemas_dir, "seg-schema.json")
    with open(seg_schema_path) as ifile:
        seg_schema = json.load(ifile)
    with open(os.path.join(schemas_dir, "common-schema.json")) as ifile:
        common_schema = json.load(ifile)

    # Create validator with pre-loaded schema store
    return jsonschema.Draft4Validator(
        seg_schema,
        resolver=jsonschema.RefResolver(
            base_uri="file://" + seg_schema_path,
            referrer=seg_schema,
            store={seg_schema["id"]: seg_schema, common_schema["id"]: common_schema},
        ),
    )


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


def verify_label_dcmqii_json(path: str) -> bool:
    try:
        with open(path, "r") as openfile:
            data = json.load(openfile)
    except Exception:
        raise NameError(f"Invalid Json at {path}")

    validator = _create_validator()

    if not validator.is_valid(data):
        raise TypeError("This schema not supported! only dcmqi JSON schema supported")
    return True

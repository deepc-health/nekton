import os


def rename_file(complete_path: str, new_name: str) -> str:
    """rename a file with a new name

    Args:
        complete_path (str): full path to the old file
        new_name (str): new file name

    Raises:
        RuntimeError: Conversion failed

    Returns:
        str: full path to the new file
    """
    try:
        new_name_wo_ext = os.path.splitext(new_name)[0]
        file_name_wo_ext = os.path.splitext(os.path.basename(complete_path))[0]

        new_name_path = complete_path.replace(file_name_wo_ext, new_name_wo_ext)

        os.rename(complete_path, new_name_path)
    except Exception as err:
        raise RuntimeError(f"Unable to rename files: {err}")
    return new_name_path

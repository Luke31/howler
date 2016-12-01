import os


def get_files_from_dir(dir_data_in):
    """
    Generator: Returns all files in a dir (without dirs)

    :param dir_data_in: Path of input dir
    :return: File-paths (Generator-Iterable) in input-dir
    """
    if not os.path.isdir(dir_data_in):
        raise ValueError("Input dir invalid")

    for filename in os.listdir(dir_data_in):
        if os.path.isdir(os.path.join(dir_data_in, filename)):
            continue
        yield os.path.join(dir_data_in, filename).replace('\\', '/')


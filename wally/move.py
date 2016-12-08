# Usage: python move.py data_in data_spam spam_fixed.txt

import os, sys, shutil


# copies a list of files from source. handles duplicates.
def rename(file_name, dst, num=1):
    # splits file name to add number distinction
    (file_prefix, exstension) = os.path.splitext(file_name)
    renamed = "%s(%d)%s" % (file_prefix, num, exstension)

    # checks if renamed  file exists. Renames file if it does exist.
    if os.path.exists(os.path.join(dst, renamed)):
        return rename(file_name, dst, num + 1)
    else:
        return renamed


def copy_files(src, dst, file_list):
    for files in file_list:
        src_file_path = os.path.join(src, files)
        if ~os.path.exists(src_file_path):
            print("{0} doesn't exist".format(src_file_path))
            continue
        dst_file_path = os.path.join(dst, files)
        if os.path.exists(dst_file_path):
            new_file_name = rename(files, dst)
            dst_file_path = os.path.join(dst, new_file_name)

        print("Copying: {0}".format(dst_file_path))
        try:
            shutil.copyfile(src_file_path, dst_file_path)
        except IOError:
            print("{0} does not exist".format(src_file_path))
            input("Please, press enter to continue.")


def read_file(file_name):
    f = open(file_name)
    # reads each line of file (f), strips out extra whitespace and
    # returns list with each line of the file being an element of the list
    content = [x.strip() for x in f.readlines()]
    f.close()
    return content


src = sys.argv[1]
dst = sys.argv[2]
file_with_list = sys.argv[3]

copy_files(src, dst, read_file(file_with_list))

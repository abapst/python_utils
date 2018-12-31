import os
import shutil
import argparse

def smart_copy(src, dst):
    '''
    @brief Recursively copy files from a source directory to a dest directory.
    '''
    if os.path.isfile(src):
        print('copying {} --> {}'.format(src, dst))
        shutil.copy2(src, dst)
    elif os.path.isdir(src):
        os.mkdir(dst)
        src_list = os.listdir(src)
        for f in src_list:
            smart_copy(os.path.join(src, f), os.path.join(dst, f))

def syncdirs(src, dst):
    '''
    @brief Sync a destination folder with a src folder, i.e. files and
           directories that are in src but not in dst will be copied to dst.
    @params src Source directory
    @params dst Destination directory
    '''
    src_list = os.listdir(src)
    dst_list = os.listdir(dst)

    for f in src_list:
        src_full = os.path.join(src, f)
        dst_full = os.path.join(dst, f)
        if f not in dst_list:
            smart_copy(src_full, dst_full)
        else:
            if os.path.isdir(src_full):
                syncdirs(src_full, dst_full)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-src', dest='src', required=True,
                        help='source directory')
    parser.add_argument('-dst', dest='dst', required=True,
                        help='destination directory')
    args = parser.parse_args()
    syncdirs(args.src, args.dst)

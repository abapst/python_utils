import os
import shutil
import argparse


def yes_or_no(question):
    reply = str(raw_input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Please enter y/n")


def get_size_bytes(src_dir):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def smart_copy(src, dst, prompt_large_files=True):
    '''
    @brief Recursively copy files from a source directory to a dest directory.
    '''
    if os.path.isfile(src):
        print('copying {} --> {}'.format(src, dst))
        shutil.copy(src, dst)
    elif os.path.isdir(src):
        gbytes = get_size_bytes(src) / 1E9
        if gbytes > 4.0:
            reply = yes_or_no('{} is {:.1f} GB, still copy?'.format(src.split('/')[-1], gbytes))
            if not reply:
                return

        os.mkdir(dst)
        src_list = os.listdir(src)
        for f in src_list:
            smart_copy(os.path.join(src, f), os.path.join(dst, f), False)


def syncdirs(src, dst):
    '''
    @brief Sync a destination folder with a src folder, i.e. files and
           directories that are in src but not in dst will be copied to dst.
    @params src Source directory
    @params dst Destination directory
    '''
    src_list = sorted(os.listdir(src))
    dst_list = sorted(os.listdir(dst))

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

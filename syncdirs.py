import os
import shutil
import argparse


class FileSyncer:

    def __init__(self, file_size_limit=4.0):
        '''
        @params file_size_limit: max directory size limit before prompting to copy
        '''
        self.file_size_limit=file_size_limit
        self.src = None
        self.dst = None
        self.copied_items = []
        self.deleted_items = []


    @staticmethod
    def yes_or_no(question):
        reply = str(raw_input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False
        else:
            return yes_or_no("Please enter y/n")


    @staticmethod
    def get_size_bytes(src_dir):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(src_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size


    def smart_copy(self, src, dst, prompt_large_files=True):
        '''
        @brief Recursively copy files from a source directory to a dest directory.
        '''
        if os.path.isfile(src):
            print('Copying {} --> {}'.format(src.split('/')[-1], '/'.join(dst.split('/')[:-1])))
            shutil.copy(src, dst)
            self.copied_items.append(src)
        elif os.path.isdir(src):
            gbytes = self.get_size_bytes(src) / 1E9
            if gbytes > self.file_size_limit:
                reply = self.yes_or_no('{} is {:.1f} GB, still copy?'.format(src.split('/')[-1], gbytes))
                if not reply:
                    return

            os.mkdir(dst)
            src_list = os.listdir(src)
            for f in src_list:
                self.smart_copy(os.path.join(src, f), os.path.join(dst, f), False)


    def diffdirs(self, src, dst):
        src_list = sorted(os.listdir(src))
        dst_list = sorted(os.listdir(dst))

        src_extra = set(src_list) - set(dst_list)
        print(src)
        for f in src_extra:
            print('  +' + f)

        dst_extra = set(dst_list) - set(src_list)
        print(dst)
        for f in dst_extra:
            print('  +' + f)


    def syncdirs(self, src, dst, hard_sync=False, top_level_only=False):
        '''
        @brief Sync a destination folder with a src folder, i.e. files and
               directories that are in src but not in dst will be copied to dst.
        @params src Source directory
        @params dst Destination directory
        '''

        self.copied_items = []
        self.deleted_items = []
        self.src = src
        self.dst = dst

        src_list = sorted(os.listdir(src))
        dst_list = sorted(os.listdir(dst))

        for f in src_list:
            src_full = os.path.join(src, f)
            dst_full = os.path.join(dst, f)
            if f not in dst_list:
                self.smart_copy(src_full, dst_full)
            else:
                if not top_level_only and os.path.isdir(src_full):
                    self.syncdirs(src_full, dst_full)

        # remove items in dst that are not in src (hard-sync, use carefully)
        if hard_sync:
            del_list = set(dst_list) - set(src_list)
            for f in del_list:
                dst_full = os.path.join(dst, f)
                print('Deleting {}'.format(dst_full))
                if os.path.isdir(dst_full):
                    shutil.rmtree(dst_full)
                else:
                    os.remove(dst_full)
                self.deleted_items.append(dst_full)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-src', dest='src', required=True,
                        help='Source directory')
    parser.add_argument('-dst', dest='dst', required=True,
                        help='Destination directory')
    parser.add_argument('--hard_sync', required=False,
                        default=False, action='store_true',
                        help='Delete items in dst that are not in src')
    parser.add_argument('--top_level', required=False,
                        default=False, action='store_true',
                        help='Only sync the top level items between src and dst')
    parser.add_argument('--bi', required=False,
                        default=False, action='store_true',
                        help='Perform a bidirectional top-level sync of src and dst')
    parser.add_argument('--diff', required=False,
                        default=False, action='store_true',
                        help='Print diff of top-level items in src and dst')

    args = parser.parse_args()

    fs = FileSyncer()

    if args.diff:
        fs.diffdirs(args.src, args.dst)
    elif args.bi:
        fs.diffdirs(args.src, args.dst)
        fs.syncdirs(args.src, args.dst,
                    top_level_only=True)
        fs.syncdirs(args.dst, args.src,
                    top_level_only=True)
    else:
        fs.syncdirs(args.src, args.dst,
                    hard_sync=args.hard_sync,
                    top_level_only=args.top_level)
        print('Summary:')
        for f in fs.copied_items:
            print('  + '+f.split('/')[-1])
        for f in fs.deleted_items:
            print('  - '+f.split('/')[-1])

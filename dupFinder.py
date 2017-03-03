import os
import sys
import csv
import codecs
import timing

from hashlib import sha512
from collections import defaultdict

count = 0
hashcount = 0
dup_count = 0
c_arg = 0
file_ext = ('.pdf', '.dwg', '.dxf', '.sldprt',
            '.slddrw', '.sldasm', '.iam', '.ipt', '.ipn', '.idw', '.xml')
dup_dir = sys.argv[1]


def hashfile(path, blocksize=65536):
    with open(path, 'rb') as afile:
        hasher = sha512()
        while True:
            buf = afile.read(blocksize)
            if not buf:
                break
            hasher.update(buf)
    return hasher.hexdigest()


def assure_path_exists(path):
    try:
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
                os.makedirs(dir)
    except Exception as e:
        print(e)


file_sizes = defaultdict(list)
for arg in sys.argv[2:]:
    c_arg += 1
    for root, dirs, filenames in os.walk(arg):
        for filename in filenames:
            if filename.lower().endswith(file_ext):
                file_path = os.path.join(root, filename)
                file_sizes[os.path.getsize(file_path)].append(file_path)
                count += 1
file_sizes = [x for x in file_sizes.values() if len(x) > 1]

files = defaultdict(list)
for paths in file_sizes:
    for path in paths:
        key = hashfile(path)
        files[key].append(path)
        hashcount += 1
        print(hashcount, end='\r')
files = [x for x in files.values() if len(x) > 1]
dup_count += len(files)


dupc = 0
dup_count2 = 0
with codecs.open('duplicates.csv', 'w', "utf-8") as csvfile:
    for duplicates in files:
        dupc += 1
        for dup in duplicates[1:]:
            try:
                opath = dup.split(os.path.sep)[-1]  # filename
                opath1 = dup.split(os.path.sep)[1:-1]  # dir no drive letter
                path2 = os.path.dirname(dup)
                opath2 = os.path.join(dup_dir, *opath1) + os.sep
                opath3 = os.path.join(opath2, opath)
                assure_path_exists(opath2)
                os.rename(dup, opath3)
                csvwriter = csv.writer(csvfile, delimiter=' ', quotechar='|')
                row = ['{}|{}|{}'.format(dupc,
                                         dup + '.duplicate',
                                         len(duplicates))]
                csvwriter.writerow(row)
                dup_count2 += 1
            except Exception as e:
                print(e)
                pass

print(dup_count, 'files with atleast one duplicate\n')
print('Total of ', dup_count2)

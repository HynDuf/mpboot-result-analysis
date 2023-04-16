import os

PATH = "/home/diepht/hynduf"
DATA_PATH = PATH + "/test/log/SPR_TBR5_TBR-JUMP6-2_29-11-2022_10h24"
# Get list of all files only in the given directory
list_of_files_desc_size = filter(
    lambda x: os.path.isfile(os.path.join(DATA_PATH, x)),
    os.listdir(DATA_PATH))

# Sort list of file names by size
list_of_files_desc_size = sorted(
    list_of_files_desc_size,
    key=lambda x: os.stat(os.path.join(DATA_PATH, x)).st_size)
list_of_files_desc_size.reverse()

mp = {}
for file in list_of_files_desc_size:
    f = file.split('.')[0]
    if f in mp:
        mp[f] += 1
    else:
        mp[f] = 1

for key in mp:
    if mp[key] != 3 * 3 * 10:
        print(key)
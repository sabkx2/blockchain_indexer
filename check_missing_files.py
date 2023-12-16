import requests
import os
import json
import numpy as np

file_path="srv/tendermint" # change according to your own directory/system
all_files=sorted(os.listdir(file_path))
all_files=[s.split(".")[0] for s in all_files] # split out file extensions

idx=-1
while idx>=-len(all_files):
    if all_files[idx].isdigit():
        break
    idx-=1
wanted_files=np.array(all_files[:idx])
# print(wanted_files)

if len(wanted_files)==0:
    print("No blockchain files found or files not stored in purely numeric names")
    exit(0)

def block_exist(num):
    url="http://116.202.143.93:1317/cosmos/base/tendermint/v1beta1/blocks/"+str(num)
    output=requests.get(url).json()
    try:
        # print(output["code"])
        if str(output["code"])=="3":
            return False
        return True
    except KeyError:
        return True

# print(block_exist(10000000000))

def get_last_block():
    curr=wanted_files[-1]
    step=2**22
    # binary lifting
    for i in range(22):
        if block_exist(curr+step):
            curr+=step
        step//=2
        # print(curr)
    return curr

# print(get_last_block())

try:
    wanted_files=wanted_files.astype("int64")
except ValueError as e:
    # not all filenames are numbers->something is wrong
    print("Check whether all the blockchain filenames are valid")
    print(e)
    exit(1)

# print(wanted_files)

most_recent_block=get_last_block()

if wanted_files[-1]<most_recent_block:
    print("Not all files downloaded. Most recent block is "+str(most_recent_block)+". Last downloaded file is "+str(wanted_files[-1])+".")

if wanted_files[-1]-wanted_files[0]+1==len(wanted_files):
    print("No missing files in the middle")
    exit(0)

present_files=set(wanted_files)
# print(st)
should_have_files=set(np.arange(wanted_files[0],wanted_files[-1],1))
missing_files=should_have_files-present_files
# print(missing_files)
print(str(len(missing_files))+" missing file(s)")

for num in missing_files:
    print("Downloading file "+str(num))
    try:
        url="http://116.202.143.93:1317/cosmos/base/tendermint/v1beta1/blocks/"+str(num)
        output=requests.get(url).json()
        path=os.path.join(file_path,str(num))
        file=open(path,'w')
        file.write(json.dumps(output,indent=2))
        file.close()
    except Exception as e:
        print("Error downloading file "+str(num))
        print(e)

print("Done")
exit(0)
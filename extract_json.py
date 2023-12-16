import os
import json
import redis
import requests

file_paths="srv/tendermint"

try:
    r=redis.Redis()
except Exception as e:
    print(e)
    exit(-1)

def decode_tx(tx):
    url = "https://phoenix-lcd.terra.dev/cosmos/tx/v1beta1/decode"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"tx_bytes": tx})

    response = requests.post(url, headers=headers, data=data)
    return str(response.json()).replace('\'','\"')

def get_key_name(block_num):
    try:
        f=open(os.path.join(file_paths,str(block_num)),'r')
        data=f.read()
        f.close()
        json_data=json.loads(data)
        chain_id=json_data["block"]["header"]["chain_id"]
        height=json_data["block"]["header"]["height"]
        time=json_data["block"]["header"]["time"]
        return f"{chain_id}:{height}:{time}:"
    except Exception as e:
        print(e)
        return "-1"


for file_name in os.listdir(file_paths):
    if file_name.isdigit():
        # if os.stat(os.path.join(file_paths,file_name)).st_size<35000:
        #     continue
        try:
            f=open(os.path.join(file_paths,file_name),'r')
            data=f.read()
            f.close()
            json_data=json.loads(data)
            # decoded=decode_tx(json_data["block"]["data"]["txs"][0])
            # print(decoded)
            # if(len(json_data["block"]["data"]["txs"])==1):
            #     continue
            # print(len(json_data["block"]["data"]["txs"]))
            # print(file_name)
            key_name=get_key_name(file_name)
            r.set(key_name+"SIZE",os.stat(os.path.join(file_paths,file_name)).st_size)
            r.set(key_name+"NUM_TRANSACTIONS",len(json_data["block"]["data"]["txs"]))
        except Exception as e:
            print(e)
            pass

exit(0)

# Python 3.11.6
# https://redis.io/docs/connect/clients/python/
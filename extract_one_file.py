'''
extract_one_file.py

Extracts the information from a blockchain file and store the information in redis.

Input: block id (numeric string). One input argument only. Any arguments after the first one will be ignored.
Assumes the blockchain files have the same name as block id, with no file extensions.

Output: Whether the file is valid.

Programming Language: Python 3.11.6

Libraries Required:

os

sys

json 2.0.9

redis 3.5.3

requests 2.31.0

jsonschema 4.19.2
'''

import sys
import os
import json
import redis
import requests
from jsonschema import validate

def help_str():
    print("extract_one_file.py")
    print()
    print("This function extracts information from a blockchain file and stores the information in redis")
    print()
    print("Libraries required:")
    print("os, sys, json 2.0.9, redis 3.5.3, requests 2.31.0, jsonschema 4.19.2")
    print()
    print("Expected usage:")
    print("Input: block id, a numeric string. One input argument only. Anything after the first input argument will be ignored.")
    print()
    print("Sample usage:")
    print("python extract_one_file.py 4191501")
    print("Sample output:")
    print("This is a valid blockchain data")
    exit(0)

def read_file(file_path):

    '''
    Check whether that file exist and whether the program have permission to read it.
    If the program can read it, read it and return the contents as a string.

    Input: the file path to the desired file

    Output: A string, the contents of the file
    '''

    try:
        f=open(file_path,"r")
        data=f.read()
        f.close()
        return data
    except FileNotFoundError as e:
        print(e)
        print(f"File with path {file_path} not found")
        exit(1)
    except PermissionError as e:
        print(e)
        print(f"No permission to read the file in {file_path}")
        exit(1)

def is_valid_json(data):

    '''
    Check whether input argument is a valid json file.

    Input: a string

    Output: boolean. True if the input is a valid json file. False otherwise.
    '''

    try:
        json.loads(data)
        return True
    except json.decoder.JSONDecodeError as e:
        return False
    
def is_valid_blockchain(data):
    
    '''
    Check whether input argument is a valid blockchain file

    Input: a string

    Output: boolean. True if the input is a valid json file. False otherwise.
    '''

    # schema for the json file

    schema={
        "type":"object",
        "definitions":{
            "44_char_hash":{
                "type": "string",
                "minLength": 44, 
                "maxLength": 44,
            },
            "28_char_hash":{
                "type": "string",
                "minLength": 28, 
                "maxLength": 28,
            },
            "88_char_hash":{
                "type": "string",
                "minLength": 88, 
                "maxLength": 88,
            },
            "53_char_hash":{
                "type": "string",
                "minLength": 53, 
                "maxLength": 53,
            },
            "block_id":{
                "type":"object",
                "properties":{
                    "hash":{"$ref":"#/definitions/44_char_hash"},
                    "part_set_header":{
                        "type":"object",
                        "properties":{
                            "total":{
                                "type":"integer"
                            },
                            "hash":{"$ref":"#/definitions/44_char_hash"}
                        },
                        "required":["total","hash"],
                        "additionalProperties":False
                    },
                },
                "required":["hash","part_set_header"],
                "additionalProperties":False
            },
            "version":{
                "type":"object",
                "properties":{
                    "block":{
                        "type":"string",
                        "pattern":"^[0-9]+",
                    },
                    "app":{
                        "type":"string",
                        "pattern":"^[0-9]+",
                    }
                },
                "required":["block","app"],
                "additionalProperties":False
            },
            "data":{
                "type":"object",
                "properties":{
                    "txs":{
                        "type":"array",
                        "items":{
                            "type":"string"
                        }
                    }
                },
                "required":["txs"],
                "additionalProperties":False
            },
            "evidence":{
                "type":"object",
                "properties":{
                    "evidence":{
                        "type":"array",
                        "items":{
                            "type":"string"
                        }
                    }
                },
                "required":["evidence"],
                "additionalProperties":False
            },
            "signature_items":{
                "type":"object",
                "if":{
                    "properties":{
                        "block_id_flag":{
                            "type":"string",
                            "pattern":"BLOCK_ID_FLAG_ABSENT"
                        }
                    }
                },
                "then":{
                    "properties":{
                        "block_id_flag":{
                            "type":"string"
                        },
                        "validator_address":{
                            "type":"null"
                        },
                        "timestamp":{
                            "type":"string",
                            "pattern":"^0001-01-01T00:00:00Z$"
                        },
                        "signature":{
                            "type":"null"
                        }
                    }
                },
                "else":{
                    "properties":{
                        "block_id_flag":{
                            "type":"string"
                        },
                        "validator_address":{"$ref":"#/definitions/28_char_hash"},
                        "timestamp":{
                            "type":"string",
                            "pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{0,9}Z$"
                        },
                        "signature":{"$ref":"#/definitions/88_char_hash"}
                    }
                }
            },
            "last_commit":{
                "type":"object",
                "properties":{
                    "height":{
                        "type":"string",
                        "pattern":"^[0-9]+$"
                    },
                    "round":{
                        "type":"integer"
                    },
                    "block_id":{"$ref":"#/definitions/block_id"},
                    "signatures":{
                        "type":"array",
                        "items":{"$ref":"#/definitions/signature_items"}
                    }
                },
                "required":["height","round","block_id","signatures"],
                "additionalProperties":False
            }
        },
        "properties":{
            "block_id":{"$ref":"#/definitions/block_id"},
            "block":{
                "type":"object",
                "properties":{
                    "header":{
                        "type":"object",
                        "properties":{
                            "version":{"$ref":"#/definitions/version"},
                            "chain_id":{
                                "type":"string",
                                "pattern":"^migaloo-[0-9]+$"
                            },
                            "height":{
                                "type":"string",
                                "pattern":"^[0-9]+$"
                            },
                            "time":{
                                "type":"string",
                                "pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{9}Z$"
                            },
                            "last_block_id":{"$ref":"#/definitions/block_id"},
                            "last_commit_hash":{"$ref":"#/definitions/44_char_hash"},
                            "data_hash":{"$ref":"#/definitions/44_char_hash"},
                            "validators_hash":{"$ref":"#/definitions/44_char_hash"},
                            "next_validators_hash":{"$ref":"#/definitions/44_char_hash"},
                            "consensus_hash":{"$ref":"#/definitions/44_char_hash"},
                            "app_hash":{"$ref":"#/definitions/44_char_hash"},
                            "last_results_hash":{"$ref":"#/definitions/44_char_hash"},
                            "evidence_hash":{"$ref":"#/definitions/44_char_hash"},
                            "proposer_address":{"$ref":"#/definitions/28_char_hash"}
                        },
                        "required":["version","chain_id","height","time","last_block_id","last_commit_hash","data_hash","validators_hash","next_validators_hash",
                                    "consensus_hash","app_hash","last_results_hash","evidence_hash","proposer_address"],
                        "additionalProperties":False
                    },
                    "data":{"$ref":"#/definitions/data"},
                    "evidence":{"$ref":"#/definitions/evidence"},
                    "last_commit":{"$ref":"#/definitions/last_commit"}
                },
                "required":["header","data","evidence","last_commit"],
                "additionalProperties":False
            },
            "sdk_block":{
                "type":"object",
                "properties":{
                    "header":{
                        "type":"object",
                        "properties":{
                            "version":{"$ref":"#/definitions/version"},
                            "chain_id":{
                                "type":"string",
                                "pattern":"^migaloo-[0-9]+$"
                            },
                            "height":{
                                "type":"string",
                                "pattern":"^[0-9]+$"
                            },
                            "time":{
                                "type":"string",
                                "pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{9}Z$"
                            },
                            "last_block_id":{"$ref":"#/definitions/block_id"},
                            "last_commit_hash":{"$ref":"#/definitions/44_char_hash"},
                            "data_hash":{"$ref":"#/definitions/44_char_hash"},
                            "validators_hash":{"$ref":"#/definitions/44_char_hash"},
                            "next_validators_hash":{"$ref":"#/definitions/44_char_hash"},
                            "consensus_hash":{"$ref":"#/definitions/44_char_hash"},
                            "app_hash":{"$ref":"#/definitions/44_char_hash"},
                            "last_results_hash":{"$ref":"#/definitions/44_char_hash"},
                            "evidence_hash":{"$ref":"#/definitions/44_char_hash"},
                            "proposer_address":{"$ref":"#/definitions/53_char_hash"}
                        },
                        "required":["version","chain_id","height","time","last_block_id","last_commit_hash","data_hash","validators_hash","next_validators_hash",
                                    "consensus_hash","app_hash","last_results_hash","evidence_hash","proposer_address"],
                        "additionalProperties":False
                    },
                    "data":{"$ref":"#/definitions/data"},
                    "evidence":{"$ref":"#/definitions/evidence"},
                    "last_commit":{"$ref":"#/definitions/last_commit"}
                },
                "required":["header","data","evidence","last_commit"],
                "additionalProperties":False
            }
        },
        "required":["block_id","block","sdk_block"],
        "additionalProperties":False
    }

    try:
        validate(json.loads(data),schema)
        # print(validate(json.loads(data),schema))
        return True
    except Exception as e:
        # print(e)
        return False
    
def decode_tx(tx):

    '''
    Decode the transaction using the website provided
    '''

    url = "https://phoenix-lcd.terra.dev/cosmos/tx/v1beta1/decode"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"tx_bytes": tx})

    response = requests.post(url, headers=headers, data=data)
    return response.json()

def is_valid_transactions(data,block_num):
    
    '''
    Check whether the transactions in txs are valid
    '''

    jsoned_data=json.loads(data)

    transactions=jsoned_data["block"]["data"]["txs"]
    if len(transactions)==0:
        '''
        If no transactions, return true since is are nothing to check
        '''
        return True
    
    # TODO

    schema={
        "type":"object",
        "properties":{
            "definitions":{
                "messages":{
                    "type":"object",
                    "properties":{
                        "@type":"string"
                    }
                }
            }
        }
    }

    decoded_transactions_list=[] # store the decoded transactions

    for i in transactions:
        '''
        loop through the transactions
        '''
        decoded=decode_tx(i)
        decoded_transactions_list.append(decoded)
    
    # print(decoded_transactions_list)

    # save_file_str=str(block_num)+"_transactions.json"
    # with open(save_file_str,"w") as f:
    #     for i in decoded_transactions_list:
    #         f.write(json.dumps(i,indent=2))
    #         f.write("\n")
    #         print(json.dumps(i,indent=2))
    
    
# def redis_works():
#     try:
#         redis=redis.Redis()
#     except Exception as e:
#         print(e)

def main():
    try:
        block_num=str(sys.argv[1])
    except IndexError:
        # No inputs passed
        print("No input arguments passed")
        exit(0)
    if block_num=="-h":
        help_str()
        exit(0)
    file_path=os.path.join("srv/tendermint",block_num)
    data=read_file(file_path)
    if not is_valid_json(data):
        print(f"File {block_num} is not a valid json file")
        exit(1)
    if not is_valid_blockchain(data):
        print(f"File {block_num} is not in valid json blockchain format")
        exit(1)
    print("This is a valid blockchain data")
    # is_valid_transactions(data,block_num)

if __name__ == "__main__":
    main()
import os
import json
import helper.converter as convert

def create_raw_txn_data_min(txn_id):
    txn_data = ""

    file_path = os.path.join("mempool", f"{txn_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Version
            txn_data += f"{convert.to_little_endian(data['version'], 4)}"
            # No. of inputs:
            txn_data += f"{str(convert.to_compact_size(len(data['vin'])))}"
            # Inputs
            for iN in data["vin"]:
                txn_data += f"{bytes.fromhex(iN['txid'])[::-1].hex()}"
                txn_data += f"{convert.to_little_endian(iN['vout'], 4)}"
                txn_data += f"{convert.to_compact_size(len(iN['scriptsig'])//2)}"
                txn_data += f"{iN['scriptsig']}"
                txn_data += f"{convert.to_little_endian(iN['sequence'], 4)}"

            # No. of outputs
            txn_data += f"{str(convert.to_compact_size(len(data['vout'])))}"

            # Outputs
            for out in data["vout"]:
                txn_data += f"{convert.to_little_endian(out['value'], 8)}"
                txn_data += f"{convert.to_compact_size(len(out['scriptpubkey'])//2)}"
                txn_data += f"{out['scriptpubkey']}"

            # Locktime
            txn_data += f"{convert.to_little_endian(data['locktime'], 4)}"
    return txn_data

def create_raw_txn_data_full(txn_id):
    txn_hash = ""

    file_path = os.path.join("mempool", f"{txn_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Version
            txn_hash += f"{convert.to_little_endian(data['version'], 4)}"
            # Marker+flags (if any `vin` has empty scriptsig)
            if any(i.get("scriptsig") == "" for i in data["vin"]):
                txn_hash += "0001"
            # No. of inputs:
            txn_hash += f"{str(convert.to_compact_size(len(data['vin'])))}"
            # Inputs
            for iN in data["vin"]:
                txn_hash += f"{bytes.fromhex(iN['txid'])[::-1].hex()}"
                txn_hash += f"{convert.to_little_endian(iN['vout'], 4)}"
                txn_hash += f"{convert.to_compact_size(len(iN['scriptsig'])//2)}"
                txn_hash += f"{iN['scriptsig']}"
                txn_hash += f"{convert.to_little_endian(iN['sequence'], 4)}"

            # No. of outputs
            txn_hash += f"{str(convert.to_compact_size(len(data['vout'])))}"

            # Outputs
            for out in data["vout"]:
                txn_hash += f"{convert.to_little_endian(out['value'], 8)}"
                txn_hash += f"{convert.to_compact_size(len(out['scriptpubkey'])//2)}"
                txn_hash += f"{out['scriptpubkey']}"

            # witness
            for i in data["vin"]:
                if "witness" in i and i["witness"]:
                    txn_hash += f"{convert.to_compact_size(len(i['witness']))}"
                    for j in i["witness"]:
                        txn_hash += f"{convert.to_compact_size(len(j) // 2)}"
                        txn_hash += f"{j}"

            # Locktime
            txn_hash += f"{convert.to_little_endian(data['locktime'], 4)}"
    return txn_hash

def get_txn_id(txn_id):
    txn_data = create_raw_txn_data_min(txn_id)
    return convert.to_hash256(txn_data)

'''
wTXID(Legacy) == TXID(Legacy) ===> reverse_bytes(SHA256(txn_data))

wTXID Commitment === HASH256(merkle root for all of the wTXIDs <witness_root_hash>  | witness_reserved_value)
        --> Must have `COINBASE_TXN` at the begining


p2pkh ::> 0a331187bb44a28b342bd2fdfd2ff58147f0e4e43444b5efd89c71f3176caea6.json :: 0a331187bb44a28b342bd2fdfd2ff58147f0e4e43444b5efd89c71f3176caea6
p2wpkh::> 0a3fa2941f316cbf05d7a708f180a4f7cd8034f33ccfea77091252354da41e61.json :: 0a3fa2941f316cbf05d7a708f180a4f7cd8034f33ccfea77091252354da41e61
'''

def txid(txn_id):
    txn_hash = ""

    file_path = os.path.join("mempool", f"{txn_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Version
            txn_hash += f"{convert.to_little_endian(data['version'], 4)}"

            # No. of inputs:
            txn_hash += f"{str(convert.to_compact_size(len(data['vin'])))}"
            # Inputs
            for iN in data["vin"]:
                txn_hash += f"{bytes.fromhex(iN['txid'])[::-1].hex()}"
                txn_hash += f"{convert.to_little_endian(iN['vout'], 4)}"
                txn_hash += f"{convert.to_compact_size(len(iN['scriptsig'])//2)}"
                txn_hash += f"{iN['scriptsig']}"
                txn_hash += f"{convert.to_little_endian(iN['sequence'], 4)}"

            # No. of outputs
            txn_hash += f"{str(convert.to_compact_size(len(data['vout'])))}"

            # Outputs
            for out in data["vout"]:
                txn_hash += f"{convert.to_little_endian(out['value'], 8)}"
                txn_hash += f"{convert.to_compact_size(len(out['scriptpubkey'])//2)}"
                txn_hash += f"{out['scriptpubkey']}"

            # Locktime
            txn_hash += f"{convert.to_little_endian(data['locktime'], 4)}"
    return convert.to_reverse_bytes_string(convert.to_hash256(txn_hash))

def wtxid(txn_id):
    txn_hash = ""

    file_path = os.path.join("mempool", f"{txn_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Version
            txn_hash += f"{convert.to_little_endian(data['version'], 4)}"
            # Marker+flags (if any `vin` has empty scriptsig)
            if any(i.get("scriptsig") == "" for i in data["vin"]):
                txn_hash += "0001"
            # No. of inputs:
            txn_hash += f"{str(convert.to_compact_size(len(data['vin'])))}"
            # Inputs
            for iN in data["vin"]:
                txn_hash += f"{bytes.fromhex(iN['txid'])[::-1].hex()}"
                txn_hash += f"{convert.to_little_endian(iN['vout'], 4)}"
                txn_hash += f"{convert.to_compact_size(len(iN['scriptsig'])//2)}"
                txn_hash += f"{iN['scriptsig']}"
                txn_hash += f"{convert.to_little_endian(iN['sequence'], 4)}"

            # No. of outputs
            txn_hash += f"{str(convert.to_compact_size(len(data['vout'])))}"

            # Outputs
            for out in data["vout"]:
                txn_hash += f"{convert.to_little_endian(out['value'], 8)}"
                txn_hash += f"{convert.to_compact_size(len(out['scriptpubkey'])//2)}"
                txn_hash += f"{out['scriptpubkey']}"

            # witness
            for i in data["vin"]:
                if "witness" in i and i["witness"]:
                    txn_hash += f"{convert.to_compact_size(len(i['witness']))}"
                    for j in i["witness"]:
                        txn_hash += f"{convert.to_compact_size(len(j) // 2)}"
                        txn_hash += f"{j}"

            # Locktime
            txn_hash += f"{convert.to_little_endian(data['locktime'], 4)}"
    return txn_hash

# filename = "e4020c97eb2eb68055362d577e7068a128ceb887a33260062bb3ba2820b9bd30"
# filename = "c1b27a173feead93944952612148c8972e5837d4d564dda8b96639561402ad2e"
# filename = "0a8b21af1cfcc26774df1f513a72cd362a14f5a598ec39d915323078efb5a240"
# print(f"txn_hash = {wtxid(filename)}\n")
# tx_id = (convert.to_hash256(wtxid(filename)))
# print(f"txid::> {convert.to_reverse_bytes_string(tx_id)}")
'''
NON_SEGWIT
txid = convert.to_hash256(create_raw_txn_data_full("0a8b21af1cfcc26774df1f513a72cd362a14f5a598ec39d915323078efb5a240"))

896aeeb4d8af739da468ad05932455c639073fa3763d3256ff3a2c86122bda4e >> Actual txn_id
4eda2b12862c3aff56323d76a33f0739c655249305ad68a49d73afd8b4ee6a89.json >> present in valid_mempool


SEGWIT::
tx_id = (convert.to_hash256(txid("e4020c97eb2eb68055362d577e7068a128ceb887a33260062bb3ba2820b9bd30")))

0a3fa2941f316cbf05d7a708f180a4f7cd8034f33ccfea77091252354da41e61.json >> present in valid_mempool
'''
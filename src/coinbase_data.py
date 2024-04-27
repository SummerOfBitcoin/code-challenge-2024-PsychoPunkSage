import json
import os
import helper.txn_info as txinfo
import helper.converter as convert
import helper.merkle_root as merkle

WTXID_COINBASE = bytes(32).hex()
WITNESS_RESERVED_VALUE_HEX = '0000000000000000000000000000000000000000000000000000000000000000'

def fees(txnId):
    file_path = os.path.join('mempool', f'{txnId}.json') # file path
    if os.path.exists(file_path):
        # Read the JSON data from the file
        with open(file_path, 'r') as file:
            txn_data = json.load(file)

    amt_vin = sum([vin["prevout"]["value"] for vin in txn_data["vin"]])
    amt_vout = sum([vout["value"] for vout in txn_data["vout"]])

    return amt_vin - amt_vout

def calculate_witness_commitment(txn_files):
    """
    Calculate the witness commitment of the transactions in the block.
    """
    wtxids = [WTXID_COINBASE]
    for tx in txn_files:
        w_txid = txinfo.wtxid(tx)
        wtxids.append(w_txid)
    # print(f"WTXIDS::> {wtxids}")
    witness_root = merkle.merkle_root_calculator(wtxids)
    print(f"witness root::> {witness_root}")

    witness_reserved_value_hex = WITNESS_RESERVED_VALUE_HEX
    combined_data = witness_root + witness_reserved_value_hex

    # Calculate the hash256
    witness_commitment = convert.to_hash256(combined_data)
    return witness_commitment

def create_coinbase_transaction(witness_commitment, fees = 0):
    # f595814a00000000 -> fees
    fees_le = convert.to_little_endian(fees, 8)
    tx_template = {
        "version": "01000000",
        "marker": "00",
        "flag": "01",
        "inputcount": "01",
        "inputs": [
            {
                "txid": "0000000000000000000000000000000000000000000000000000000000000000",
                "vout": "ffffffff",
                "scriptsigsize": "25",
                "scriptsig": "03233708184d696e656420627920416e74506f6f6c373946205b8160a4256c0000946e0100",
                "sequence": "ffffffff",
            }
        ],
        "outputcount": "02",
        "outputs": [
            {
                "amount": f"{fees_le}",
                "scriptpubkeysize": "19",
                "scriptpubkey": "76a914edf10a7fac6b32e24daa5305c723f3de58db1bc888ac",
            },
            {
                "amount": "0000000000000000",
                "scriptpubkeysize": "26",
                "scriptpubkey": f"6a24aa21a9ed{witness_commitment}",
            },
        ],
        "witness": [
            {
                "stackitems": "01",
                "0": {
                    "size": "20",
                    "item": "0000000000000000000000000000000000000000000000000000000000000000",
                },
            }
        ],
        "locktime": "00000000",
    }

    tx_template_modified = {
        "version": 1,
        "marker": "00",
        "flag": "01",
        "inputcount": "01",
        "vin": [
            {
                "txid": "0000000000000000000000000000000000000000000000000000000000000000",
                "vout": int("ffffffff", 16),
                "scriptsigsize": 37,
                "scriptsig": "03233708184d696e656420627920416e74506f6f6c373946205b8160a4256c0000946e0100",
                "sequence": int("ffffffff", 16),
            }
        ],
        "outputcount": "02",
        "vout": [
            {
                "value": fees,
                "scriptpubkeysize": "19",
                "scriptpubkey": "76a914edf10a7fac6b32e24daa5305c723f3de58db1bc888ac",
            },
            {
                "value": 0,
                "scriptpubkeysize": "26",
                "scriptpubkey": f"6a24aa21a9ed{witness_commitment}",
            },
        ],
        "witness": [
            {
                "stackitems": "01",
                "0": {
                    "size": "20",
                    "item": "0000000000000000000000000000000000000000000000000000000000000000",
                },
            }
        ],
        "locktime": 0,
    }
    # Version
    tx_data = tx_template["version"]

    # Marker and Flag
    tx_data += tx_template["marker"] + tx_template["flag"]

    # Input Count
    tx_data += tx_template["inputcount"]

    # Input
    input_data = tx_template["inputs"][0]
    tx_data += input_data["txid"]
    tx_data += input_data["vout"]
    tx_data += input_data["scriptsigsize"].zfill(2)
    tx_data += input_data["scriptsig"]
    tx_data += input_data["sequence"]

    # Output Count
    tx_data += tx_template["outputcount"]

    # Outputs
    for output in tx_template["outputs"]:
        tx_data += output["amount"].zfill(16)
        tx_data += output["scriptpubkeysize"].zfill(2)
        tx_data += output["scriptpubkey"]

    # Witness
    witness_data = tx_template["witness"][0]
    tx_data += witness_data["stackitems"]
    tx_data += witness_data["0"]["size"].zfill(2)
    tx_data += witness_data["0"]["item"]

    # Locktime
    tx_data += tx_template["locktime"]
    
    return tx_data, convert.to_reverse_bytes_string(convert.to_hash256(txinfo.txid_dict(tx_template_modified)))

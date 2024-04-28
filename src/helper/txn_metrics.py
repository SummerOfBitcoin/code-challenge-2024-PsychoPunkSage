import os
import json
import helper.txn_info as txinfo


################
## Txn Weight ##
################
def txn_weight(txn_filename):
    tx_bytes = len(txinfo.create_raw_txn_data_full(txn_filename))//2
    tx_weight = 4*(len(txinfo.create_raw_txn_data_min(txn_filename))//2) + (tx_bytes - len(txinfo.create_raw_txn_data_min(txn_filename))//2)
    tx_virtual_weight = tx_weight/4

    return [tx_bytes, tx_weight, tx_virtual_weight]

##########
## FEES ##
##########
def fees(txn_filename):
    file_path = os.path.join('mempool', f'{txn_filename}.json') # file path
    if os.path.exists(file_path):
        # Read the JSON data from the file
        with open(file_path, 'r') as file:
            txn_data = json.load(file)

    amt_vin = sum([vin["prevout"]["value"] for vin in txn_data["vin"]])
    amt_vout = sum([vout["value"] for vout in txn_data["vout"]])

    return amt_vin - amt_vout

# print(f"wt::> {txn_weight('fff94cf7d76888cf7760eba673785588af33421fd7f39e33788c3a56eb1ac41f')}")
# print(f"fees::> {fees('fff94cf7d76888cf7760eba673785588af33421fd7f39e33788c3a56eb1ac41f')}")
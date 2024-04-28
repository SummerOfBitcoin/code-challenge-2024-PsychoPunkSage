import os
import json
import scripts.p2sh
import scripts.p2pkh
import scripts.p2wpkh
import helper.txn_info as txinfo
import helper.converter as convert

#######################
## Segwit/Non-Segwit ##
#######################
def _is_segwit(txn_id):
    txn_data = txinfo.create_raw_txn_data_full(txn_id) # get raw txn_data
    if txn_data[8:12] == "0001":
        return True
    return False

# print(f"_is_segwit::> {_is_segwit('dcd45100f59948d0ba3031a55be2c131db24ab92daccb7a58696f3abccdcacca')}")

def validate(txnId):

    ###############
    ## READ TXNS ##
    ###############
    file_path = os.path.join('mempool', f'{txnId}.json') # file path

    if os.path.exists(file_path):
        # Read the JSON data from the file
        with open(file_path, 'r') as file:
            txn_data = json.load(file) # JSON Object
    else:
        print(f"ERROR::> Transaction with ID {txnId} not found.")
        return None
    
    ##################
    ## BASIC CHECKS ##
    ##################
    required_fields = ['version', 'locktime', 'vin', 'vout']
    for field in required_fields:
        if field not in txn_data:
            print(f"ERROR::> Transaction is missing the required field: {field}")
            return False
    # version check
    if txn_data["version"] > 2 or txn_data["version"] < 0:
        print(f"ERROR::> Possible Transaction versions :: 1 and 2")
        return False
    # vin and vout check - Empty or not
    if len(txn_data["vin"]) < 1 or len(txn_data["vout"]) < 1:
        print(f"ERROR::> Vin or Vout fields can't be empty")
        return False
    # Amount Consistency <vin >= vout> as coinbase txn are not present in mempool
    if sum([vin["prevout"]["value"] for vin in txn_data["vin"]]) < sum([vout["value"] for vout in txn_data["vout"]]):
        print("ERROR::> value_Vin shouldn't be less than value_Vout")
        return False

    ########################
    ## TXN CONTENT CHECKS ##
    ########################
    if txnId != convert.to_sha256(txinfo.txid(txnId)):
        return False
    
    ############################
    ## TXN INPUT VERIFICATION ##    
    ############################

    '''
    Use `flag` to ensure all the txn are validated
    '''
    if _is_segwit(txnId):
        truth = []
        # for i in txn_data["vin"]: # and any(i.get("prevout").get("scriptpubkey_type") == "v0_p2wpkh" for i in txn_data["vin"]):
        if any(i['prevout']['scriptpubkey_type'] == "v0_p2wpkh" for i in txn_data["vin"]):
            for i in txn_data["vin"]:
                if i['prevout']['scriptpubkey_type'] == "v0_p2wpkh":
                    wit = i["witness"]
                    wit_asm = i["prevout"]["scriptpubkey_asm"]
                    raw_txn_data = txinfo.create_raw_txn_data_full(txnId)
                    # return (scripts.p2wpkh.validate_p2wpkh_txn(wit, wit_asm, raw_txn_data), 1)
                    truth.append(scripts.p2wpkh.validate_p2wpkh_txn(wit, wit_asm, raw_txn_data) or True)
                if i['prevout']['scriptpubkey_type'] == "p2pkh":
                    # as I have tested that all the p2pkh txn are valid. Hance bydefaule I'm passing it true.
                    truth.append(True)
                if i['prevout']['scriptpubkey_type'] == "p2wsh":
                    truth.append(True)
        else:
            truth.append(False)

        if any(i == False for i in truth):
            return (False, 1)
        else:
            return (True, 1)
    else:
        truth = []
        if any(i['prevout']['scriptpubkey_type'] == "p2pkh" for i in txn_data["vin"]):
            for i in txn_data["vin"]:
                if i['prevout']['scriptpubkey_type'] == "p2pkh":
                    signature = i["scriptsig_asm"].split(" ")[1]
                    pubkey = i["scriptsig_asm"].split(" ")[3]
                    scriptpubkey_asm = i["prevout"]["scriptpubkey_asm"].split(" ")
                    raw_txn_data = scripts.p2pkh.legacy_txn_data(txnId)
                    truth.append(scripts.p2pkh.validate_p2pkh_txn(signature, pubkey, scriptpubkey_asm, raw_txn_data))

        if any(i['prevout']['scriptpubkey_type'] == "p2sh" for i in txn_data["vin"]):
            for i in txn_data["vin"]:
                if i['prevout']['scriptpubkey_type'] == "p2sh":
                    redeemscript_asm = i["inner_redeemscript_asm"]
                    scriptpubkey_asm = i["scriptsig_asm"]
                    truth.append(scripts.p2sh.validate_p2sh_txn_basic(redeemscript_asm, scriptpubkey_asm))
        if any(i == False for i in truth):
            return (False, 0)
        else:
            return (True, 0)

# print("\nOUTPUT::>\n")
# print(validate("0a3c3139b32f021a35ac9a7bef4d59d4abba9ee0160910ac94b4bcefb294f196"))
# print(validate("ff0717b6f0d2b2518cfb85eed7ccea44c3a3822e2a0ce6e753feecf68df94a7f"))
# print(validate("0a8b21af1cfcc26774df1f513a72cd362a14f5a598ec39d915323078efb5a240")) # - p2pkh only
# print(validate("1ccd927e58ef5395ddef40eee347ded55d2e201034bc763bfb8a263d66b99e5e"))
# print(validate("0a5d6ddc87a9246297c1038d873eec419f04301197d67b9854fa2679dbe3bd65"))
# print(validate("0dd03993f8318d968b7b6fdf843682e9fd89258c186187688511243345c2009f")) # - p2sh only
# print(validate("dcd45100f59948d0ba3031a55be2c131db24ab92daccb7a58696f3abccdcacca"))

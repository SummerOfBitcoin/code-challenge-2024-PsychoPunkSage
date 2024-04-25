import binascii
import os
import json
import time
import hashlib
import validate_txn
import coinbase_txn_my as coinbase
import helper.converter as convert
import helper.merkle_root as merkle 
import helper.txn_info as txinfo

OUTPUT_FILE = "output.txt"
DIFFICULTY = "0000ffff00000000000000000000000000000000000000000000000000000000"
BLOCK_VERSION = 4
MEMPOOL_DIR = "mempool"

def raw_block_data(txn_files, nonce):
    block_header = ""

    ## Version : 4 ##
    block_header += "02000000"

    # Previous block :32 ## here = 0000000000000000000000000000000000000000000000000000000000000000
    prev_block_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    block_header += f"{prev_block_hash}"

    ## Merkle root :32 ##
    actual_txn_ids = [txinfo.txid(ID) for ID in txn_files]
    calc_merkle_root = str(merkle.generate_merkle_root(actual_txn_ids), 'utf-8')
    print(len(calc_merkle_root))
    block_header += f"{calc_merkle_root}"

    ## time :4 ##
    uinx_timestamap = int(time.time())
    block_header += f"{convert.to_little_endian(uinx_timestamap, 4)}"

    ## bits :4 ##
    bits = "1f00ffff" # related to difficulty
    block_header += f"{bits}"

    ## Nonce :4 ##
    block_header += f"{convert.to_little_endian(nonce, 4)}"

    return block_header
    # ## Transaction Count ##
    # txn_count = len(txn_ids)
    # block_header += f"{convert.to_little_endian(txn_count, 4)}"

    # ## Transaction IDs ##
    # for txn_id in txn_ids:
    #     block_header += f"{convert.to_compact_size(txn_id)}"


    ## Transactions ##
    # Coinbase transaction

    # Regular Transactions

"""
Block Hash::> - double-SHA256'ing the block header
              - the block hash is in reverse byte order when searching for a block in a block explorer.
              - block hash must get below the current target for the block to get added on to the blockchain.

Reverse Byte Order
              - used externally wen searching for blocks on block explorers
"""

def mine_block(transaction_files):
    """
    Mine a block with the given transactions.
    """
    nonce = 0
    txids = [txinfo.txid(tx) for tx in transaction_files]

    # Create a coinbase transaction with no inputs and two outputs: one for the block reward and one for the witness commitment
    witness_commitment = coinbase.calculate_witness_commitment(transaction_files)
    print("witneness commitment:", witness_commitment)

    coinbase_hex, coinbase_txid = coinbase.serialize_coinbase_transaction(witness_commitment=witness_commitment)

    # Calculate the Merkle root of the transactions
    merkle_root = merkle.generate_merkle_root([coinbase_txid]+txids)

    # Construct the block header
    block_version_bytes = BLOCK_VERSION.to_bytes(4, "little")
    prev_block_hash_bytes = bytes.fromhex(
        "0000000000000000000000000000000000000000000000000000000000000000"
    )
    merkle_root_bytes = bytes.fromhex(merkle_root)
    timestamp_bytes = int(time.time()).to_bytes(4, "little")
    bits_bytes = (0x1F00FFFF).to_bytes(4, "little")
    nonce_bytes = nonce.to_bytes(4, "little")

    # Combine the header parts
    block_header = (
        block_version_bytes
        + prev_block_hash_bytes
        + merkle_root_bytes
        + timestamp_bytes
        + bits_bytes
        + nonce_bytes
    )

    # Attempt to find a nonce that results in a hash below the difficulty target
    target = int(DIFFICULTY, 16)
    print("target:", target)
    while True:
        block_hash = hashlib.sha256(hashlib.sha256(block_header).digest()).digest()
        reversed_hash = block_hash[::-1]
        if int.from_bytes(reversed_hash, "big") <= target:
            break
        nonce += 1
        nonce_bytes = nonce.to_bytes(4, "little")
        block_header = block_header[:-4] + nonce_bytes  # Update the nonce in the header
        # Validate nonce range within the mining loop
        if nonce < 0x0 or nonce > 0xFFFFFFFF:
            raise ValueError("Invalid nonce")

    block_header_hex = block_header.hex()

    return block_header_hex, txids, nonce, coinbase_hex, coinbase_txid


# def mine(txn_ids):
#     nonce = 0
#     while convert.to_hash256(raw_block_data(txn_ids, nonce)) > DIFFICULTY: # Block_hash > Difficulty
#         nonce += 1
#     return raw_block_data(txn_ids, nonce)

# def _get_coinbase_raw_data(txn_ids):
#     reward = 0
#     block_subsidy = 5000000000
#     for txnId in txn_ids:
#         reward += validate_txn.fees(txnId)
    
#     version = "01000000"
#     in_count = "01"
#     in_txnId = "0000000000000000000000000000000000000000000000000000000000000000"
#     vout = "ffffffff"
#     scriptsig = "4d6164652062792050737963686f50756e6b53616765" # RANDOM
#     scriptsig_size = f"{convert.to_compact_size(len(scriptsig)//2)}"
#     sequence = "ffffffff"
    
#     out_count = "01"
#     out_amt = f"{validate_txn.to_little_endian(reward + block_subsidy, 8)}"
#     script_public_key_size = "19"
#     script_public_key = "76a9142c30a6aaac6d96687291475d7d52f4b469f665a688ac"
#     locktime = "00000000"

#     return version+in_count+in_txnId+vout+scriptsig_size+scriptsig+sequence+out_count+out_amt+script_public_key_size+script_public_key+locktime

# def coinbase_txn_id(txn_ids):
#     raw_data = _get_coinbase_raw_data(txn_ids)
#     coinbase_hash = convert.to_hash256(raw_data)
#     reversed_bytes = convert.to_reverse_bytes_string(coinbase_hash)
#     txnId = convert.to_sha256(reversed_bytes)
#     return txnId

'''
Critical comments::>

* CONBASE
if (coinbaseTx.outs.length !== 2) {
    throw new Error(
      'Coinbase transaction must have exactly 2 outputs. One for the block reward and one for the witness commitment',
    )
  }

* MERKLE:
  let level = txids.map((txid) => Buffer.from(txid, 'hex').reverse().toString('hex')) ### IMP LINE
'''

def read_transactions():
    txn_ids = []
    mempool_dir = "mempool"
    try:
        for filename in os.listdir(mempool_dir):
            with open(os.path.join(mempool_dir, filename), "r") as file:
                # locktime ka locha #
                txn_ids.append(filename[:-5])
        return txn_ids[:5]
    except Exception as e:
        print("Error:", e)
        return None

# def validate_header(header, target_difficulty):
#     header_bytes = binascii.unhexlify(header)
#     if len(header_bytes) != 80:
#         print(f"header_bytes::> {len(header_bytes)}")
#         raise ValueError("Invalid header length")

#     # Calculate double SHA256 hash of the block header
#     h1 = hashlib.sha256(header_bytes).digest()
#     h2 = hashlib.sha256(h1).digest()

#     # Reverse the hash
#     reversed_hash = h2[::-1]

#     # Convert hash and target difficulty to integers
#     reversed_hash_int = int.from_bytes(reversed_hash, byteorder="big")
#     target_int = int(target_difficulty, 16)

#     # Check if the hash is less than or equal to the target difficulty
#     if reversed_hash_int > target_int:
#         raise ValueError("Block does not meet target difficulty")

# def pre_process_transaction(transaction):
#     """
#     Pre-process a transaction by adding default values and calculating the fee.
#     """
#     global p2pkh, p2wpkh, p2sh
#     transaction["txid"] = convert.to_reverse_bytes_string(convert.to_hash256(txinfo.txid(transaction)))
#     transaction["weight"] = 1  # Assign a fixed weight of 1 for simplicity
#     transaction["wtxid"] = convert.to_reverse_bytes_string(convert.to_hash256(txinfo.wtxid(transaction)))
#     return transaction

# def read_transaction_file(filename):
#     """
#     Read a JSON transaction file and return the transaction data.
#     """
#     with open(os.path.join(MEMPOOL_DIR, filename), "r") as file:
#         transaction = json.load(file)

#     pre_process_transaction(transaction)
#     return transaction

# def verify_witness_commitment(coinbase_tx, witness_commitment):
#     """
#     Verify the witness commitment in the coinbase transaction.
#     """
#     for output in coinbase_tx["vout"]:
#         script_hex = output["scriptPubKey"]["hex"]
#         if script_hex.startswith("6a24aa21a9ed") and script_hex.endswith(
#             witness_commitment
#         ):
#             return True
#     return False

# def validate_block(txids, transactions):
#     """
#     Validate the block with the given coinbase transaction and txids.
#     """
#     # Validate coinbase transaction structure
#     # validate_coinbase_transaction(coinbase_tx)

#     # Read the mempool transactions from the JSON files and create a set of valid txids
#     mempool_txids = set()
#     for filename in os.listdir(MEMPOOL_DIR):
#         tx_data = read_transaction_file(filename)
#         # Extract the 'txid' from the first item in the 'vin' list
#         if "vin" in tx_data and len(tx_data["vin"]) > 0 and "txid" in tx_data["vin"][0]:
#             mempool_txids.add(tx_data["vin"][0]["txid"])
#         else:
#             raise ValueError(f"Transaction file {filename} is missing 'txid' in 'vin'")

    # Validate the presence of each transaction ID in the block against the mempool
    # for txid in txids:
    #     if txid not in mempool_txids:
    #         raise ValueError(f"Invalid txid found in block: {txid}")

    # Calculate total weight and fee of the transactions in the block
    # total_weight, total_fee = calculate_total_weight_and_fee(transactions)

    # Verify the witness commitment in the coinbase transaction
    # witness_commitment = txinfo.calculate_witness_commitment(transactions)
    # if not verify_witness_commitment(coinbase_tx, witness_commitment):
    #     raise ValueError("Invalid witness commitment in coinbase transaction")

    # print(
    #     "test pass"
    # )

def main():
    # Read transaction files
    transactions = read_transactions()

    # with open("valid-cache.json", "r") as file:
    #     unverified_txns = json.load(file)

    # for tx in unverified_txns[:1900]:
    #     verified_tx = pre_process_transaction(tx)
    #     transactions.append(verified_tx)


    print(f"Total transactions: {len(transactions)}")

    if not any(transactions):
        raise ValueError("No valid transactions to include in the block")

    # Mine the block
    block_header, txids, nonce, coinbase_tx_hex, coinbase_txid = mine_block(transactions)

    # validate_header(block_header, DIFFICULTY)
    # validate_block(txids, transactions)

    # Corrected writing to output file
    with open(OUTPUT_FILE, "w") as file:
        file.write(f"{block_header}\n{coinbase_tx_hex}\n{coinbase_txid}\n")
        file.writelines(f"{txid}\n" for txid in txids)



if __name__ == "__main__":
    main()
























##############
# Block init #
##############
class Block:
    def __init__(self, previous_hash, transactions, merkle_root):
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.merkle_root = merkle_root
        self.timestamp = time.time()
        self.nonce = 0

    def compute_hash(self):
        block_header = str(self.previous_hash) + str(self.merkle_root) + str(self.timestamp) + str(self.nonce)
        return hashlib.sha256(block_header.encode()).hexdigest()
    
    def mine_block(self):
        target = '0' * DIFFICULTY
        while self.compute_hash()[:DIFFICULTY] != target:
            self.nonce += 1
        print("Block mined:", self.compute_hash())


def get_witness_commitment():
    # Implement the logic to extract witness commitment from the coinbase transaction
    # If it exists
    pass

"""
COINBASE TXN::>

:> Coinbase:
    @> https://learnmeabitcoin.com/technical/transaction/input/#coinbase
A coinbase is a special type of input found in coinbase transactions.
The input for a coinbase transaction doesn't need to reference any previous outputs, as a coinbase transaction is simply used to collect the block reward. Therefore, the TXID is set to all zeros, the VOUT is set to the maximum value, and a miner is free to put any data they like inside the ScriptSig.
For example, this is the coinbase transaction for block
"""

##################
## Coinbase txn ##
##################

def create_coinbase_txn_data(txn_list):
    reward = 0
    for txnId in txn_list:
        reward += validate_txn.fees(txnId)
    
    version = "01000000"
    in_count = "01"
    in_txnId = "0000000000000000000000000000000000000000000000000000000000000000"
    vout = "ffffffff"
    scriptsig_size = "07"
    scriptsig = "0453ec131c0108" # RANDOM
    sequence = "ffffffff"

    out_count = "01"
    out_amt = f"{validate_txn.to_little_endian(reward, 8)}"

    return version+in_count+in_txnId+vout+scriptsig_size+scriptsig+sequence+out_count+out_amt

def get_coinbase_txn_id(txn_list):
    data = create_coinbase_txn_data(txn_list)

    bytes_data = bytes.fromhex(data)
    txn_id_bytes = hashlib.sha256(hashlib.sha256(bytes_data).digest()).digest()
    txid = txn_id_bytes.hex()

    return txid[::-1]


"""
def create_witness_commitment(txn_ids):
    # Compute the Merkle root of the transaction IDs
    merkle_root = compute_merkle_root(txn_ids)

    # Construct the witness commitment script
    witness_commitment_script = bytearray.fromhex('6a')  # OP_RETURN
    witness_commitment_script.extend(len(merkle_root).to_bytes(1, byteorder='big'))  # Push the Merkle root size
    witness_commitment_script.extend(merkle_root)  # Push the Merkle root

    return bytes(witness_commitment_script)
"""

# witness calculation


"""
ISSUES::
- Do I need to serialize the transaction before calculating `merkle root`?

- mempool/0a8b21af1cfcc26774df1f513a72cd362a14f5a598ec39d915323078efb5a240.json
=> Serialized Hash::> <02000000><01><25c9f7c56ab4b9c358cb159175de542b41c7d38bf862a045fa5da51979e37ffb><01000000><6b><4830450221008f619822a97841ffd26eee942d41c1c4704022af2dd42600f006336ce686353a0220659476204210b21d605baab00bef7005ff30e878e911dc99413edb6c1e022acd012102c371793f2e19d1652408efef67704a2e9953a43a9dd54360d56fc93277a5667d><ffffffff><02><54e805>00000000001976a9141ef7874d338d24ecf6577e6eadeeee6cd579c67188acc8910000000000001976a9142e391b6c47778d35586b1f4154cbc6b06dc9840c88ac00000000


hash256 your transaction to get the txid
and reverse it and sha256 once again to verify if it matches your file name

OBJECTIVE::
- Also, can anyone confirm if i understand the process correctly as of now:

- There are multiple JSON files. And each file is a whole transaction. I have to verify the signatures and scripts of each object in the "vin" array. If I can verify all the objects in vin array, I will say that this particular JSON file is a valid transaction. While, if even one of them cant be verified I will say its not a valid transaction, and disregard the ENTIRE file. Correct?
After that, I will have the set of verified, but unconfirmed transactions, and will proceed to mine the block. 

- you'll have to parse and serialise the entire transaction to validate the signature from vins

- assume validity of locktime based on block height. You need to validate locktime which are UNIX timestamps

- Claculate weight of the transaction
"""


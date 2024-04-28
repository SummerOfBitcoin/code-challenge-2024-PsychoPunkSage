import time
import hashlib
import list_valid_txn
import coinbase_data as coinbase
import helper.converter as convert
import helper.txn_info as txinfo
import helper.merkle_root as merkle 
import helper.txn_metrics as metrics

BLOCK_VERSION = 4
MEMPOOL_DIR = "mempool"
OUTPUT_FILE = "output.txt"
DIFFICULTY = "0000ffff00000000000000000000000000000000000000000000000000000000"
PREV_BLOCK_HASH = "0000000000000000000000000000000000000000000000000000000000000000"
NONCE_MIN = 0x0
NONCE_MAX = 0xFFFFFFFF

def _block_header_wo_nonce(merkle_root):
    """
    Constructs a block header without the nonce.

    @param merkle_root: The Merkle root of the block.
    @type  merkle_root: str
    @return           : The block header without the nonce.
    @rtype            : bytes
    """
    block_version_bytes = bytes.fromhex(convert.to_little_endian(BLOCK_VERSION, 4))
    prev_block_hash_bytes = bytes.fromhex(PREV_BLOCK_HASH)
    merkle_root_bytes = bytes.fromhex(merkle_root)
    timestamp_bytes = bytes.fromhex(convert.to_little_endian(int(time.time()), 4))
    bits_bytes = bytes.fromhex(convert.to_little_endian(int("1F00FFFF", 16), 4))
    return block_version_bytes+prev_block_hash_bytes+merkle_root_bytes+timestamp_bytes+bits_bytes

def mine_block(transaction_files):
    """
    Mine a block with the given transactions.

    @param transaction_files: List of transaction files to include in the block.
    @type  transaction_files: list
    @return                 : Tuple containing block header hex, transaction IDs, nonce, coinbase hex, and coinbase transaction ID.
    @rtype                  : tuple
    """
    nonce = 0
    txids = [txinfo.txid(tx) for tx in transaction_files]

    # Witness Commitment
    witness_commitment = coinbase.calculate_witness_commitment(transaction_files)
    print("witneness commitment:", witness_commitment)

    fees = sum([metrics.fees(tx) for tx in transaction_files])
    # wt = sum([validate_txn.txn_weight(tx)[1] for tx in transaction_files])
    # print(f"fees::> {fees}")
    # print(f"wt::> {wt}")
    coinbase_hex, coinbase_txid = coinbase.create_coinbase_transaction(witness_commitment=witness_commitment, fees= fees)

    # Merkle root calculation of [coinbase + other] transaction
    merkle_root = merkle.merkle_root_calculator([coinbase_txid]+txids)

    ################
    # BLOCK HEADER #
    ################
    nonce_bytes = bytes.fromhex(convert.to_little_endian(nonce, 4))
    block_header = _block_header_wo_nonce(merkle_root) + nonce_bytes
    # print(f"BH::> {block_header}")

    #################
    # CORRECT NONCE #
    #################
    target = int(DIFFICULTY, 16)
    # print("target:", target)
    while True:
        block_hash = hashlib.sha256(hashlib.sha256(block_header).digest()).digest()
        rev_hash = block_hash[::-1]
        if int.from_bytes(rev_hash, "big") <= target:
            break
        nonce += 1
        nonce_bytes = bytes.fromhex(convert.to_little_endian(nonce, 4))
        block_header = block_header[:-4] + nonce_bytes  # Update the nonce (LAST 4 bytes) in the header....
        # Nonce Range Validation
        if nonce < NONCE_MIN or nonce > NONCE_MAX:
            raise ValueError("Invalid nonce")

    print(f"nonce::> {nonce}")
    block_header_hex = block_header.hex() # Final Hash

    return block_header_hex, txids, nonce, coinbase_hex, coinbase_txid

def main():
    # Read transaction files
    # transactions = read_transactions()
    transactions = list_valid_txn.list_valid_txn()

    if not any(transactions):
        raise ValueError("No valid transactions to include in the block")

    n = 0
    wt = 0
    while wt < 4000000:
        wt += metrics.txn_weight(transactions[n])[1]
        n += 1
    print(f"Total transactions: {len(transactions[:n-1])}")
    # Mine the block
    block_header, txids, nonce, coinbase_tx_hex, coinbase_txid = mine_block(transactions[: n-1])

    # Corrected writing to output file
    with open(OUTPUT_FILE, "w") as file:
        file.write(f"{block_header}\n{coinbase_tx_hex}\n{coinbase_txid}\n")
        file.writelines(f"{txid}\n" for txid in txids)



if __name__ == "__main__":
    main()
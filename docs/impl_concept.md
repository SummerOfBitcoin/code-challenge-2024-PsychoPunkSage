## ToDo: Simulate Mining of Blocks

>> Write a code that will process the txns, mines them, validates them and put them in a block.

> **INPUT:**
> Folders with JSON Files

> **OUTPUT:** (Block - output.txt)
> - First line: The block header.
> - Second line: The serialized coinbase transaction.
> - Following lines: The transaction IDs (txids) of the transactions mined in the block, in order. The first txid should be that of the coinbase transaction

> **Given:**
> - Difficulty target: `0000ffff00000000000000000000000000000000000000000000000000000000`

### Things to remember:

>> **Block Mining:**

> **Step 1: Transaction Selection**

`Mempool Overview`: The mempool is a collection of all pending transactions waiting to be included in a block.<br>
`Transaction Prioritization`: Transactions may be prioritized based on factors like transaction fee, transaction size, etc.<br>
`Transaction Sorting`: Sort transactions based on priority, with higher fee transactions typically given priority.<br>
`Transaction Filtering`: Remove any transactions deemed invalid or conflicting.

> **Step 2: Transaction Validation**

`Input Validation`: Check if each transaction's inputs are valid and exist in the UTXO (Unspent Transaction Output) set.<br>
- **Access UTXO Set**: Access the Unspent Transaction Output (UTXO) set, which contains records of all unspent transaction outputs.
- **Check Inputs**: For each transaction, verify that all inputs referenced by the transaction are present in the UTXO set.
- **UTXO Usage**: Ensure that inputs are not already spent by checking if they exist in the UTXO set.

`Double Spending Check`: Ensure no inputs are spent more than once.<br>
- **Transaction History**: Maintain a record of all spent transaction outputs to detect double spending attempts.
- **Transaction Order**: Validate that each input of a transaction has not been previously spent in another transaction within the same block or earlier blocks.
  
`Script Validation`: Validate the transaction scripts, including signature verification.<br>
- **Script Execution**: Execute the scriptSig and scriptPubKey scripts associated with each transaction input and output.
- **Signature Verification**: Verify that the signature provided in the transaction input matches the corresponding public key and the associated output's scriptPubKey.


`Transaction Fee Check`(optional): Verify that the transaction fee is sufficient according to current network standards.<br>
- **Fee Calculation**: Calculate the transaction fee as the difference between the total input amounts and the total output amounts.
- **Minimum Fee Requirement**: Compare the calculated fee with the minimum required fee according to network policies and current block space availability.
- **Fee Rate Consideration**: Take into account the transaction fee rate (satoshi per byte) to determine if the fee is sufficient for timely inclusion in a block.

`Consensus Rules Compliance`(optional): Ensure all transactions adhere to Bitcoin's consensus rules.<br>

> **Step 3: Block Header Construction**

`Version`: Define the block version number.<br>
`Previous Block Hash`: Include the hash of the previous block in the blockchain to maintain the chain's continuity.<br>
`Merkle Root`: Calculate the Merkle root hash of all valid transactions included in the block.<br>
`Timestamp`: Assign a timestamp to the block, indicating when the block was created.<br>
`Target Difficulty`: Determine the target difficulty for mining the block.<br>
`Nonce`: Initialize the nonce value, which miners will increment during mining to find a valid block hash.<br>

> **Step 4: Mining**

`Proof-of-Work`: Start the mining process by selecting a nonce value and combining it with the block header.<br>
- Start by initializing the block header with necessary information like version, previous block hash, Merkle root, timestamp, and target difficulty.
- Generate a nonce value and append it to the block header.
- Combine the block header with the nonce to form a candidate block.

`Block Hash Calculation`: Hash the block header using the SHA-256 cryptographic hash function.<br>
- Hash the candidate block using the SHA-256 cryptographic hash function.
- This hashing process creates a unique hash value for the block.

`Difficulty Adjustment`: Compare the resulting hash with the target difficulty. If the hash meets the difficulty criteria (has a sufficient number of leading zeros), the block is considered mined.<br>
- It will be constant for us := `0000ffff00000000000000000000000000000000000000000000000000000000`

`Nonce Incrementation`: If the hash does not meet the difficulty criteria, increment the nonce value and repeat the hashing process.<br>
- If the hash does not meet the difficulty criteria, increment the nonce value by 1.
- Update the block header with the new nonce.
- Repeat the hashing process by combining the updated block header with the incremented nonce.

`Block Submission`: Once a valid block hash is found, broadcast the block to the network for validation and inclusion in the blockchain.<br>
- We need to output the Block infos in `output.txt`

> **Step 5: Block Validation (Performed by Network Nodes)** \<optional/Not req. here>

`Consensus Verification`: Network nodes verify the validity of the block, including the transactions it contains and its adherence to consensus rules.<br>
`Chain Longest-Valid Rule`: Nodes accept the block only if it extends the longest valid chain and is considered valid according to network consensus.<br>
`Block Propagation`: Validated blocks are propagated to other nodes in the network for further verification and propagation.<br>
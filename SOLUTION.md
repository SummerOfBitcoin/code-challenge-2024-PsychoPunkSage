# **Work Documentation**

>> **The purpose of the work documentation is to offer transparency and clarity regarding the execution of tasks and the attainment of objectives. It serves as a reference point for evaluators to understand the workflow and rationale behind various actions undertaken during the project.**

> **Disclaimer:**

The limited number of commits visible in my project repository is attributed to the initial stages of development conducted within a sandbox environment. During this phase, I diligently iterated on the project, periodically pushing updates to the sandbox repository. Only after achieving a significant milestone and ensuring the quality and stability of the code did I transition it to my primary repository. This approach allowed for thorough testing and validation before committing to the main repository, ensuring that only appreciable progress was reflected in the public-facing version.

**`Sandbox Environment::> `** [LINK](https://github.com/PsychoPunkSage/OpenSource_Logs/tree/main/BIP)

## **Design Approach:**

> **Tree View (Main code)**

<details>
<summary>Tree Structure</summary>

```
src
├── blocks.py
├── coinbase_data.py
├── helper
│   ├── converter.py
│   ├── merkle_root.py
│   ├── pubKey_uncompressor.py
│   ├── __pycache__
│   │   ├── converter.cpython-311.pyc
│   │   ├── merkle_root.cpython-311.pyc
│   │   ├── txn_info.cpython-311.pyc
│   │   └── txn_metrics.cpython-311.pyc
│   ├── txn_info.py
│   └── txn_metrics.py
├── list_valid_txn.py
├── __pycache__
│   ├── coinbase_data.cpython-311.pyc
│   ├── coinbase_txn_my.cpython-311.pyc
│   ├── list_valid_txn.cpython-311.pyc
│   └── validate_txn.cpython-311.pyc
├── scripts
│   ├── p2pkh.py
│   ├── p2sh.py
│   ├── p2wpkh.py
│   └── __pycache__
│       ├── p2pkh.cpython-311.pyc
│       ├── p2sh.cpython-311.pyc
│       └── p2wpkh.cpython-311.pyc
└── validate_txn.py

6 directories, 23 files
```

</details><br>


* As evident (from above tree str), the primary codebase resides within the **`src`** directory. Each file and folder within this directory is meticulously named to reflect its designated functionality, thereby ensuring clarity and ease of understanding.
* My codebase follows a strictly **discretized structure**, adhering to the principle of `Write Once and Use Many` times, with some exceptions where necessary. Each file is organized based on its functionality, ensuring clarity and efficiency in code management. For instance, within the `helper/converter directory`, you'll find code dedicated to data conversion tasks, such as transforming data formats like `HASH256` and `HASH160`. This modular approach enhances code reusability, maintainability, and overall development agility.

### Quick Rundown of COdeBase

1. `helper`
   - These modules encapsulate functionality that is extensively utilized throughout the entire codebase on numerous occasions.
   - **converter.py** ::> `to_compact_size(())` `to_little_endian()` `to_hash160()` `to_hash256()` `to_sha256()` `to_reverse_bytes_string()`
   - **merkle_root.py** ::> `merkle_root_calculator()`
   - **txn_info.py** ::> `create_raw_txn_data_min()` `create_raw_txn_data_full()` `txid()` `wtxid()` `coinbase_txn_id()`
   - **txn_metrics.py** ::> `txn_weight()` `fees()`
   - Each file has a distinct set of functions, each characterized by a consistent level of performance.

2. `scripts`
   - These files are designed to function autonomously and can be executed individually, operating independently from one another. Each file encapsulates its own distinct codebase, complete with requisite helper functions, ensuring self-sufficiency and seamless execution in isolation.
   - **p2pkh** ::> `validate_signature` `_to_compact_size` `_little_endian` `to_hash160` `segwit_txn_data` `legacy_txn_data` `validate_p2pkh_txn`
   - **p2wpkh** ::> `validate_signature` `_to_compact_size` `_little_endian ` `segwit_txn_data` `to_hash160` `_validate_p2wpkh_txn` `validate_p2wpkh_txn`
   - **p2sh** ::> `to_hash160` `to_compact_size` `to_little_endian` `legacy_txn_data` `validate_p2sh_txn_basic` `validate_p2sh_txn_adv`
   - As you can see I have only verified **`p2sh`**(partially) **`p2wpkh`** and **`p2pkh`**  transactions. I used these transaction to formulate my block.

3. `coinbase_data.py`
   - **Implementation**: `calculate_witness_commitment()` and `create_coinbase_transaction()`
   - The function `create_coinbase_transaction` is used to generate coinbase transaction data and its corresponding transaction ID, aligning with its descriptive name. Conversely, `calculate_witness_commitment` is specifically used for computing the witness commitment of the coinbase transaction. 
   - This file exclusively handles operations pertaining to coinbase transactions.

4. `validate_txn.py`
   - This script systematically evaluates each transaction, providing a comprehensive assessment of their validity.
   - It orchestrates fundamental validation procedures alongwith transaction validation scripts housed in the designated **`scripts`** folder.
   - It serves as the central hub for all transaction validation operations, seamlessly integrating various components and functionalities related to transaction validation.

5. `list_valid_txn.py`
   - The script undertakes a comprehensive parsing process, examining each transaction contained within the **MEMPOOL** directory. Utilizing the validation scripts within the **`validate_txn`** file, it cross-validates each transaction to ascertain its integrity.

   - Upon completion of the validation process, the script generates a list of valid transactions. It arranges this list to ensure that all **SegWit transactions** are positioned at the **forefront**, followed by non-SegWit transactions. This arrangement aims to optimize the mining process by prioritizing SegWit transactions, ***thereby maximizing the accrued fees*** and enhancing overall efficiency.

6. `blocks.py`
   - This is the **main function** that orchestrates the process of block mining, utilizing key implementations such as `_block_header_wo_nonce()`, `mine_block()`, and `main()`. It receives a list of valid transactions from **`list_valid_txn.py`** and determining the total transactions to be included in the block within the constraints of *maximum weight allowance*. Subsequently, the function calculates the **block header** by identifying the appropriate **nonce** that fulfills the specified difficulty criteria, ultimately resulting in the successful mining of the block.

## **Implementation Details:**

### Work-flow:
![Work-flow diagram](<image/workflow.jpg>)
- from the above diagram you can see how different components of my code interact with each-other at runtime.

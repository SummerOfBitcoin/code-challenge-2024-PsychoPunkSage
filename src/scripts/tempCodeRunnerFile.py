redeemscript_asm = txn_data["vin"][3]["inner_redeemscript_asm"]
scriptpubkey_asm = txn_data["vin"][3]["scriptsig_asm"]

print(f"p2sh(basic)::> {validate_p2sh_txn_basic(redeemscript_asm, scriptpubkey_asm), scriptsig_asm}")
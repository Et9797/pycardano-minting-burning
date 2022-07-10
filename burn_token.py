from pycardano import *

NETWORK = Network.TESTNET
chain_context = BlockFrostChainContext(
    project_id='',
    network=NETWORK
)

# Token minter 
skey1 = PaymentSigningKey.load("usr1.skey")
vkey1 = PaymentVerificationKey.from_signing_key(skey1)
addr1 = Address(vkey1.hash(), network=NETWORK)
policy_skey = PaymentSigningKey.load("policy.skey")
policy_vkey = PaymentVerificationKey.from_signing_key(policy_skey)

# Receiver of token
skey2 = PaymentSigningKey.load("usr2.skey")
vkey2 = PaymentVerificationKey.from_signing_key(skey2)
addr2 = Address(vkey2.hash(), network=NETWORK)


#---- Create policy id (hash of policy script) ----
pubkey_policy = ScriptPubkey(policy_vkey.hash())
must_before_slot = InvalidHereAfter(70_000_000)
policy = ScriptAll([pubkey_policy, must_before_slot])
policy_id = policy.hash()
print(f"policy_id: {policy_id}", end='\n\n')

#---- Token to burn ----
token = MultiAsset.from_primitive(
    {
        policy_id.payload: {
            b'FingerLickinGood6969': -1
        }
    }
)
# Token utxo
utxos = chain_context.utxos(str(addr2))
token_burn_utxo = [
    utxo for utxo in utxos if utxo.input.transaction_id.payload.hex()
    == '79a08fe15ad3c197c7c5e97d6c6886dc78e882b68217d17641cff408a3341b1d' 
].pop()

#---- Build and submit burning token tx ----
builder = TransactionBuilder(chain_context)

builder.ttl = must_before_slot.after
builder.native_scripts = [policy]
builder.mint = token

builder.add_input(token_burn_utxo)

signed_tx = builder.build_and_sign(signing_keys=[skey2, policy_skey], change_address=addr1)
print(signed_tx, end="\n\n")
print(f"transaction id: {signed_tx.id}", end="\n\n")
chain_context.submit_tx(signed_tx.to_cbor())
print("###### Transaction submitted. ######")

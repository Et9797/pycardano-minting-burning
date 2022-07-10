from pycardano import *
import json

NETWORK = Network.TESTNET
chain_context = BlockFrostChainContext(
    project_id='testnetVrmjl6D9NhZQF7HM2AZYDew9HyWXnw7a',
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
with open("./policy.id", "w") as f:
    f.write(policy_id.payload.hex())

#---- Create token ----
token = MultiAsset.from_primitive(
    {
        policy_id.payload: {
            b'FingerLickinGood6969': 1
        }
    }
)

#---- Create metadata ----
metadata = {
    721: {
        policy_id.payload.hex(): {
            'FingerLickinGood6969': {
                'description': "Finger Licking Good Token",
                'name': 'FingerLickingGood6969',
                'id': 6969,
                'image': 'ipfs://QmRhTTbUrPYEw3mJGGhQqQST9k86v1DPBiTTWJGKDJsVFw'
            }
        }
    }
}

with open('./metadata.txt', "w") as f:
    json.dump(metadata, f)

#---- Build and submit minting tx ----
builder = TransactionBuilder(chain_context)

auxiliary_data = AuxiliaryData(AlonzoMetadata(metadata=Metadata(metadata)))
builder.auxiliary_data = auxiliary_data

builder.ttl = must_before_slot.after

builder.native_scripts = [policy]

builder.mint = token

builder.add_input_address(addr1)
# min_val = min_lovelace(Value(0, token), chain_context) # or just 2_000_000 flat
builder.add_output(
    TransactionOutput(
        addr2,
        Value(2_000_000, token)
    )
)

signed_tx = builder.build_and_sign(signing_keys=[skey1, policy_skey], change_address=addr1)
print(signed_tx, end="\n\n")
print(f"transaction id: {signed_tx.id}", end='\n\n')
chain_context.submit_tx(signed_tx.to_cbor())
print("######## Transaction submitted #########")
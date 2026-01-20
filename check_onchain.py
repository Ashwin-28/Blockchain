from web3 import Web3
import json
import os

BLOCKCHAIN_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0x299264E267764B8B6604Fd3a62bB018222AbC967"
SUBJECT_ID = "2244a0cdc0db2dbb7ec00baef0a5fa6d2a35bc8c9b39751bad67a9a090e9a48c"

w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))

abi_path = "c:/Users/Ramanathan/Desktop/Kavin/Blockchain_AG/build/contracts/BiometricRegistry.json"
with open(abi_path, 'r') as f:
    contract_json = json.load(f)
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_json['abi'])

print(f"Checking subject: {SUBJECT_ID}")
exists, active = contract.functions.checkSubjectStatus(bytes.fromhex(SUBJECT_ID)).call()
print(f"Exists: {exists}")
print(f"Active: {active}")

total_subjects = contract.functions.totalSubjects().call()
print(f"Total Subjects: {total_subjects}")

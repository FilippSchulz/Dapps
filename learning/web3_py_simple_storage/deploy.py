import os
from solcx import compile_standard
from web3 import Web3
import json
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", 'r') as file:
    simple_storage_file = file.read()

# Compile Our solidity code

compiled_sol = compile_standard(
    {
        'language': 'Solidity',
        'sources': {'SimpleStorage.sol': {'content': simple_storage_file}},
        'settings': {
            'outputSelection': {
                '*': {'*': ['abi', 'metadata', 'evm.bytecode', 'evm.sourceMap']}
            }
        },

    },
    solc_version='0.6.0',
)

# get compiled version of solidity code
with open('compiled_code.json', 'w') as file:
    json.dump(compiled_sol, file)

# get bytecode

bytecode = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['evm']['bytecode']['object']

# get ABI
ABI = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['abi']

# For connecting to Rinkeby [TestNet]

w3 = Web3(Web3.HTTPProvider(os.getenv('ENDPOINT')))
chain_id = int(os.getenv('CHAIN_ID'))
my_address = os.getenv('MY_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')

# create contract in python
SimpleStorage = w3.eth.contract(abi=ABI, bytecode=bytecode)

# get the number of transactions
nonce = w3.eth.getTransactionCount(my_address)

# make txn
txn = SimpleStorage.constructor().buildTransaction({"chainId": chain_id, "from": my_address, "nonce": nonce})

# signed txn
sign_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)

# send signed txn and deploying contract

tx_hash = w3.eth.send_raw_transaction(sign_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# working with contract
# Call - simulate function action | not make a change in blockchain
# Transact - Make a change in blockchain

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=ABI)

# get value of favorite number | simulating
print(simple_storage.functions.retrieve().call())
print(simple_storage.functions.store(15).call())

# get store and value of favorite number | Make a change in blockchain

store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId": chain_id, "from": my_address, "nonce": nonce + 1})

sign_txn_store = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
tx_hash_store = w3.eth.send_raw_transaction(sign_txn_store.rawTransaction)
print(simple_storage.functions.retrieve().call())

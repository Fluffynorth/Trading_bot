import json
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account

# Constants
PHOENIXPLORER_URL = "https://rpc.phoenixplorer.com"
WALLET_ADDRESS = "Wallet-Address-Goes-Here"
PRIVATE_KEY = "Private-Key-Goes-Here"
TOKEN_A_ABI_FILE = "token_a_abi.json"
TOKEN_B_ABI_FILE = "token_b_abi.json"
ROUTER_ABI_FILE = "router_abi.json"
TOKEN_A_ADDRESS = "0xcb186051DD62914B6dFc56c257823bfDA20DbEe6"
TOKEN_B_ADDRESS = "0x542502B1eB20d220F8dD8eaE7cB8F870Af7b0b6B"
ROUTER_ADDRESS = "0x8d5567953B0aC3348C959c722D4327f29155AEE4"
Factory_ADDRESS = "0xaeA039F542c88Cc14A6Ca38deeeECf91D9B790D6"
TRADE_AMOUNT_A = 100000000000000000000  # 1 Token A
TRADE_AMOUNT_B = 100000000000000000000  # 2 Token B
GAS_LIMIT = 250000
GAS_PRICE = 3 * 10**9  # 3 Gwei
CHAIN_ID = 13381


# Setup Web3
w3 = Web3(Web3.HTTPProvider(PHOENIXPLORER_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
assert w3.is_connected()

# Load ABIs
with open(TOKEN_A_ABI_FILE) as f:
    token_a_abi = json.load(f)

with open(TOKEN_B_ABI_FILE) as f:
    token_b_abi = json.load(f)

with open(ROUTER_ABI_FILE) as f:
    router_abi = json.load(f)

# Setup Contracts
token_a = w3.eth.contract(address=TOKEN_A_ADDRESS, abi=token_a_abi)
token_b = w3.eth.contract(address=TOKEN_B_ADDRESS, abi=token_b_abi)
router = w3.eth.contract(address=ROUTER_ADDRESS, abi=router_abi)

while True:
    # Approve Router for Token A
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
    tx_a_approval = token_a.functions.approve(ROUTER_ADDRESS, TRADE_AMOUNT_A).build_transaction({
        'chainId': CHAIN_ID,
        'gas': GAS_LIMIT,
        'gasPrice': GAS_PRICE,
        'nonce': nonce,
    })

    signed_tx_a_approval = Account.sign_transaction(tx_a_approval, PRIVATE_KEY)
    tx_hash_a_approval = w3.eth.send_raw_transaction(signed_tx_a_approval.rawTransaction)
    print(f"Token A approval transaction sent, tx hash: {tx_hash_a_approval.hex()}")

    # Approve Router for Token B
    nonce += 1
    tx_b_approval = token_b.functions.approve(ROUTER_ADDRESS, TRADE_AMOUNT_B).build_transaction({
        'chainId': CHAIN_ID,
        'gas': GAS_LIMIT,
        'gasPrice': GAS_PRICE,
        'nonce': nonce,
    })
    signed_tx_b_approval = Account.sign_transaction(tx_b_approval, PRIVATE_KEY)
    tx_hash_b_approval = w3.eth.send_raw_transaction(signed_tx_b_approval.rawTransaction)
    print(f"Token B approval transaction sent, tx hash: {tx_hash_b_approval.hex()}")

    # Swap Token A for Token B
    nonce += 1
    deadline = int(time.time()) + 600  # 10 minutes from now
    path = [TOKEN_A_ADDRESS, TOKEN_B_ADDRESS]
    tx_a_to_b = router.functions.swapExactTokensForTokens(
        TRADE_AMOUNT_A,
        0,  # minimum amount of Token B to receive, set to 0 to accept any amount
        path,
        WALLET_ADDRESS,
        deadline).build_transaction({
            'chainId': CHAIN_ID,
            'gas': GAS_LIMIT,
            'gasPrice': GAS_PRICE,
            'nonce': nonce,
        })

    signed_tx_a_to_b = w3.eth.account.sign_transaction(tx_a_to_b, PRIVATE_KEY)
    tx_hash_a_to_b = w3.eth.send_raw_transaction(signed_tx_a_to_b.rawTransaction)
    print(f"Token A to Token B swap transaction sent, tx hash: {tx_hash_a_to_b.hex()}")

    # Swap Token B for Token A
    nonce += 1
    deadline = int(time.time()) + 600  # 10 minutes from now
    path = [TOKEN_B_ADDRESS, TOKEN_A_ADDRESS]
    tx_b_to_a = router.functions.swapExactTokensForTokens(
        TRADE_AMOUNT_B,
        0,  # minimum amount of Token A to receive, set to 0 to accept any amount
        path,
        WALLET_ADDRESS,
        deadline).build_transaction({
            'chainId': CHAIN_ID,
            'gas': GAS_LIMIT,
            'gasPrice': GAS_PRICE,
            'nonce': nonce,
        })

    signed_tx_b_to_a = w3.eth.account.sign_transaction(tx_b_to_a, PRIVATE_KEY)
    tx_hash_b_to_a = w3.eth.send_raw_transaction(signed_tx_b_to_a.rawTransaction)
    print(f"Token B to Token A swap transaction sent, tx hash: {tx_hash_b_to_a.hex()}")

    # Wait for a minute
    time.sleep(80)
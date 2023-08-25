import requests
import json
import time
import threading
from web3 import Web3
import asyncio
from private import private_keys, abi, addresses ,min_wait_time,max_wait_time,account_delay1,account_delay2,max_retry_attempts,max_share_amount,min_share_amount,max_share_price
import random

w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))


account_delay = random.randint(account_delay1, account_delay2)

def buy_and_sell_randomly(private_key, account_number):
    try:
        w3.eth.default_account = w3.eth.account.from_key(private_key).address
        contract_address = "0xCF205808Ed36593aa40a44F10c7f7C2F67d4A4d4"
        contract = w3.eth.contract(address=contract_address, abi=abi)

        # Choose a random wallet address
        random_address = random.choice(addresses)
        random_address = w3.to_checksum_address(random_address)

        retry_count = 0
        while retry_count < max_retry_attempts:
            try:
                # Generate a random number of shares to buy
                random_share_amount = random.randint(min_share_amount, max_share_amount)

                # Get the current share price
                share_price = float(contract.functions.getBuyPriceAfterFee(random_address, random_share_amount).call()) / pow(10, 18)

                # Check if the share price exceeds the maximum allowed
                if share_price > max_share_price:
                    print(f"Account {account_number}: Share price ({share_price} ETH) exceeds maximum allowed price. Retrying with different shares...")
                    random_share_amount = random.randint(min_share_amount, max_share_amount)
                    retry_count += 1
                    continue

                # Buy random shares
                input_buy = contract.encodeABI(fn_name="buyShares", args=[random_address, random_share_amount])
                nonce_buy = w3.eth.get_transaction_count(w3.eth.default_account)
                tx_buy = {
                    'chainId': 8453,
                    'gas': 89000,
                    'from': w3.eth.default_account,
                    'to': contract_address,
                    'gasPrice': w3.to_wei('1.5', 'gwei'),
                    'nonce': nonce_buy,
                    'value': w3.to_wei(share_price * random_share_amount, "ether"),
                    'data': input_buy
                }

                signed_tx_buy = w3.eth.account.sign_transaction(tx_buy, private_key)
                tx_hash_buy = w3.eth.send_raw_transaction(signed_tx_buy.rawTransaction)

                print(f"Account {account_number}: Buy Transaction sent for {random_share_amount} shares at {share_price} ETH each: {tx_hash_buy.hex()}")

                # Wait for a random amount of time
                wait_time = random.randint(min_wait_time, max_wait_time)
                print(f"Account {account_number}: Waiting for {wait_time} seconds before selling...")
                time.sleep(wait_time)

                # Sell the shares
                input_sell = contract.encodeABI(fn_name="sellShares", args=[random_address, random_share_amount])
                nonce_sell = w3.eth.get_transaction_count(w3.eth.default_account)
                tx_sell = {
                    'chainId': 8453,
                    'gas': 78888,
                    'from': w3.eth.default_account,
                    'to': contract_address,
                    'gasPrice': w3.to_wei('1.5', 'gwei'),
                    'nonce': nonce_sell,
                    'data': input_sell
                }

                signed_tx_sell = w3.eth.account.sign_transaction(tx_sell, private_key)
                tx_hash_sell = w3.eth.send_raw_transaction(signed_tx_sell.rawTransaction)

                print(f"Account {account_number}: Sell Transaction sent for {random_share_amount} shares: {tx_hash_sell.hex()}")

                break  # Exit the retry loop if buying and selling succeeded

            except Exception as e:
                if 'insufficient funds for gas * price + value' in str(e):
                    print(f"Account {account_number}: Insufficient funds, retrying with different shares...")
                    random_share_amount = random.randint(min_share_amount, max_share_amount)
                    retry_count += 1
                    continue
                else:
                    print(f"Account {account_number}: An error occurred:", str(e))
                    break  # Exit the retry loop for other errors

    except Exception as e:
        print("An error occurred:", str(e))

    # Delay between accounts
    time.sleep(account_delay)


# Infinite loop to repeat the buy and sell operations
account_number = 1
while True:
    # Choose a random private key
    random_private_key = random.choice(private_keys)
    buy_and_sell_randomly(random_private_key, account_number)
    account_number += 1

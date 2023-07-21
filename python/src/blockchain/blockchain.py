from .transaction import Transaction, TransactionOutput
from .block import Block
import requests
import time

class Blockchain:
    def __init__(self, difficulty, pending_transactions, nodes):
        self.chain = []
        self.difficulty = difficulty
        self.pending_transactions = pending_transactions
        self.nodes = nodes
        self.create_genesis_block()

    def create_genesis_block(self):
        # Create a genesis block with index 0, current time, an empty list of transactions, and a dummy previous hash
        genesis_block = Block(0, time.time(), [], "0")
        # Mine the genesis block with the given difficulty
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def add_block(self, block):
        if block.validate_transactions() and block.previous_hash == self.chain[-1].hash:
            self.chain.append(block)
            self.pending_transactions = []
            self.broadcast_block(block)
            # Return True if the block is added successfully
            return True
        else:
            # Return False if the block is invalid or rejected
            return False

    def validate_chain(self):
        # Loop through all blocks in the chain except the genesis block
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
           
            if current_block.hash != current_block.calculate_hash():
                return False
           
            if current_block.previous_hash != previous_block.hash:
                return False
        
        # Return True if all blocks are valid
        return True

    def create_transaction(self, sender, receiver, amount, private_key):
        # Create a list of unspent transaction outputs (UTXOs) for the sender
        inputs = self.get_utxo(sender)
        # Check if the sender has enough balance to make the transaction
        input_sum = 0
        for input in inputs:
            input_sum += input.amount
        if input_sum < amount:
            return False
        # Create a list of new transaction outputs for the receiver and the sender (if there is any change)
        outputs = []
        outputs.append(TransactionOutput(receiver, amount))
        if input_sum > amount:
            outputs.append(TransactionOutput(sender, input_sum - amount))
        # Create a new transaction with the sender, receiver, amount, inputs, and outputs
        transaction = Transaction(sender, receiver, amount, None, inputs, outputs)
        # Sign the transaction with the sender's private key
        signature = transaction.sign_transaction(private_key)
        transaction.signature = signature
        # Add the transaction to the pending transactions list
        self.pending_transactions.append(transaction)
        # Return True if the transaction is created successfully
        return True

    def get_balance(self, address):
        # Get the list of unspent transaction outputs (UTXOs) for the address
        utxos = self.get_utxo(address)
        # Sum up the amounts of all UTXOs and return it as the balance
        balance = 0
        for utxo in utxos:
            balance += utxo.amount
        return balance

    def get_utxo(self, address):
        utxos = []
        for block in self.chain:
            for transaction in block.transactions:
                for output in transaction.outputs:
                    if output.receiver == address:
                        spent = False
                        for block2 in self.chain:
                            for transaction2 in block2.transactions:
                                for input in transaction2.inputs:
                                    # Check if the input references the output
                                    if input.sender == address and input.amount == output.amount and input.signature == output.signature:
                                        spent = True
                                        # Break out of the inner loops
                                        break
                                if spent:
                                    break
                            if spent:
                                break
                        # If the output is not spent, add it to the UTXOs list
                        if not spent:
                            utxos.append(output)
        # Return the UTXOs list
        return utxos

    def broadcast_block(self, block):
        for node in self.nodes:
            # Send a POST request to the node's /add_block route with the block data as JSON
            requests.post(f"http://{node}/add_block", json=block.__dict__)

    def request_blocks(self):
        chain_replaced = False
        for node in self.nodes:
            print(f"Requesting blocks from {node}...")
            try:
                # Send a GET request to the node's /get_blocks route and get the response as JSON
                response = requests.get(f"http://{node}/get_blocks").json()
                # Get the length of the node's chain and compare it with your own chain's length
                node_chain_length = response["length"]
                my_chain_length = len(self.chain)
                # If the node's chain is longer than your own chain, replace your chain with the node's chain
                if node_chain_length > my_chain_length:
                    self.chain = [Block(**block_data) for block_data in response["chain"]]
                    print(f"Chain replaced with {node}'s chain")
                    chain_replaced = True
                else:
                    print(f"No need to replace chain with {node}'s chain")
            except Exception as e:
                print(f"Error while requesting blocks from {node}: {e}")
        return chain_replaced

    def consensus(self):
        chain_replaced = False
        for node in self.nodes:
            print(f"Checking {node}'s chain...")
            try:
                # Send a GET request to the node's /validate_chain route and get the response as JSON
                response = requests.get(f"http://{node}/validate_chain").json()
                # Get the validity and length of the node's chain and compare it with your own chain's validity and length
                node_chain_validity = response["valid"]
                node_chain_length = response["length"]
                my_chain_validity = self.validate_chain()
                my_chain_length = len(self.chain)
                # If the node's chain is valid and longer than your own chain, replace your chain with the node's chain
                if node_chain_validity and node_chain_length > my_chain_length:
                    self.chain = [Block(**block_data) for block_data in response["chain"]]
                    print(f"Chain replaced with {node}'s chain")
                    chain_replaced = True
                else:
                    print(f"No need to replace chain with {node}'s chain")
            except Exception as e:
                print(f"Error while checking {node}'s chain: {e}")
        return chain_replaced

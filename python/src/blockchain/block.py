import hashlib
import time

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Concatenate the block data into a string
        block_data = str(self.index) + str(self.timestamp) + str(self.transactions) + str(self.previous_hash) + str(self.nonce)
        # Encode the string using UTF-8 encoding
        block_data = block_data.encode()
        # Calculate the SHA-256 hash of the encoded data
        return hashlib.sha256(block_data).hexdigest()

    def mine_block(self, difficulty):
        # Generate a string of zeros with the same length as the difficulty
        target = "0" * difficulty
        # Loop until the hash starts with enough zeros
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

        print(f"Block {self.index} mined with nonce {self.nonce} and hash {self.hash}")

    def validate_transactions(self):
        # Loop through all transactions in the block
        for transaction in self.transactions:
            if not transaction.validate_transaction():
                # Return False if any transaction is invalid
                return False
        # Return True if all transactions are valid
        return True

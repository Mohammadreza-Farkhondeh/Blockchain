import ecdsa # A library for creating and verifying digital signatures using elliptic curve cryptography

class Transaction:
    def __init__(self, sender, receiver, amount, signature, inputs, outputs):
        self.sender = sender # The public key of the sender of the transaction
        self.receiver = receiver # The public key of the receiver of the transaction
        self.amount = amount # The amount of tokens to transfer
        self.signature = signature # The digital signature of the transaction
        self.inputs = inputs # The list of unspent transaction outputs (UTXOs) that are used as inputs for the transaction
        self.outputs = outputs # The list of new transaction outputs that are created by the transaction

    def sign_transaction(self, private_key):
        transaction_data = str(self.sender) + str(self.receiver) + str(self.amount)
        # Encode the string using UTF-8 encoding
        transaction_data = transaction_data.encode()
        # Create a signing key object from the private key
        signing_key = ecdsa.SigningKey.from_string(private_key)
        # Sign the transaction data using the signing key and SHA-256 hash function
        signature = signing_key.sign(transaction_data, hashfunc=hashlib.sha256)
        return signature.hex()

    def verify_signature(self):
        transaction_data = str(self.sender) + str(self.receiver) + str(self.amount)
        # Encode the string using UTF-8 encoding
        transaction_data = transaction_data.encode()
        # Create a verifying key object from the sender's public key
        verifying_key = ecdsa.VerifyingKey.from_string(self.sender)
        # Verify the signature using the verifying key and SHA-256 hash function
        try:
            verifying_key.verify(bytes.fromhex(self.signature), transaction_data, hashfunc=hashlib.sha256)
            return True
        except ecdsa.BadSignatureError:
            return False

    def validate_transaction(self):
        # Check if the sender is None, meaning this is a coinbase transaction that generates new tokens
        if self.sender == None:
            return True
        # Check if the signature is valid
        if not self.verify_signature():
            return False
        input_sum = 0
        output_sum = 0
        for input in self.inputs:
            input_sum += input.value
        for output in self.outputs:
            output_sum += output.value
        output_sum += self.amount
        if input_sum >= output_sum:
            return True
        else:
            return False


class TransactionOutput:
    def __init__(self, address, amount):
        self.address = address
        self.amount = amount
        self.id = self.generate_id()

    def generate_id(self):
        output_data = str(self.address) + str(self.amount)
        # Encode the string using UTF-8 encoding
        output_data = output_data.encode()
        # Create a hash of the output data using SHA-256 algorithm
        output_hash = hashlib.sha256(output_data).hexdigest()
        return output_hash

    def __str__(self):
        # Return a string representation of the transaction output
        return f"TransactionOutput(id={self.id}, address={self.address}, amount={self.amount})"

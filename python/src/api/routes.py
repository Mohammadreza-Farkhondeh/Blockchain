from fastapi import APIRouter, Request
from pydantic import BaseModel
from app import app, node

router = APIRouter()

class TransactionRequest(BaseModel):
    sender: str # The public key of the sender of the transaction
    receiver: str # The public key of the receiver of the transaction
    amount: float # The amount of tokens to transfer
    private_key: str # The private key of the sender of the transaction

class PeerRequest(BaseModel):
    address: str # The network address of the peer, such as "localhost:5001"

class MessageRequest(BaseModel):
    message: str

@app.get("/get_state")
def get_state():
    return {"length": len(node.blockchain.chain), "chain": [block.__dict__ for block in node.blockchain.chain]}

@app.post("/create_transaction")
def create_transaction(transaction_request: TransactionRequest):
    if node.blockchain.create_transaction(transaction_request.sender, transaction_request.receiver, transaction_request.amount, transaction_request.private_key):
        return {"message": "Transaction created successfully"}
    else:
        return {"message": "Transaction failed"}

@app.get("/get_balance/{address}")
def get_balance(address: str):
    balance = node.blockchain.get_balance(address)
    return {"balance": balance}

@app.get("/mine_block")
def mine_block():
    new_block = Block(len(node.blockchain.chain), time.time(), node.blockchain.pending_transactions, node.blockchain.chain[-1].hash)
    new_block.mine_block(node.blockchain.difficulty)
    if node.blockchain.add_block(new_block):
        return {"message": f"Block {new_block.index} mined and added successfully"}
    else:
        return {"message": f"Block {new_block.index} rejected"}

@app.post("/connect_peer")
def connect_peer(peer_request: PeerRequest):
    node.connect_peer(peer_request.address)

@app.post("/disconnect_peer")
def disconnect_peer(peer_request: PeerRequest):
    node.disconnect_peer(peer_request.address)

@app.post("/send_message/{peer}")
def send_message(peer: str, message_request: MessageRequest):
    node.send_message(peer, message_request.message)

@app.post("/receive_message")
def receive_message(request: Request):
    address = request.json()["address"]
    message = request.json()["message"]
    node.receive_message(address, message)
    node.handle_message(address, message)

@app.post("/add_block")
def add_block(request: Request):
    block = Block(**request.json())
    if node.blockchain.add_block(block):
        return {"message": f"Block {block.index} added successfully"}
    else:
        return {"message": f"Block {block.index} rejected"}

@app.get("/get_blocks")
def get_blocks():
    return {"length": len(node.blockchain.chain), "chain": [block.__dict__ for block in node.blockchain.chain]}

@app.get("/validate_chain")
def validate_chain():
    return {"valid": node.blockchain.validate_chain(), "length": len(node.blockchain.chain)}

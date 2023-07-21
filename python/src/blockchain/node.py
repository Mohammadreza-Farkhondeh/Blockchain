from .block import Block

class Node:
    def __init__(self, address, peers, blockchain):
        self.address = address # The network address of the node, such as "localhost:5000"
        self.peers = peers # The set of peers that are connected to the node, such as {"localhost:5001", "localhost:5002"}
        self.blockchain = blockchain # The blockchain object that belongs to the node

    def connect_peer(self, peer):
        if peer not in self.peers:
            self.peers.add(peer)
            # Send a POST request to the peer's /connect_peer route with your own address as JSON
            print(f"Peer {peer} connected")
        else:
            print(f"Peer {peer} already connected")

    def disconnect_peer(self, peer):
        if peer in self.peers:
            self.peers.remove(peer)
            # Send a POST request to the peer's /disconnect_peer route with your own address as JSON
            requests.post(f"http://{peer}/disconnect_peer", json={"address": self.address})
            print(f"Peer {peer} disconnected")
        else:
            print(f"Peer {peer} not connected")

    def send_message(self, peer, message):
        if peer in self.peers:
            # Send a POST request to the peer's /send_message route with your own address and the message as JSON
            requests.post(f"http://{peer}/send_message", json={"address": self.address, "message": message})
            print(f"Message sent to {peer}")
        else:
            print(f"Peer {peer} not connected")

    def receive_message(self, address, message):
        print(f"Message received from {address}: {message}")

    def handle_message(self, address, message):
        # Check the type of the message and perform the appropriate action
        if message["type"] == "add_block":
            block = Block(**message["data"])
            if self.blockchain.add_block(block):
                print(f"Block {block.index} added from {address}")
            else:
                print(f"Block {block.index} rejected from {address}")
        elif message["type"] == "get_blocks":
            response = {"length": len(self.blockchain.chain), "chain": [block.__dict__ for block in self.blockchain.chain]}
            requests.post(f"http://{address}/get_blocks", json=response)
        elif message["type"] == "validate_chain":
            response = {"valid": self.blockchain.validate_chain(), "length": len(self.blockchain.chain)}
            requests.post(f"http://{address}/validate_chain", json=response)
        else:
            print(f"Unknown message type from {address}")

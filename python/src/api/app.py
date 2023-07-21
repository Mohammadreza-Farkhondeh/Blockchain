#!/usr/bin/env python

from fastapi import FastAPI
from blockchain.blockchain import Blockchain
from blockchain.node import Node

app = FastAPI()

# Create a blockchain object with a difficulty of 4, an empty list of pending transactions, and an empty set of nodes
blockchain = Blockchain(4, [], set())

# Create a node object with an address of "localhost:5000", an empty set of peers, and the blockchain object
node = Node("localhost:5000", set(), blockchain)

from routes import *

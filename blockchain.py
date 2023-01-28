import hashlib
import json
from time import time
from textwrap import dedent
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transaction = []

        # The genesis Block

        self.new_block(previous_hash = 1, proof = 1)

    def createBlock(self, proof, previous_hash=None):
        """
        Creates a new Blockchain

        :param proof: <int> The from the proof of work Algorithm
        :param previous_hash: (Optional) <str> Hash of the previous block
        :return: <dict>     New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transaction': self.current_transaction,
            'proof': proof,
            'previous_hash': previous_hash or self.generateHash(self.lastBlock())
        }
        self.current_transaction = []

        self.chain.append(block)
        return block

    def createTransaction(self, sender, recipient, amount):
        """
        Creates a transaction that will go onto the chain

        :param sender : <str>   Address of the sender
        :param recipient: <str> Address of the reciever
        :param amount: <str> Amount
        :return: <str> The index that holds the transaction
        """
        self.current_transaction.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.lastBlock['index'] + 1

    @staticmethod    
    def generateHash(block):
        """
        Generate a SHA-256 hash of a Block

        :param block: <dict> Block
        :return: <str>
        """
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    @property
    def lastBlock(self):
        return self.chain[-1]

    def proofOfWork(self, last_proof):
        """
        Simple Proof of Work Algorithm:
        - Find a number p such that hash(pp) contains leadin 4 zeros, where p is the previous p
        p is the previous proof, and p the new proof 
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.validProof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def validProof(last_proof, proof):
        """
        Validates the proof: Does hash(last_proof, proof)
        contain 4 leading zeros
        :param last_proof: <int> Previous proof
        :param proof: <int> Current proof
        :return: <bool> True if correct and False if not
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# Initiate and start our Node 
app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

# Initiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # Run the proof of Work algo to get next the proof

    last_block = blockchain.lastBlock
    last_proof = last_block['proof']
    proof = blockchain.proofOfWork(last_proof)

    # The sender will be 0 to signify that this node has been mined as a new coin
    blockchain.createTransaction(sender=0, recipient=node_identifier, amount=1)
    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.generateHash(last_block)
    block = blockchain.createBlock(proof, previous_hash)

    response = {
        'message': "New Block forged",
        'index': block['index'],
        'transaction': block['transaction'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    input_values = request.get_json()
    
    # Verify the needed fields for the blockchain
    required = ['sender', 'recipient', 'amount']
    if not all(k in input_values for k in required):
        return 'Missing input values', 400

    # Create a new transaction
    index = blockchain.createTransaction(input_values['sender'], input_values['recipient']
    , input_values['amount'])

    response = {'message': f'Transaction will be added to the Block {index}'}

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.', port=5000)
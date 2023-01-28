import hashlib
import json
from time import time

class Blockchain:
    def __init__(self) -> None:
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
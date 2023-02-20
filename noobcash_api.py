from flask import Flask, render_template

#Pycryptodome
#pip install pycroptodome 
#doc:https://pycryptodome.readthedocs.io/en/latest/
from Crypto.PublicKey import RSA

import hashlib
import time

#---------------------------------------------------------------------------------------------------------------
#Aciver l'environnement virtuel:
        #env_noobcash\Scripts\activate

#set up flask app for the env (need to restart after)
        #setx FLASK_APP "noobcash_api.py"

#Run l'app flask:
        #flask run


#---------------------------------------------------------------------------------------------------------------

#Block class
class Block:
    index = 0
    def __init__(self,transactions,previous_hash):
        Block.index += 1
        self.index = Block.index
        self.timestamp = time.time()
        self.transactions = transactions
        self.nonce = 0
        self.current_hash = ""
        self.previous_hash = previous_hash

#Blockchain class
class Blockchain:
    def __init__(self):
        self.validated_block = list()
        
#Wallet class
class Wallet:
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key
        self.NBC = 100

#Node class
class Node(Wallet):
    id = 0
    def __init__(self):
        self.id = f"id {Node.id}"
        Node.id += 1

#Transcation class
class Transaction_Input:
    def __init__(self):
        pass
        
class Transaction_Output:
    def __init__(self):
        pass

class Transaction:
    def __init__(self, sender_address, receiver_address, amount, transaction_inputs, transaction_outputs):
        self.sender_address, self.receiver_address = sender_address, receiver_address
        self.amount = amount
        self.transaction_id = None
        self.transaction_inputs, self.transaction_outputs = transaction_inputs, transaction_outputs
        self.signature = None

#---------------------------------------------------------------------------------------------------------------
# Creates a new transaction that contains all necessary fields. 
# The field transaction_inputs is filled with the Transactions that contain all ids of UTXOs
# required to get the amount we want to spend. 
def create_wallet(size):
    key = RSA.generate(size)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    return Wallet(public_key, private_key)

def create_transaction(sender_address, receiver_address, amount, transaction_inputs,transaction_outputs):
    
    # Generate object Transaction
    newTransaction = Transaction(sender_address, receiver_address, amount, transaction_inputs,transaction_outputs)
    

    #Generate transaction_id with hash
    data = (str(sender_address) + str(receiver_address) + str(amount)).encode()
    # for transaction_input in transaction_inputs:
    #     data += transaction_input.previous_output_id.encode()
    # for transaction_output in transaction_outputs:
    #     data += transaction_output.id.encode()
    transaction_id = hashlib.sha256(data).hexdigest()
    print("transaction_id:", transaction_id)
    newTransaction.transaction_id = transaction_id
    return newTransaction


def sign_transaction(transaction, wallet):
    private_key=str(wallet.private_key).encode()
    signature = hashlib.sha256(private_key).hexdigest()
    print ("signature:", signature)
    transaction.signature = signature

def verify_signature(transaction):
    pass


def wallet_balance():  
    pass

def mine_block(block, difficulty):
    target = '0' * difficulty
    nonce = 0

    while block.current_hash[0:difficulty]!=target:
        block.nonce = nonce
        block.timestamp = time.time()
        data = f"{block.timestamp}{block.transactions}{block.nonce}{block.previous_hash}".encode()

        block.current_hash = hashlib.sha256(data).hexdigest()
        nonce += 1

    broadcast_block(block)

def broadcast_block(block):

    pass

#---------------------------------------------------------------------------------------------------------------
#Test ZOne

#test create_wallet
wal1 = create_wallet(2048)
wal2 = create_wallet(2048)
# print(f"\n\nwal1:{wal1.private_key}\n\n")
# print(f"wal2:{wal2.private_key}\n\n")

#Test creation transaction:
l_inputs=[]
l_outputs=[]
# test_transaction = create_transaction(1111, 2222, 43, l_inputs, l_outputs)
# sign_transaction(test_transaction,wal1)
# test_transaction2 = create_transaction(1111, 2222, 43, l_inputs, l_outputs)
# sign_transaction(test_transaction2,wal1)

#test mine_block
# block1 = Block(100,"000dendzojddnascnljbdczlcdc")
# block2 =Block(200,"000dendzojgdvdcdddnascnljbdczlcdc")
# mine_block(block1,3)
# mine_block(block2,3)
# print(vars(block1))
# print(vars(block2))


#---------------------------------------------------------------------------------------------------------------
app= Flask(__name__)

@app.route('/noobcash', methods=['GET', 'POST'])
def user():
    return render_template("user.html")

# if __name__ == '__main__':
#     app.run(debug=True, port=9103)
# if __name__ == '__main__':
#     app.run(debug=True, port=9103)

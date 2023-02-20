from flask import Flask, render_template
from Crypto.PublicKey import RSA #pip install pycroptodome

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
#Initialisation

index_iteration = 0

#---------------------------------------------------------------------------------------------------------------
#Block class
class Block:
    def __init__(self,index,transactions,previous_hash):
        self.index = index
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

#Transcation class
class Transaction_Input:
    def __init__(self) -> None:
        pass
        
class Transaction_Output:
    def __init__(self) -> None:
        pass

class Transcaction:
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
    public_key = key.publickey().export_key()
    private_key = key.export_key()

    return Wallet(public_key, private_key)

def create_transaction():
    
    # Transaction(parametres)
    # generate transaction_id: the transaction’s hash
    # Transaction.transaction_id...
    #return Transaction
    pass

def sign_transaction():
    # gérer signature
    # Transaction.signature = ...

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
    print(vars(block))


#---------------------------------------------------------------------------------------------------------------
#Test ZOne

#test create_wallet
wal1 = create_wallet(2048)
wal2 = create_wallet(2048)

# print(f"\n\nwal1:{wal1.private_key}\n\n")
# print(f"wal2:{wal2.private_key}\n\n")

#test mine_block
block = Block(0,100,"000dendzojddnascnljbdczlcdc")
mine_block(block,3)


#---------------------------------------------------------------------------------------------------------------
app= Flask(__name__)

@app.route('/noobcash', methods=['GET', 'POST'])
def user():
    return render_template("user.html")

# if __name__ == '__main__':
#     app.run(debug=True, port=9103)

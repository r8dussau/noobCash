from flask import Flask, render_template

#Pycryptodome
#pip install pycroptodome 
#doc:https://pycryptodome.readthedocs.io/en/latest/
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

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
        #self.balance = 100

#Node class
class Node:
    id = 0
    def __init__(self):
        self.id = Node.id
        Node.id += 1
        self.wallet = create_wallet(self.id,2048)
        self.UTXOs = []

#Transcation class
#Après la derneire fondu, ce que le recipient a recu
class Transaction_Input:
    def __init__(self,previous_outputID):
        self.previous_outputID = previous_outputID

# Une transaction = 2 output: -Ce que A donne à B                       EX:A a 1000 et donne 400 -> 1000 fond en 1)400 2)600, 1)part vers B
#                             -Ce que A récupère (ce qu'il lui reste)   EX:A recoit 2)600
class Transaction_Output:
    def __init__(self, transaction_id, recipient_publicKey, amount):
        self.transaction_id = transaction_id
        self.recipient_publicKey = recipient_publicKey
        self.amount = amount
        data = (str(self.transaction_id) + str(self.recipient_publicKey) + str(self.amount)).encode()
        self.id = SHA256.new(data).hexdigest()

class Transaction:
    def __init__(self, transaction_id, sender_publicKey, receiver_publicKey, amount, transaction_inputs, transaction_outputs):
        self.transaction_id = transaction_id
        self.sender_publicKey, self.receiver_publicKey = sender_publicKey, receiver_publicKey
        self.amount = amount
        self.transaction_inputs = transaction_inputs
        self.transaction_outputs = transaction_outputs
        #a modifier! (hashage pour ID de transaction unique)
        self.signature = None

#---------------------------------------------------------------------------------------------------------------
# Creates a new transaction that contains all necessary fields. 
# The field transaction_inputs is filled with the Transactions that contain all ids of UTXOs
# required to get the amount we want to spend. 
def create_wallet(nodeID, size):
    id = nodeID
    key = RSA.generate(size)
    #Private Key writen in private_nodeNumber.pem
    private_key = key.export_key()
    file_out = open("private_"+str(id)+".pem", "wb")
    file_out.write(private_key)
    file_out.close()
    #Public Key writen in public_nodeNumber.pem
    public_key = key.publickey().export_key()
    file_out = open("public_"+str(id)+".pem", "wb")
    file_out.write(public_key)
    file_out.close()

    return Wallet(public_key, private_key)

def create_transaction(sender_publicKey, receiver_publicKey, amount):
    # Generate object Transaction
    
    #Generate transaction_id with hash
    data = (str(sender_publicKey) + str(receiver_publicKey) + str(amount)).encode()

#Input(s)
    transaction_inputs=[]
    for node in nodes:
        if node.wallet.public_key == sender_publicKey:
            UTXOs = node.UTXOs
    for utxo in UTXOs:
        if (utxo.recipient_publicKey == sender_publicKey):
            input = Transaction_Input(utxo.id)
            print('boudin:',utxo.id)
            transaction_inputs.append(input)
            print('Une transactiona  été détecter dans UTXO, je le balance dans inputs')

    #Outputs
    #faire un wallet_balance(listnode[wallet.public_key==sender_publicKey])
    balance = 100     
    transaction_outputs = []
    send_output = Transaction_Output("test", receiver_publicKey, amount)
    receive_output = Transaction_Output("test", sender_publicKey, balance-amount)
    transaction_outputs.append(send_output)
    transaction_outputs.append(receive_output)

    print("TAILLE de inputs:",len(transaction_inputs),'\n')
    for transaction_input in transaction_inputs:
        data += transaction_input.previous_outputID.encode()
    print("TAILLE de outputs:",len(transaction_outputs))
    for transaction_output in transaction_outputs:
        data += transaction_output.transaction_id.encode()
    transaction_id = SHA256.new(data).hexdigest()

    #rename Transaction_outputs:
    for transaction_output in transaction_outputs:
        transaction_output.transaction_id = transaction_id

    newTransaction = Transaction(transaction_id, sender_publicKey, receiver_publicKey, amount, transaction_inputs, transaction_outputs)
    return newTransaction


def sign_transaction(transaction, node):
    message = (str(transaction.sender_publicKey) + str(transaction.receiver_publicKey) + str(transaction.amount)).encode()
    node_id = node.id
    key = RSA.import_key(open('private_'+str(node_id)+'.pem').read())
    h = SHA256.new(message)
    signature = pss.new(key).sign(h)
    transaction.signature = signature


def verify_signature(transaction, node):
    node_id = node.id
    key = RSA.import_key(open('public_'+str(node_id)+'.pem').read())
    message = (str(transaction.sender_publicKey) + str(transaction.receiver_publicKey) + str(transaction.amount)).encode()
    h = SHA256.new(message)
    verifier = pss.new(key)
    try:
        verifier.verify(h, transaction.signature)
        print ("The signature is authentic.")
        node0.UTXOs.append(transaction.transaction_outputs[1])
        return True
    except (ValueError, TypeError):
        print ("The signature is not authentic.")
        return False

def validate_transaction(transaction, node):
    # Check if signature is good
    if verify_signature(transaction, node):
        # Check if the sender as the amount needed for the transaction
        # for transaction_input in transaction_inputs:
        print("la signature est bien vérifiée")
        # balance = wallet_balance(node.wallet)
        # if transaction.amount >= balance:
        #     print("Tu as assez de thunes gazié")
        # else:
        #     print("Tes sur la paille gazié")


def wallet_balance(wallet):  
    balance = 0
    for node in nodes:
            if node.wallet.public_key == wallet.public_key:
                UTXOs = node.UTXOs
    for utxo in UTXOs:
        if utxo.recipient == wallet.public_key:
            balance+=utxo.amount
    return balance

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
#Listes des nodes:
nodes = []
#node0
node0 = Node()
nodes.append(node0)
#node1
node1 = Node()
nodes.append(node1)

#Mettre 100 balles sur node0:
output0 = Transaction_Output("test",node0.wallet.public_key,100)
node0.UTXOs.append(output0)

test_transaction = create_transaction(node0.wallet.public_key, node1.wallet.public_key, 43)
sign_transaction(test_transaction,node0)
verify_signature(test_transaction,node0)
validate_transaction(test_transaction, node0)
print(len(node0.UTXOs))
for i in range (len(node0.UTXOs)):
    print(node0.UTXOs[i].amount)
#---------------------------------------------------------------------------------------------------------------
app= Flask(__name__)

@app.route('/noobcash', methods=['GET', 'POST'])
def user():
    return render_template("user.html")

# if __name__ == '__main__':
#     app.run(debug=True, port=9103)
# if __name__ == '__main__':
#     app.run(debug=True, port=9103)

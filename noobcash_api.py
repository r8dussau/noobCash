from flask import Flask, render_template

#Pycryptodome
#pip install pycroptodome 
#doc:https://pycryptodome.readthedocs.io/en/latest/
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from random import randint

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
#Node class
class Node:
    id = 0
    def __init__(self):
        self.id = Node.id
        Node.id += 1
        self.ipAdress = f"{randint(0,200)}.{randint(0,200)}.{randint(0,200)}.{randint(0,10)}"
        self.ipPort = randint(0,5000)
        self.wallet = create_wallet(self.id,2048)
        self.validateBlock = list()
        self.transaction = list()
        self.iteration = 0
        self.UTXOs = []


#Block class
class Block:
    index = 0
    def __init__(self, timestamp, transactions, prev_hash):
        Block.index += 1
        self.index = Block.index
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = 0
        self.current_hash = ""
        self.previous_hash = prev_hash

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
    #Generate transaction_id with hash
    data = (str(sender_publicKey) + str(receiver_publicKey) + str(amount)).encode()

#Input(s)
    balance = 0
    transaction_inputs=[]
    for node in nodes:
        if node.wallet.public_key == sender_publicKey:
            UTXOs = node.UTXOs
    for utxo in UTXOs:
        if (utxo.recipient_publicKey == sender_publicKey):
            input = Transaction_Input(utxo.id)
            balance += utxo.amount
            transaction_inputs.append(input)
            print('Une transaction  été détecter dans UTXO, je le balance dans inputs')


    #Outputs
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

    if balance-amount >= 0:
        print('Assez de thunes')
        newTransaction = Transaction(transaction_id, sender_publicKey, receiver_publicKey, amount, transaction_inputs, transaction_outputs)
        return newTransaction
    else:
        print('Pas assez de thunes',balance)
        return None


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
        return True
    except (ValueError, TypeError):
        print ("The signature is not authentic.")
        return False

def validate_transaction(transaction, node):
    # Check if signature is good
    if verify_signature(transaction, node):
        print("La signature est bien vérifiée")
        for input in transaction.transaction_inputs:
            for utxo in node.UTXOs:
                if input.previous_outputID != utxo.id:
                    print("Pas valide")
                    return False
                else:
                    node.UTXOs.remove(utxo)
                    node.UTXOs.append(transaction.transaction_outputs[1])
                    print('Valide')
                    return True
            


def wallet_balance(wallet):  
    balance = 0
    for node in nodes:
            if node.wallet.public_key == wallet.public_key:
                UTXOs = node.UTXOs
    for utxo in UTXOs:
        if utxo.recipient_publicKey == wallet.public_key:
            balance+=utxo.amount
    return balance

def mine_block(node, difficulty, capacity):
    nonce = 0
    if len(node.transaction) >= capacity: 
        #create a block when there are at least 5 transaction in a node
        block = Block(time.time(), node.transaction[0:5],vars(node.validateBlock[node.iteration-1])['current_hash'])
        #remove 5 first element in the transaction list of the node
        for i in range(5):
            node.transaction.pop(0)

        #proof of work
        while block.current_hash[0:difficulty] != '0'*difficulty:
            block.nonce = nonce
           
            data = f"{block.timestamp}{block.transactions}{block.nonce}{block.previous_hash}".encode()

            block.current_hash = hashlib.sha256(data).hexdigest()
            
            nonce += 1

        return block

def broadcast_block(block, nodes):
    for node in nodes:
        node.validateBlock.append(block)
        #node.update()
        node.iteration += 1

def validate_block(node, block):
    newBlock = vars(node.validateBlock[-1])
    prevBlock = vars(node.validateBlock[-2])

    data = f"{block.timestamp}{block.transactions}{block.nonce}{block.previous_hash}".encode()
    hash_result = hashlib.sha256(data).hexdigest()

    if (newBlock['previous_hash']==hash_result) and (newBlock['previous_hash'] == prevBlock['current_hash']):
        #add list blockchain
        pass
        

#---------------------------------------------------------------------------------------------------------------
#Test ZOne
#Listes des nodes:
n = 2 #choose number of nodes with the front end
nodes = list()
for i in range(n): 
    nodes.append(Node())

#Mettre 100 balles sur node0:
output0 = Transaction_Output("test",nodes[0].wallet.public_key,100)
nodes[0].UTXOs.append(output0)

test_transaction = create_transaction(nodes[0].wallet.public_key, nodes[1].wallet.public_key, 90)
if test_transaction != None:
    sign_transaction(test_transaction,nodes[0])
    verify_signature(test_transaction,nodes[0])
    validate_transaction(test_transaction,nodes[0])

b = wallet_balance(nodes[0].wallet)
print("balance:",b)

for node in nodes:
    #Generation of the Genesis block
    if node.id==0:
        genesisBlock = Block(time.time(),[100*n],1) 
        genesisBlock.current_hash = '0'*64

    #simulation of the list transaction
    node.transaction = [0,1,2,3,4,5,6,7,8,9,10,11]
    
broadcast_block(genesisBlock,nodes)
print(nodes[0].iteration)

#test mine_block
block1 = mine_block(nodes[0],3,5)
#print(vars(block1))
broadcast_block(block1,nodes)
#print(vars(nodes[0].validateBlock[nodes[0].iteration-1]))

block2 = mine_block(nodes[0],3,5)
#print(vars(block2))
broadcast_block(block2,nodes)
#print(vars(nodes[0].validateBlock[nodes[0].iteration-1]))

for node in nodes:
    for i in range(len(node.validateBlock)):
        #print(f"{vars(node.validateBlock[block1.index-1])}\n")
        print(f"{vars(node.validateBlock[i])}\n")


# broadcast_block(block1,nodes)

#---------------------------------------------------------------------------------------------------------------
app= Flask(__name__)

@app.route('/noobcash', methods=['GET', 'POST'])
def user():
    return render_template("user.html")

# if __name__ == '__main__':
#     app.run(debug=True, port=9103)
# if __name__ == '__main__':
#     app.run(debug=True, port=9103)

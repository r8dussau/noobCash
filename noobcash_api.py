from flask import Flask, render_template
from multiprocessing import Process

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
        self.validateBlocks = list()
        self.iteration = 0
        self.UTXOs = []

        #---------------------------------------------
        #RAPH
        # self.finTime = 0
        # self.minedBlock = 0

        #---------------------------------------------

        
        #Create genesis block
        if self.id == 0:
            #genesis_utxo = Transaction_Output("genesis",self.wallet.public_key,100)
            #self.UTXOs.append(genesis_utxo)
            genesisTransaction = create_transaction("0",self.wallet.public_key,100,True)
            output0 = Transaction_Output("genesis",self.wallet.public_key,100)
            self.UTXOs.append(output0)
            genesisBlock = (Block(time.time(),genesisTransaction,1))

            genesisBlock.current_hash="0"*64
            self.validateBlocks.append(genesisBlock)
            #ajouter aussi ce bloc à la blockchain
        else:
            self.validateBlocks.append(nodes[0].validateBlocks[0])
        
        self.jcurrentBlock = Block(time.time(),[],self.validateBlocks[len(self.validateBlocks)-1].current_hash)
        #self.validateBlocks.append(self.jcurrentBlock)
        
#Block class
class Block:
    def __init__(self, timestamp, transactions, prev_hash):
        self.index = 0
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = 0
        self.current_hash = ""
        self.previous_hash = prev_hash

#Blockchain class
class Blockchain:
    def __init__(self):
        self.list = list()
        
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

def create_transaction(sender_publicKey, receiver_publicKey, amount, isGenesis=False):
    if isGenesis:
        print('Création de la genesis transaction')
        newTransaction =  Transaction("genesis", "0", receiver_publicKey, amount, [], [])
        return newTransaction
    else:
    
        #Generate transaction_id with hash
        data = (str(sender_publicKey) + str(receiver_publicKey) + str(amount)).encode()
        balance = 0

        #Inputs:
        transaction_inputs=[]
        #Cas classique:
        for node in nodes:
            if node.wallet.public_key == sender_publicKey:
                UTXOs = node.UTXOs
        for utxo in UTXOs:
            if (utxo.recipient_publicKey == sender_publicKey):
                input = Transaction_Input(utxo.id)
                balance += utxo.amount
                transaction_inputs.append(input)
        #Outputs
        #Cas classique:
        transaction_outputs = []
        send_output = Transaction_Output("test", receiver_publicKey, amount)
        receive_output = Transaction_Output("test", sender_publicKey, balance-amount)
        transaction_outputs.append(send_output)
        transaction_outputs.append(receive_output)
        for transaction_input in transaction_inputs:
            data += transaction_input.previous_outputID.encode()
        for transaction_output in transaction_outputs:
            data += transaction_output.transaction_id.encode()
        transaction_id = SHA256.new(data).hexdigest()

        #rename Transaction_outputs:
        for transaction_output in transaction_outputs:
            transaction_output.transaction_id = transaction_id

        #Check balance
        if balance-amount >= 0:
            newTransaction = Transaction(transaction_id, sender_publicKey, receiver_publicKey, amount, transaction_inputs, transaction_outputs)
            return newTransaction
        else:
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
        # print ("The signature is authentic.")
        return True
    except (ValueError, TypeError):
        # print ("The signature is not authentic.")
        return False

def validate_transaction(transaction, node):
    # Check if signature is good
    if verify_signature(transaction, node):
        # print("La signature est bien vérifiée")
        for input in transaction.transaction_inputs:
            for utxo in node.UTXOs:
                if input.previous_outputID != utxo.id:
                    # print("Pas valide")
                    return False
                else:
                    node.UTXOs.remove(utxo)
                    node.UTXOs.append(transaction.transaction_outputs[1])
                    # print('Valide')
                    return True

def broadcast_transaction(transaction):
    for node in nodes:
        node.jcurrentBlock.transactions.append(transaction)
            

def wallet_balance(wallet):  
    balance = 0
    for node in nodes:
            if node.wallet.public_key == wallet.public_key:
                UTXOs = node.UTXOs
    for utxo in UTXOs:
        if utxo.recipient_publicKey == wallet.public_key:
            balance+=utxo.amount
    return balance

def mine_block(node, difficulty):

    #---------------------------------------------
    #RAPH
    node.finTime = 0
    finTime = 0
    debutTime = time.time()

    #---------------------------------------------



    nonce = 0
    #proof of work
    while node.jcurrentBlock.current_hash[0:difficulty] != '0'*difficulty:
        node.jcurrentBlock.nonce = nonce
        data = f"{node.jcurrentBlock.timestamp}{node.jcurrentBlock.transactions}{node.jcurrentBlock.nonce}{node.jcurrentBlock.previous_hash}".encode()
        node.jcurrentBlock.current_hash = hashlib.sha256(data).hexdigest()
        nonce += 1
    mined_block = node.jcurrentBlock

    #---------------------------------------------
    #RAPH
    # print("\n\n\n")
    # node.finTime = int(time.time()*1000000)-int(debutTime*1000000)
    # print(node.finTime)
    # node.minedBlock = mined_block
    #finTime = node.finTime
    finTime = int(time.time()*1000000)-int(debutTime*1000000)
    print("\n\n\n")
    print(time.time())
    print(debutTime)
    print(finTime)
    #---------------------------------------------

    return mined_block, finTime

def broadcast_block(block):
    for node in nodes:
        node.jcurrentBlock = block

def validate_block(node):
    newBlock = node.jcurrentBlock
    prevBlock = node.validateBlocks[-1]
    data = f"{newBlock.timestamp}{newBlock.transactions}{newBlock.nonce}{newBlock.previous_hash}".encode()
    hash_result = hashlib.sha256(data).hexdigest()
    if hash_result != vars(newBlock)['current_hash']:
        return False

    # print('---------------------------------')
    # print('new:',vars(newBlock)['previous_hash'])
    # print('pre:',vars(prevBlock)['current_hash'])
    # print('---------------------------------')

    if vars(newBlock)['previous_hash'] != vars(prevBlock)['current_hash']:
        return False
    
    # blockchain.list.append(newBlock)

    return True
    
# def validate_chain(node):
#     if validate_block(node):
#         return True
#     else:
#         return False

#---------------------------------------------------------------------------------------------------------------
#Test ZOne
#Listes des nodes:
nodes = list()
def createNode(nodes):
    nodes.append(Node())
    for node in nodes:
        print(node.id)
blockchain = []

""" test_transaction = create_transaction(nodes[0].wallet.public_key, nodes[1].wallet.public_key, 10)
if test_transaction != None:
    sign_transaction(test_transaction,nodes[0])
    verify_signature(test_transaction,nodes[0])
    isValid = validate_transaction(test_transaction,nodes[0])
    broadcast_transaction(test_transaction)

test_transaction1 = create_transaction(nodes[0].wallet.public_key, nodes[1].wallet.public_key, 10)
if test_transaction1 != None:
    sign_transaction(test_transaction1,nodes[0])
    verify_signature(test_transaction1,nodes[0])
    isValid = validate_transaction(test_transaction1,nodes[0])
    broadcast_transaction(test_transaction1) """

# createNode(nodes)
# createNode(nodes)

def transaction(nodes, nodeSender, nodeRecever, amount, capacity):

    test_transaction = create_transaction(nodeSender.wallet.public_key, nodeRecever.wallet.public_key, amount)
    if test_transaction != None:
        sign_transaction(test_transaction,nodeSender)
        verify_signature(test_transaction,nodeSender)
        if validate_transaction(test_transaction,nodeSender):
            broadcast_transaction(test_transaction)

    timeList = {}
    mined = {}
    for node in nodes: 
        if len(node.jcurrentBlock.transactions) == capacity:
            mined_block, finTime = mine_block(node,3)
            timeList = timeList | {node.id : finTime}
            mined = mined | {node.id : mined_block}

    if len(node.jcurrentBlock.transactions) == capacity:
        timeListSorted = dict(sorted(timeList.items(), key=lambda item:item[1], reverse=False))
        idGoodMinedBlock = list(timeListSorted.keys())[0]
        goodMinedBlock = list(mined.items())[idGoodMinedBlock][1]

        broadcast_block(goodMinedBlock)

        for node in nodes:
            if validate_block(node):
                    mined_block.index = len(node.validateBlocks)
                    node.validateBlocks.append(mined_block)
            node.jcurrentBlock = Block(time.time(),[],mined_block.current_hash)
        
        timeList = {}
        timeListSorted = {}
        mined = {}

# transaction(nodes, nodes[0], nodes[1], 10, 3)
# transaction(nodes, nodes[0], nodes[1], 10, 3)
# transaction(nodes, nodes[0], nodes[1], 10, 3)


def minage(nodes):
    timeList = {}
    mined = {}
    for node in nodes: 
        if len(node.jcurrentBlock.transactions) == 2:
            mined_block, finTime = mine_block(node,3)
            timeList = timeList | {node.id : finTime}
            mined = mined | {node.id : mined_block}
        
    timeListSorted = dict(sorted(timeList.items(), key=lambda item:item[1], reverse=False))
    idGoodMinedBlock = list(timeListSorted.keys())[0]
    goodMinedBlock = list(mined.items())[idGoodMinedBlock][1]

    broadcast_block(goodMinedBlock)

    for node in nodes:
        if validate_block(node):
                mined_block.index = len(node.validateBlocks)
                node.validateBlocks.append(mined_block)
        node.jcurrentBlock = Block(time.time(),[],mined_block.current_hash)

    print(timeList)
    print(timeListSorted)
    print(mined)
    print(goodMinedBlock)





def node0():
    print(f"ICI LE TEMPS 0: {time.time()}")
    if len(nodes[0].jcurrentBlock.transactions) == 2:
        mined_block = mine_block(nodes[0],2)
        #print(mined_block)
        """ broadcast_block(mined_block)
        if validate_block(nodes[0]):
            mined_block.index = len(nodes[0].validateBlocks)
            nodes[0].validateBlocks.append(mined_block)
        nodes[0].jcurrentBlock = Block(time.time(),[],mined_block.current_hash)

        print ('LENnode0:',len(nodes[0].validateBlocks))
        print ('node0:',nodes[0].validateBlocks[0].current_hash)
        print ('node0:',nodes[0].validateBlocks[1].current_hash) """

def node1():
    print(f"ICI LE TEMPS 1: {time.time()}")
    if len(nodes[1].jcurrentBlock.transactions) == 2:
        mined_block = mine_block(nodes[1],2)
        #print(mined_block)
        """ broadcast_block(mined_block)
        if validate_block(nodes[1]):
            mined_block.index = len(nodes[1].validateBlocks)
            nodes[1].validateBlocks.append(mined_block)
        nodes[1].jcurrentBlock = Block(time.time(),[],mined_block.current_hash)

        print ('LENnode1:',len(nodes[1].validateBlocks))
        print ('node1:',nodes[1].validateBlocks[0].current_hash)
        print ('node1:',nodes[1].validateBlocks[1].current_hash) """





def best_mined_block(nodes):
    order = {}
    mined = {}
    for node in nodes:
        order = order | {node.id : node.finTime}
        mined = mined | {node.id : node.mined_block}
        
    orderSorted = dict(sorted(order.items(), key=lambda item:item[1], reverse=False))
    idMINER = list(orderSorted.keys())[0]
    leBlockSuperBienMine = list(mined.items())[idMINER]
    print(orderSorted)
    print(mined)
    print(leBlockSuperBienMine)

# node0()
# node1()
# best_mined_block(nodes)

""" def node0():
    print(f"ICI LE TEMPS 0: {time.time()}")
    if len(nodes[0].jcurrentBlock.transactions) == 2:
        mined_block = mine_block(nodes[0],2)
        #print(mined_block)
        broadcast_block(mined_block)
        if validate_block(nodes[0]):
            mined_block.index = len(nodes[0].validateBlocks)
            nodes[0].validateBlocks.append(mined_block)
        nodes[0].jcurrentBlock = Block(time.time(),[],mined_block.current_hash)

        print ('LENnode0:',len(nodes[0].validateBlocks))
        print ('node0:',nodes[0].validateBlocks[0].current_hash)
        print ('node0:',nodes[0].validateBlocks[1].current_hash)

def node1():
    print(f"ICI LE TEMPS 1: {time.time()}")
    if len(nodes[1].jcurrentBlock.transactions) == 2:
        mined_block = mine_block(nodes[1],2)
        #print(mined_block)
        broadcast_block(mined_block)
        if validate_block(nodes[1]):
            mined_block.index = len(nodes[1].validateBlocks)
            nodes[1].validateBlocks.append(mined_block)
        nodes[1].jcurrentBlock = Block(time.time(),[],mined_block.current_hash)

        print ('LENnode1:',len(nodes[1].validateBlocks))
        print ('node1:',nodes[1].validateBlocks[0].current_hash)
        print ('node1:',nodes[1].validateBlocks[1].current_hash) """

    
# print ('node1:',len(nodes[1].validateBlocks))

# print("------------------------------")
# print(vars(nodes[1].validateBlocks[0]))
# print(vars(nodes[1].validateBlocks[1]))
# print(vars(nodes[1].validateBlocks[2]))
#---------------------------------------------------------------------------------------------------------------
app= Flask(__name__)

@app.route('/noobcash', methods=['GET', 'POST'])
def html():
    #createNode(nodes)
    return render_template("user.html")

@app.route('/create_node', methods=['GET', 'POST'])
def creation():
    createNode(nodes)
    print("yesir")
    return "OK"

# @app.route('/f1', methods=['GET', 'POST'])
# def create_node():
#     createNode(nodes)
#     return render_template("user.html")

# @app.route('/f2', methods=['GET', 'POST'])
# def create_node():
#     createNode(nodes)
#     return render_template("user.html")

if __name__ == '__main__':
    app.run(debug=True, port=9103)
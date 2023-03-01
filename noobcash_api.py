#Pycryptodome
#pip install pycryptodome 
#doc:https://pycryptodome.readthedocs.io/en/latest/
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from random import randint

import hashlib
import time
import re

#---------------------------------------------------------------------------------------------------------------
#Class space 

#Node class
class Node:
    id = 0
    def __init__(self,initialNodeNumber):
        self.id = Node.id
        Node.id += 1
        self.ipAdress = f"{randint(0,200)}.{randint(0,200)}.{randint(0,200)}.{randint(0,10)}"
        self.ipPort = randint(0,5000)
        self.wallet = create_wallet(self.id,2048)
        self.validateBlocks = list()
        self.UTXOs = []

        #Create genesis block
        if self.id == 0:
            genesisTransaction = create_transaction("0",self.wallet.public_key,100*initialNodeNumber,True)
            output0 = Transaction_Output("genesis",self.wallet.public_key,100*initialNodeNumber)
            self.UTXOs.append(output0)
            genesisBlock = (Block(time.time(),genesisTransaction,1))

            genesisBlock.current_hash="0"*64
            self.validateBlocks.append(genesisBlock)
            blockchain.append(genesisBlock)
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
        
#Wallet class
class Wallet:
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key
        #self.balance = 100

#Transaction_Input class
class Transaction_Input:
    def __init__(self,previous_outputID):
        self.previous_outputID = previous_outputID

#Transaction_Output class
class Transaction_Output:
    def __init__(self, transaction_id, recipient_publicKey, amount):
        self.transaction_id = transaction_id
        self.recipient_publicKey = recipient_publicKey
        self.amount = amount
        data = (str(self.transaction_id) + str(self.recipient_publicKey) + str(self.amount)).encode()
        self.id = SHA256.new(data).hexdigest()

#Transaction class
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
    file_out = open("key_folder/private_"+str(id)+".pem", "wb")
    file_out.write(private_key)
    file_out.close()
    #Public Key writen in public_nodeNumber.pem
    public_key = key.publickey().export_key()
    file_out = open("key_folder/public_"+str(id)+".pem", "wb")
    file_out.write(public_key)
    file_out.close()

    return Wallet(public_key, private_key)

def create_transaction(sender_publicKey, receiver_publicKey, amount, isGenesis=False):
    if isGenesis:
        #print('Création de la genesis transaction')
        newTransaction =  Transaction("genesis", "0", receiver_publicKey, amount, [], [])
        return newTransaction
    else:
        #Generate transaction_id with hash
        data = (str(sender_publicKey) + str(receiver_publicKey) + str(amount)).encode()
        balance = 0

        #Inputs:
        transaction_inputs=[]
        for node in nodes:
            if node.wallet.public_key == sender_publicKey:
                UTXOs = node.UTXOs
        for utxo in UTXOs:
            if (utxo.recipient_publicKey == sender_publicKey) and balance<amount:
                input = Transaction_Input(utxo.id)
                balance += utxo.amount
                transaction_inputs.append(input)
        #Outputs
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
            #print("Enough Money for the transaction")
            return newTransaction
            
        else:
            #print("Not enough money for the transaction")
            return None


def sign_transaction(transaction, node):
    message = (str(transaction.sender_publicKey) + str(transaction.receiver_publicKey) + str(transaction.amount)).encode()
    node_id = node.id
    key = RSA.import_key(open('key_folder/private_'+str(node_id)+'.pem').read())
    h = SHA256.new(message)
    signature = pss.new(key).sign(h)
    transaction.signature = signature
    #print("Transaction signed")


def verify_signature(transaction, node):
    node_id = node.id
    key = RSA.import_key(open('key_folder/public_'+str(node_id)+'.pem').read())
    message = (str(transaction.sender_publicKey) + str(transaction.receiver_publicKey) + str(transaction.amount)).encode()
    h = SHA256.new(message)
    verifier = pss.new(key)
    try:
        verifier.verify(h, transaction.signature)
        #print ("The signature is authentic.")
        return True
    except (ValueError, TypeError):
        #print ("The signature is not authentic.")
        return False

# def validate_transaction(transaction, node):
#     # Check if signature is good
#     if verify_signature(transaction, node):
#         for input in transaction.transaction_inputs:
#             for utxo in node.UTXOs:
#                 if input.previous_outputID != utxo.id:
#                     print("Some money don't come from UTXOs")
#                     return False
#                 else:
#                     #Sender
#                     node.UTXOs.remove(utxo)
#                     node.UTXOs.append(transaction.transaction_outputs[0])#donne
#                     node.UTXOs.append(transaction.transaction_outputs[1])#reprend
#                     for n in nodes:
#                         if n.wallet.public_key==transaction.receiver_publicKey:
#                             n.UTXOs.append(transaction.transaction_outputs[0])
#                     print('Transaction is fully validated')
#                     return True

def validate_transaction(transaction,node):
    isUTXO = False
    for input in transaction.transaction_inputs:
        for utxo in node.UTXOs:
            if input.previous_outputID == utxo.id:
                isUTXO = True
        
                node.UTXOs.remove(utxo)
                # transaction.transaction_inputs.pop()
                # print('removed!')
                # print('leninputs apres remove:',len(transaction.transaction_inputs))
                #checker si on supprime bien TOUT les UTXOs!
    # print('tu vas recup',transaction.transaction_outputs[1].amount)
    if isUTXO:
        node.UTXOs.append(transaction.transaction_outputs[1])#reprend
        for node in nodes:
            if node.wallet.public_key == transaction.receiver_publicKey:
                node.UTXOs.append(transaction.transaction_outputs[0])
                #print('Targeted wallet is available')
        return True
    else:
        #One input is not from unspent money!
        #print("You're trying to use money wich is not from you're unspent money!")
        return False
        

def broadcast_transaction(transaction):
    for node in nodes:
        node.jcurrentBlock.transactions.append(transaction)
    #print("Transaction broadcasted to all nodes")
            
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
    node.finTime = 0
    finTime = 0
    debutTime = time.time()
    nonce = 0
    #proof of work
    while node.jcurrentBlock.current_hash[0:difficulty] != '0'*difficulty:
        node.jcurrentBlock.nonce = nonce
        data = f"{node.jcurrentBlock.timestamp}{node.jcurrentBlock.transactions}{node.jcurrentBlock.nonce}{node.jcurrentBlock.previous_hash}".encode()
        node.jcurrentBlock.current_hash = hashlib.sha256(data).hexdigest()
        nonce += 1
    mined_block = node.jcurrentBlock
    finTime = int(time.time()*1000000)-int(debutTime*1000000)
    return mined_block, finTime

def broadcast_block(block):
    for node in nodes:
        node.jcurrentBlock = block
    #print("First mined block is broadcasted to all other nodes")

def validate_block(node):
    newBlock = node.jcurrentBlock
    prevBlock = node.validateBlocks[-1]
    data = f"{newBlock.timestamp}{newBlock.transactions}{newBlock.nonce}{newBlock.previous_hash}".encode()
    hash_result = hashlib.sha256(data).hexdigest()
    # if hash_result != vars(newBlock)['current_hash']:
    if hash_result != newBlock.current_hash:
        #print("Error in block validation")
        return False

    # if vars(newBlock)['previous_hash'] != vars(prevBlock)['current_hash']:
    if newBlock.previous_hash != prevBlock.current_hash:
        #print("Error in block validation")
        return False

    return True
    
def validate_chain():

    for i in range(len(blockchain)):
        newBlock = blockchain[i+1]
        prevBlock = blockchain[i]

        data = f"{newBlock.timestamp}{newBlock.transactions}{newBlock.nonce}{newBlock.previous_hash}".encode()
        
        hash_result = hashlib.sha256(data).hexdigest()

        if hash_result != newBlock.current_hash:
            return False

        if newBlock.previous_hash != prevBlock.current_hash:
            #print("Error in block validation")
            return False

        return True


#---------------------------------------------------------------------------------------------------------------
#Function which is called by the Front-end

def make_transaction(nodes, nodeSender, nodeRecever, amount, capacity, difficulty):
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
            mined_block, finTime = mine_block(node,difficulty)
            timeList = timeList | {node.id : finTime}
            mined = mined | {node.id : mined_block}

    if len(node.jcurrentBlock.transactions) == capacity:
        timeListSorted = dict(sorted(timeList.items(), key=lambda item:item[1], reverse=False))
        idGoodMinedBlock = list(timeListSorted.keys())[0]
        goodMinedBlock = list(mined.items())[idGoodMinedBlock][1]
        #print(goodMinedBlock)
        broadcast_block(goodMinedBlock)

        for node in nodes:
            if validate_block(node):
                    mined_block.index = len(node.validateBlocks)
                    #print(node.id," validate block",mined_block.index)
                    node.validateBlocks.append(mined_block)
                    # print('girafe',vars(mined_block.transactions))
            node.jcurrentBlock = Block(time.time(),[],mined_block.current_hash)
        
        selectedNode = None
        previousNode = None
        for node in nodes:
            if node.id == 0:
                selectedNode = node
                previousNode = node
            else:
                if len(node.validateBlocks)>len(previousNode.validateBlocks):
                    selectedNode = node
        #print(selectedNode.validateBlocks[-1])
        blockchain.append(selectedNode.validateBlocks[-1])
        #print(f"Is the chain validated ? {validate_chain()}")

def view_transactions():
    my_dict = {}
    for i in range (len(blockchain[-1].transactions)):
        my_dict = my_dict | {blockchain[-1].transactions[i].transaction_id : blockchain[-1].transactions[i].amount}
    return my_dict

#---------------------------------------------------------------------------------------------------------------
#Experimental evaluation

def throughput(txtPath):
    with open(txtPath, "r") as f:
        datas = f.read()
    sender = int(re.search(r'\d{1,2}', txtPath).group())
    balise_receiver = "<recipient_node_id>(.+?)</recipient_node_id>"
    balise_amount = "<amount>(.+?)</amount>"
    receivers = re.findall(balise_receiver, datas)
    amounts = re.findall(balise_amount, datas)

    for i in range(len(receivers)):
        test_transaction = create_transaction(nodes[sender].wallet.public_key, nodes[int(receivers[i])].wallet.public_key, int(amounts[i]))
        if test_transaction != None:
            sign_transaction(test_transaction,nodes[sender])
            verify_signature(test_transaction,nodes[sender])
            if validate_transaction(test_transaction,nodes[sender]):
                broadcast_transaction(test_transaction)
    return len(receivers)

def block_time(txtPath, capacity, difficulty):
    with open(txtPath, "r") as f:
        datas = f.read()
    sender = int(re.search(r'\d{1,2}', txtPath).group())
    balise_receiver = "<recipient_node_id>(.+?)</recipient_node_id>"
    balise_amount = "<amount>(.+?)</amount>"
    receivers = re.findall(balise_receiver, datas)
    amounts = re.findall(balise_amount, datas)
    for i in range(len(receivers)):
        make_transaction(nodes, nodes[sender], nodes[int(receivers[i])], int(amounts[i]), capacity, difficulty)

#Display the test of performance 1
def test_performance_1(capacity, difficulty):
    for i in range (initialNodeNumber-1):
        make_transaction(nodes, nodes[0], nodes[i+1], 100, capacity, difficulty)
    sTime = time.time()
    len1 = throughput("transactions_files/transaction0.txt")
    len2 = throughput("transactions_files/transaction1.txt")
    len3 = throughput("transactions_files/transaction2.txt")
    len4 = throughput("transactions_files/transaction3.txt")
    len5 = throughput("transactions_files/transaction4.txt")
    eTime = time.time()
    difference = eTime - sTime
    transPerSec = (len1+len2+len3+len4+len5) / difference
    print(f"Throughput = {transPerSec} transactions served per second for a capacity = {capacity} and a difficulty = {difficulty}\n")

#Display the test of performance 2
def test_performance_2(capacity, difficulty):
    for i in range (initialNodeNumber-1):
        make_transaction(nodes, nodes[0], nodes[i+1], 100, capacity, difficulty)
    sTime = time.time()
    block_time("transactions_files/transaction0.txt", capacity, difficulty)
    block_time("transactions_files/transaction1.txt", capacity, difficulty)
    block_time("transactions_files/transaction2.txt", capacity, difficulty)
    block_time("transactions_files/transaction3.txt", capacity, difficulty)
    block_time("transactions_files/transaction4.txt", capacity, difficulty)
    eTime = time.time()
    difference = eTime - sTime
    blockTime = difference/ len(blockchain)
    print(f"BlockTime = {blockTime}sec to add a block in the blockchain for a capacity = {capacity} and a difficulty = {difficulty}\n")

# print("\nPerformance Test 1:\n")
# test_performance_1(1,4)
# test_performance_1(1,5)
# test_performance_1(5,4)
# test_performance_1(5,5)
# test_performance_1(10,4)
# test_performance_1(10,5)

# print("\nPerformance Test 2:\n")
# test_performance_2(1,4)
# test_performance_2(1,5)
# test_performance_2(5,4)
# test_performance_2(5,5)
# test_performance_2(10,4)
# test_performance_2(10,5)

#---------------------------------------------------------------------------------------------------------------
#Initialization Area
#Listes des nodes:
nodes = list()
blockchain = []
initialNodeNumber = 5
capacity = 3
difficulty = 3
def Init_Nodes(nodes,initialNodeNumber):
    for i in range(initialNodeNumber):
        nodes.append(Node(initialNodeNumber))

Init_Nodes(nodes,5)
print ('Nombre de nodes:',len(nodes))
for i in range (initialNodeNumber-1):
    make_transaction(nodes, nodes[0], nodes[i+1], 100, capacity, difficulty)



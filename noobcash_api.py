from flask import Flask, render_template
from Crypto.PublicKey import RSA
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
    def __init__(self,index,timestamp,transactions,nonce,current_hash,previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.current_hash = current_hash
        self.previous_hash = previous_hash
        

class Wallet:
    def __init__(self, key_size):
        self.key_size = key_size
        self.key = RSA.generate(self.key_size)
    
    def get_public_key(self):
        return self.key.publickey().export_key()
    
    def get_private_key(self):
        return self.key.export_key()


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


#---------------------------------------------------------------------------------------------------------------
app= Flask(__name__)

@app.route('/noobcash', methods=['GET', 'POST'])
def user():
    return render_template("user.html")

if __name__ == '__main__':
    app.run(debug=True, port=9103)

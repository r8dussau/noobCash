from flask import Flask, render_template

#---------------------------------------------------------------------------------------------------------------

#Aciver l'environnement virtuel:
#env_noobcash\Scripts\activate

#set up flask app for the env (need to restart after)
#setx FLASK_APP "noobcash_api.py"

#Run l'app flask:
#flask run

#---------------------------------------------------------------------------------------------------------------


app= Flask(__name__)

@app.route('/noobcash', methods=['GET', 'POST'])
def user():
    return render_template("user.html")

if __name__ == '__main__':
    app.run(debug=True, port=9103)

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
        


#Transcation class
class Transaction_Input:
    def __init__(self) -> None:
        pass
        
class Transaction_Output:
    def __init__(self) -> None:
        pass

class Transcaction:
    def __init__(self, sender_address, receiver_address, amount, transaction_id,
                 transaction_inputs, transaction_outputs, signature):
        self.sender_address, self.receiver_address = sender_address, receiver_address
        self.amount = amount
        self.transaction_id = transaction_id
        self.transaction_inputs, self.transaction_outputs = transaction_inputs, transaction_outputs
        self.signature = signature

#---------------------------------------------------------------------------------------------------------------
# Creates a new transaction that contains all necessary fields. 
# The field transaction_inputs is filled with the Transactions that contain all ids of UTXOs
# required to get the amount we want to spend. 
def create_transaction():
    pass

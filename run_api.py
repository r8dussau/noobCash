from flask import Flask, request, render_template
from noobcash_api import nodes, wallet_balance, make_transaction, view_transactions, capacity, difficulty

#---------------------------------------------------------------------------------------------------------------
#Aciver l'environnement virtuel:
        #env_noobcash\Scripts\activate

#set up flask app for the env (need to restart after)
        #setx FLASK_APP "noobcash_api.py"

#Run l'app flask:
        #flask run
#---------------------------------------------------------------------------------------------------------------

app= Flask(__name__)

@app.route('/noobcash')
def index():
    return render_template('index.html')

@app.route('/transaction')
def transaction():
    my_list = []
    for node in nodes:
        my_list.append(node.id)
    return render_template('transaction.html', my_list=my_list)

@app.route('/view')
def view():
    return render_template('view.html')

@app.route('/balance')
def balance():
    my_list = []
    for node in nodes:
        my_list.append(node.id)
    return render_template('balance.html', my_list=my_list)

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/call-function', methods=['POST'])
def call_function():
    function_name = request.json['function_name']

    if function_name == 'import_balance':
        my_id = request.json['option']
        result = wallet_balance(nodes[int(my_id)].wallet)
        return str(result)
    
    if function_name == 'make_transaction':
        id_sender = request.json['option1']
        id_reciever = request.json['option2']
        amount = request.json['amount']
        make_transaction(nodes,nodes[int(id_sender)], nodes[int(id_reciever)], int(amount), capacity, difficulty)
        return amount
    
    if function_name == 'view_transaction':
        my_dict = view_transactions()
        return my_dict

    return "Nothing is called"

if __name__ == '__main__':
    app.run(debug=True, port=9103)
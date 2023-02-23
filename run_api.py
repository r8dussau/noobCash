from flask import Flask, request, send_file, render_template
from noobcash_api import createNode, transaction, nodes

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
    return render_template('transaction.html')

@app.route('/view')
def view():
    return render_template('view.html')

@app.route('/balance')
def balance():
    return render_template('balance.html')

@app.route('/help')
def help():
    return render_template('help.html')

""" 
@app.route('/noobcash')
def index():
    return render_template('index.html')
    #return send_file('index.html')

@app.route('/appelle-fonction', methods=['POST'])
def call_function():
    nom_fonction = request.json['nom_fonction']

    if nom_fonction == 'createNode':
        createNode(nodes)
        return f"You just created the node with the id {nodes[-1].id}"

    if nom_fonction == 'transaction':
        transaction(nodes, nodes[0], nodes[1], 1, 2)
        return "The 2nd function is called"

    return "Nothing is called"
 """

if __name__ == '__main__':
    app.run(debug=True, port=9103)
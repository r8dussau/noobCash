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


app= Flask(__name__)

@app.route('/noobcash', methods=['GET', 'POST'])
def user():
    return render_template("user.html")


class Wallet:
    def __init__(self, key_size):
        self.key_size = key_size
        self.key = RSA.generate(self.key_size)
    
    def get_public_key(self):
        return self.key.publickey().export_key()
    
    def get_private_key(self):
        return self.key.export_key()
        
keygen = Wallet(2048)
public_key = keygen.get_public_key()
private_key = keygen.get_private_key()
print(public_key)
print(private_key)




if __name__ == '__main__':
    app.run(debug=True, port=9103)
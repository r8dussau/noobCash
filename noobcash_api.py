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
# NoobCash  
NoobCash project from Distributed Systems Semester 9 course in Electronical and Computer Engineering School, NTUA.  
Back-end Python API and Front-end HTML with script from JavaScript are available on this git.  

### Components
All components can be found in NoobCash folder: 
- *templates* folder contains all HTML simple with the Javascript scripts that link each HTML file to each other and to the Python Flask file.  
- *key_folder* is the folder where public and private keys are stored locally.  
- *transactions_files* is the folder where the transactions files in txt format are stored. 
- *run_api.py* contains the python code allowing the creation of the website locally.
- *noobcash_api.py* contains all the back-end code.

### Authors
- Szymon Kubiszewski 
- Jules Morin
- Raphaël Dussauze

## Installation

### Python requirements 

The python API needs the following librairy to run:

- flask
- pycryptodome

You can use the package manager [pip](https://pip.pypa.io/en/stable/) to install these librairy in a python environnement:

```bash
pip install flask
pip install pycryptodome
```

## Usage

Once all the library are well installed, you can run the *run_api.py* If everything works fine, your terminal should return this:

```bash
 * Serving Flask app 'run_api'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on 'http://127.0.0.1:9103'
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 770-094-169
```

The http link is the local host link you should copy past in your browser to test all endpoint.  
You should then enter this link on your browser to start the test:

```bash
http://127.0.0.1:9103/noobcash
```


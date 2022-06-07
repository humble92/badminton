from flask import Flask

app = Flask(__name__)
app.secret_key = 'dafk;ladsjghdsagljk'

@app.route('/')
def home():
    return 'project home page for basic UI'

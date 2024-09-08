from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route("/")
def map():
    return send_from_directory('www', 'map.html')

@app.route("/www/<filename>")
def static_content(filename):
    return send_from_directory('www', filename)



app.run(host='0.0.0.0', port=81)




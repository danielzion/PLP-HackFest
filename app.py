from flask import Flask, render_template, request
import os
import goslate
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
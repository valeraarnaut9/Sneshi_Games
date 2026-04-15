from flask import Flask, request

app = Flask(__name__)

API_KEY = "afg68h5gi57ghyy4479qr36llbzxc468"

@app.route("/")
def home():
    key = request.args.get("key")

    if key == API_KEY:
        return "1"
    else:
        return "NO ACCESS"

if __name__ == "__main__":
    app.run()

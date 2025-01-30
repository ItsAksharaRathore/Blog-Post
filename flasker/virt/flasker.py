from flask import Flask, render_template


# create a Flask Instance
app = Flask(__name__)
# create a route decorator
@app.route('/')

def index():
    return "<h1>Hellooooooooo!</h1>"

if __name__ == '__main__':
    app.run(debug=True)

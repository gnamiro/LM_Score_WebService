# Imports necessary libraries
from crypt import methods
from flask import Flask
from flask import jsonify, request
from static.bertModel import PersianMaskedModel
# Define the app
app = Flask(__name__)

# Get a welcoming message once you start the server.


@app.route('/', methods=['POST'])
def home():
    request_data = request.get_json()

    sentence = None
    words = []
    if(request_data):
        if('sentence' in request_data):
            sentence = request_data['request_data']
        if('words' in request_data):
            words = request_data['words']

        return '''
            <h1> The sentence value is: {}</h1>
            <h1> The words values are: {}</h1>'''.format(sentence, words)
    # response = {'status': 200, 'response': {'1': 10, '2': 20, '3': 24}}

    return '''
        <form method="POST">
        <div><label>Sentence: <input type="text" name="sentence"></label></div>
        <div><label>Words: <input type="text" name="words"></label></div>
        <input type="submit" value="Submit">
        </form>
    '''


@app.route('/', methods=['GET'])
def main():
    pass


# If the file is run directly,start the app.
if __name__ == '__main__':
    maskedModel = PersianMaskedModel()

    app.run(debug=True)

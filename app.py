# Imports necessary libraries
# from crypt import methods
# from urllib import response
from flask import Flask
from flask import jsonify, request
from static.bertModel import PersianMaskedModel
# Define the app
app = Flask(__name__)

# Get a welcoming message once you start the server.


@app.route('/', methods=['POST'])
def home():
    request_data = request.get_json()
    # print(request_data)
    sentence = None
    words = []
    if(request_data):
        if('sentence' in request_data):
            sentence = request_data['sentence']
        if('words' in request_data):
            words = request_data['words']

        result = maskedModel.calculate_probability(sentence, words)

        _response = {'sentence': sentence,
                     'words': words,
                     'modelRespawns': result}

        return jsonify(_response)

    return '''
        <h1 style='color:red'>403 Access Forbiden, There is no way immma let you pass through!</h1>
    '''
    # response = {'status': 200, 'response': {'1': 10, '2': 20, '3': 24}}


@app.route('/', methods=['GET'])
def main():
    return '''
        <form method="POST">
        <div><label>Sentence: <input type="text" name="sentence"></label></div>
        <div><label>Words: <input type="text" name="words"></label></div>
        <input type="submit" value="Submit">
        </form>
    '''


# If the file is run directly,start the app.
if __name__ == '__main__':
    maskedModel = PersianMaskedModel()

    app.run(debug=True)

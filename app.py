# Imports necessary libraries
# from crypt import methods
# from urllib import response
from flask import Flask
from flask import jsonify, request
from flask_cors import CORS
from static.bertModel import PersianMaskedModel
# Define the app
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
# Get a welcoming message once you start the server.

cors = CORS(app, resources={r"/": {"origins": "http://localhost:5500"}})


@app.route('/', methods=['POST'])
# @cross_origin(origin='localhost', headers=['Content- Type'])
def home():
    try:
        request_data = request.get_json()
        print(request_data)
        sentence = None
        words = []
        if(request_data):
            if('sentence' in request_data):
                sentence = request_data['sentence']
            if('words' in request_data):
                words = request_data['words']

            assert type(words) == list
            assert type(sentence) == str

            result = maskedModel.calculate_probability(sentence, words)

            _response = {'sentence': sentence,
                         'words': words,
                         'modelRespawns': result}

            return jsonify(_response)
    except AssertionError:
        return '''
            <h1 style='color:red'>500 SERVER ERROR, pls check your input format, it has to be list for words and string for sentence</h1>
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

# LM_Score_WebService

Designing web service for Persian language grammar scoring model with flask

## A piece of advice for running this program:

### Remember, for using the pars-bert model, you need to clone the model from [https://huggingface.co/HooshvareLab/bert-base-parsbert-uncased](huggingface) website to your working directory. To speed up server performance, it is better to clone it first rather than downloading the model with the help of the transformers library.

first create a virtual environment with:

> python -m venv .env

Then activate venv with:

-for windows use:

> source .env/Scripts/activate

-for linux:

> source .env/bin/activate

then you can install the requirements with:

> pip install -r requirements.txt

after installing requirments, run app.py:

> python app.py

Within a few minutes, you can see from the terminal that the server is running on 127.0.0.1:5000.

<hr>
For using front, you can run FrontEnd files locally.

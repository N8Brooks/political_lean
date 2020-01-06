from simpletransformers.classification import ClassificationModel
import json

args = {'max_seq_length':512}
model = ClassificationModel('roberta', 'Outputs/', use_cuda=False, args=args)
mapping = {0:'L', 1:'LC', 2:'C', 3:'RC', 4:'R'}

def read_article(file_json):
    article = ''
    filedata = json.dumps(file_json)
    if len(filedata) < 100000:
        article = filedata
    return article

def lean(request):
    request_json = request.get_json(silent=True)
    sentences = read_article(request_json)
    pred, _ = model.predict([sentences])

    return mapping[pred[0]]


"""
from newspaper import fulltext
import requests

html = requests.get('https://www.cnn.com/2019/12/24/health/black-market-vapes/index.html').text
sentences = fulltext(html)
print(model.predict([sentences]))
"""
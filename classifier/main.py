from simpletransformers.classification import ClassificationModel
import json

model = ClassificationModel('albert', 'outputs/', use_cuda=False)
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

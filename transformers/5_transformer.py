# -*- coding: utf-8 -*-

from simpletransformers.classification import ClassificationModel
import pandas as pd
from sklearn.utils import shuffle
from sklearn.metrics import f1_score, accuracy_score

def f1_multiclass(labels, preds):
    return f1_score(labels, preds, average='micro')

train = pd.read_csv('2_train.csv',index_col='Unnamed: 0')[['content', 'label']]
test = pd.read_csv('2_test.csv', index_col='Unnamed: 0')[['content', 'label']]

mapping = {'L':0, 'LC':1, 'C':2, 'RC':3, 'R':4}
train['label'] = train['label'].apply(lambda x: mapping[x])
test['label'] = test['label'].apply(lambda x: mapping[x])
train = shuffle(train)
test = shuffle(test)
test.columns = ['text', 'label']
train.columns = ['text', 'label']

model = ClassificationModel('albert', 'albert-base-v1', num_labels=5)

args = {'overwrite_output_dir': True, 'train_batch_size': 25,
        'eval_batch_size': 25, 'gradient_accumulation_steps':10, 
        'weight_decay':4e-4, 'learning_rate':8e-4, 'adam_epsilon':8e-4, 
        'warmup_ratio':3e-2, 'max_grad_norm':5}
model.train_model(train, args=args)

result, model_outputs, wrong_predictions = model.eval_model(test, \
                                                            f1=f1_multiclass,\
                                                            acc=accuracy_score)

print(result)
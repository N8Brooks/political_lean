# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 00:08:57 2019

@author: Nate
"""

from simpletransformers.classification import ClassificationModel
import pandas as pd
from sklearn.utils import shuffle
from sklearn.metrics import f1_score, accuracy_score
from skopt import gp_minimize
from skopt.space import Real, Integer
from tqdm import tqdm

def f1_multiclass(labels, preds):
    return f1_score(labels, preds, average='micro')

# data
train = pd.read_csv('2_train.csv',index_col='Unnamed: 0')[['content', 'label']]
test = pd.read_csv('2_test.csv', index_col='Unnamed: 0')[['content', 'label']]
mapping = {'L':0, 'LC':1, 'C':2, 'RC':3, 'R':4}
train['label'] = train['label'].apply(lambda x: mapping[x])
test['label'] = test['label'].apply(lambda x: mapping[x])
train = shuffle(train)
test = shuffle(test)
test.columns = ['text', 'label']
train.columns = ['text', 'label']

# hyper parameter ranges
space = [
        Integer(1, 128, name='train_batch_size'),
        Integer(1, 10, name='gradient_accumulation_steps'),
        Real(0., 1e-3, name='weight_decay'),
        Real(0., 1e-3, name='learning_rate'),
        Real(0., 1e-3, name='adam_epsilon'),
        Real(0., 0.25, name='warmup_ratio'),
        Real(0., 10, name='max_grad_norm'),
        ]

pbar = tqdm(total=100)
# minimize 1-f1_score for the given list of hyper parameter ranges 
def objective(args):
    pbar.update(1)
    try:
        # cast np values to python and convert list to dict
        args = list(map(int, args[:3])) + list(map(float, args[3:]))
        args = dict(zip(['train_batch_size', 'gradient_accumulation_steps', 
                         'weight_decay', 'learning_rate', 
                         'learning_rate', 'adam_epsilon', 'warmup_ratio', 
                         'max_grad_norm'], args))
        args['overwrite_output_dir'] = True
        args['eval_batch_size'] = args['train_batch_size']
        model = ClassificationModel('albert', 'albert-base-v1', num_labels=5)    

        # train model, find reverse f1, force garbage collection
        model.train_model(train, args=args)
        result, *_ = model.eval_model(test, f1=f1_multiclass, 
                                      acc=accuracy_score)
        del model
        return 1. - result['f1']
    except:
        print('skip')
        return 1.

# call minimization function and print best hyper parameter values
res_gp = gp_minimize(objective, space, n_calls=128)
print(res_gp.x)
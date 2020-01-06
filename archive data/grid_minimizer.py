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
from skopt.space import Real, Integer, Categorical
from tqdm import tqdm
from skopt.utils import use_named_args
import multiprocessing as mp
from sklearn.metrics import confusion_matrix

# accuracy metrics function
def f1(labels, preds):
    return f1_score(labels, preds, average='micro')

def func(params, train, test):
    # attempt to read df
    try:
        df = pd.read_csv('opt_results.csv', index_col='Unnamed: 0')
    except:
        df = pd.DataFrame()
    
    args = dict()
    
    try:
        model = ClassificationModel('roberta', 'roberta-base', num_labels=5)
        args = {'overwrite_output_dir': True,'reprocess_input_data': True,
                'sliding_window': True, 'train_batch_size':8, 'eval_batch_size':8,
                'gradient_accumulation_steps':2, 'max_seq_length':512}
        
        args.update(params)
        
        model.train_model(train, args=args)
        
        result, outputs, _ = model.eval_model(test, f1=f1, acc=accuracy_score)
        predict = [row.argmax() for row in outputs]
        
        args.update(result)
        args['confusion_matrix'] = confusion_matrix(test['label'], predict)
        
    except Exception as e:
        # add exception and 0 for metrics
        print(e)
        args['exception'] = e
    
    # append and save df
    df = df.append(args, ignore_index=True)
    writing = True
    while writing:
        try:
            df.to_csv('opt_results.csv')
            writing = False
        except Exception as e:
            print(e)


if __name__ == '__main__':
    params = [{'num_train_epochs':1, 'learning_rate':2e-5},
              {'num_train_epochs':1, 'learning_rate':3e-5},
              {'num_train_epochs':2, 'learning_rate':4e-5},
              {'num_train_epochs':4, 'learning_rate':4e-5}]
    
    train = pd.read_csv('tmp_train.csv',index_col='Unnamed: 0')
    test = pd.read_csv('tmp_test.csv', index_col='Unnamed: 0')
    test.columns = ['text', 'label']
    train.columns = ['text', 'label']
    
    for args in params:
        p = mp.Process(target=func, args=(args, train, test,))
        p.start()
        p.join()
        p.terminate()
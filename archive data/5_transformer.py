# -*- coding: utf-8 -*-

from simpletransformers.classification import ClassificationModel
import pandas as pd
from sklearn.utils import shuffle
from sklearn.metrics import f1_score, accuracy_score
from gensim.parsing.preprocessing import preprocess_string
from sklearn.metrics import confusion_matrix

def f1_multiclass(labels, preds):
    return f1_score(labels, preds, average='micro')

if __name__ == '__main__':
    
    """
    train = pd.read_csv('tmp_train.csv',index_col='Unnamed: 0')
    test = pd.read_csv('tmp_test.csv', index_col='Unnamed: 0')
    """
    train = pd.read_csv('train.csv',index_col='Unnamed: 0', usecols=['Unnamed: 0', 'content', 'label'])
    test = pd.read_csv('test.csv', index_col='Unnamed: 0', usecols=['Unnamed: 0', 'content', 'label'])
    mapping = {'L':0, 'LC':1, 'C':2, 'RC':3, 'R':4}
    test.label = test.label.apply(mapping.get)
    train.label = train.label.apply(mapping.get)
    
    test.columns = ['text', 'label']
    train.columns = ['text', 'label']
    
    model = ClassificationModel('roberta', 'roberta-base', num_labels=5)
    
    args = {
            'overwrite_output_dir': True, 'reprocess_input_data': False,
            'sliding_window': True,
            'train_batch_size':8, 'eval_batch_size':8,
            'gradient_accumulation_steps':2,
            'max_seq_length':512,
            'num_train_epochs':3,
            'learning_rate':2e-5,
            'adam_epsilon':5e-6
            }
    
    model.train_model(train, args=args)
    
    result, model_outputs, wrong_predictions = model.eval_model(test, \
                                                            f1=f1_multiclass, \
                                                            acc=accuracy_score)
    
    test['predict'] = [row.argmax() for row in model_outputs]
    
    print(result)
    
    print(confusion_matrix(test['label'], test['predict']))

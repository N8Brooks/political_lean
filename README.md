# political_lean
 A chrome extension to determine political lean of an article using machine learning. 

* Build by going to chrome extensions, developer mode, loading unpacked, and then select the 'unpacked extension' folder here. 
* The 'unpacked extension' folder contains the chrome extension itself. It gives you a button that will send webpage text off to be classified. 
* The 'classifier' folder contains the ml model which we are running on google cloud functions which returns article classification. 
* The 'transformers' folder contains the python scripts used for training the model and hyper-parameter optimization. 
* The 'web scraping' folder contains scripts used for web scraping testing. 

![showing political classification of articles](https://github.com/N8Brooks/political_lean/blob/master/lean.gif)
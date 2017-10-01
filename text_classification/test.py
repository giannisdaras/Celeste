import sklearn
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from firebase import firebase

f1=open('john.txt','r')
f2=open('mary.txt','r')
f3=open('marios.txt','r')
temp=[]
temp.append(''.join(f1.readlines()))
temp.append(''.join(f2.readlines()))
temp.append(''.join(f3.readlines()))
f1.close()
f2.close()
f3.close()
text_clf = Pipeline([('vect', CountVectorizer()),('tfidf', TfidfTransformer()),('clf', MultinomialNB()),])
text_clf.fit(temp,[0,1,2])
firebase = firebase.FirebaseApplication('https://celeste-54d66.firebaseio.com/', None)
peopleDict={0:'John','1':'Marios','2':'mary'}
result=peopleDict[text_clf.predict(['beautiful, awesome, handsome'])[0]]
firebase.put('/url','current',result)


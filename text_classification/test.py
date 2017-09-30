import sklearn
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

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
print(text_clf.predict(['studying all time nerd geek']))
import time
import numpy as np
import pandas as pd 
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn import preprocessing
from sklearn.naive_bayes import GaussianNB
from sklearn.decomposition import PCA
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import f1_score


file1=open('training_data.csv','w')
file2=open('training_results.csv','w')


#party configuration
for i in range(100):
	file1.write(str(np.random.randint(4,20))+','+'2'+str(np.random.randint(0,4))+','+str(np.random.randint(0,1))+','+str(np.random.randint(0,70))+','+str(np.random.randint(10,40))+'\n')
	file2.write('4'+'\n')

#temperature configuration
for i in range(100):
	file1.write(str(np.random.randint(0,20))+','+str(np.random.randint(0,1))+str(np.random.randint(0,9))+','+str(np.random.randint(0,1))+','+str(np.random.randint(0,255))+','+str(np.random.randint(10,24)) +'\n')
	file2.write('2'+'\n')

#temperature configuration
for i in range(100):
	file1.write(str(np.random.randint(0,20))+','+str(np.random.randint(0,1))+str(np.random.randint(0,9))+','+str(np.random.randint(0,1))+','+str(np.random.randint(0,255))+','+str(np.random.randint(28,40))+'\n')
	file2.write('3'+'\n')

#window configuration
for i in range(100):
	file1.write(str(np.random.randint(0,20))+','+ '2'+str(np.random.randint(0,4))+','+str(np.random.randint(0,1))+','+str(np.random.randint(0,70))+','+str(np.random.randint(10,40))+'\n')
	file2.write('5'+'\n')

for i in range(1000):
	file1.write(str(np.random.randint(0,20))+','+ str(np.random.randint(0,1)) +str(np.random.randint(0,9))+','+str(np.random.randint(0,1))+','+str(np.random.randint(0,255))+','+str(np.random.randint(10,40))+'\n')
	file2.write('1'+'\n')

file1.close()
file2.close()

X = np.genfromtxt('training_data.csv', delimiter=',')
y = np.genfromtxt('training_results.csv', delimiter=',')


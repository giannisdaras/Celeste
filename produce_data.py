import time
import numpy as np

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


with open('increased_neural_data.txt', 'w') as fout:
	with open('increased_positives.txt', 'r') as fin:
		
		while True:
			l = fin.readline()
			if l == None or l == '':
				break
			else:
				l = l.strip('\n')
				if '/0/' in l:
					fout.write('{} 0\n'.format(l))
				elif '/1/' in l:
					fout.write('{} 1\n'.format(l))
				elif '/2/' in l:
					fout.write('{} 2\n'.format(l))
				
					

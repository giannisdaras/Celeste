import wget
f=open('urls.txt')
images=f.readlines()
for i in range(len(images)):
	filename = wget.download(images[i])

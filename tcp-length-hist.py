import numpy as np
import sys
import matplotlib.pyplot as plt

myfile = sys.argv[1]
mylist = []

#Assume that the file has a packet length per line

#These are sample commands to make the input file from tcpdump raw result
#tcpdump -r tcp_m_dump -n src 10.10.1.2 > l0-send.txt
#awk 'NF>1{print $NF}' l0-send.txt  > l0-send-size.txt
with open(myfile, 'rU') as f:
	for line in f:
		line = line.splitlines()[0]
		print (line)
		mylist.append(int(line))

np_array = np.array(mylist)
print (np_array)
plt.hist(np_array)
plt.show()
plt.close()
#bins = np.linspace(0, 200, 400)


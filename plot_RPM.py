import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file


raw_data = []
with open(filename) as inputfile:
	absolute_time = []
	zero_time = []
	RPM = []

	for line in inputfile:
		raw_data.append(line.strip())

	for i in range(len(raw_data)):
		temp = raw_data[i].split(" ")
		if (temp[2][2:8]) == "F00400":
			absolute_time.append((temp[0]).strip('(').strip(')'))
			first_nibble = (temp[2][9:])[6:8]
			second_nibble = (temp[2][9:])[8:10]
			RPM.append(int((second_nibble + first_nibble),16)/8)
			print("{}{}".format(second_nibble,first_nibble))
	
	fix_time = float((absolute_time[0]))
	
	for i in range(len(absolute_time)):
		zero_time.append(float(absolute_time[i])-fix_time)
	print(max(RPM))
	f=plt.figure()
	plt.plot(zero_time,RPM)
	f.suptitle('Engine Speed VS Zero Time', fontsize=18,fontname='Arial')
	plt.xlabel('Zero Time (s)',fontsize=14, fontname='Arial')
	plt.ylabel('Engine Speed (RPM)',fontsize=14,fontname='Arial')
	#f.savefig("RPM_vs_zero_time.pdf", bbox_inches='tight')
	plt.show()



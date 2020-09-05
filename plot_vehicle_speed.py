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
	Vehicle_speed = []

	for line in inputfile:
		raw_data.append(line.strip())

	for i in range(len(raw_data)):
		temp = raw_data[i].split(" ")
		if (temp[2][2:8]) == "FEF100":
			absolute_time.append((temp[0]).strip('(').strip(')'))
			first_nibble = (temp[2][9:])[2:4]
			second_nibble = (temp[2][9:])[4:6]
			Vehicle_speed.append(int((second_nibble + first_nibble),16)/256*0.621371)

	
	fix_time = float((absolute_time[0]))
	
	for i in range(len(absolute_time)):
		zero_time.append(float(absolute_time[i])-fix_time)

	f=plt.figure()
	plt.plot(zero_time,Vehicle_speed)
	f.suptitle('Vehicle Speed VS Zero Time', fontsize=18,fontname='Arial')
	plt.xlabel('Zero Time (s)',fontsize=14, fontname='Arial')
	plt.ylabel('Vehicle Speed (mph)',fontsize=14,fontname='Arial')

	plt.show()

a = "pizza name"
b = "detail"
print(a+b+"nice")
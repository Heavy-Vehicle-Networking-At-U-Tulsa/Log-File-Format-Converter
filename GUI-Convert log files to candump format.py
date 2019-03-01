'''
GUI has each menu to convert from NMFTA Logger 1, Vehicle Spy log files to readable format. 
Data can be saved as candump format or readable format.
'''
from tkinter import *
from tkinter.filedialog import *
from tkinter.tix import *
import os
import struct
import pandas as pd
import xlrd
import numpy as np

class App(object):
	def __init__(self, master):
		frame = Frame(master)
		frame.pack()
		self.text = Text(master, height = 250, width = 250)
		self.text.pack(side = LEFT, fill = BOTH)
		scrollbar.config(command = self.text.yview)
		menu = Menu(master)
		root.config(menu=menu)
		# file menu for NMFTA CAN Logger file
		NMFTA_filemenu = Menu(menu, tearoff=0)
		menu.add_cascade(label="NMFTA Logger 1", menu=NMFTA_filemenu)
		NMFTA_filemenu.add_command(label="Open", command=self.NMFTA_open)
		NMFTA_filemenu.add_command(label="Show Transport Protocol Messages", command=self.NMFTA_Transport_protocol_open)
		NMFTA_filemenu.add_command(label="Save as candump format", command=self.file_save_candump)
		NMFTA_filemenu.add_command(label="Save as text format", command=self.file_save_text)        
		NMFTA_filemenu.add_separator()
		NMFTA_filemenu.add_command(label="Exit", command=self.do_exit)

		# file menu for CAN Logger 2 file
		Logger2_filemenu = Menu(menu, tearoff=0)
		menu.add_cascade(label="CAN_Logger_2", menu=Logger2_filemenu)
		Logger2_filemenu.add_command(label="Open", command=self.Logger2_open)
		#Logger2_filemenu.add_command(label="Show Transport Protocol Messages", command=self.Logger2_Transport_protocol_open)
		Logger2_filemenu.add_command(label="Save as candump format", command=self.file_save_candump)
		Logger2_filemenu.add_command(label="Save as text format", command=self.file_save_text)        
		Logger2_filemenu.add_separator()
		Logger2_filemenu.add_command(label="Exit", command=self.do_exit)

		# file menu for Vehicle Spy Logger file
		Vspy_filemenu = Menu(menu, tearoff=0)
		menu.add_cascade(label="Vehicle Spy", menu=Vspy_filemenu)
		Vspy_filemenu.add_command(label="Open", command=self.vspy_open)
		Vspy_filemenu.add_command(label="Save as candump format", command=self.file_save_candump)
		Vspy_filemenu.add_command(label="Save as text format", command=self.file_save_text)
		Vspy_filemenu.add_separator()
		Vspy_filemenu.add_command(label="Exit", command=self.do_exit)

	def NMFTA_open(self):
		filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
		fileLocation = 0
		file_size = os.path.getsize(filename)
		message_list =[]
		candump_list =[]
		with open(filename,'rb') as binFile:
			while(fileLocation<file_size):
				block =binFile.read(512) #read every 512 bytes
				fileLocation+=512
				for recordNum in range(21): #Parse through CAN message
					record = block[4+recordNum*24:4+(recordNum+1)*24]
					timeSeconds = struct.unpack("<L",record[0:4])[0]
					timeMicrosecondsAndDLC = struct.unpack("<L",record[8:12])[0]
					timeMicroseconds = timeMicrosecondsAndDLC & 0x00FFFFFF
					abs_time = timeSeconds + timeMicroseconds * 0.000001
					ID = struct.unpack("<L",record[12:16])[0]
					message_bytes = record[16:24]
					#create list for all data parsed
					candump_list.append("({:0.6f}) can0 {:08X}#{}"
										.format(abs_time,ID,''.join(["{:02X}"
											.format(b) for b in message_bytes])))
					message_list.append(["{:0.6f}".format(abs_time),"can0","{:08X}"
										.format(ID),]+["{:02X}"
											.format(b) for b in message_bytes])

		#Create data frame for display and save option
		pd.options.display.max_rows = len(message_list)
		self.message_dataframe = pd.DataFrame(message_list, 
									columns=["Abs. Time","Channel","ID",
											"B0","B1","B2","B3","B4","B5","B6","B7"])
		self.message_dataframe.index= np.arange(1,len(self.message_dataframe)+1) #Start index at 1
		self.candump_dataframe = pd.DataFrame(candump_list)
		#show on text window
		text = self.message_dataframe
		self.text.delete(0.0,END)
		self.text.insert(END,text)

	def Logger2_open(self):
		filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
		fileLocation = 0
		file_size = os.path.getsize(filename)
		message_list =[]
		candump_list =[]
		with open(filename,'rb') as binFile:
			while(fileLocation<file_size):
				block =binFile.read(512) #read every 512 bytes
				fileLocation+=512
				for recordNum in range(19): #Parse through CAN message
					record = block[4+recordNum*25:4+(recordNum+1)*25]
					channel = record[0]
					timeSeconds = struct.unpack("<L",record[1:5])[0]
					timeMicrosecondsAndDLC = struct.unpack("<L",record[13:17])[0]
					timeMicroseconds = timeMicrosecondsAndDLC & 0x00FFFFFF
					abs_time = timeSeconds + timeMicroseconds * 0.000001
					ID = struct.unpack("<L",record[9:13])[0]
					message_bytes = record[17:25]
					#create list for all data parsed
					candump_list.append("({:0.6f}) can{:0.0f} {:08X}#{}"
										.format(abs_time,channel,ID,''.join(["{:02X}"
											.format(b) for b in message_bytes])))
					message_list.append(["{:0.6f}".format(abs_time),"can{:0.0f}".format(channel),"{:08X}"
										.format(ID),]+["{:02X}"
											.format(b) for b in message_bytes])

		#Create data frame for display and save option
		pd.options.display.max_rows = len(message_list)
		self.message_dataframe = pd.DataFrame(message_list, 
									columns=["Abs. Time","Channel","ID",
											"B0","B1","B2","B3","B4","B5","B6","B7"])
		self.message_dataframe.index= np.arange(1,len(self.message_dataframe)+1) #Start index at 1
		self.candump_dataframe = pd.DataFrame(candump_list)
		#show on text window
		text = self.message_dataframe
		self.text.delete(0.0,END)
		self.text.insert(END,text)
		

	def NMFTA_Transport_protocol_open(self):
		filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
		fileLocation = 0
		file_size = os.path.getsize(filename)
		message_list =[]
		candump_list=[]
		with open(filename,'rb') as binFile:
			while(fileLocation<file_size):
				block =binFile.read(512)
				fileLocation+=512
				for recordNum in range(21):
					record = block[4+recordNum*24:4+(recordNum+1)*24]
					timeSeconds = struct.unpack("<L",record[0:4])[0]
					timeMicrosecondsAndDLC = struct.unpack("<L",record[8:12])[0]
					timeMicroseconds = timeMicrosecondsAndDLC & 0x00FFFFFF
					abs_time = timeSeconds + timeMicroseconds * 0.000001
					message_bytes = record[16:24]
					ID = struct.unpack("<L",record[12:16])[0]
					Transport_ID = hex(ID).upper()[2:].zfill(8)[2:4] #Transport ID with PGN = 60416 and 60160
					if Transport_ID =="EC" or Transport_ID =="EB":
						message_list.append(["{:0.6f}".format(abs_time),"can0","{:08X}".format(ID),]+["{:02X}".format(b) for b in message_bytes])
						candump_list.append("({:0.6f}) can0 {:08X}#{}".format(abs_time,ID,''.join(["{:02X}".format(b) for b in message_bytes])))

		#Create data frame for display and save option
		pd.options.display.max_rows = len(message_list) #show full capcity
		self.message_dataframe = pd.DataFrame(message_list, columns=["Abs. Time","Channel","ID","B0","B1","B2","B3","B4","B5","B6","B7"])
		self.message_dataframe.index= np.arange(1,len(self.message_dataframe)+1) #Start index at 1
		self.candump_dataframe = pd.DataFrame(candump_list)
		#show on text window
		text = self.message_dataframe
		self.text.delete(0.0,END)
		self.text.insert(END,text)	

	def vspy_open(self):
		filename = askopenfilename()
		workbook = xlrd.open_workbook(filename)
		sheet = workbook.sheet_by_name('in')
		message_list = []
		candump_list = []
		Byte = [None] * 8
		rownum = 0

		while rownum < (sheet.nrows-38): #The actual CAN data starts on row 39
			abs_time = sheet.cell_value(rownum+38,1)
			if sheet.cell_value(rownum+38,7) =="J1708": #Check type of channel
				rownum = rownum +1
				continue								#Skip if J1708 type
			if sheet.cell_value(rownum+38,7) =="HS CAN": 
				channel = "can0"
			if sheet.cell_value(rownum+38,7) =="MS CAN": 
				channel = "can1"
			#Check to see if ID is a string or float, then convert to string if it is float
			if type(sheet.cell_value(rownum+38,9))==type(1.23):
				ID = ('%f' % (sheet.cell_value(rownum+38,9),)).rstrip('0').rstrip('.')
			elif type(sheet.cell_value(rownum+38,9))==type('String'):
				ID = "{:08X}".format(int(sheet.cell_value(rownum+38,9),16))

			#Check to see if each byte is string or float, then convert to string if it is float
			for i in range(8):
				if type(sheet.cell_value(rownum+38,i+12))==type(1.23):
					Byte[i]= int(('%f' % (sheet.cell_value(rownum+38,i+12),)).rstrip('0').rstrip('.'),16)
				elif type(sheet.cell_value(rownum+38,i+12))==type("string"):
					if sheet.cell_value(rownum+38,i+12) == "": #If cells are empty, pad with FF
						Byte[i] = int("FF",16)
					else:
						Byte[i]= int(sheet.cell_value(rownum+38,i+12),16)
			#Create the lists
			message_list.append(["{:0.6f}".format(abs_time), channel,"{}".format(ID)]+["{:02X}".format(b) for b in Byte])		
			candump_list.append("({:0.6f}) {} {}#{}".format(abs_time,channel,ID,''.join(["{:02X}".format(b) for b in Byte])))			
			rownum = rownum +1

		pd.options.display.max_rows = len(message_list)
		self.message_dataframe = pd.DataFrame(message_list, columns=["Abs. Time","Channel","ID",
																	"B0","B1","B2","B3","B4","B5","B6","B7"])
		self.message_dataframe.index= np.arange(1,len(self.message_dataframe)+1) #Start index at 1
		self.candump_dataframe = self.candump_dataframe = pd.DataFrame(candump_list)
		text = self.message_dataframe
		self.text.delete(0.0,END)
		self.text.insert(END,text)

	def file_save_candump(self):
		fout = asksaveasfile(mode='w', defaultextension=".txt",
							filetypes=[("Text files",".txt"),
													("CSV files",".csv")],
										 initialdir="dir",
										 title="Save as")
		self.candump_dataframe.to_csv(fout, index = False, header = False)
		fout.close()


	def file_save_text(self):
		name = asksaveasfile(mode ='w',defaultextension=".txt",
						 filetypes=[("Text files",".txt")],
						 initialdir="dir",
						 title="Save as")
		name.write(str(self.message_dataframe))
		name.close()

	def do_exit(self):
		root.destroy()

root = Tk()
scrollbar = Scrollbar(root)
scrollbar.pack( side = RIGHT, fill=Y )
root.title("Format convert")
app = App(root)
root.mainloop()
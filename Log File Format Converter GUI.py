program_title = "CAN Logger Format Converter"
program_version = "2.0beta"
program_author = "Duy Van"
program_position = "Department of Mechanical Engineering"
program_affiliation = "The University of Tulsa"

license_text ='''Unless otherwise noted or conflicting, the contents of this repository are released under the MIT license:

Permission is hereby granted, free of charge, to any person obtaining a copy of this software, hardware and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE OR HARDWARE.
'''
import sys
import os
import struct
import pandas as pd
import numpy as np

from PyQt5.QtWidgets import (QMainWindow,
							 QWidget,
							 QApplication,
							 QAction,
							 QMessageBox,
							 QTableView,
							 QGroupBox,
							 QBoxLayout,
							 QVBoxLayout,
							 QTableWidget,
							 QDockWidget,
							 QScrollArea,
							 QLabel,
							 QGridLayout,
							 QFileDialog,
							 QProgressDialog,
							 QAbstractScrollArea,
							 QPushButton)

from PyQt5.QtCore import (Qt,
						  QCoreApplication,
						  QAbstractTableModel)

from PyQt5.QtGui import QIcon

class FormatConverter(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setGeometry(100,100,1820,980)
		self.showMaximized()

		self.home_directory = os.getcwd()

		# Upon startup, run a user interface routine
		self.init_ui()


	def init_ui(self):
	#Builds Graphical User Interface (GUI)
		menubar = self.menuBar()

		#Start with a status bar
		self.statusBar().showMessage('Ready')
        #Build common menu options
        
        
        #File Menu Items
		file_menu = menubar.addMenu('&File')
		open_file = QAction(QIcon(r'icons8_Open_48px.png'), '&Open', self)
		open_file.setShortcut('Ctrl+O')
		open_file.setStatusTip('Open new File')
		open_file.triggered.connect(self.load_file)
		file_menu.addAction(open_file)


		save_file = QAction(QIcon(r'floppy-disk-save-button-icon-65887.png'), '&Save', self)
		save_file.setShortcut('Ctrl+S')
		save_file.setStatusTip('Save File')
		save_file.triggered.connect(self.save)
		file_menu.addAction(save_file)

		exit_action = QAction(QIcon(r'icons8_Exit_Sign_48px.png'), '&Exit', self)        
		exit_action.setShortcut('Ctrl+Q')
		exit_action.setStatusTip('Exit application')
		exit_action.triggered.connect(self.close)
		file_menu.addAction(exit_action)

		'''
		#Data Menu Items
		view_menu = menubar.addMenu('&View')
		transport_show = QAction(QIcon(r'transport_truck.png'), '&Find Transport Messages', self)
		transport_show.setStatusTip('Show all the transport layer messages in J1939')
		transport_show.triggered.connect(self.show_transport)
		view_menu.addAction(transport_show)
		'''

		#Help Menu Items
		help_menu = menubar.addMenu('&Help')
		about_action = QAction(QIcon(r'icons8_Info_40px.png'), '&About', self) 
		about_action.setStatusTip('Show Program Information') 
		about_action.triggered.connect(self.show_about_dialog)
		help_menu.addAction(about_action)

		#build the entries in the dockable tool bar
		self.main_toolbar = self.addToolBar("Main")
		self.main_toolbar.addAction(open_file)
		self.main_toolbar.addAction(save_file)
		self.main_toolbar.addAction(exit_action)
		self.main_toolbar.addAction(about_action)

		'''
		self.data_toolbar = self.addToolBar("Data")
		self.data_toolbar.addAction(transport_show)
		'''

		self.main_widget = QWidget(self)
		#$self.graph_canvas = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        
        #Define where the widgets go in the window
        #We start by defining some boxes that we can arrange

        #Set up a Table to display CAN Messages data
		self.data_table = QTableView(self)
        #Create a GUI box to put all the table and data widgets in
		table_box = QGroupBox("Transport Data")
        #Create a layout for that box using the vertical
		table_box_layout = QVBoxLayout()
        #Add the widgets into the layout
		table_box_layout.addWidget(self.data_table)
        #setup the layout to be displayed in the box
		table_box.setLayout(table_box_layout)

        #Set up a table to display CAN ID data
		self.can_table = QTableView()
		can_box = QGroupBox("CAN Log Data")
        #Create a layout for that box using the vertical
		can_box_layout = QVBoxLayout()
        #Add the widgets into the layout
		can_box_layout.addWidget(self.can_table)
        #setup the layout to be displayed in the box
		can_box.setLayout(can_box_layout)

		

		#Now we can set all the previously defined boxes into the main window
		self.grid_layout = QGridLayout(self.main_widget)
		self.grid_layout.addWidget(can_box,0,0,1,1) 
		self.grid_layout.addWidget(table_box,0,1)
		self.grid_layout.setRowStretch(0, 3)
        
		self.main_widget.setLayout(self.grid_layout)
		self.setCentralWidget(self.main_widget)
        
		self.setWindowTitle(program_title)
		self.setWindowIcon(QIcon(r'transport_truck.png'))
		self.show()

		self.message_dataframe = None



	def show_about_dialog(self):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setText("{}\nVersion: {}\nWritten by:\n\t{}\n\t{}\n\t{}".format(
							program_title,
							program_version,
							program_author,
							program_position,
							program_affiliation))
		#msg.setInformativeText("""Windows icons by Icons8\nhttps://icons8.com/download-huge-windows8-set""")
		msg.setWindowTitle("About")
		msg.setDetailedText("The full path of the file is \n{}".format(os.path.abspath(os.getcwd())))
		msg.setStandardButtons(QMessageBox.Ok)
		#msg.setWindowModality(Qt.ApplicationModal)
		msg.exec_()



	def load_file(self):
		msg = QMessageBox()
		msg.setText("Choose Log File Type:")
		msg.setWindowTitle("Open")
		msg.setIcon(QMessageBox.Question)
		pbutton1 = msg.addButton(str('NMFTA Logger 1'),QMessageBox.ActionRole)
		pbutton2 = msg.addButton(str('CAN Logger 2'),QMessageBox.ActionRole)
		msg.setStandardButtons(QMessageBox.Close)
		msg.exec_()

		if (msg.clickedButton() == pbutton1):
			self.load_NMFTA_logger1()
			self.show_transport()
		elif (msg.clickedButton() == pbutton2):
			self.load_logger2()
			self.show_transport()

	def load_NMFTA_logger1(self):
		print('Loading NMFTA Logger 1 Data')
		pybutton = QPushButton('Show messagebox', self)
		#pybutton.clicked.connect(self.clickMethod)
		pybutton.resize(200,64)
		pybutton.move(50, 50)
		options = QFileDialog.Options()
		options |= QFileDialog.Detail
		self.data_file_name, data_file_type = QFileDialog.getOpenFileName(self,
											"Open Binary Log File",
											self.home_directory,
											"Binary Log Files (*.bin);;All Files (*)",
											options = options)
		if self.data_file_name:
			print(self.data_file_name)
			self.statusBar().showMessage(
				"Successfully Opened {}.".format(self.data_file_name))
			#Add file location to window title 
			self.setWindowTitle(program_title + " - " + self.data_file_name)
			self.load_NMFTA_logger1_binary()

		else:
			self.statusBar().showMessage("Failed to open file.")

	def load_NMFTA_logger1_binary(self):
		print("Logger 1")
		#This may be a long process, so let's show a progress bar:
		fileLocation = 0
		startTime = None
		file_size = os.path.getsize(self.data_file_name)
		print("File size is {} bytes".format(file_size))

		loading_progress = QProgressDialog(self)
		loading_progress.setMinimumWidth(300)
		loading_progress.setWindowTitle("Loading and Converting Binary")
		loading_progress.setMinimumDuration(0)
		loading_progress.setMaximum(file_size)
		loading_progress.setWindowModality(Qt.ApplicationModal)

		message_list =[]
		candump_list =[]
		with open(self.data_file_name,'rb') as binFile:
			while(fileLocation<file_size):
				block =binFile.read(512) #read every 512 bytes
				fileLocation+=512
				binFile.seek(fileLocation)
				loading_progress.setValue(fileLocation)
				if loading_progress.wasCanceled():
					break
				for recordNum in range(21): #Parse through CAN message
					record = block[4+recordNum*24:4+(recordNum+1)*24]
					timeSeconds = struct.unpack("<L",record[0:4])[0]
					timeMicrosecondsAndDLC = struct.unpack("<L",record[8:12])[0]
					timeMicroseconds = timeMicrosecondsAndDLC & 0x00FFFFFF
					DLC = timeMicrosecondsAndDLC & 0xFF000000
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

		self.load_can_table(self.message_dataframe)

	def load_logger2(self):
		print('Loading CAN Logger 2 Data')
		pybutton = QPushButton('Show messagebox', self)
		#pybutton.clicked.connect(self.clickMethod)
		pybutton.resize(200,64)
		pybutton.move(50, 50)
		options = QFileDialog.Options()
		options |= QFileDialog.Detail
		self.data_file_name, data_file_type = QFileDialog.getOpenFileName(self,
											"Open Binary Log File",
											self.home_directory,
											"Binary Log Files (*.bin);;All Files (*)",
											options = options)
		if self.data_file_name:
			print(self.data_file_name)
			self.statusBar().showMessage(
				"Successfully Opened {}.".format(self.data_file_name))
			#Add file location to window title 
			self.setWindowTitle(program_title + " - " + self.data_file_name)
			self.load_logger2_binary()

		else:
			self.statusBar().showMessage("Failed to open file.")

	def load_logger2_binary(self, append_data_frame = False):
		#This may be a long process, so let's show a progress bar:
		fileLocation = 0
		startTime = None
		file_size = os.path.getsize(self.data_file_name)
		print("File size is {} bytes".format(file_size))

		loading_progress = QProgressDialog(self)
		loading_progress.setMinimumWidth(300)
		loading_progress.setWindowTitle("Loading and Converting Binary")
		loading_progress.setMinimumDuration(0)
		loading_progress.setMaximum(file_size)
		loading_progress.setWindowModality(Qt.ApplicationModal)

		message_list =[]
		candump_list =[]
		with open(self.data_file_name,'rb') as binFile:
			while(fileLocation<file_size):
				block =binFile.read(512) #read every 512 bytes
				fileLocation+=512
				binFile.seek(fileLocation)
				loading_progress.setValue(fileLocation)
				if loading_progress.wasCanceled():
					break
				for recordNum in range(19): #Parse through CAN message
					record = block[4+recordNum*25:4+(recordNum+1)*25]
					channel = record[0]
					timeSeconds = struct.unpack("<L",record[1:5])[0]
					timeMicrosecondsAndDLC = struct.unpack("<L",record[13:17])[0]
					timeMicroseconds = timeMicrosecondsAndDLC & 0x00FFFFFF
					DLC = (timeMicrosecondsAndDLC & 0xFF000000)>>24
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

		self.load_can_table(self.message_dataframe)




	def load_can_table(self,message_df):
		loading_progress = QProgressDialog(self)
		loading_progress.setMinimumWidth(300)
		loading_progress.setWindowTitle("Loading CAN Table")
		loading_progress.setMinimumDuration(0)
		loading_progress.setWindowModality(Qt.ApplicationModal)



		self.can_data_display_model = CANMessageModel(message_df)
		self.can_table.setModel(self.can_data_display_model)
		self.can_table.resizeColumnsToContents()
		self.can_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
		header = self.can_table.horizontalHeader()
		self.can_table.selectionModel().selectedColumns()
		loading_progress.close()




	def save(self):
		if self.message_dataframe is not None:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Question)
			msg.setText("Choose Format to Save File:")
			msg.setWindowTitle("Save File")
			pbuttonT = msg.addButton(str('Text Format'),QMessageBox.ActionRole)
			pbuttonC = msg.addButton(str('candump Format'),QMessageBox.ActionRole)
			msg.setStandardButtons(QMessageBox.Close)
			msg.exec_()

			if (msg.clickedButton() == pbuttonT):
				self.save_text()
			elif (msg.clickedButton() == pbuttonC):
				self.save_candump()

		else:
			info_box = QMessageBox()
			info_box.setWindowTitle("Save")
			info_box.setText("There is no file")
			info_box.setStandardButtons(QMessageBox.Ok)
			info_box.setIcon(QMessageBox.Information)
			info_box.exec_()

	def save_text(self):
		print('Save Data as Text')
		options = QFileDialog.Options()
		options |= QFileDialog.Detail
		self.data_file_name, data_file_type = QFileDialog.getSaveFileName(self,
											"Save File",
											self.home_directory,
											"Text Files (*.txt);;All Files (*)",
											options = options)
		if self.data_file_name:
			print(self.data_file_name)
			file = open(self.data_file_name,'w')
			file.write(str(self.message_dataframe))
			file.close()

	def save_candump(self):
		print("Save Data as candump")
		options = QFileDialog.Options()
		options |= QFileDialog.Detail
		self.data_file_name, data_file_type = QFileDialog.getSaveFileName(self,
											"Save File",
											self.home_directory,
											"Text Files (*.txt);;All Files (*)",
											options = options)
		if self.data_file_name:
			print(self.data_file_name)
			file = open(self.data_file_name,'w')
			self.candump_dataframe.to_csv(file,index = False, header = False)
			file.close()

	def show_transport(self):
		loading_progress = QProgressDialog(self)
		loading_progress.setMinimumWidth(300)
		loading_progress.setWindowTitle("Finding J1939 Transport Protocol Messages")
		loading_progress.setMinimumDuration(0)
		loading_progress.setWindowModality(Qt.ApplicationModal)

		self.id_selection_list = []
		for trial_id in self.message_dataframe["ID"].value_counts().index:
			if trial_id[2:4] == "EB":
				self.id_selection_list.append(trial_id)
			if trial_id[2:4] == "EC":
				self.id_selection_list.append(trial_id)

		df = self.message_dataframe.loc[self.message_dataframe['ID'].isin(self.id_selection_list)]
		#print(df)

		self.data_display_model = CANMessageModel(df)
		self.data_table.setModel(self.data_display_model)
		self.data_table.resizeColumnsToContents()
		self.data_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
		header = self.data_table.horizontalHeader()
		self.data_table.selectionModel().selectedColumns()
		loading_progress.close()




class CANMessageModel(QAbstractTableModel): 
	"""
	Class to populate a table view with a pandas dataframe
	"""
	def __init__(self, data, parent=None):
		QAbstractTableModel.__init__(self, parent)
		self._data = data
    
	def rowCount(self, parent=None):
		return self._data.shape[0]

	def columnCount(self, parent=None):
		return self._data.shape[1]

	def data(self, index, role=Qt.DisplayRole):
		if index.isValid():
			if role == Qt.DisplayRole:
                #return str(self._data.iloc[index.row(), index.column()])
				data_val = self._data.iloc[index.row(), index.column()]
                #print(type(data_val))
				if type(data_val) is np.int64:
					if data_val < 256 and index.column() > 7:  
						return "{:02X}".format(data_val)
					else:
						if  index.column() == 3: #The CAN ID column
							return "{:08X}".format(data_val)
						else:
							return "{}".format(data_val)
				elif type(data_val) is np.float64:
						return "{:0.6f}".format(data_val)
				else:
					return str(data_val)
		return None

	def headerData(self, col, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self._data.columns[col]
		return None





if __name__ == '__main__':
    #Start the program this way according to https://stackoverflow.com/questions/40094086/python-kernel-dies-for-second-run-of-pyqt5-gui
	app = QCoreApplication.instance()
	if app is None:
		app = QApplication(sys.argv)
	execute = FormatConverter()
	sys.exit(app.exec_())
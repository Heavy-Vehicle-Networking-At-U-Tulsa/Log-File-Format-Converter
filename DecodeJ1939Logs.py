#!/bin/env/python

program_title = "NMFTA CAN Data Analyzer"
program_version = "0.1beta"
program_author = "Jeremy Daily"
program_position = "Department of Mechanical Engineering"
program_affiliation = "The University of Tulsa"

license_text ='''Unless otherwise noted or conflicting, the contents of this repository are released under the MIT license:

Permission is hereby granted, free of charge, to any person obtaining a copy of this software, hardware and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE OR HARDWARE.
'''
import pretty_j1939.parse
import pandas as pd
import numpy as np

import sys
import struct
import bitstring

from PyQt5.QtWidgets import (QMainWindow,
                             QWidget,
                             QTreeView,
                             QMessageBox,
                             QHBoxLayout,
                             QFileDialog,
                             QLabel,
                             QSlider,
                             QCheckBox,
                             QLineEdit,
                             QVBoxLayout,
                             QApplication,
                             QPushButton,
                             QTableWidget,
                             QTableView,
                             QTableWidgetItem,
                             QScrollArea,
                             QAbstractScrollArea,
                             QAbstractItemView,
                             QSizePolicy,
                             QGridLayout,
                             QGroupBox,
                             QAction,
                             QDockWidget,
                             QProgressDialog)
from PyQt5.QtCore import (Qt,
                          QTimer,
                          QVariant,
                          QCoreApplication,
                          QAbstractTableModel,
                          QModelIndex)
from PyQt5.QtGui import QIcon
from functools import partial

from graphing import * #this is a custom class file for graphics

rcParams.update({'figure.autolayout': True}) #Depends of matplotlib from graphing

class CANDecoderMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(100,100,1820,980)
        #self.showMaximized()

        self.home_directory = os.getcwd()
        #self.message_dataframe = None

        # Upon startup, run a user interface routine
        self.init_ui()

        #load the J1939 Database
        pretty_j1939.parse.init_j1939db()

        #load an example file
        self.data_file_name = "example.bin"
        self.load_binary()

    def init_ui(self):
        #Builds Graphical User Interface (GUI)

        #Start with a status bar
        self.statusBar().showMessage('Ready')

        #Build common menu options
        menubar = self.menuBar()

        #File Menu Items
        file_menu = menubar.addMenu('&File')
        open_file = QAction(QIcon(r'icons8_Open_48px_1.png'), '&Open', self)
        open_file.setShortcut('Ctrl+O')
        open_file.setStatusTip('Open new File')
        open_file.triggered.connect(self.load_data)
        file_menu.addAction(open_file)

        exit_action = QAction(QIcon(r'icons8_Exit_Sign_48px.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        #Data Menu Items
        data_menu = menubar.addMenu('&Data')
        load_action = QAction(QIcon(r'icons8_Data_Sheet_48px.png'), '&Load Selected IDs', self)
        load_action.setStatusTip('Filter selected message IDs into the Data Table')
        load_action.triggered.connect(self.load_message_table)
        data_menu.addAction(load_action)

        #Data Menu Items
        view_menu = menubar.addMenu('&View')
        transport_action = QAction(QIcon(r'icons8_Variation_48px.png'), '&Find Transport Messages', self)
        transport_action.setStatusTip('Find all the transport layer messages in J1939')
        transport_action.triggered.connect(self.find_transport_pgns)
        view_menu.addAction(transport_action)

        transport_show = QAction(QIcon(r'icons8_New_Presentation_48px.png'), '&Show Transport Message Window', self)
        transport_show.setStatusTip('Display the dockable transport layer message window.')
        transport_show.triggered.connect(self.show_transport_dock)
        view_menu.addAction(transport_show)


        #Help Menu Items
        help_menu = menubar.addMenu('&Help')
        about_action = QAction(QIcon(r'icons8_Info_40px.png'), '&About', self)
        about_action.setStatusTip('Show Program Information')
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)


        #build the entries in the dockable tool bar
        self.main_toolbar = self.addToolBar("Main")
        self.main_toolbar.addAction(open_file)
        self.main_toolbar.addAction(exit_action)
        self.main_toolbar.addAction(about_action)

        self.data_toolbar = self.addToolBar("Data")
        self.data_toolbar.addAction(load_action)
        self.data_toolbar.addAction(transport_action)

        #self.main_widget = QWidget()

        self.main_widget = QWidget(self)
        self.graph_canvas = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)

        #Define where the widgets go in the window
        #We start by defining some boxes that we can arrange

        #Set up a Table to display CAN Messages data
        #self.data_table = QTableWidget()
        self.data_table = QTableView(self)
        #Create a GUI box to put all the table and data widgets in
        table_box = QGroupBox("Data Table")
        #Create a layout for that box using the vertical
        table_box_layout = QVBoxLayout()
        #Add the widgets into the layout
        table_box_layout.addWidget(self.data_table)
        #setup the layout to be displayed in the box
        table_box.setLayout(table_box_layout)

        #Set up a table to display CAN ID data
        self.can_id_table = QTableWidget()
        can_id_box = QGroupBox("CAN ID Table")
        #Create a layout for that box using the vertical
        can_id_box_layout = QVBoxLayout()
        #Add the widgets into the layout
        can_id_box_layout.addWidget(self.can_id_table)
        #setup the layout to be displayed in the box
        can_id_box.setLayout(can_id_box_layout)

        self.transport_layer_table = QTableWidget()
        transport_layer_box = QWidget()
        self.transport_layer_dock = QDockWidget("Transport Layer Message Table", self)
        #Create a layout for that box using the vertical
        transport_layer_layout = QVBoxLayout()
        #Add the widgets into the layout
        transport_layer_layout.addWidget(self.transport_layer_table)
        self.transport_layer_dock.setWidget(transport_layer_box)
        #setup the layout to be displayed in the box
        transport_layer_box.setLayout(transport_layer_layout)

        #Setup the area for plotting SPNs
        self.control_scroll_area = QScrollArea()
        self.control_scroll_area.setWidgetResizable(True)
        #Create the container widget
        self.control_box = QWidget()
        #put the container widget into the scroll area
        self.control_scroll_area.setWidget(self.control_box)
        #create a layout strategy for the container
        self.control_box_layout = QVBoxLayout()
        #assign the layout strategy to the container
        self.control_box.setLayout(self.control_box_layout)
        #set the layout so labels are at the top
        self.control_box_layout.setAlignment(Qt.AlignTop)

        label = QLabel("Select a CAN ID to see and plot the available Suspect Parameter Numbers.")
        self.control_box_layout.addWidget(label)

        #Setup the area for plotting SPNs
        self.info_scroll_area = QScrollArea()
        self.info_scroll_area.setWidgetResizable(True)
        #Create the container widget
        self.info_box = QGroupBox("Suspect Parameter Number (SPN) Information")
        #put the container widget into the scroll area
        self.info_scroll_area.setWidget(self.info_box)
        #create a layout strategy for the container
        self.info_box_layout = QVBoxLayout()
        #assign the layout strategy to the container
        self.info_box.setLayout(self.info_box_layout)
        #set the layout so labels are at the top
        self.info_box_layout.setAlignment(Qt.AlignTop)



        #Ignore the box creation for now, since the graph box would just have 1 widget
        #graph_box = QGroupBox("Plots")

        #Now we can set all the previously defined boxes into the main window
        self.grid_layout = QGridLayout(self.main_widget)
        self.grid_layout.addWidget(can_id_box,0,0,1,2)
        self.grid_layout.addWidget(self.control_scroll_area,1,0)
        self.grid_layout.addWidget(self.info_scroll_area,1,1)
        self.grid_layout.addWidget(self.graph_canvas,1,2,2,1)
        self.grid_layout.addWidget(table_box,0,2)
        self.grid_layout.addWidget(self.transport_layer_dock,2,0,1,2)
        self.grid_layout.setRowStretch(0, 3)

        self.main_widget.setLayout(self.grid_layout)
        self.setCentralWidget(self.main_widget)

        self.setWindowTitle(program_title)
        self.show()


    def show_about_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("{}\nVersion: {}\nWritten by:\n\t{}\n\t{}\n\t{}".format(
                program_title,
                program_version,
                program_author,
                program_position,
                program_affiliation))
        msg.setInformativeText("""Windows icons by Icons8\nhttps://icons8.com/download-huge-windows8-set""")
        msg.setWindowTitle("About")
        msg.setDetailedText("The full path of the file is \n{}".format(os.path.abspath(os.getcwd())))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowModality(Qt.ApplicationModal)
        msg.exec_()


    def load_data(self):
        print("Loading Data")
        options = QFileDialog.Options()
        options |= QFileDialog.Detail
        self.data_file_name,data_file_type = QFileDialog.getOpenFileName(self,
                                        "Open Binary Log File",
                                        #"{}".format(self.home_directory),
                                        self.home_directory,
                                        "Binary Log Files (*.bin);;All Files (*)",
                                        options=options)
        if self.data_file_name:
            print(self.data_file_name)
            self.statusBar().showMessage(
                    "Successfully Opened {}.".format(self.data_file_name))
            self.setWindowTitle(program_title + " - " + self.data_file_name)
            self.load_binary()

        else:
           self.statusBar().showMessage("Failed to open file.")

    def load_binary(self,append_data_frame = False):
        #This may be a long process, so let's show a progress bar:


        fileLocation = 0
        startTime = None
        file_size = os.path.getsize(self.data_file_name)
        print("File size is {} bytes".format(file_size))

        loading_progress = QProgressDialog(self)
        loading_progress.setMinimumWidth(600)
        loading_progress.setWindowTitle("Loading and Converting Binary")
        loading_progress.setMinimumDuration(0)
        loading_progress.setMaximum(file_size)
        loading_progress.setWindowModality(Qt.ApplicationModal)

        message_list = []
        first_time = True
        with open(self.data_file_name,'rb') as binFile:
            while (fileLocation < file_size):
                block = binFile.read(512) # This is because the original binary data was created
                fileLocation+=512
                binFile.seek(fileLocation)
                #print(".",end='')
                loading_progress.setValue(fileLocation)
                if loading_progress.wasCanceled():
                    break
                if block[0:4] == b'CAN2':
                    for recordNum in range(19):
                        record = block[4+recordNum*25:4+(recordNum+1)*25]
                        channel = record[0]
                        timeSeconds = struct.unpack("<L",record[1:5])[0]
                        timeMicrosecondsAndDLC = struct.unpack("<L",record[13:17])[0]
                        timeMicroseconds = timeMicrosecondsAndDLC & 0x00FFFFFF
                        real_time = timeSeconds + timeMicroseconds * 0.000001
                        if first_time:
                            previous_time = real_time
                            first_time = False
                        DLC = (timeMicrosecondsAndDLC & 0xFF000000) >> 24
                        ID = struct.unpack("<L",record[9:13])[0]
                        (PGN,DA,SA) = pretty_j1939.parse.parse_j1939_id(ID)
                        message_bytes = record[17:25]

                        if startTime == None:
                            startTime=timeSeconds + timeMicroseconds * 0.000001
                        delta_time = real_time - previous_time
                        previous_time = real_time
                        rel_time = real_time-startTime

                        message_list.append([channel,real_time,rel_time,delta_time,ID,PGN,DA,SA,DLC] + [b for b in message_bytes] + [message_bytes])

                else:
                    channel = 0
                    for recordNum in range(21):
                        record = block[4+recordNum*24:4+(recordNum+1)*24]

                        timeSeconds = struct.unpack("<L",record[0:4])[0]
                        timeMicrosecondsAndDLC = struct.unpack("<L",record[8:12])[0]
                        timeMicroseconds = timeMicrosecondsAndDLC & 0x00FFFFFF
                        real_time = timeSeconds + timeMicroseconds * 0.000001
                        if first_time:
                            previous_time = real_time
                            first_time = False
                        DLC = (timeMicrosecondsAndDLC & 0xFF000000) >> 24
                        ID = struct.unpack("<L",record[12:16])[0]
                        (PGN,DA,SA) = pretty_j1939.parse.parse_j1939_id(ID)
                        message_bytes = record[16:24]

                        if startTime is None:
                            startTime=timeSeconds + timeMicroseconds * 0.000001
                        delta_time = real_time - previous_time
                        previous_time = real_time
                        rel_time = real_time-startTime

                        message_list.append([channel,real_time,rel_time,delta_time,ID,PGN,DA,SA,DLC] + [b for b in message_bytes] + [message_bytes])

        self.message_dataframe = pd.DataFrame(message_list, columns = ["Channel","Abs. Time","Rel. Time","Delta Time","ID","PGN","DA","SA","DLC","B0","B1","B2","B3","B4","B5","B6","B7","Bytes"])

        #self.load_message_table(self.message_dataframe)
        self.load_can_id_table()
        self.find_transport_pgns()

    def load_message_table(self,message_df):

        loading_progress = QProgressDialog(self)
        loading_progress.setMinimumWidth(300)
        loading_progress.setWindowTitle("Loading Data Table")
        loading_progress.setMinimumDuration(4000)

        loading_progress.setWindowModality(Qt.ApplicationModal)


        message_df.drop("Delta Time",axis=1,inplace=True)
        time_deltas = message_df["Abs. Time"].diff()
        #print(time_deltas)
        message_df.insert(2,"Delta Time",time_deltas)

        print(message_df.head())

        self.can_data_display_model = CANMessageModel(message_df)
        self.data_table.setModel(self.can_data_display_model)
        self.data_table.resizeColumnsToContents()
        self.data_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        header = self.data_table.horizontalHeader()
        self.data_table.selectionModel().selectedColumns()
        header.sectionClicked.connect(self.plot_column)
        self.time_list=message_df["Rel. Time"].tolist()
        loading_progress.close()


    def plot_column(self):
        #print("Clicked Header")
        #header_indicies = self.data_table.selectionModel().selectedColumns()
        #print(QTableWidget.currentColumn)
        self.graph_canvas.clear()
        values = {}
        for selection in self.data_table.selectedIndexes():
            #print(str(selection.row()) + ' ' + str(selection.column()))
            #print(selection.data())
            if selection.column() == 16:
                return #bytes won't convert
            if selection.column() >= 7 and selection.column() <= 15:
                val = int(selection.data(),16)
            elif selection.column() == 3:
                val = int(selection.data(),16)
            else:
                val = float(selection.data())
            try:
                values[selection.column()].append(val)
            except:
                values[selection.column()]=[val]

        for key,vals in values.items():
            #print(key)
            #print(vals)
            self.graph_canvas.plot_data(self.time_list,vals,"Col {}".format(key))
        self.graph_canvas.title(self.data_file_name)
        self.graph_canvas.xlabel("Time (sec)")
        self.graph_canvas.ylabel("Value")

    def load_can_id_table(self):
        loading_progress = QProgressDialog(self)
        loading_progress.setMinimumWidth(300)
        loading_progress.setWindowTitle("Loading CAN ID Table")
        loading_progress.setMinimumDuration(0)
        loading_progress.setWindowModality(Qt.ApplicationModal)

        #Find the number of times each unique ID happens
        unique_ids = self.message_dataframe["ID"].value_counts()
        print(unique_ids.head())
        self.CAN_groups = self.message_dataframe.groupby(["ID"])
        #print(CAN_groups.get_group(unique_ids.index[0]))
        #return
        unique_ids.sort_index(inplace=True)
        print(unique_ids.head())

        self.can_id_table.setRowCount(0)
        self.can_id_table.clear()
        self.can_id_table_columns = ["Hex CAN ID", "PGN","Acronym","DA","SA","Source","Count","Period (ms)", "Freq. (Hz)"]
        self.can_id_table.setColumnCount(len(self.can_id_table_columns))
        self.can_id_table.setHorizontalHeaderLabels(self.can_id_table_columns)

        row = 0
        loading_progress.setMaximum(len(unique_ids))
        for unique_id,count in unique_ids.items():

            if loading_progress.wasCanceled():
                break

            #Get the pandas data frame for each unique ID
            df = self.CAN_groups.get_group(unique_id)

            if count > 1:
                time_deltas = df["Abs. Time"].diff()
                period = time_deltas.mean()*1000
            else:
                period = 0

            (PGN,DA,SA) = pretty_j1939.parse.parse_j1939_id(unique_id)
            formatted_da, da_name = pretty_j1939.parse.get_formatted_address_and_name(DA)
            formatted_sa, sa_name = pretty_j1939.parse.get_formatted_address_and_name(SA)

            if period > 0:
                frequency = 1000/period
            else:
                frequency = 0

            acronym = pretty_j1939.parse.get_pgn_acronym(PGN)

            row = self.can_id_table.rowCount()
            loading_progress.setValue(row+1)
            self.can_id_table.insertRow(row)
            row_values = ["{:08X}".format(unique_id),
                          "{:8d}".format(PGN),
                          str(acronym),
                          str(formatted_da),
                          #da_name,
                          str(formatted_sa),
                          str(sa_name),
                          "{:12d}".format(count),
                          "{:5d}".format(int(period)) ,
                          "{:9.3f}".format(frequency)]

            for col in range(self.can_id_table.columnCount()):
                entry = QTableWidgetItem(row_values[col])
                entry.setFlags(entry.flags() & ~Qt.ItemIsEditable)
                self.can_id_table.setItem(row,col,entry)

        self.statusBar().showMessage("Found {} unique IDs.".format(row))

        print("Finished loading CAN ID Table.")

        self.id_selection_list=[] #create an empty list
        self.can_id_table.setSortingEnabled(True)
        self.can_id_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        #self.can_id_table.doubleClicked.connect(self.load_message_table)
        self.can_id_table.itemSelectionChanged.connect(self.create_spn_plot_buttons)
        self.can_id_table.resizeColumnsToContents()
        self.can_id_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def plot_SPN(self, spn, pgn, id_key):
        if self.spn_plot_checkbox[spn].isChecked():
            callback = self.statusBar().showMessage

            name, offset, scale, spn_end, spn_length, spn_start, units = \
                pretty_j1939.parse.lookup_all_spn_params(callback, spn, pgn)

            self.info_box_layout.addWidget(QLabel("SPN {}: {}".format(spn,name)))
            self.info_box_layout.addWidget(QLabel("  Resolution: {}, Units: {}".format(scale,units)))
            self.info_box_layout.addWidget(QLabel("  Offset: {} {}, Length: {} bits".format(offset,units,spn_length)))
            self.info_box_layout.addWidget(QLabel("  Start Bit: {}, End Bit: {}".format(spn_start,spn_end)))

            values = []
            valid_times = []
            df = self.CAN_groups.get_group(id_key)

            for theBytes, time in zip(df["Bytes"], df["Rel. Time"]):
                try:
                    spn_value = pretty_j1939.parse.get_spn_value(bitstring.Bits(bytes=theBytes), spn, pgn)
                    if spn_value is None:
                        continue
                    #print("SPN value: {}\n".format(spn_value))
                    values.append(spn_value)
                    valid_times.append(time)
                except ValueError:
                    pass

            #Plot the data
            self.graph_canvas.plot_data(valid_times, values, "SPN {}".format(spn))
            self.graph_canvas.title(os.path.basename(self.data_file_name))
            self.graph_canvas.xlabel("Time (sec)")
            self.graph_canvas.ylabel("{} ({})".format(name,units))

            #Disable the button to show it's been plotted
            while self.spn_plot_checkbox[spn].isChecked() == False:
                self.spn_plot_checkbox[spn].setChecked(True)
            self.spn_plot_checkbox[spn].setEnabled(False)

    def clear_plots(self):
        self.graph_canvas.clear()
        #Clear the information box
        while self.info_box_layout.count():
            item = self.info_box_layout.takeAt(0)
            item.widget().deleteLater()

        for spn in sorted(self.spn_list):
            self.spn_plot_checkbox[spn].setEnabled(True)
            self.spn_plot_checkbox[spn].setChecked(False)

    def create_spn_plot_buttons(self):
        try:
            self.clear_plots()
        except:
            pass
        #print("getting selection")
        row_indicies = self.can_id_table.selectionModel().selectedRows()
        self.id_selection_list=[]
        for index in row_indicies:
            #print(index.row(),end=' ')
            id_item = self.can_id_table.item(index.row(), 0)
            #print(id_item.text())
            self.id_selection_list.append(id_item.text())

        # clear a layout and delete all widgets
        while self.control_box_layout.count():
            item = self.control_box_layout.takeAt(0)
            item.widget().deleteLater()
        #add a clear plot button
        clear_button = QPushButton("Clear and Reset Plot",self)
        clear_button.clicked.connect(self.clear_plots)
        self.control_box_layout.addWidget(clear_button)

        self.spn_list=[]
        id_keys = [int(id_text,16) for id_text in self.id_selection_list]

        self.message_selection = self.message_dataframe.loc[self.message_dataframe['ID'].isin(id_keys)]
        self.load_message_table(self.message_selection)

        self.spn_plot_checkbox={}

        for id_key in id_keys:
            #we need to look up the PGN that was put into the ID_dict. The key was the ID as an integer
            (PGN,DA,SA) = pretty_j1939.parse.parse_j1939_id(id_key)
            #selected_data_frames.append(self.CAN_groups.get_group(id_key))
            try:
                pgn_object = pretty_j1939.parse.get_pgn_object(PGN)
                for spn in pgn_object['SPNs']:
                    spn_name = pretty_j1939.parse.get_spn_name(spn)
                    self.spn_list.append(spn)
                    self.spn_plot_checkbox[spn] = QCheckBox("Plot SPN {}: {}".format(spn, spn_name), self)
                    if pretty_j1939.parse.is_spn_numerical_values(pretty_j1939.parse.get_spn_object(spn)['Units']):
                        # We need to pass the SPN to the plotter
                        self.spn_plot_checkbox[spn].stateChanged.connect(partial(self.plot_SPN, spn, PGN, id_key))
                    else:
                        self.spn_plot_checkbox[spn].setDisabled(True)
            except KeyError:
                pass
        for spn in sorted(self.spn_list):
            self.control_box_layout.addWidget(self.spn_plot_checkbox[spn])
        #set newly updated widget to display in the scroll box
        self.control_scroll_area.setWidget(self.control_box)

    def find_transport_pgns(self):
        loading_progress = QProgressDialog(self)
        loading_progress.setMinimumWidth(300)
        loading_progress.setWindowTitle("Finding J1939 Transport Protocol Messages")
        loading_progress.setMinimumDuration(0)
        loading_progress.setWindowModality(Qt.ApplicationModal)

        self.id_selection_list = []
        #self.message_dataframe["ID"].value_counts().index
        for message_id in self.message_dataframe["ID"].value_counts().index:
            #print("{:08X}".format(message_id & 0x00FF0000))
            if pretty_j1939.parse.is_transport_message(message_id):
                self.id_selection_list.append(message_id)

        print(self.id_selection_list)
        df = self.message_dataframe.loc[self.message_dataframe['ID'].isin(self.id_selection_list)]
        print(df.head())
        self.load_message_table(df)

        all_bams = {}

        def process_bam_found(data_bytes, sa, pgn):
            if sa in all_bams.keys():
                all_bams[sa].append((data_bytes, pgn))
            else:
                all_bams[sa] = [(data_bytes, pgn)]

        bam_processor = pretty_j1939.parse.get_bam_processor(process_bam_found)

        row=0
        loading_progress.setMaximum(len(df))
        for index,line in df.iterrows():
            row+=1
            loading_progress.setValue(row)
            if loading_progress.wasCanceled():
                break

            message_id = line["ID"]
            sa = line["SA"]
            message_bytes = line["Bytes"]
            timestamp = line["Abs. Time"]

            bam_processor(message_bytes, message_id)

        #Set the headers
        self.transport_layer_table_columns = ["PGN","Acronym","SA","Data"]
        self.transport_layer_table.setColumnCount(len(self.transport_layer_table_columns))
        self.transport_layer_table.setHorizontalHeaderLabels(self.transport_layer_table_columns)
        #self.transport_layer_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.transport_layer_table.clearContents()

        display = {}
        for sa, pgn_and_data_list in sorted(all_bams.items()):
            formatted_sa = "{:3d}".format(sa)
            for data_and_pgn in pgn_and_data_list:
                formatted_pgn = "{:8d}".format(data_and_pgn[1])
                pgn_acronym = pretty_j1939.parse.get_pgn_acronym(data_and_pgn[1])

                data = data_and_pgn[0].decode("ascii","backslashreplace")

                display[formatted_pgn + formatted_sa]=[formatted_pgn, pgn_acronym, formatted_sa, data]

        self.transport_layer_table.setRowCount(0)
        for row_values in sorted(display.values()):
                row = self.transport_layer_table.rowCount()
                self.transport_layer_table.insertRow(row)
                for col in range(self.transport_layer_table.columnCount()):
                    data_and_pgn = QTableWidgetItem(row_values[col])
                    data_and_pgn.setFlags(data_and_pgn.flags() & ~Qt.ItemIsEditable)
                    self.transport_layer_table.setItem(row,col,data_and_pgn)

        self.transport_layer_table.resizeColumnsToContents()
        self.transport_layer_table.setSortingEnabled(True)
        self.transport_layer_dock.show()#.setFloating(True)
        #close the progress bar
        #loading_transport_progress.setValue(row+2)

    def show_transport_dock(self):
        self.transport_layer_dock.show()

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
    execute = CANDecoderMainWindow()
    sys.exit(app.exec_())

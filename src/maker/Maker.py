# =========================================================================
#             FILE: Maker.py
#
#            USAGE: ---
#
#      DESCRIPTION: This define all components of the Makerchip Tab.
#
#          OPTIONS: ---
#     REQUIREMENTS: ---
#             BUGS: ---
#            NOTES: ---
#           AUTHOR: Sumanto Kar, sumantokar@iitb.ac.in, FOSSEE, IIT Bombay
# ACKNOWLEDGEMENTS: Rahul Paknikar, rahulp@iitb.ac.in, FOSSEE, IIT Bombay
#                Digvijay Singh, digvijay.singh@iitb.ac.in, FOSSEE, IIT Bombay
#                Prof. Maheswari R. and Team, VIT Chennai
#     GUIDED BY: Steve Hoover, Founder Redwood EDA
#                Kunal Ghosh, VLSI System Design Corp.Pvt.Ltd
#                Anagha Ghosh, VLSI System Design Corp.Pvt.Ltd
# OTHER CONTRIBUTERS:
#                Prof. Madhuri Kadam, Shree L. R. Tiwari College of Engineering
#                Rohinth Ram, Madras Institue of Technology
#                Charaan S., Madras Institue of Technology
#                Nalinkumar S., Madras Institue of Technology
#  ORGANIZATION: eSim Team at FOSSEE, IIT Bombay
#       CREATED: Monday 29, November 2021
#      REVISION: Tuesday 25, January 2022
# =========================================================================

# importing the files and libraries
from xml.etree import ElementTree as ET  # noqa:F401
import hdlparse.verilog_parser as vlog
import time  # noqa:F401
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread, Qt  # noqa:F401
from PyQt5.QtWidgets \
    import QApplication, \
    QWidget, QLabel, QVBoxLayout  # noqa:F401
from configuration.Appconfig import Appconfig
import os
import subprocess  # noqa:F401
import watchdog.events
import watchdog.observers
from os.path import expanduser
home = expanduser("~")
# import inotify.adapters

# declaring the global variables
# verilogfile stores the name of the file
# toggle flag stores the object of the toggling button
verilogFile = []
toggle_flag = []

# beginning class Maker. This class create the Maker Tab


class Maker(QtWidgets.QWidget):

    # initailising the varaibles
    def __init__(self, filecount):
        print(self)

        QtWidgets.QWidget.__init__(self)
        self.count = 0
        self.text = ""
        self.filecount = filecount
        self.entry_var = {}
        self.createMakerWidget()
        self.obj_Appconfig = Appconfig()
        verilogFile.append("")

    # Creating the various components of the Widget(Maker Tab)
    def createMakerWidget(self):

        self.grid = QtWidgets.QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(self.createoptionsBox(), 0, 0, QtCore.Qt.AlignTop)
        self.grid.addWidget(self.creategroup(), 1, 0, 5, 0)
        # self.grid.addWidget(self.creategroup(), 1, 0, 5, 0)
        self.show()

    # This function is to Add new  verilog file
    def addverilog(self):

        init_path = '../../../'
        if os.name == 'nt':
            init_path = ''
        self.verilogfile = QtCore.QDir.toNativeSeparators(
            QtWidgets.QFileDialog.getOpenFileName(
                self, "Open verilog Directory",
                init_path + "home", "*v"
            )[0]
        )
        if self.verilogfile == "":
            self.verilogfile = self.entry_var[0].text()

        if self.verilogfile == "":
            reply = QtWidgets.QMessageBox.critical(
                None,
                "Error Message",
                "<b>Error: No Verilog File Chosen.\
                Please chose a Verilog file</b>",
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Ok:
                self.addverilog()
                self.obj_Appconfig.print_info('Add Verilog File Called')

            elif reply == QtWidgets.QMessageBox.Cancel:
                self.obj_Appconfig.print_info('No Verilog File Chosen')
                return

        self.text = open(self.verilogfile).read()
        self.entry_var[0].setText(self.verilogfile)
        self.entry_var[1].setText(self.text)
        global verilogFile

        verilogFile[self.filecount] = self.verilogfile
        if self.refreshoption in toggle_flag:
            toggle_flag.remove(self.refreshoption)

        self.observer = watchdog.observers.Observer()
        self.event_handler = Handler(
            self.verilogfile,
            self.refreshoption,
            self.observer)

        self.observer.schedule(
            self.event_handler,
            path=self.verilogfile,
            recursive=True)
        self.observer.start()
        # self.notify=notify(self.verilogfile,self.refreshoption)
        # self.notify.start()
        # open("filepath.txt","w").write(self.verilogfile)

    # This function is used to call refresh while
    # running Ngspice to Verilog Converter
    # (as the original one gets destroyed)
    def refresh_change(self):
        if self.refreshoption in toggle_flag:
            self.toggle = toggle(self.refreshoption)
            self.toggle.start()

    # It is used to refresh the file in eSim if its edited anywhere else
    def refresh(self):
        if not hasattr(self, 'verilogfile'):
            return
        self.text = open(self.verilogfile).read()
        self.entry_var[1].setText(self.text)
        print("NgVeri File: " + self.verilogfile + " Refreshed")
        self.obj_Appconfig.print_info(
            "NgVeri File: " + self.verilogfile + " Refreshed")
        self.observer = watchdog.observers.Observer()
        self.event_handler = Handler(
            self.verilogfile,
            self.refreshoption,
            self.observer)

        self.observer.schedule(
            self.event_handler,
            path=self.verilogfile,
            recursive=True)
        self.observer.start()
        # self.notify.start()
        global toggle_flag
        if self.refreshoption in toggle_flag:
            toggle_flag.remove(self.refreshoption)

    # This function is used to save the edited file in eSim
    def save(self):
        wr = self.entry_var[1].toPlainText()
        open(self.verilogfile, "w+").write(wr)

    # This is used to run the makerchip-app
    def runmakerchip(self):
        init_path = '../../'
        if os.name == 'nt':
            init_path = ''  # noqa:F841
        try:
            if not os.path.isfile(home + "/.makerchip_accepted"):
                reply = QtWidgets.QMessageBox.warning(
                    None, "Terms of Services", "Please review the makerchip\
                         Terms of Service \
                         (<a href='https://www.makerchip.com/terms/'>\
                         https://www.makerchip.com/terms/</a> ).\
                          Have you read and do you accept \
                          these Terms of Service? [y/N]:",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )

                if reply == QtWidgets.QMessageBox.Yes:
                    f = open(home + "/.makerchip_accepted", "w")
                    f.close()
                else:
                    return
            print("Running Makerchip..............................")
            # self.file = open(self.verilogfile,"w")
            # self.file.write(self.entry_var[1].toPlainText())
            # self.file.close()
            filename = self.verilogfile
            if self.verilogfile.split('.')[-1] != "tlv":
                reply = QtWidgets.QMessageBox.warning(
                    None,
                    "Do you want to automate top module?",
                    "<b>Click on YES if you want top module \
                    to be automatically added. \
                    NOTE: a .tlv file will be created \
                    in the directory of current verilog file\
                        and the makerchip will be running on \
                        this file. Otherwise click on NO.</b><br/> \
                    <b> To not open Makerchip, click CANCEL</b>",
                    QtWidgets.QMessageBox.Yes
                    | QtWidgets.QMessageBox.No
                    | QtWidgets.QMessageBox.Cancel)
                if reply == QtWidgets.QMessageBox.Cancel:
                    return
                if reply == QtWidgets.QMessageBox.Yes:
                    code = open(self.verilogfile).read()
                    text = code
                    filename = '.'.join(
                        self.verilogfile.split('.')[:-1]) + ".tlv"
                    file = os.path.basename('.'.join(
                        self.verilogfile.split('.')[:-1]))
                    f = open(filename, 'w')
                    flag = 1  # noqa F841
                    ports = ""  # noqa F841
                    code = code.replace(" wire ", " ")
                    code = code.replace(" reg ", " ")
                    vlog_ex = vlog.VerilogExtractor()
                    vlog_mods = vlog_ex.extract_objects_from_source(code)
                    lint_off = open("../maker/lint_off.txt").readlines()
                    string = '''\\TLV_version 1d: tl-x.org\n\\SV\n'''
                    for item in lint_off:
                        string += "/* verilator lint_off " + \
                            item.strip("\n") + "*/  "
                    string += '''\n\n//Your Verilog/System \
Verilog Code Starts Here:\n''' + \
                        text + '''\n\n//Top Module Code \
Starts here:\n\tmodule top(input \
logic clk, input logic reset, input logic [31:0] cyc_cnt, \
output logic passed, output logic failed);\n'''
                    print(file)
                    for m in vlog_mods:
                        if m.name.lower() == file.lower():
                            for p in m.ports:
                                if str(
                                        p.name) != "clk" and str(
                                        p.name) != "reset" and str(
                                        p.name) != "cyc_cnt" and str(
                                        p.name) != "passed" and str(
                                        p.name) != "failed":
                                    string += '\t\tlogic ' + p.data_type\
                                     + " " + p.name + ";//" + p.mode + "\n"
                    if m.name.lower() != file.lower():
                        QtWidgets.QMessageBox.critical(
                            None,
                            "Error Message",
                            "<b>Error: File name and module \
                            name are not same. Please \
                            ensure that they are same</b>",
                            QtWidgets.QMessageBox.Ok)

                        self.obj_Appconfig.print_info(
                            'NgVeri Stopped due to File \
name and module name not matching error')
                        return
                    string += "//The $random() can be replaced \
if user wants to assign values\n"
                    for m in vlog_mods:
                        if m.name.lower() == file.lower():
                            for p in m.ports:
                                if str(
                                        p.mode) == "input" or str(
                                        p.mode) == "inout":
                                    if str(
                                            p.name) != "clk" and str(
                                            p.name) != "reset" and str(
                                            p.name) != "cyc_cnt" and str(
                                            p.name) != "passed" and str(
                                            p.name) != "failed":
                                        string += '\t\tassign ' + p.name\
                                         + " = " + "$random();\n"

                    for m in vlog_mods:
                        if m.name.lower() == file.lower():
                            string += '\t\t' + m.name + " " + m.name + '('
                            i = 0
                            for p in m.ports:
                                i = i + 1
                                string += "."+p.name+"("+p.name+")"
                                if i == len(m.ports):
                                    string += ");\n\t\n\\TLV\n//\
Add \\TLV here if desired\
                                     \n\\SV\nendmodule\n\n"
                                else:
                                    string += ", "
                    f.write(string)

            self.process = QtCore.QProcess(self)
            cmd = 'makerchip ' + filename
            print("File: " + filename)
            self.process.start(cmd)
            print(
                "Makerchip command process pid ---------- >",
                self.process.pid())
        except BaseException as e:
            print(e)
            self.msg = QtWidgets.QErrorMessage(self)
            self.msg.setModal(True)
            self.msg.setWindowTitle("Error Message")
            self.msg.showMessage(
                "Error in running Makerchip. \
Please check if Verilog File Chosen.")
            self.msg.exec_()
            print("Error in running Makerchip. \
Please check if Verilog File Chosen.")
        #   initial = self.read_file()

        # while True:
        #     current = self.read_file()
        #     if initial != current:
        #         for line in current:
        #             if line not in initial:
        #                 print(line)
        #         initial = current
        # self.processfile = QtCore.QProcess(self)
        # self.processfile.start("python3 notify.py")
        # print(self.processfile.readChannel())

    # This creates the buttons/options

    def createoptionsBox(self):

        self.optionsbox = QtWidgets.QGroupBox()
        self.optionsbox.setTitle("Select Options")
        self.optionsgrid = QtWidgets.QGridLayout()
        # self.optionsbox2 = QtWidgets.QGroupBox()
        # self.optionsbox2.setTitle("Note: Please save the file once edited")
        # self.optionsgrid2 = QtWidgets.QGridLayout()
        self.optionsgroupbtn = QtWidgets.QButtonGroup()
        self.addoptions = QtWidgets.QPushButton("Add Top Level Verilog file")
        self.optionsgroupbtn.addButton(self.addoptions)
        self.addoptions.clicked.connect(self.addverilog)
        self.optionsgrid.addWidget(self.addoptions, 0, 1)
        # self.optionsbox.setLayout(self.optionsgrid)
        # self.grid.addWidget(self.creategroup(), 1, 0, 5, 0
        self.refreshoption = QtWidgets.QPushButton("Refresh")
        self.optionsgroupbtn.addButton(self.refreshoption)
        self.refreshoption.clicked.connect(self.refresh)
        self.optionsgrid.addWidget(self.refreshoption, 0, 2)
        # self.optionsbox.setLayout(self.optionsgrid)
        # self.grid.addWidget(self.creategroup(), 1, 0, 5, 0)
        self.saveoption = QtWidgets.QPushButton("Save")
        self.optionsgroupbtn.addButton(self.saveoption)
        self.saveoption.clicked.connect(self.save)
        self.optionsgrid.addWidget(self.saveoption, 0, 3)
        # self.optionsbox.setLayout(self.optionsgrid)
        # self.grid.addWidget(self.creategroup(), 1, 0, 5, 0)
        self.runoptions = QtWidgets.QPushButton("Edit in Makerchip")
        self.optionsgroupbtn.addButton(self.runoptions)
        self.runoptions.clicked.connect(self.runmakerchip)
        self.optionsgrid.addWidget(self.runoptions, 0, 4)
        # self.optionsbox.setLayout(self.optionsgrid)
        # self.grid.addWidget(self.creategroup(), 1, 0, 5, 0)
        if not os.path.isfile(home + "/.makerchip_accepted"):
            self.acceptTOS = QtWidgets.QPushButton("Accept Makerchip TOS")
            self.optionsgroupbtn.addButton(self.acceptTOS)
            self.acceptTOS.clicked.connect(self.makerchipaccepted)
            self.optionsgrid.addWidget(self.acceptTOS, 0, 5)
            # self.optionsbox.setLayout(self.optionsgrid)
            # self.grid.addWidget(self.creategroup(), 1, 0, 5, 0)
        self.optionsbox.setLayout(self.optionsgrid)
        return self.optionsbox

    # This function is called to accept TOS of makerchip

    def makerchipaccepted(self):
        reply = QtWidgets.QMessageBox.warning(
            None, "Terms of Services", "Please review the makerchip\
                         Terms of Service \
                         (<a href='https://www.makerchip.com/terms/'>\
                         https://www.makerchip.com/terms/</a> ).\
                          Have you read and do you \
                          accept these Terms of Service? [y/N]:",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            f = open(home + "/.makerchip_accepted", "w")
            f.close()
        # else:
        #    return

    # This function adds the other parts of widget like text box

    def creategroup(self):

        self.trbox = QtWidgets.QGroupBox()
        self.trbox.setTitle(".tlv file")
        # self.trbox.setDisabled(True)
        # self.trbox.setVisible(False)
        self.trgrid = QtWidgets.QGridLayout()
        self.trbox.setLayout(self.trgrid)

        self.start = QtWidgets.QLabel("Path to .tlv file")
        self.trgrid.addWidget(self.start, 1, 0)
        self.count = 0
        self.entry_var[self.count] = QtWidgets.QLabel(" - ")
        self.trgrid.addWidget(self.entry_var[self.count], 1, 1)
        self.entry_var[self.count].setMaximumWidth(1000)
        self.count += 1

        # CSS
        self.trbox.setStyleSheet(" \
        QGroupBox { border: 1px solid gray; border-radius: \
        9px; margin-top: 0.5em; } \
        QGroupBox::title { subcontrol-origin: margin; left: \
         10px; padding: 0 3px 0 3px; } \
        ")

        self.start = QtWidgets.QLabel(".tlv code")
        # self.start2 = QtWidgets.QLabel("Note: \
        # Please save the file once edited")
        # self.start2.setStyleSheet("background-color: red")
        self.trgrid.addWidget(self.start, 2, 0)
        # self.trgrid.addWidget(self.start2, 3,0)
        self.entry_var[self.count] = QtWidgets.QTextEdit()
        self.trgrid.addWidget(self.entry_var[self.count], 2, 1)
        self.entry_var[self.count].setMaximumWidth(1000)
        self.entry_var[self.count].setMaximumHeight(1000)
        # self.entry_var[self.count].textChanged.connect(self.save)
        self.count += 1

        # CSS
        self.trbox.setStyleSheet(" \
        QGroupBox { border: 1px solid gray; border-radius: \
        9px; margin-top: 0.5em; } \
        QGroupBox::title { subcontrol-origin: margin; left: \
         10px; padding: 0 3px 0 3px; } \
        ")

        return self.trbox


# The Handler class is used to create a watch on the files using WatchDog
class Handler(watchdog.events.PatternMatchingEventHandler):
    # this function initialisses the variable and the objects of watchdog
    def __init__(self, verilogfile, refreshoption, observer):
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(
            self, ignore_directories=True, case_sensitive=False)
        self.verilogfile = verilogfile
        self.refreshoption = refreshoption
        self.obj_Appconfig = Appconfig()
        self.observer = observer
        self.toggle = toggle(self.refreshoption)

    # if a file is modified, toggle starts to toggle the refresh button
    def on_modified(self, event):
        print("Watchdog received modified event - % s." % event.src_path)
        msg = QtWidgets.QErrorMessage()
        msg.setWindowTitle("eSim Message")
        msg.showMessage(
            "NgVeri File: " +
            self.verilogfile +
            " modified. Please click on Refresh")
        msg.exec_()
        print("NgVeri File: " + self.verilogfile +
              " modified. Please click on Refresh")
        # self.obj_Appconfig.print_info("NgVeri File:\
        # "+self.verilogfile+" modified. Please click on Refresh")
        global toggle_flag
        if not(self.refreshoption in toggle_flag):
            toggle_flag.append(self.refreshoption)
        # i.rm_watch()
        self.observer.stop()
        self.toggle.start()


# class notify(QThread):
#     def __init__(self,verilogfile,refreshoption):#,obj_Appconfig):
#         QThread.__init__(self)
#         self.verilogfile=verilogfile
#         self.refreshoption=refreshoption
#         self.obj_Appconfig = Appconfig()
#         self.toggle=toggle(self.refreshoption)


#     def __del__(self):
#         self.wait()

#     def run(self):
#         i = inotify.adapters.Inotify()

#         i.add_watch(self.verilogfile)

#         for event in i.event_gen():
#             if not self.refreshoption.isVisible():
#                 break
#             if event!=None:
#                 print(event)
#                 if "IN_CLOSE_WRITE" in event[1] :
#                         msg = QtWidgets.QErrorMessage()
#                         msg.setModal(True)
#                         msg.setWindowTitle("eSim Message")
#                         msg.showMessage(
#                             "NgVeri File: "+self.verilogfile+"\
# modified. Please click on Refresh")
#                         msg.exec_()
#                         print("NgVeri File: "+self.verilogfile+"\
# modified. Please click on Refresh")
#                         # self.obj_Appconfig.print_info("NgVeri File: \
# "+self.verilogfile+" modified. Please click on Refresh")
#                         global toggle_flag
#                         toggle_flag.append(self.refreshoption)
#                         #i.rm_watch()
#                         self.toggle.start()
#                         break


# This class is used to toggle a button(change colour by toggling)
class toggle(QThread):
    # initialising the threads
    def __init__(self, option):
        QThread.__init__(self)
        self.option = option

    def __del__(self):
        self.wait()

    # running the thread to toggle
    def run(self):

        while True:
            self.option.setStyleSheet("background-color: red")
            self.sleep(1)
            self.option.setStyleSheet("background-color: none")
            self.sleep(1)
            print(toggle_flag)
            if not self.option.isVisible():
                break
            if self.option not in toggle_flag:
                break

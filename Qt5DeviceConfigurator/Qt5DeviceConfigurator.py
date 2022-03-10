#!/usr/bin/env python3
# version 0.8.2
import os
############## SETTINGS ##############

### where the scripts and desktop files will be saved
BASH_PATH = os.path.expanduser('~')
# AUTOSTART_PATH = os.path.expanduser('~')+"/.config/autostart"
AUTOSTART_PATH = BASH_PATH
### the default width of various dialogs
DIALOGWIDTH = 400
### external program for the monitor settings
MONITOR_PROG = "arandr"

############ END SETTINGS ############

from PyQt5.QtCore import (Qt,QMargins)
from PyQt5.QtWidgets import (QSlider,QLayout,QSizePolicy,qApp,QBoxLayout,QLabel,QPushButton,QDesktopWidget,QApplication,QDialog,QGridLayout,QMessageBox,QTabWidget,QWidget,QComboBox,QCheckBox)
from PyQt5.QtGui import QIcon
import sys
import shutil
import subprocess
import stat
import lxml.etree


if not shutil.which(MONITOR_PROG):
    MONITOR_PROG = ""


class firstMessage(QWidget):
    
    def __init__(self, *args):
        super().__init__()
        title = args[0]
        message = args[1]
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("icons/program.png"))
        box = QBoxLayout(QBoxLayout.TopToBottom)
        box.setContentsMargins(5,5,5,5)
        self.setLayout(box)
        label = QLabel(message)
        box.addWidget(label)
        button = QPushButton("Close")
        box.addWidget(button)
        button.clicked.connect(self.close)
        self.show()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


# check for xinput
XINPUT_EXIST = 0
if shutil.which("xinput"):
    XINPUT_EXIST = 1

# check for xset
XSET_EXIST = 0
if shutil.which("xset"):
    XSET_EXIST = 1

# check for setxkbmap
SETXKBMAP_EXIST = 0
if shutil.which("setxkbmap"):
    SETXKBMAP_EXIST = 1

PROG_MISSED = "Missed:"
if not XSET_EXIST:
    PROG_MISSED += " xset"
if not XINPUT_EXIST:
    PROG_MISSED += " xinput"
if not SETXKBMAP_EXIST:
    PROG_MISSED += " setxkbmap"

if PROG_MISSED != "Missed:":
    app = QApplication(sys.argv)
    fm = firstMessage("Info", "xinput, xset and setxkbmap are required.\n{}".format(PROG_MISSED))
    sys.exit(app.exec_())

WINW = 600
WINH = 100

# simple dialog message
# type - message - parent
class MyDialog(QMessageBox):
    def __init__(self, *args):
        super(MyDialog, self).__init__(args[-1])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Information)
            self.setStandardButtons(QMessageBox.Ok)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Critical)
            self.setStandardButtons(QMessageBox.Ok)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Question)
            self.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        self.setWindowIcon(QIcon("icons/program.png"))
        self.setWindowTitle(args[0])
        self.resize(DIALOGWIDTH,300)
        self.setText(args[1])
        retval = self.exec_()
    
    # def event(self, e):
        # result = QMessageBox.event(self, e)
        # #
        # self.setMinimumHeight(0)
        # self.setMaximumHeight(16777215)
        # self.setMinimumWidth(0)
        # self.setMaximumWidth(16777215)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # # 
        # return result


########################### MAIN WINDOW ############################
# 1
class MainWin(QWidget):
    
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        #
        self.setWindowIcon(QIcon("icons/program.png"))
        #
        self.resize(int(WINW), int(WINH))
        #
        self.setWindowTitle("Device Configurator")
        #
        ###### main box
        self.vbox = QBoxLayout(QBoxLayout.TopToBottom)
        self.vbox.setContentsMargins(QMargins(2,2,2,2))
        self.setLayout(self.vbox)
        #
        self.mtab = QTabWidget()
        self.mtab.setContentsMargins(QMargins(0,0,0,0))
        self.mtab.setMovable(False)
        self.mtab.setTabsClosable(False)
        self.vbox.addWidget(self.mtab)
        ### button box
        self.obox1 = QBoxLayout(QBoxLayout.LeftToRight)
        self.obox1.setContentsMargins(QMargins(0,0,0,0))
        self.vbox.addLayout(self.obox1)
        #
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        self.obox1.addWidget(close_btn)
        ######## TAB 1 MOUSE
        # starting values
        self.start_speed_val = 100
        self.start_clickFast_val = 0
        self.start_lh_ckb_value = 0
        # setted values
        self.speed_val = 0.0
        self.clickFast_val = 0
        self.lh_ckb_value = 0
        #
        page1 = QWidget()
        self.mtab.addTab(page1, "Mouse")
        self.grid1 = QGridLayout()
        self.grid1.setColumnStretch(1,3)
        page1.setLayout(self.grid1)
        # mice list
        self.mcombo = QComboBox()
        self.mcombo.activated.connect(self.on_mcombo)
        self.grid1.addWidget(self.mcombo, 0, 0, 1, 10, Qt.AlignLeft)
        self.pop_mcombo()
        # disable this tab if no mice
        if self.mcombo.count() == 0:
            page1.setEnabled(False)
        # 
        label_speed = QLabel("Speed:")
        label_speed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.grid1.addWidget(label_speed, 1, 0, 1, 10, Qt.AlignLeft)
        # label for speed indicator
        self.label_slider_moveFast = QLabel()
        self.grid1.addWidget(self.label_slider_moveFast, 2, 0, 1, 10, Qt.AlignCenter)
        # decrease speed
        label_slow = QPushButton("slow")
        label_slow.clicked.connect(self.on_label_slow_speed)
        label_slow.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.grid1.addWidget(label_slow, 3, 0, Qt.AlignRight)
        # slider visual indicator
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.slider_speed.setMinimum(0)
        self.slider_speed.setMaximum(200)
        self.slider_speed.setSliderPosition(0)
        self.slider_speed.setPageStep(5)
        self.slider_speed.setSingleStep(5)
        self.grid1.addWidget(self.slider_speed, 3, 1, 1, 8, Qt.AlignCenter)
        self.slider_speed.setEnabled(False)
        # increase the speed
        label_fast = QPushButton("fast")
        label_fast.clicked.connect(self.on_label_fast_speed)
        label_fast.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.grid1.addWidget(label_fast, 3, 10, Qt.AlignLeft)
        ## double click
        label_doubleClick = QLabel("Double Click Speed:")
        label_doubleClick.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.grid1.addWidget(label_doubleClick, 4, 0, 1, 8, Qt.AlignLeft)
        label_doubleClick.setEnabled(False)
        # help button
        hlp_btn = QPushButton("Help")
        hlp_btn.clicked.connect(self.on_hlp_btn)
        self.grid1.addWidget(hlp_btn, 4, 9, 1, 2, Qt.AlignCenter)
        # disabled
        self.label_slider_clickFast = QLabel("0")
        self.grid1.addWidget(self.label_slider_clickFast, 5, 0, 1, 10, Qt.AlignCenter)
        self.label_slider_clickFast.setEnabled(False)
        # disabled
        label_clickSlow = QPushButton("slow")
        label_clickSlow.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.grid1.addWidget(label_clickSlow, 6, 0, Qt.AlignRight)
        label_clickSlow.setEnabled(False)
        self.slider_clickFast = QSlider(Qt.Orientation.Horizontal)
        self.slider_clickFast.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.slider_clickFast.setMinimum(0)
        self.slider_clickFast.setMaximum(1000)
        self.slider_clickFast.setSliderPosition(0.0)
        self.slider_clickFast.setPageStep(25)
        self.slider_clickFast.setSingleStep(25)
        self.grid1.addWidget(self.slider_clickFast, 6, 1, 1, 8, Qt.AlignCenter)
        self.slider_clickFast.setEnabled(False)
        # disabled
        label_clickFast = QPushButton("fast")
        label_clickFast.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.grid1.addWidget(label_clickFast, 6, 10, Qt.AlignLeft)
        label_clickFast.setEnabled(False)
        ## left handed checkbox
        self.lh_ckb = QCheckBox("Left Handed")
        # 
        self.lh_ckb.setChecked(0)
        self.grid1.addWidget(self.lh_ckb, 7 , 0, 1, 10, Qt.AlignLeft)
        ##
        test_btn_1 = QPushButton("Test")
        test_btn_1.clicked.connect(self.on_test_btn_1)
        self.grid1.addWidget(test_btn_1, 9, 0, 1, 4, Qt.AlignLeft)
        #
        reset_btn_1 = QPushButton("Reset")
        reset_btn_1.clicked.connect(self.on_reset_btn_1)
        self.grid1.addWidget(reset_btn_1, 9, 5, 1, 2, Qt.AlignCenter)
        #
        self.apply_btn_1 = QPushButton("Apply")
        self.apply_btn_1.clicked.connect(self.on_apply_btn1)
        self.grid1.addWidget(self.apply_btn_1, 9, 7, 1, 4, Qt.AlignLeft)
        # a mouse has been found
        if self.mcombo.currentText():
            self.on_start_mouse(self.mcombo.currentText())
        else:
            page1.setEnabled(False)
        ######### TAB 2 KEYBOARD
        # starting values
        self.start_rip_val = 0
        self.start_int_val = 0
        self.start_rip_ckb_value = 0
        self.start_kb_model = ""
        self.start_kb_layout = ""
        self.start_kb_variant = ""
        # setted values
        self.rip_val = 0
        self.int_val = 0
        self.rip_ckb_value = 0
        self.kb_model = ""
        self.kb_layout = ""
        self.kb_variant = ""
        #
        page2 = QWidget()
        self.mtab.addTab(page2, "Keyboard")
        self.grid2 = QGridLayout()
        page2.setLayout(self.grid2)
        ## 1
        label_ripChars = QLabel("Repeat Delay:")
        self.grid2.addWidget(label_ripChars, 0, 0, 1, 11, Qt.AlignLeft)
        # label for value
        self.label_wait_rip = QLabel()
        self.grid2.addWidget(self.label_wait_rip, 1, 0, 1, 11, Qt.AlignCenter)
        #
        label_waiting_s = QPushButton("Short")
        label_waiting_s.clicked.connect(self.on_label_waiting_s)
        self.grid2.addWidget(label_waiting_s, 2, 0, Qt.AlignRight)
        #
        self.slider_rip = QSlider(Qt.Orientation.Horizontal)
        self.slider_rip.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.slider_rip.setMinimum(0)
        self.slider_rip.setMaximum(1500)
        self.slider_rip.setPageStep(10)
        self.slider_rip.setSingleStep(10)
        self.slider_rip.setSliderPosition(0)
        self.grid2.addWidget(self.slider_rip, 2, 1, 1, 8, Qt.AlignCenter)
        self.slider_rip.setEnabled(False)
        # 
        label_waiting_l = QPushButton("Long")
        label_waiting_l.clicked.connect(self.on_label_waiting_l)
        self.grid2.addWidget(label_waiting_l, 2, 10, Qt.AlignLeft)
        ## 2
        label_intChars = QLabel("Repeat Interval:")
        self.grid2.addWidget(label_intChars, 3, 0, 1, 11, Qt.AlignLeft)
        # label for value
        self.label_int = QLabel()
        self.grid2.addWidget(self.label_int, 4, 0, 1, 11, Qt.AlignCenter)
        #
        label_int_s = QPushButton("Short")
        label_int_s.clicked.connect(self.on_label_int_s)
        self.grid2.addWidget(label_int_s, 5, 0, Qt.AlignRight)
        #
        self.slider_int = QSlider(Qt.Orientation.Horizontal)
        self.slider_int.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.slider_int.setMinimum(0)
        self.slider_int.setMaximum(100)
        self.slider_int.setPageStep(5)
        self.slider_int.setSingleStep(5)
        self.slider_int.setSliderPosition(0)
        self.grid2.addWidget(self.slider_int, 5, 1, 1, 8, Qt.AlignCenter)
        self.slider_int.setEnabled(False)
        # 
        label_int_l = QPushButton("Long")
        label_int_l.clicked.connect(self.on_label_int_l)
        self.grid2.addWidget(label_int_l, 5, 10, Qt.AlignLeft)
        #
        ## 3 - checkbox
        self.rip_ckb = QCheckBox("Beep when there is an error of keyboard input")
        # 
        self.rip_ckb.setChecked(0)
        self.grid2.addWidget(self.rip_ckb, 6, 0, 1, 11, Qt.AlignLeft)
        ## 
        label_kb_model_1 = QLabel("Model :")
        self.grid2.addWidget(label_kb_model_1, 7, 0, 1, 2, Qt.AlignLeft)
        self.label_kb_model = QLabel("")
        self.grid2.addWidget(self.label_kb_model, 7, 2, 1, 2, Qt.AlignLeft)
        label_kb_layout_1 = QLabel("Layout :")
        self.grid2.addWidget(label_kb_layout_1, 8, 0, 1, 2, Qt.AlignLeft)
        self.label_kb_layout = QLabel("")
        self.grid2.addWidget(self.label_kb_layout, 8, 2, 1, 2, Qt.AlignLeft)
        label_kb_variant_1 = QLabel("Variant: ")
        self.grid2.addWidget(label_kb_variant_1, 9, 0, 1, 2, Qt.AlignLeft)
        self.label_kb_variant = QLabel("")
        self.grid2.addWidget(self.label_kb_variant, 9, 2, 1, 2, Qt.AlignLeft)
        ##
        self.keyb_btn = QPushButton("Keyboard Configuration...")
        self.keyb_btn.clicked.connect(self.on_keyb_btn)
        self.grid2.addWidget(self.keyb_btn, 10, 0, 1, 8, Qt.AlignLeft)
        ##
        test_btn_2 = QPushButton("Test")
        test_btn_2.clicked.connect(self.on_test_btn_2)
        self.grid2.addWidget(test_btn_2, 11, 0, 1, 4, Qt.AlignLeft)
        #
        reset_btn_2 = QPushButton("Reset")
        reset_btn_2.clicked.connect(self.on_reset_btn_2)
        self.grid2.addWidget(reset_btn_2, 11, 5, 1, 2, Qt.AlignCenter)
        #
        self.apply_btn_2 = QPushButton("Apply")
        self.apply_btn_2.clicked.connect(self.on_apply_btn2)
        self.grid2.addWidget(self.apply_btn_2, 11, 8, 1, 4, Qt.AlignLeft)
        #
        self.on_start_keyboard()
        ############## TAB 3 MONITOR
        # starting values
        self.start_standby_val = 0
        self.start_suspend_val = 0
        self.start_off_val = 0
        self.start_stimeout_val = 0
        self.start_scycle_val = 0
        # setted values
        self.standby_val = 0
        self.suspend_val = 0
        self.off_val = 0
        self.stimeout_val = 0
        self.scycle_val = 0
        #
        page3 = QWidget()
        self.mtab.addTab(page3, "Monitor")
        self.grid3 = QGridLayout()
        page3.setLayout(self.grid3)
        #
        # program to setting the monitor
        if MONITOR_PROG:
            monitor_btn = QPushButton("Monitor Settings...")
            monitor_btn.setToolTip("{} will be executed.".format(os.path.basename(MONITOR_PROG)))
            monitor_btn.clicked.connect(self.on_monitor_btn)
            self.grid3.addWidget(monitor_btn, 0, 0, 1, 4, Qt.AlignLeft)
        else:
            monitor_lbl = QLabel("Application {} not found.".format(MONITOR_PROG))
            self.grid3.addWidget(monitor_lbl, 0, 0, 1, 4, Qt.AlignLeft)
        ## screensaver off/on
        self.screensaver_on_off_btn = QPushButton("Scrsvr On/Off")
        self.screensaver_on_off_btn.setToolTip("Set the screensaver off/on.\nApply is not needed.")
        self.screensaver_on_off_btn.clicked.connect(self.on_screensaver_on_off)
        self.grid3.addWidget(self.screensaver_on_off_btn, 0, 9, 1, 2, Qt.AlignLeft)
        ## standby
        standby_label = QLabel("Standby:")
        self.grid3.addWidget(standby_label, 1, 0, Qt.AlignLeft)
        # value
        self.standby_lbl = QLabel()
        self.grid3.addWidget(self.standby_lbl, 1, 1, 1, 9, Qt.AlignCenter)
        #
        self.standby_min = QPushButton("Less")
        self.standby_min.clicked.connect(self.on_standby_min)
        self.grid3.addWidget(self.standby_min, 2, 0, 1, 1, Qt.AlignLeft)
        #
        self.standby_slider = QSlider(Qt.Orientation.Horizontal)
        self.standby_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.standby_slider.setMinimum(0)
        self.standby_slider.setMaximum(1200) # 10 minutes max
        self.standby_slider.setPageStep(30)
        self.standby_slider.setSingleStep(30)
        self.standby_slider.setSliderPosition(0)
        self.grid3.addWidget(self.standby_slider, 2, 1, 1, 8, Qt.AlignCenter)
        self.standby_slider.setEnabled(False)
        #
        self.standby_max = QPushButton("More")
        self.standby_max.clicked.connect(self.on_standby_max)
        self.grid3.addWidget(self.standby_max, 2, 10, 1, 1, Qt.AlignLeft)
        #
        ## suspend
        suspend_label = QLabel("Suspend:")
        self.grid3.addWidget(suspend_label, 3, 0, Qt.AlignLeft)
        # value
        self.suspend_lbl = QLabel()
        self.grid3.addWidget(self.suspend_lbl, 3, 1, 1, 9, Qt.AlignCenter)
        #
        self.suspend_min = QPushButton("Less")
        self.suspend_min.clicked.connect(self.on_suspend_min)
        self.grid3.addWidget(self.suspend_min, 4, 0, 1, 1, Qt.AlignLeft)
        #
        self.suspend_slider = QSlider(Qt.Orientation.Horizontal)
        self.suspend_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.suspend_slider.setMinimum(0)
        self.suspend_slider.setMaximum(1200) # 10 minutes max
        self.suspend_slider.setPageStep(30)
        self.suspend_slider.setSingleStep(30)
        self.suspend_slider.setSliderPosition(0)
        self.grid3.addWidget(self.suspend_slider, 4, 1, 1, 8, Qt.AlignCenter)
        self.suspend_slider.setEnabled(False)
        #
        self.suspend_max = QPushButton("More")
        self.suspend_max.clicked.connect(self.on_suspend_max)
        self.grid3.addWidget(self.suspend_max, 4, 10, 1, 1, Qt.AlignLeft)
        #
        ## monitor off
        moff_label = QLabel("Monitor off:")
        self.grid3.addWidget(moff_label, 5, 0, Qt.AlignLeft)
        # value
        self.moff_lbl = QLabel()
        self.grid3.addWidget(self.moff_lbl, 5, 1, 1, 9, Qt.AlignCenter)
        #
        self.moff_min = QPushButton("Less")
        self.moff_min.clicked.connect(self.on_moff_min)
        self.grid3.addWidget(self.moff_min, 6, 0, 1, 1, Qt.AlignLeft)
        #
        self.moff_slider = QSlider(Qt.Orientation.Horizontal)
        self.moff_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.moff_slider.setMinimum(0)
        self.moff_slider.setMaximum(1200) # 10 minutes max
        self.moff_slider.setPageStep(30)
        self.moff_slider.setSingleStep(30)
        self.moff_slider.setSliderPosition(0)
        self.grid3.addWidget(self.moff_slider, 6, 1, 1, 8, Qt.AlignCenter)
        self.moff_slider.setEnabled(False)
        #
        self.moff_max = QPushButton("More")
        self.moff_max.clicked.connect(self.on_moff_max)
        self.grid3.addWidget(self.moff_max, 6, 10, 1, 1, Qt.AlignLeft)
        # 
        ## screensaver timeout
        stimeout_label = QLabel("Screensaver timeout:")
        self.grid3.addWidget(stimeout_label, 7, 0, Qt.AlignLeft)
        # value
        self.stimeout_lbl = QLabel()
        self.grid3.addWidget(self.stimeout_lbl, 7, 1, 1, 9, Qt.AlignCenter)
        #
        self.stimeout_min = QPushButton("Less")
        self.stimeout_min.clicked.connect(self.on_stimeout_min)
        self.grid3.addWidget(self.stimeout_min, 8, 0, 1, 1, Qt.AlignLeft)
        #
        self.stimeout_slider = QSlider(Qt.Orientation.Horizontal)
        self.stimeout_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.stimeout_slider.setMinimum(0)
        self.stimeout_slider.setMaximum(1200) # 10 minutes max
        self.stimeout_slider.setPageStep(30)
        self.stimeout_slider.setSingleStep(30)
        self.stimeout_slider.setSliderPosition(0)
        self.grid3.addWidget(self.stimeout_slider, 8, 1, 1, 8, Qt.AlignCenter)
        self.stimeout_slider.setEnabled(False)
        #
        self.stimeout_max = QPushButton("More")
        self.stimeout_max.clicked.connect(self.on_stimeout_max)
        self.grid3.addWidget(self.stimeout_max, 8, 10, 1, 1, Qt.AlignLeft)
        #
        ## screensaver cycle
        scycle_label = QLabel("Screensaver cycle:")
        self.grid3.addWidget(scycle_label, 9, 0, Qt.AlignLeft)
        # value
        self.scycle_lbl = QLabel()
        self.grid3.addWidget(self.scycle_lbl, 9, 1, 1, 9, Qt.AlignCenter)
        #
        self.scycle_min = QPushButton("Less")
        self.scycle_min.clicked.connect(self.on_scycle_min)
        self.grid3.addWidget(self.scycle_min, 10, 0, 1, 1, Qt.AlignLeft)
        #
        self.scycle_slider = QSlider(Qt.Orientation.Horizontal)
        self.scycle_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.scycle_slider.setMinimum(0)
        self.scycle_slider.setMaximum(1200) # 10 minutes max
        self.scycle_slider.setPageStep(30)
        self.scycle_slider.setSingleStep(30)
        self.scycle_slider.setSliderPosition(0)
        self.grid3.addWidget(self.scycle_slider, 10, 1, 1, 8, Qt.AlignCenter)
        self.scycle_slider.setEnabled(False)
        #
        self.scycle_max = QPushButton("More")
        self.scycle_max.clicked.connect(self.on_scycle_max)
        self.grid3.addWidget(self.scycle_max, 10, 10, 1, 1, Qt.AlignLeft)
        ##
        test_btn_3 = QPushButton("Test")
        test_btn_3.clicked.connect(self.on_test_btn_3)
        self.grid3.addWidget(test_btn_3, 11, 0, 1, 4, Qt.AlignLeft)
        #
        reset_btn_3 = QPushButton("Reset")
        reset_btn_3.clicked.connect(self.on_reset_btn_3)
        self.grid3.addWidget(reset_btn_3, 11, 5, 1, 2, Qt.AlignCenter)
        #
        self.apply_btn_3 = QPushButton("Apply")
        self.apply_btn_3.clicked.connect(self.on_apply_btn3)
        self.grid3.addWidget(self.apply_btn_3, 11, 8, 1, 4, Qt.AlignLeft)
        #
        self.on_start_monitor()
        
        

########### MONITOR #############
    
    def on_start_monitor(self):
        try:
            cmd = "xset q | grep 'Standby'"
            ret = subprocess.check_output(cmd, shell=True)
            ret_temp = ret.decode()
            list_value = [int(s) for s in ret_temp.split() if s.isdigit()]
            self.start_standby_val, self.start_suspend_val, self.start_off_val = list_value
            self.standby_val = self.start_standby_val
            self.standby_lbl.setText(str(self.start_standby_val))
            self.standby_slider.setSliderPosition(self.start_standby_val)
            self.suspend_val = self.start_suspend_val
            self.suspend_lbl.setText(str(self.start_suspend_val))
            self.suspend_slider.setSliderPosition(self.start_suspend_val)
            self.off_val = self.start_off_val
            self.moff_lbl.setText(str(self.start_off_val))
            self.moff_slider.setSliderPosition(self.start_off_val)
        except Exception as E:
            MyDialog("Error", str(E), self)
        try:
            cmd = "xset q | grep 'timeout'"
            ret = subprocess.check_output(cmd, shell=True)
            ret_temp = ret.decode()
            list_value = [int(s) for s in ret_temp.split() if s.isdigit()]
            self.start_stimeout_val, self.start_scycle_val = list_value
            self.stimeout_val = self.start_stimeout_val
            self.stimeout_lbl.setText(str(self.start_stimeout_val))
            self.stimeout_slider.setSliderPosition(self.start_stimeout_val)
            self.scycle_val = self.start_scycle_val
            self.scycle_lbl.setText(str(self.start_scycle_val))
            self.scycle_slider.setSliderPosition(self.start_scycle_val)
        except Exception as E:
            MyDialog("Error", str(E), self)
    
    # revert all the settings to the starting values
    def on_reset_btn_3(self):
        ret = retDialogBox("Question", "Revert all the changes?", self)
        if ret.getValue() == 0:
            return
        #
        try:
            if self.standby_val != self.start_standby_val \
            or self.suspend_val != self.start_suspend_val \
            or self.off_val != self.start_off_val:
                cmd = "xset dpms {} {} {}".format(int(self.start_standby_val), int(self.start_suspend_val), int(self.start_off_val))
                subprocess.Popen(cmd, shell=True)
            if int(self.standby_lbl.text()) != self.start_standby_val \
            or int(self.suspend_lbl.text()) != self.start_standby_val \
            or int(self.moff_lbl.text()) != self.start_off_val:
                self.standby_val = self.start_standby_val
                self.standby_slider.setSliderPosition(self.start_standby_val)
                self.standby_lbl.setText(str(self.start_standby_val))
                self.suspend_val = self.start_suspend_val
                self.suspend_slider.setSliderPosition(self.start_suspend_val)
                self.suspend_lbl.setText(str(self.start_suspend_val))
                self.off_val = self.start_off_val
                self.moff_slider.setSliderPosition(self.start_off_val)
                self.moff_lbl.setText(str(self.start_off_val))
        except Exception as E:
            MyDialog("Error", str(E), self)
        #
        try:
            if self.stimeout_val != self.start_stimeout_val \
            or self.scycle_val != self.start_scycle_val:
                cmd = "xset s {} {}".format(int(self.start_stimeout_val), int(self.start_scycle_val))
                subprocess.Popen(cmd, shell=True)
            if int(self.stimeout_lbl.text()) != self.start_stimeout_val \
            or int(self.scycle_lbl.text()) != self.start_scycle_val:
                self.stimeout_val = self.start_stimeout_val
                self.stimeout_slider.setSliderPosition(self.start_stimeout_val)
                self.stimeout_lbl.setText(str(self.start_stimeout_val))
                self.scycle_val = self.start_scycle_val
                self.scycle_slider.setSliderPosition(self.start_scycle_val)
                self.scycle_lbl.setText(str(self.start_scycle_val))
        except Exception as E:
            MyDialog("Error", str(E), self)
        
    #
    def on_apply_btn3(self):
        # save: 1 bash script - 2  autostart desktop file - 3 apply without making any scripts
        ret = chooseDialog(self, 1)
        if ret.getValue() == 0:
            return
        #
        commands_to_execute = []
        #
        if int(self.standby_lbl.text()) != self.start_standby_val \
        or int(self.standby_lbl.text()) != self.standby_val \
        or int(self.suspend_lbl.text()) != self.start_suspend_val \
        or int(self.suspend_lbl.text()) != self.suspend_val \
        or int(self.moff_lbl.text()) != self.start_off_val \
        or int(self.moff_lbl.text()) != self.off_val:
            suspend_val = min(int(self.suspend_lbl.text()), int(self.moff_lbl.text()))
            # resetted
            self.suspend_slider.setSliderPosition(suspend_val)
            self.suspend_lbl.setText(str(suspend_val))
            standby_val = min(int(self.standby_lbl.text()), int(self.suspend_lbl.text()))
            # resetted
            self.standby_slider.setSliderPosition(standby_val)
            self.standby_lbl.setText(str(standby_val))
            off_val = int(self.moff_lbl.text())
            str_dpms = "xset dpms {} {} {}".format(standby_val, suspend_val, off_val)
            commands_to_execute.append(str_dpms)
        #
        if int(self.stimeout_lbl.text()) != self.start_stimeout_val \
        or int(self.stimeout_lbl.text()) != self.stimeout_val \
        or int(self.scycle_lbl.text()) != self.start_scycle_val \
        or int(self.scycle_lbl.text()) != self.scycle_val:
            str_scr = "xset s {} {}".format(int(self.stimeout_lbl.text()), int(self.scycle_lbl.text()))
            commands_to_execute.append(str_scr)
        #
        if ret.getValue() == 1:
            try:
                bash_file = os.path.join(BASH_PATH, "monitor.sh")
                ff = open(bash_file, "w")
                ff.write("#!/bin/bash\n")
                for ccom in commands_to_execute:
                    ff.write(ccom+"\n")
                ff.close()
                st = os.stat(bash_file)
                os.chmod(bash_file, st.st_mode | stat.S_IEXEC)
            except Exception as E:
                MyDialog("Error", str(E), self)
        elif ret.getValue() == 2:
            try:
                desktop_file = os.path.join(AUTOSTART_PATH, "monitor.desktop")
                command_exec = ""
                for ccom in commands_to_execute:
                    command_exec += ccom+";"
                exec_command = 'sh -c "{}"'.format(command_exec)
                ff = open(desktop_file, "w")
                ff.write("[Desktop Entry]\nVersion=1.0\nType=Application\nName=Mouse Personal Settings\nNoDisplay=true\nExec={0}\n".format(exec_command))
                ff.close()
                st = os.stat(desktop_file)
                os.chmod(desktop_file, st.st_mode | stat.S_IEXEC)
            except Exception as E:
                MyDialog("Error", str(E), self)
        # apply the settings
        if ret.getValue() == 3:
            try:
                for ccom in commands_to_execute:
                    subprocess.Popen(ccom, shell=True)
                #
                self.standby_val = int(self.standby_lbl.text())
                self.suspend_val = int(self.suspend_lbl.text())
                self.off_val = int(self.moff_lbl.text())
                #
                self.stimeout_val = int(self.stimeout_lbl.text())
                self.scycle_val = int(self.scycle_lbl.text())
            except Exception as E:
                MyDialog("Error", str(E), self)
    
    #
    def on_standby_min(self):
        old_value = int(self.standby_lbl.text())
        if old_value > 0:
            self.standby_slider.setSliderPosition(old_value - 30)
            self.standby_lbl.setText(str(old_value - 30))
    
    def on_standby_max(self):
        old_value = int(self.standby_lbl.text())
        if old_value < 1200:
            self.standby_slider.setSliderPosition(old_value + 30)
            self.standby_lbl.setText(str(old_value + 30))
    
    #
    def on_suspend_min(self):
        old_value = int(self.suspend_lbl.text())
        if old_value > 0:
            self.suspend_slider.setSliderPosition(old_value - 30)
            self.suspend_lbl.setText(str(old_value - 30))
    
    def on_suspend_max(self):
        old_value = int(self.suspend_lbl.text())
        if old_value < 1200:
            self.suspend_slider.setSliderPosition(old_value + 30)
            self.suspend_lbl.setText(str(old_value + 30))
    
    #
    def on_moff_min(self):
        old_value = int(self.moff_lbl.text())
        if old_value > 0:
            self.moff_slider.setSliderPosition(old_value - 30)
            self.moff_lbl.setText(str(old_value - 30))
    
    def on_moff_max(self):
        old_value = int(self.moff_lbl.text())
        if old_value < 1200:
            self.moff_slider.setSliderPosition(old_value + 30)
            self.moff_lbl.setText(str(old_value + 30))
    
    #
    def on_stimeout_min(self):
        old_value = int(self.stimeout_lbl.text())
        if old_value > 0:
            self.stimeout_slider.setSliderPosition(old_value - 30)
            self.stimeout_lbl.setText(str(old_value - 30))
    
    def on_stimeout_max(self):
        old_value = int(self.stimeout_lbl.text())
        if old_value < 1200:
            self.stimeout_slider.setSliderPosition(old_value + 30)
            self.stimeout_lbl.setText(str(old_value + 30))
    
    #
    def on_scycle_min(self):
        old_value = int(self.scycle_lbl.text())
        if old_value > 0:
            self.scycle_slider.setSliderPosition(old_value - 30)
            self.scycle_lbl.setText(str(old_value - 30))
    
    def on_scycle_max(self):
        old_value = int(self.scycle_lbl.text())
        if old_value < 1200:
            self.scycle_slider.setSliderPosition(old_value + 30)
            self.scycle_lbl.setText(str(old_value + 30))
    
    def on_screensaver_on_off(self):
        cmd = "xset q | grep 'timeout'"
        ret = subprocess.check_output(cmd, shell=True)
        ret_temp = ret.decode()
        list_value = [int(s) for s in ret_temp.split() if s.isdigit()]
        stimeout_val, scycle_val = list_value
        if stimeout_val:
            cmd = "xset s off"
            subprocess.Popen(cmd, shell=True)
            self.stimeout_val = 0
            self.stimeout_slider.setSliderPosition(0)
            self.stimeout_lbl.setText(str(0))
        else:
            self.stimeout_slider.setSliderPosition(self.start_stimeout_val)
            self.stimeout_lbl.setText(str(self.start_stimeout_val))
            self.stimeout_val = self.start_stimeout_val
            cmd = "xset s {} {}".format(int(self.stimeout_val), int(self.scycle_val))
            subprocess.run(cmd, shell=True)
    
    #
    def on_test_btn_3(self):
        sb_val = "Cannot read this value"
        sp_val = "Cannot read this value"
        mo_val = "Cannot read this value"
        st_val = "Cannot read this value"
        sc_val = "Cannot read this value"
        try:
            cmd = "xset q | grep 'Standby'"
            ret = subprocess.check_output(cmd, shell=True)
            ret_temp = ret.decode()
            list_value = [int(s) for s in ret_temp.split() if s.isdigit()]
            sb_val, sp_val, mo_val = list_value
        except:
            pass
        try:
            cmd = "xset q | grep 'timeout'"
            ret = subprocess.check_output(cmd, shell=True)
            ret_temp = ret.decode()
            list_value = [int(s) for s in ret_temp.split() if s.isdigit()]
            st_val, sc_val = list_value
        except:
            pass
        msg = """The actual active 'monitor configuration' is:

Monitor:
Standby: {0}
Suspend: {1}
Power off: {2}

Screensaver:
Timeout: {3}
Cycle: {4}""".format(sb_val, sp_val, mo_val, st_val, sc_val)
        MyDialog("Info", msg, self)
        return
    
    # execute external program for setting the monitor
    def on_monitor_btn(self):
        try:
            subprocess.Popen([MONITOR_PROG], shell=True)
        except Exception as E:
            MyDialog("Error", str(E), self)

########### END MONITOR #############

########### KEYBOARD ###########
    
    # setting some values on starting - keyboard
    def on_start_keyboard(self):
        ### KEYBOARD
        ## key delay and interval
        try:
            cmd = "xset q | grep 'auto repeat delay'"
            ret = subprocess.check_output(cmd, shell=True)
            ret_temp = ret.decode()
            list_value = [int(s) for s in ret_temp.split() if s.isdigit()]
            self.start_rip_val, self.start_int_val = list_value
            self.rip_val = self.start_rip_val
            self.int_val = self.start_int_val
            self.label_wait_rip.setText(str(self.start_rip_val))
            self.slider_rip.setSliderPosition(self.start_rip_val)
            self.label_int.setText(str(self.start_int_val))
            self.slider_int.setSliderPosition(self.start_int_val)
        except:
            pass
        ## beep
        try:
            cmd = "xset q | grep 'bell percent'"
            ret = subprocess.check_output(cmd, shell=True)
            ret_temp = ret.decode()
            list_value = [int(s) for s in ret_temp.split() if s.isdigit()]
            self.start_rip_ckb_value = bool(list_value[0])
            self.rip_ckb_value = bool(list_value[0])
            self.rip_ckb.setChecked(bool(list_value[0]))
        except:
            pass
        #
        ## the model
        try:
            cmd = "setxkbmap -query | grep model | cut -d : -f 2"
            ret = subprocess.check_output(cmd, shell=True)
            if ret.decode():
                self.start_kb_model = ret.decode().lstrip(" ").strip("\n")
                self.kb_model = self.start_kb_model
                self.label_kb_model.setText(self.start_kb_model)
        except:
            pass
        ## the layout
        cmd = "setxkbmap -query | grep layout | cut -d : -f 2"
        try:
            ret = subprocess.check_output(cmd, shell=True)
            if ret.decode():
                self.start_kb_layout = ret.decode().lstrip(" ").strip("\n")
                self.kb_layout = self.start_kb_layout
                self.label_kb_layout.setText(self.start_kb_layout)
        except:
            pass
        ## the variant
        cmd = "setxkbmap -query | grep variant | cut -d : -f 2"
        try:
            ret = subprocess.check_output(cmd, shell=True)
            if ret.decode():
                self.start_kb_variant = ret.decode().lstrip(" ").strip("\n")
                self.kb_variant = self.start_kb_variant
                self.label_kb_variant.setText(self.start_kb_variant)
        except:
            pass
    
    # 
    def on_label_waiting_s(self):
        rip_value = int(self.label_wait_rip.text())
        if rip_value > 100:
            self.slider_rip.setSliderPosition(rip_value - 10)
            self.label_wait_rip.setText(str(rip_value - 10))
        
    def on_label_waiting_l(self):
        rip_value = int(self.label_wait_rip.text())
        if rip_value < 1500:
            self.slider_rip.setSliderPosition(rip_value + 10)
            self.label_wait_rip.setText(str(rip_value + 10))
        
    def on_label_int_s(self):
        rip_value = int(self.label_int.text())
        if rip_value > 10:
            self.slider_int.setSliderPosition(rip_value - 5)
            self.label_int.setText(str(rip_value - 5))
    
    def on_label_int_l(self):
        rip_value = int(self.label_int.text())
        if rip_value < 100:
            self.slider_int.setSliderPosition(rip_value + 5)
            self.label_int.setText(str(rip_value + 5))
    
    
    # change the keyboard model layout variant
    def on_keyb_btn(self):
        ret = keyboardDialog(self)
        if ret.getValue():
            kb_model, kb_layout, kb_variant = ret.getValue()
            self.label_kb_model.setText(kb_model)
            self.label_kb_layout.setText(kb_layout)
            self.label_kb_variant.setText(kb_variant)
    
    # revert all the settings to the starting values
    def on_reset_btn_2(self):
        ret = retDialogBox("Question", "Revert all the changes?", self)
        if ret.getValue() == 0:
            return
        # delay and rate
        try:
            if self.rip_val != self.start_rip_val \
            or self.int_val != self.start_int_val:
                cmd = "xset r rate {} {}".format(self.start_rip_val, self.start_int_val)
                subprocess.Popen(cmd, shell=True)
            #
            if int(self.label_wait_rip.text()) != self.start_rip_val \
            or int(self.label_int.text())  != self.start_int_val:
                self.rip_val = self.start_rip_val
                self.label_wait_rip.setText(str(self.start_rip_val))
                self.slider_rip.setSliderPosition(self.start_rip_val)
                self.int_val = self.start_int_val
                self.label_int.setText(str(self.start_int_val))
                self.slider_int.setSliderPosition(self.start_int_val)
        except Exception as E:
            MyDialog("Error", str(E), self)
        # beep
        if self.rip_ckb_value != self.start_rip_ckb_value:
            str_new_rip_ckb = "on"
            if self.start_rip_ckb_value == 0:
                str_new_rip_ckb = "off"
            cmd = "xset b {}".format(str_new_rip_ckb)
            try:
                subprocess.Popen(cmd, shell=True)
            except Exception as E:
                MyDialog("Error", str(E), self)
        #
        if self.rip_ckb.isChecked() != self.start_rip_ckb_value:
            self.rip_ckb_value = self.start_rip_ckb_value
            self.rip_ckb.setChecked(self.start_rip_ckb_value)
        ### keyboard model layout variant settings
        if self.kb_model != self.start_kb_model \
        or self.kb_layout != self.start_kb_layout \
        or self.kb_variant != self.start_kb_variant:
            if self.start_kb_variant == "":
                cmd = "setxkbmap -model {} -layout {}".format(self.start_kb_model, self.start_kb_layout)
            else:
                cmd = "setxkbmap -model {} -layout {} -variant {}".format(self.start_kb_model, self.start_kb_layout, self.start_kb_variant)
            try:
                subprocess.Popen(cmd, shell=True)
            except Exception as E:
                MyDialog("Error", str(E), self)
        #
        if self.label_kb_model.text() != self.start_kb_model \
        or self.label_kb_layout.text() != self.start_kb_layout \
        or self.label_kb_variant.text() != self.start_kb_variant:
            self.kb_model = self.start_kb_model
            self.label_kb_model.setText(self.start_kb_model)
            self.kb_layout = self.start_kb_layout
            self.label_kb_layout.setText(self.start_kb_layout)
            self.kb_variant = self.start_kb_variant
            self.label_kb_variant.setText(self.start_kb_variant)
    
    #
    def on_apply_btn2(self):
        ret = chooseDialog(self, 2)
        if ret.getValue() == 0:
            return
        #
        commands_to_execute = []
        # delay and rate
        if int(self.label_wait_rip.text()) != self.start_rip_val \
        or self.rip_val != self.start_rip_val \
        or int(self.label_int.text()) != self.start_int_val \
        or self.int_val != self.start_int_val:
            str_rip_int_val = "xset r rate {} {}".format(int(self.label_wait_rip.text()), int(self.label_int.text()))
            commands_to_execute.append(str_rip_int_val)
        # beep
        if int(self.rip_ckb.isChecked()) != self.start_rip_ckb_value \
        or self.rip_ckb_value != self.start_rip_ckb_value:
            str_new_rip_ckb = "on"
            if int(self.rip_ckb.isChecked()) == 0:
                str_new_rip_ckb = "off"
            str_rip_ckb = "xset b {}".format(str_new_rip_ckb)
            commands_to_execute.append(str_rip_ckb)
            self.rip_ckb_value = self.rip_ckb.isChecked()
        # keyboard model layout variant settings
        if self.label_kb_model.text() != self.start_kb_model \
        or self.start_kb_model != self.kb_model \
        or self.label_kb_layout.text() != self.start_kb_layout \
        or self.start_kb_layout != self.kb_layout \
        or self.label_kb_variant.text() != self.start_kb_variant \
        or self.start_kb_variant != self.kb_variant:
            if self.label_kb_variant.text() != self.kb_variant:
                str_kb_model = "setxkbmap -model {} -layout {} -variant {}".format(self.label_kb_model.text(), self.label_kb_layout.text(), self.label_kb_variant.text())
            else:
                str_kb_model = "setxkbmap -model {} -layout {}".format(self.label_kb_model.text(), self.label_kb_layout.text())
            commands_to_execute.append(str_kb_model)
        #
        if ret.getValue() == 1:
            try:
                bash_file = os.path.join(BASH_PATH, "keyboard.sh")
                ff = open(bash_file, "w")
                ff.write("#!/bin/bash\n")
                for ccom in commands_to_execute:
                    ff.write(ccom+"\n")
                ff.close()
                st = os.stat(bash_file)
                os.chmod(bash_file, st.st_mode | stat.S_IEXEC)
            except Exception as E:
                MyDialog("Error", str(E), self)
        elif ret.getValue() == 2:
            try:
                desktop_file = os.path.join(AUTOSTART_PATH, "keyboard.desktop")
                command_exec = ""
                for ccom in commands_to_execute:
                    command_exec += ccom+";"
                exec_command = 'sh -c "{}"'.format(command_exec)
                ff = open(desktop_file, "w")
                ff.write("[Desktop Entry]\nVersion=1.0\nType=Application\nName=Mouse Personal Settings\nNoDisplay=true\nExec={0}\n".format(exec_command))
                ff.close()
                st = os.stat(desktop_file)
                os.chmod(desktop_file, st.st_mode | stat.S_IEXEC)
            except Exception as E:
                MyDialog("Error", str(E), self)
        # change the keyboard setting
        if ret.getValue() == 3:
            try:
                for ccom in commands_to_execute:
                    subprocess.Popen(ccom, shell=True)
                #
                self.rip_val = int(self.label_wait_rip.text())
                self.int_val = int(self.label_int.text())
                self.kb_model = self.label_kb_model.text()
                self.kb_layout = self.label_kb_layout.text()
                self.kb_variant = self.label_kb_variant.text()
            except Exception as E:
                MyDialog("Error", str(E), self)
    
    
    
    # get the current values
    def on_test_btn_2(self):
        rip_val = "Cannot read this value"
        int_val = "Cannot read this value"
        #
        try:
            cmd = "xset q | grep 'auto repeat delay'"
            ret = subprocess.check_output(cmd, shell=True)
            ret_temp = ret.decode()
            list_value = [int(s) for s in ret_temp.split() if s.isdigit()]
            rip_val, int_val = list_value
        except:
            pass
        #
        rip_ckb_value = "Cannot read this value"
        try:
            cmd = "xset q | grep 'bell percent'"
            ret = subprocess.check_output(cmd, shell=True)
            ret_temp = ret.decode()
            list_value = [int(s) for s in ret_temp.split() if s.isdigit()]
            rip_ckb_value = bool(list_value[0])
        except:
            pass
        #
        kb_model = "Cannot read this value"
        kb_layout = "Cannot read this value"
        kb_variant = "Cannot read this value"
        if SETXKBMAP_EXIST:
            ## the model
            try:
                cmd = "setxkbmap -query | grep model | cut -d : -f 2"
                ret = subprocess.check_output(cmd, shell=True)
                if ret.decode():
                    kb_model = ret.decode().lstrip(" ").strip("\n")
            except:
                pass
            ## the layout
            cmd = "setxkbmap -query | grep layout | cut -d : -f 2"
            try:
                ret = subprocess.check_output(cmd, shell=True)
                if ret.decode():
                    kb_layout = ret.decode().lstrip(" ").strip("\n")
            except:
                pass
            ## the variant
            cmd = "setxkbmap -query | grep variant | cut -d : -f 2"
            try:
                ret = subprocess.check_output(cmd, shell=True)
                if ret.decode():
                    kb_variant = ret.decode().lstrip(" ").strip("\n")
                else:
                    kb_variant = ""
            except:
                pass
        #
        msg = """The actual active keyboard configuration is:

Repeat delay: {0}

Repeat interval: {1}

Beep when there is an error keyboard input: {2}

Model: {3}

Layout: {4}

Variant: {5}""".format(rip_val, int_val, rip_ckb_value, kb_model or "(Not setted)", kb_layout or "(Not setted)", kb_variant or "(Not setted)")
        MyDialog("Info", msg, self)
        return

########### END KEYBOARD ###########

########## MOUSE ###########
    
    # switch mouse
    def on_mcombo(self):
        self.on_start_mouse(self.mcombo.currentText())
    
    # setting some values on starting - mouse
    def on_start_mouse(self, mouse_name):
        ### MOUSE
        # get the value
        cmd = "xinput list-props '{0}' | grep 'libinput Accel Speed' | head -n 1 | cut -f 3".format(mouse_name)
        try:
            ret = subprocess.check_output(cmd, shell=True)
            if ret.decode().strip("\n"):
                ret_value = int((float(ret.decode().strip("\n")) + 1) * 100)
                self.start_speed_val = ret_value
                self.speed_val = ret_value
                self.label_slider_moveFast.setText(str(ret_value))
                self.slider_speed.setSliderPosition(ret_value)
        except Exception as E:
            MyDialog("Error", str(E), self)
        #
        ### left handled
        # get the value
        cmd = "xinput list-props '{0}' | grep 'libinput Left Handed Enabled' | head -n 1 | cut -f 3".format(mouse_name)
        try:
            ret = subprocess.check_output(cmd, shell=True)
            ret_value = int(ret.decode().strip("\n"))
            self.start_lh_ckb_value = ret_value
            self.lh_ckb_value = ret_value
            self.lh_ckb.setChecked(ret_value)
        except Exception as E:
            MyDialog("Error", str(E), self)
    

    # revert mouse settings to starting values
    def on_reset_btn_1(self):
        ret = retDialogBox("Question", "Revert all the changes?", self)
        if ret.getValue() == 0:
            return
        mouse_name = self.mcombo.currentText()
        try:
            if self.speed_val != self.start_speed_val:
                cmd = "xinput set-prop '{}' 'libinput Accel Speed' {}".format(mouse_name, round((self.start_speed_val/100)-1,2))
                subprocess.Popen(cmd, shell=True)
            if int(self.label_slider_moveFast.text()) != self.start_speed_val:
                self.label_slider_moveFast.setText(str(self.start_speed_val))
                self.slider_speed.setSliderPosition(self.start_speed_val)
                self.speed_val = self.start_speed_val
        except Exception as E:
            MyDialog("Error", str(E), self)
        #
        try:
            if self.lh_ckb_value != self.start_lh_ckb_value:
                cmd = "xinput set-prop '{}' 'libinput Left Handed Enabled' {}".format(mouse_name, int(self.start_lh_ckb_value))
                subprocess.Popen(cmd, shell=True)
            if self.lh_ckb.isChecked() != self.start_lh_ckb_value:
                self.lh_ckb.setChecked(self.start_lh_ckb_value)
                self.lh_ckb_value = self.start_lh_ckb_value
        except Exception as E:
            MyDialog("Error", str(E), self)
    
    #
    def on_apply_btn1(self):
        # save: 1 bash script - 2 autostart desktop file - 3 apply without making any script
        ret = chooseDialog(self, 1)
        if ret.getValue() == 0:
            return
        #
        commands_to_execute = []
        # 
        mouse_name = self.mcombo.currentText()
        # 
        if self.start_speed_val != int(self.label_slider_moveFast.text()) \
        or self.start_speed_val != self.speed_val:
            str_speed_val = "xinput set-prop '{}' 'libinput Accel Speed' {}".format(mouse_name, round(int(self.label_slider_moveFast.text())/100-1,2))
            commands_to_execute.append(str_speed_val)
        #
        if self.start_lh_ckb_value != int(self.lh_ckb.isChecked()) \
        or self.start_lh_ckb_value != self.lh_ckb_value:
            left_hdl = "xinput set-prop '{}' 'libinput Left Handed Enabled' {}".format(mouse_name, int(self.lh_ckb.isChecked()))
            commands_to_execute.append(left_hdl)
        #
        if ret.getValue() == 1:
            try:
                bash_file = os.path.join(BASH_PATH, "mouse.sh")
                ff = open(bash_file, "w")
                ff.write("#!/bin/bash\n")
                for ccom in commands_to_execute:
                    ff.write(ccom+"\n")
                ff.close()
                st = os.stat(bash_file)
                os.chmod(bash_file, st.st_mode | stat.S_IEXEC)
            except Exception as E:
                MyDialog("Error", str(E), self)
        elif ret.getValue() == 2:
            try:
                desktop_file = os.path.join(AUTOSTART_PATH, "mouse.desktop")
                command_exec = ""
                for ccom in commands_to_execute:
                    command_exec += ccom+";"
                exec_command = 'sh -c "{}"'.format(command_exec)
                ff = open(desktop_file, "w")
                ff.write("[Desktop Entry]\nVersion=1.0\nType=Application\nName=Mouse Personal Settings\nNoDisplay=true\nExec={0}\n".format(exec_command))
                ff.close()
                st = os.stat(desktop_file)
                os.chmod(desktop_file, st.st_mode | stat.S_IEXEC)
            except Exception as E:
                MyDialog("Error", str(E), self)
        # apply the settings
        if ret.getValue() == 3:
            try:
                for ccom in commands_to_execute:
                    subprocess.Popen(ccom, shell=True)
                #
                self.speed_val = int(self.label_slider_moveFast.text())
                self.lh_ckb_value = int(self.lh_ckb.isChecked())
            except Exception as E:
                MyDialog("Error", str(E), self)
    
    # tab1 pointer speed - slow
    def on_label_slow_speed(self):
        speed_value = int(self.label_slider_moveFast.text())
        if speed_value > 0:
            speed_value -= 5
            self.slider_speed.setSliderPosition(speed_value)
            self.label_slider_moveFast.setText(str(speed_value))
    
    # tab1 pointer speed - fast
    def on_label_fast_speed(self):
        speed_value = int(self.label_slider_moveFast.text())
        if speed_value < 200:
            speed_value += 5
            self.slider_speed.setSliderPosition(speed_value)
            self.label_slider_moveFast.setText(str(speed_value))
        
    
    # find any useful mice
    def pop_mcombo(self):
        cmd = "xinput list | grep pointer | grep slave | cut -f 2 | cut -d = -f 2"
        cmd_ret = subprocess.check_output(cmd, shell=True)
        id_list = cmd_ret.decode().split("\n")[:-1]
        # 
        for el in id_list:
            cmd_ret = ""
            try:
                cmd = "xinput list-props {} | grep 'Accel Speed'".format(el)
                cmd_ret = subprocess.check_output(cmd, shell=True)
            except:
                continue
            if cmd_ret:
                cmd = "xinput list-props {} | grep Device | head -n 1 | cut -d \\' -f 2".format(el)
                cmd_ret = subprocess.check_output(cmd, shell=True)
                self.mcombo.addItem(cmd_ret.decode().strip("\n"))

    #
    def on_hlp_btn(self):
        msg = """Copy in the hidden file .Xesources

*.multiClickTime: 500

or whatever value you want.
A logout is needed.

Remove it for the default behaviour.

Or check whether your window manager supports this option."""
        MyDialog("Info", msg, self)

    # 
    def on_test_btn_1(self):
        mouse_name = self.mcombo.currentText()
        speed_val = "Cannot read this value"
        cmd = "xinput list-props '{0}' | grep 'libinput Accel Speed' | head -n 1 | cut -f 3".format(mouse_name)
        try:
            ret = subprocess.check_output(cmd, shell=True)
            if ret.decode():
                speed_val = round(float(ret.decode().strip("\n")), 2)
        except:
            pass
        #
        left_hdl = "Cannot read this value"
        cmd = "xinput list-props '{0}' | grep 'libinput Left Handed Enabled' | head -n 1 | cut -f 3".format(mouse_name)
        try:
            ret = subprocess.check_output(cmd, shell=True)
            if ret.decode().strip("\n"):
                left_hdl = bool(int(ret.decode().strip("\n")))
        except:
            pass
        #
        msg = """The actual active mouse configuration is:

Mouse name: {0}

Pointer speed: {1}
(0.0 is the default value; positive value means faster, negative value means slower)

Left handed: {2}""".format(mouse_name, speed_val, left_hdl)
        MyDialog("Info", msg, self)
        return

########## END MOUSE ###########

# keyboard model
class keyboardDialog(QDialog):
    def __init__(self, parent):
        super(keyboardDialog, self).__init__(parent)
        self.window = parent
        #
        self.setWindowIcon(QIcon("icons/program.png"))
        self.setWindowTitle("Keyboard")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(600, 100)
        #
        vbox = QBoxLayout(QBoxLayout.TopToBottom)
        vbox.setContentsMargins(5,5,5,5)
        self.setLayout(vbox)
        #
        grid = QGridLayout()
        vbox.addLayout(grid)
        ##
        label_model = QLabel("Model:")
        grid.addWidget(label_model, 0, 1, Qt.AlignLeft)
        self.combo1 = QComboBox()
        grid.addWidget(self.combo1, 0, 1, 1, 10, Qt.AlignRight)
        ##
        label_disp = QLabel("Layout:")
        grid.addWidget(label_disp, 1, 1, Qt.AlignLeft)
        self.combo2 = QComboBox()
        grid.addWidget(self.combo2, 1, 1, 1, 10, Qt.AlignRight)
        ##
        label_var = QLabel("Variant:")
        grid.addWidget(label_var, 2, 1, Qt.AlignLeft)
        self.combo3 = QComboBox()
        grid.addWidget(self.combo3, 2, 1, 1, 10, Qt.AlignRight)
        ### button box
        hbox = QBoxLayout(QBoxLayout.LeftToRight)
        vbox.addLayout(hbox)
        #
        button1 = QPushButton("Cancel")
        button1.clicked.connect(self.close)
        hbox.addWidget(button1)
        #
        button2 = QPushButton("Accept")
        button2.clicked.connect(self.faccept)
        hbox.addWidget(button2)
        #
        self.Value = []
        # 
        self.repository = "/usr/share/X11/xkb/rules/base.xml"
        #
        self.kb_models = []
        self.kb_layouts = []
        self.kb_variant = []
        self.on_pop()
        # 
        self.exec_()
    
    # get the list of keyboard models
    def on_get_models(self):
        tree = lxml.etree.parse(self.repository)
        models = tree.xpath("//model")
        for model in models:
            modelName = model.xpath("./configItem/name")[0].text
            self.kb_models.append(modelName)
        self.kb_models.sort()
        
    #
    def on_get_layouts(self):
        tree = lxml.etree.parse(self.repository)
        layouts = tree.xpath("//layout")
        for layout in layouts:
            layoutName = layout.xpath("./configItem/name")[0].text
            variantNameList = []
            for variant in layout.xpath("./variantList/variant/configItem/name"):
                variantName = variant.text
                variantNameList.append(variantName)
            self.kb_layouts.append([layoutName, variantNameList])
        self.kb_layouts.sort()
        
    # 
    def on_pop(self):
        if not os.path.exists(self.repository):
            return
        ### keyboard models
        self.on_get_models()
        if self.kb_models:
            self.combo1.addItems(self.kb_models)
            # layouts and variants
            self.on_get_layouts()
            # the model
            if self.window.start_kb_model:
                kb_idx = self.kb_models.index(self.window.start_kb_model)
                self.combo1.setCurrentIndex(kb_idx)
            # the layout
            if self.window.start_kb_layout:
                # layout_idx = None
                variant_list = []
                #
                for idx,elist in enumerate(self.kb_layouts):
                    self.combo2.addItem(elist[0])
                    if elist[0] == self.window.start_kb_layout:
                        variant_list = elist[1]
                        self.combo2.setCurrentIndex(idx)
                        self.combo2.currentIndexChanged.connect(self.on_combo2)
                # the variants
                if variant_list:
                    variant_list.append("")
                    self.combo3.addItems(variant_list)
                    if self.window.start_kb_variant in variant_list:
                        kb_idx = variant_list.index(self.window.start_kb_variant)
                        self.combo3.setCurrentIndex(kb_idx)
                    else:
                        self.combo3.setCurrentIndex(len(variant_list)-1)
    
    def getValue(self):
        return self.Value
        
    def faccept(self):
        self.Value = [self.combo1.currentText(), self.combo2.currentText(), self.combo3.currentText()]
        self.close()
    
    def on_combo2(self, fval):
        # update the variant
        new_layout = self.combo2.currentText()
        variant_list = []
        for idx,elist in enumerate(self.kb_layouts):
            if elist[0] == new_layout:
                variant_list = elist[1]
                break
        #
        variant_list.append("")
        self.combo3.clear()
        self.combo3.addItems(variant_list)
        self.combo3.setCurrentIndex(len(variant_list)-1)
        
# 
class chooseDialog(QDialog):
    def __init__(self, parent, dtype):
        super(chooseDialog, self).__init__(parent)
        self.dtype = dtype
        self.setWindowIcon(QIcon("icons/program.png"))
        self.setWindowTitle("Save as...")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(600, 100)
        #
        vbox = QBoxLayout(QBoxLayout.TopToBottom)
        vbox.setContentsMargins(5,5,5,5)
        self.setLayout(vbox)
        #
        ### button box
        hbox = QBoxLayout(QBoxLayout.LeftToRight)
        vbox.addLayout(hbox)
        #
        button1 = QPushButton("Bash script")
        button1.clicked.connect(self.on_bash)
        hbox.addWidget(button1)
        #
        button2 = QPushButton("Autostart")
        button2.clicked.connect(self.on_autostart)
        hbox.addWidget(button2)
        #
        button4 = QPushButton("Apply only")
        button4.clicked.connect(self.on_not_script)
        hbox.addWidget(button4)
        #
        button3 = QPushButton("Close")
        button3.clicked.connect(self.close)
        hbox.addWidget(button3)
        #
        self.Value = 0
        #
        self.exec_()
        
    def on_bash(self):
        self.Value = 1
        self.close()
    
    def on_autostart(self):
        self.Value = 2
        self.close()
    
    def on_not_script(self):
        self.Value = 3
        self.close()
    
    def getValue(self):
        return self.Value
        

# dialog - return of the choise yes or no
class retDialogBox(QMessageBox):
    def __init__(self, *args):
        super(retDialogBox, self).__init__(args[-1])
        self.setWindowIcon(QIcon("icons/progam.png"))
        self.setWindowTitle(args[0])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Information)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Critical)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Question)
        self.resize(DIALOGWIDTH, 100)
        self.setText(args[1])
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        #
        self.Value = None
        retval = self.exec_()
        #
        if retval == QMessageBox.Yes:
            self.Value = 1
        elif retval == QMessageBox.Cancel:
            self.Value = 0
    
    def getValue(self):
        return self.Value
    
    # def event(self, e):
        # result = QMessageBox.event(self, e)
        # #
        # self.setMinimumHeight(0)
        # self.setMaximumHeight(16777215)
        # self.setMinimumWidth(0)
        # self.setMaximumWidth(16777215)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # #
        # textEdit = self.findChild(QTextEdit)
        # if textEdit != None :
            # textEdit.setMinimumHeight(0)
            # textEdit.setMaximumHeight(16777215)
            # textEdit.setMinimumWidth(0)
            # textEdit.setMaximumWidth(16777215)
            # textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # #
        # return result


###################

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWin()
    window.show()
    ret = app.exec_()
    sys.exit(ret)

####################

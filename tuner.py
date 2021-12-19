#!/usr/bin/python3

import logging
logging.basicConfig(level=logging.WARNING)

import xmlrpc.client
import os, sys
from typing import final
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QFontDatabase

def relpath(filename):
		try:
			base_path = sys._MEIPASS # pylint: disable=no-member
		except:
			base_path = os.path.abspath(".")
		return os.path.join(base_path, filename)

def load_fonts_from_dir(directory):
		families = set()
		for fi in QDir(directory).entryInfoList(["*.ttf", "*.woff", "*.woff2"]):
			_id = QFontDatabase.addApplicationFont(fi.absoluteFilePath())
			families |= set(QFontDatabase.applicationFontFamilies(_id))
		return families


class MainWindow(QtWidgets.QMainWindow):
    oldfreq = ''
    oldmode = ''
    oldbw = ''
    settings_dict ={
        "host": "127.0.0.1",
        "port": 4532
    }
    ft8freq = {
        "2": "7074000",
        "6": "50323000",
        "10": "28074000",
        "12": "24915000",
        "15": "21074000",
        "17": "18100000",
        "20": "14074000",
        "30": "10136000",
        "40": "7074000",
        "80": "3573000",
        "160": "1840000"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(self.relpath("main.ui"), self)
        self.tunebutton.clicked.connect(self.mainloop)
        self.oldfreq, self.oldmode, self.oldbw = self.getCurrentRadioState()
        self.freq_label.setText(self.oldfreq)
        self.mode_label.setText(self.oldmode)
        self.server = xmlrpc.client.ServerProxy("http://localhost:12345")

    def relpath(self, filename):
        """
        lets the program know where the temp execution location is.
        """
        try:
            base_path = sys._MEIPASS # pylint: disable=no-member
        except:
            base_path = os.path.abspath(".")
        finally:
            return os.path.join(base_path, filename)

    def getCurrentRadioState(self):
        try:
            freq = self.server.rig.get_vfo()
            mode = self.server.rig.get_mode()
            bw = self.server.rig.get_bw()[0]
            self.errorline_label.setText("")
            logging.info(f"getCurrentRadioState:{freq} {mode} {bw}")
            return freq, mode, bw
        except Exception as e:
            self.errorline_label.setText(f"{e}")
            return "0000000", "ERR", "0"

    def changefreq(self, tunefreq):
        logging.info(f"changefreq: {tunefreq}")
        try:
            self.server.rig.set_frequency(float(tunefreq))
        except Exception as e:
            self.errorline_label.setText(f"{e}")
            return

    def changemode(self, isft8):
        logging.info(f"changemode:{isft8}")
        try:
            if isft8:
                self.server.rig.set_mode("CW")
                self.server.rig.set_bw(int(500))
                return
            self.server.rig.set_mode(self.oldmode)
            self.server.rig.set_bandwidth(int(self.oldbw))
        except Exception as e:
            self.errorline_label.setText(f"{e}")
            return

    def getband(self, freq):
        """
        Convert a (string) frequency in hz into a (string) band.
        Returns a (string) band.
        Returns a "0" if frequency is out of band.
        """
        if freq.isnumeric():
            frequency = int(float(freq))
            if frequency > 1800000 and frequency < 2000000:
                return "160"
            if frequency > 3500000 and frequency < 4000000:
                return "80"
            if frequency > 5330000 and frequency < 5406000:
                return "60"
            if frequency > 7000000 and frequency < 7300000:
                return "40"
            if frequency > 10100000 and frequency < 10150000:
                return "30"
            if frequency > 14000000 and frequency < 14350000:
                return "20"
            if frequency > 18068000 and frequency < 18168000:
                return "17"
            if frequency > 21000000 and frequency < 21450000:
                return "15"
            if frequency > 24890000 and frequency < 24990000:
                return "12"
            if frequency > 28000000 and frequency < 29700000:
                return "10"
            if frequency > 50000000 and frequency < 54000000:
                return "6"
            if frequency > 144000000 and frequency < 148000000:
                return "2"
        else:
            return "0"

    def pollIdleRadio(self):
        if self.tunebutton.isChecked():
            return
        freq, mode, _ = self.getCurrentRadioState()
        self.freq_label.setText(freq)
        self.mode_label.setText(mode)

    def tune(self):
        self.oldfreq, self.oldmode, self.oldbw = self.getCurrentRadioState()
        band = self.getband(self.oldfreq)
        if band:
            self.changefreq(self.ft8freq[band])
            self.changemode(True)
            freq, mode, _ = self.getCurrentRadioState()
            self.freq_label.setText(freq)
            self.mode_label.setText(mode)


    def doneTuning(self):
        self.changefreq(self.oldfreq)
        self.changemode(False)
        freq, mode, _ = self.getCurrentRadioState()
        self.freq_label.setText(freq)
        self.mode_label.setText(mode)

    def mainloop(self):
        if self.tunebutton.isChecked():
            self.tune()
            return
        self.doneTuning()

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    font_dir = relpath("font")
    families = load_fonts_from_dir(os.fspath(font_dir))
    logging.info(families)
    window = MainWindow()
    window.show()
    timer = QtCore.QTimer()
    timer.timeout.connect(window.pollIdleRadio)
    timer.start(200)
    app.exec()

if __name__ == "__main__":
    main()

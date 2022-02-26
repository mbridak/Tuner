#!/usr/bin/python3
"""Changed your radio to a 'safe' frequency to tune it."""
# pylint: disable=broad-except
import xmlrpc.client
import os
import sys
import logging


from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QFontDatabase

logging.basicConfig(level=logging.WARNING)


def relpath(filename):
    """
    Checks to see if program has been packaged with pyinstaller.
    If so base dir is in a temp folder.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = getattr(sys, "_MEIPASS")
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, filename)


def load_fonts_from_dir(directory):
    """Load font families"""
    families_set = set()
    for thing in QDir(directory).entryInfoList(["*.ttf", "*.woff", "*.woff2"]):
        _id = QFontDatabase.addApplicationFont(thing.absoluteFilePath())
        families_set |= set(QFontDatabase.applicationFontFamilies(_id))
    return families_set


class MainWindow(QtWidgets.QMainWindow):
    """the main window"""

    oldfreq = ""
    oldmode = ""
    oldbw = ""
    settings_dict = {"host": "127.0.0.1", "port": 4532}
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
        "60": "5358500",
        "80": "3573000",
        "160": "1840000",
    }

    def __init__(self, *args, **kwargs):
        """Initialize"""
        super().__init__(*args, **kwargs)
        uic.loadUi(self.relpath("main.ui"), self)
        self.tunebutton.clicked.connect(self.mainloop)
        self.oldfreq, self.oldmode, self.oldbw = self.get_current_radio_state()
        self.freq_label.setText(self.oldfreq)
        self.mode_label.setText(self.oldmode)
        self.server = xmlrpc.client.ServerProxy("http://localhost:12345")

    @staticmethod
    def relpath(filename: str) -> str:
        """
        If the program is packaged with pyinstaller,
        this is needed since all files will be in a temp
        folder during execution.
        """
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base_path = getattr(sys, "_MEIPASS")
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, filename)

    def get_current_radio_state(self):
        """Gets the current radio state. Surprise!"""
        try:
            freq = self.server.rig.get_vfo()
            mode = self.server.rig.get_mode()
            bandwidth = self.server.rig.get_bw()[0]
            self.errorline_label.setText("")
            logging.info("get_current_radio_state:%s %s %s", freq, mode, bandwidth)
            return freq, mode, bandwidth
        except Exception as err:
            self.errorline_label.setText(f"{err}")
            return "0000000", "ERR", "0"

    def changefreq(self, tunefreq):
        """Changes the radio frequency"""
        logging.info("changefreq: %s", tunefreq)
        try:
            self.server.rig.set_frequency(float(tunefreq))
        except Exception as err:
            self.errorline_label.setText(f"{err}")
            return

    def changemode(self, isft8):
        """Changes the radios mode"""
        logging.info("changemode:%s", isft8)
        try:
            if isft8:
                self.server.rig.set_mode("CW")
                self.server.rig.set_bw(int(500))
                return
            self.server.rig.set_mode(self.oldmode)
            self.server.rig.set_bandwidth(int(self.oldbw))
        except Exception as err:
            self.errorline_label.setText(f"{err}")
            return

    def getband(self, freq):
        """
        Convert a (string) frequency in hz into a (string) band.
        Returns a (string) band.
        Returns a "0" if frequency is out of band.
        """
        if freq.isnumeric():
            frequency = int(float(freq))
            if 2000000 > frequency > 1800000:
                return "160"
            if 4000000 > frequency > 3500000:
                return "80"
            if 5406000 > frequency > 5330000:
                return "60"
            if 7300000 > frequency > 7000000:
                return "40"
            if 10150000 > frequency > 10100000:
                return "30"
            if 14350000 > frequency > 14000000:
                return "20"
            if 18168000 > frequency > 18068000:
                return "17"
            if 21450000 > frequency > 21000000:
                return "15"
            if 24990000 > frequency > 24890000:
                return "12"
            if 29700000 > frequency > 28000000:
                return "10"
            if 54000000 > frequency > 50000000:
                return "6"
            if 148000000 > frequency > 144000000:
                return "2"
        else:
            return "0"

    def poll_idle_radio(self):
        """Polls the radio"""
        if self.tunebutton.isChecked():
            return
        freq, mode, _ = self.get_current_radio_state()
        self.freq_label.setText(freq)
        self.mode_label.setText(mode)

    def tune(self):
        """Set radio up for tune."""
        self.oldfreq, self.oldmode, self.oldbw = self.get_current_radio_state()
        band = self.getband(self.oldfreq)
        if band:
            self.changefreq(self.ft8freq[band])
            self.changemode(True)
            freq, mode, _ = self.get_current_radio_state()
            self.freq_label.setText(freq)
            self.mode_label.setText(mode)
        info = self.server.rig.get_info()
        if "R:IC-7300" in info:
            self.server.rig.cat_string("xFExFEx94xE0x1Cx01x02xFD")

    def done_tuning(self):
        """Change the radio state back after tune"""
        self.changefreq(self.oldfreq)
        self.changemode(False)
        freq, mode, _ = self.get_current_radio_state()
        self.freq_label.setText(freq)
        self.mode_label.setText(mode)

    def mainloop(self):
        """Handles the state"""
        if self.tunebutton.isChecked():
            self.tune()
            return
        self.done_tuning()


def main():
    """The main loop"""
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    font_dir = relpath("font")
    families = load_fonts_from_dir(os.fspath(font_dir))
    logging.info(families)
    window = MainWindow()
    window.show()
    timer = QtCore.QTimer()
    timer.timeout.connect(window.poll_idle_radio)
    timer.start(200)
    app.exec()


if __name__ == "__main__":
    main()

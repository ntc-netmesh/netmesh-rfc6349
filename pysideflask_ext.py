import os
import sys

from PySide2 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
from PySide2.QtCore import Qt

import socket

class ApplicationThread(QtCore.QThread):
    def __init__(self, application, port=5000):
        super(ApplicationThread, self).__init__()
        self.application = application
        self.port = port

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(port=self.port, threaded=True)

class MainGUI(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Message',
            "Close this app?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class WebPage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, root_url):
        super(WebPage, self).__init__()
        self.root_url = root_url

    def home(self):
        self.load(QtCore.QUrl(self.root_url))

    def acceptNavigationRequest(self, url, kind, is_main_frame):
        """Open external links in browser and internal links in the webview"""
        ready_url = url.toEncoded().data().decode()
        is_clicked = kind == self.NavigationTypeLinkClicked
        if is_clicked and self.root_url not in ready_url:
            QtGui.QDesktopServices.openUrl(url)
            return False
        return super(WebPage, self).acceptNavigationRequest(url, kind, is_main_frame)


def init_gui(application, port=0, width=800, height=600,
             window_title="PySideFlask", icon="appicon.png", argv=None):
  
    if argv is None:
        argv = sys.argv

    if port == 0:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        sock.close()

    
    print("Opening NetMesh RFC-6349 App...")
    
    # Application Level
    qtapp = QtWidgets.QApplication(argv)
    webapp = ApplicationThread(application, port)
    webapp.start()
    qtapp.aboutToQuit.connect(webapp.terminate)

    # Main Window Level
    window = MainGUI()
    window.resize(width, height)
    window.setWindowTitle(window_title)
    window.setWindowIcon(QtGui.QIcon(icon))

    # WebView Level
    webView = QtWebEngineWidgets.QWebEngineView(window)
    webView.setContextMenuPolicy(Qt.PreventContextMenu)
    webView.setAcceptDrops(False)
    webView.setMinimumSize(800, 600)
    
    window.setCentralWidget(webView)

    # WebPage Level
    page = WebPage('http://127.0.0.1:{}'.format(port))
    
    profile = page.profile()
    profile.clearHttpCache()
    profile.clearAllVisitedLinks()
    profile.downloadRequested.connect(onDownloadRequested)
    
    page.home()
    webView.setPage(page)
    
    window.show()
    
    print("App opened")
    
    return qtapp.exec_()

@QtCore.Slot(QtWebEngineWidgets.QWebEngineDownloadItem)
def onDownloadRequested(download):
  download.accept()
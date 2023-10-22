import sys
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView

class HTMLWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a QWebEngineView widget
        self.webview = QWebEngineView(self)

        # Set the central widget to the web view
        self.setCentralWidget(self.webview)

        # Set window properties
        self.setWindowTitle("HTML Viewer")
        self.setGeometry(100, 100, 800, 600)
        
        self.html_content = """
        <html>
        <head>
            <title>HTML Viewer</title>
        </head>
        <body>
            <h1>Hello, PySide6!</h1>
            <p id='change_this'>This is an example of loading HTML content in a PySide6 window.</p>
        </body>
        </html>
        """
        
        self.html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Eye Acuity Test</title>
            <style>
                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                }
                .instructions {
                    font-size: 18px;
                    margin: 20px;
                }
                .letters {
                    font-size: 36px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h1>Eye Acuity Test</h1>
            <div class="instructions">
                <p>Instructions: Stand at a distance of <strong>10 feet (3 meters)</strong> from the screen. Cover one eye with your hand. Read the letters from top to bottom.</p>
            </div>
            <div class="letters">
                <p>E F P T O Z L R N D E</p>
            </div>
        </body>
        </html>

        """
        
        # Load an HTML content
        self.load_html_content()
        #self.interact_with_page()

    def load_html_content(self):
        # Define the HTML content

        # Load the HTML content into the web view
        self.webview.setHtml(self.html_content, QUrl("about:blank"))
        
        # wait for page to finish loading before calling js
        self.webview.page().loadFinished.connect(self.interact_with_page)

    def interact_with_page(self):
        pass
        #self.webview.page().runJavaScript("document.getElementById('change_this').innerHTML = 'This is an example of chaging content with JS!'")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HTMLWindow()
    window.show()
    sys.exit(app.exec_())

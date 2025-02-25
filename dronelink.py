import sys
import os

current_dir = os.path.dirname(os.path.realpath(__file__))
src_path = os.path.join(current_dir, "src")

sys.path.insert(0, src_path)

from main import MainApp

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings

    app = QApplication(sys.argv)
    settings = QSettings("DroneTek", "DroneLink")
    model_key = settings.value("model", "Default")

    main_window = MainApp(model_key)
    main_window.showMaximized()
    main_window.show()

    sys.exit(app.exec_())

import sys
from PyQt5.QtWidgets import QApplication
from src.views.main_window import MainWindow
from src.controllers.project_controller import ProjectController
from src.models.project import Project

def main():
    app = QApplication(sys.argv)
    
    # Create initial project
    project = Project("New Project", None)
    
    # Create controller
    controller = ProjectController(project)
    
    # Create and show main window
    window = MainWindow(controller)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

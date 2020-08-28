import nuke
from nukeScript import *

pools_list = ['None', 'Nuke']

submit_in_list = ['Linux', 'Windows']

frame_per_task_list = ['3', '4', '8', '10', '12', '16']


class Panel(NukeScript):
    def __init__(self, selection):
        super(Panel, self).__init__()
        self.selection = selection
        self.master_layout = QVBoxLayout()
        self.loadWrite()  ### For nuke to find all Write nodes
        self.initUI()
        self.setLayout(self.master_layout)
        self.setWindowTitle('CGRU RENDERER')
        self.setMinimumWidth(300)
        self.buttonConnects()

    def buttonConnects(self):
        """ All button presses"""
        self.button2.clicked.connect(self.cancelButton)
        self.button1.clicked.connect(self.submitOk)

    def initUI(self):
        """common UI for all"""
        self.hori_lay_buttons = QHBoxLayout()
        self.form_lay = QFormLayout()
        self.button1 = QPushButton('ok')
        self.button2 = QPushButton('cancel')
        self.job_paused = QCheckBox()
        self.job_paused.setStyleSheet("color: Orange")
        self.pool = QComboBox()
        self.pool.addItems(pools_list)
        self.pool.setCurrentIndex(1)
        self.submit_in = QComboBox()
        self.submit_in.addItems(submit_in_list)
        self.frames_per_task = QComboBox()
        self.frames_per_task.addItems(frame_per_task_list)
        self.frames_per_task.setCurrentIndex(1)
        self.form_lay.addRow('Submit Paused', self.job_paused)
        self.form_lay.addRow('Pool', self.pool)
        self.form_lay.addRow('Frame Per Task', self.frames_per_task)
        self.form_lay.addRow('Submit In', self.submit_in)

        # setting ok and cancel buttons
        self.hori_lay_buttons.addWidget(self.button1)
        self.hori_lay_buttons.addWidget(self.button2)
        self.master_layout.addLayout(self.form_lay)
        self.master_layout.addLayout(self.hori_lay_buttons)

    def cancelButton(self):
        """ Cancel Button """
        self.close()

    def submitOk(self):
        """ OK Button/Submit """
        self.submitok()


def run():
    """Shows all write nodes in the node graph"""
    run.panel = Panel('full')
    run.panel.show()

def run_selected():
    """Shows only selected write nodes"""
    run_selected.panel = Panel('selected')
    if not run_selected.panel.write_nodes:
        nuke.message('Atleast Select one Write Node')
    else:
        run_selected.panel.show()


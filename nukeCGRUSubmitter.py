import os
import sys

import nuke
from PySide2.QtWidgets import *

cgruPath = r'E:\Download\compressed_file\cgru.2.3.1.windows\cgru.2.3.1'
sys.path.append(r'{}\afanasy\python'.format(cgruPath))
sys.path.append(r'{}\lib\python'.format(cgruPath))
os.environ['CGRU_LOCATION'] = cgruPath

import af

write_list = ['write1', 'write2', 'write3', 'write4']

pools_list = ['None', 'Nuke']

submit_in_list = ['Linux', 'Windows']

frame_per_task_list = ['3', '4', '8', '10', '12', '16']


class Panel(QWidget):
    write_nodes = []

    def __init__(self):
        super(Panel, self).__init__()
        # self.nuke_lister = NukeNodeLister()

        self.master_layout = QVBoxLayout()
        self.hori_lay_buttons = QHBoxLayout()

        form_lay = QFormLayout()

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

        self.loadWrite() ### For nuke to find all Write nodes

        form_lay.addRow('Submit Paused', self.job_paused)
        form_lay.addRow('Pool', self.pool)
        form_lay.addRow('Frame Per Task', self.frames_per_task)
        form_lay.addRow('Submit In', self.submit_in)

        # setting ok and cancel
        self.hori_lay_buttons.addWidget(self.button1)
        self.hori_lay_buttons.addWidget(self.button2)

        self.master_layout.addLayout(form_lay)
        self.master_layout.addLayout(self.hori_lay_buttons)

        self.setLayout(self.master_layout)
        self.setWindowTitle('CGRU RENDERER')
        self.setMinimumWidth(300)

        self.button2.clicked.connect(self.cancelButton)
        self.button1.clicked.connect(self.submitOk)


    def loadWrite(self):
        self.write_nodes = []
        for node in self.all_nodes():
            nf = self.get_node_info(node)
            self.select_writenodes(nf[0], nf[1], nf[2])


    def select_writenodes(self, write_name, frameFirst, lastFrame):
        frames = '{}:{}'.format(frameFirst, lastFrame)
        check_box = QCheckBox(write_name)

        line_edit_frames = QLineEdit()
        line_edit_frames.setText(frames)
        line_edit_frames.setStyleSheet("color: orange")

        lay_h = QFormLayout()
        lay_h.addRow('Frame Range', line_edit_frames)

        layout_vertical_write = QVBoxLayout()
        layout_vertical_write.addWidget(check_box)
        layout_vertical_write.addLayout(lay_h)

        self.master_layout.addLayout(layout_vertical_write)

    def all_nodes(self):
        nodes = nuke.allNodes()
        for node in nodes:
            if node.Class() == 'Write' and node not in self.write_nodes:
                if not node['disable'].value():
                    self.write_nodes.append(node)
        return self.write_nodes

    def get_node_info(self, writeNode):
        root_framerange = nuke.root()
        self.write_name = writeNode['name'].value()
        self.seqName = writeNode['file'].value().replace('%04d', '@####@')

        if writeNode['use_limit'].value():
            self.write_firstframe = int(writeNode['first'].value())
            self.write_lastframe = int(writeNode['last'].value())
        else:
            self.write_firstframe = int(root_framerange['first_frame'].value())
            self.write_lastframe = int(root_framerange['last_frame'].value())

        return (self.write_name, self.write_firstframe, self.write_lastframe,self.seqName)

    def nukeRootinfos(self):
        self.root = nuke.root()['name'].value()
        self.wn = os.path.basename(self.root)
        self.jobname = self.wn.split('.')
        self.jobname = self.jobname[0]
        self.workDir = os.path.dirname(self.root)

        return (self.jobname, self.workDir, self.wn)

    def setJobs(self, writename, framefirst, framelast, framepertask, seqname):

        """send jobs from nuke to cgru"""

        job_name = '{}_{}'.format(writename, self.nukeRootinfos()[0])
        job = af.Job(job_name)
        job.setMaxRunningTasks(15)
        block = af.Block('Nuke_Render', 'nuke')
        block.setWorkingDirectory(self.nukeRootinfos()[1])
        block.setCommand('nuke -i -X {} -x {} @#@,@#@'.format(writename, self.nukeRootinfos()[2]))
        block.setFiles([seqname])
        block.setNumeric(framefirst, framelast, framepertask)
        job.blocks.append(block)
        if self.job_paused.isChecked():
            job.offline()
        job.send()

    def cancelButton(self):
        """ Cancel Button """

        self.close()

    def submitOk(self):
        """ OK Button/Submit """

        nuke.scriptSave("")
        write_info = []
        for widget in self.master_layout.children():
            if isinstance(widget, QVBoxLayout):
                writeName_vb = widget.itemAt(0).widget()
                frameRange_vb = widget.children()
                frameRange_vb = frameRange_vb[0].itemAt(1).widget()
                widget_pair = (writeName_vb, frameRange_vb)
                write_info.append(widget_pair)

        for pair_widget in write_info:
            if pair_widget[0].isChecked():
                splitter = pair_widget[1].text().split(':')
                frameF = int(splitter[0])
                frameL = int(splitter[1])
                self.setJobs(pair_widget[0].text(), frameF, frameL, int(self.frames_per_task.currentText()), self.get_node_info(nuke.toNode(pair_widget[0].text()))[3])
                self.close()


def run():
    # app = QApplication(sys.argv)
    run.panel = Panel()
    run.panel.show()
    # sys.exit(app.exec_())


# run()

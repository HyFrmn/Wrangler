#!/usr/bin/env python

import sys
import cPickle

from PyQt4 import QtGui, QtCore

import wrangler.db
from wrangler import *
from wrangler.gui.core import WranglerGUI

class StableModel(QtCore.QAbstractListModel):
    def __init__(self):
        QtCore.QAbstractListModel.__init__(self)
        self.tasks = []
        for i in range(0, 25):
            self.tasks.append('%d Item' % i)
        print self.tasks

    def rowCount(self):
        return len(self.tasks)

    def data(self, index, role):
        if index.isValid:
            if index.row() < len(self.tasks):
                if role == QtCore.DisplayRole:
                    return self.tasks[index.row()]
        print index, role

class JobTable(QtGui.QTreeWidget):
    def __init__(self,  *args):
        QtGui.QTreeWidget.__init__(self, *args)
        self.setItemsExpandable(False)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.menu = QtGui.QMenu()
        self.menu.addAction('&View Tasks', self.view_tasks)
        self.menu.addAction('&Refresh', self.refresh)

    def refresh(self):
        #Initialize Table
        self.clear()
        self.setColumnCount(3)
        self.setHeaderLabels(['ID', 'Name', 'Status','Waiting','Running', 'Paused', 'Finished', 'Total Tasks'])
        
        #Get Jobs from Database. 
        db = wrangler.db.Session()
        jobs = db.query(Job).all()
        for i, job in enumerate(jobs):
            item = QtGui.QTreeWidgetItem(self)
            item.setText(0, str(job.id))
            item.setText(1, str(job.name))
            item.setText(2, str(job.status))
            item.setText(3, str(job.waiting))
            item.setText(4, str(job.running))
            item.setText(5, str(job.paused))
            item.setText(6, str(job.finished))
            item.setText(7, str(len(job.tasks)))

    def view_tasks(self):
        item = self.selectedItems()[0]
        jobid = item.text(0)
        db = wrangler.db.Session()
        job = db.query(Job).filter_by(id=jobid).one()
        task_dialog = TaskDialog(self)
        task_dialog.refresh(job)
        db.close()
        #task_table.setFocus()
        task_dialog.show()

    def mouseReleaseEvent(self, event):
        if event.button() == 2:
            pos = event.globalPos()
            self.menu.popup(pos)


class CattleTable(QtGui.QTreeWidget):
    def __init__(self, *args):
        QtGui.QTreeWidget.__init__(self, *args)
        self.setItemsExpandable(False)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

    def refresh(self):
        self.clear()
        self.setColumnCount(6)
        self.setHeaderLabels(['Hostname', 'Memory', 'System', 'Processor', 'CPU Counts', 'Enabled'])

        db = wrangler.db.Session()
        cattle = db.query(Cattle).all()
        for c in cattle:
            item = QtGui.QTreeWidgetItem(self)
            item.setText(0, str(c.hostname))
            item.setText(1, str(c.memory))
            item.setText(2, str(c.system))
            item.setText(3, str(c.processor))
            item.setText(4, str(c.ncpus))
            item.setText(5, str(c.enabled))

class TaskDialog(QtGui.QDialog):
    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        self.setGeometry(10, 10, 640, 480)
        self.task_table = TaskTable(self)
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.task_table)
        self.setLayout(self.layout)

    def refresh(self, job):
        self.setWindowTitle('Tasks for job: "%s"' % job.name)
        self.task_table.refresh(job)



class TaskTable(QtGui.QTreeWidget):
    def __init__(self, *args):
        QtGui.QTreeWidget.__init__(self, *args)
        self.setItemsExpandable(False)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setGeometry(10, 10, 640, 480)

    def refresh(self, job):
        self.clear()
        self.setColumnCount(4)
        self.setHeaderLabels(['ID', 'Priority', 'Status', 'Command'])

        for task in job.tasks:
            item = QtGui.QTreeWidgetItem(self)
            item.setText(0, str(task.id))
            item.setText(1, str(task.priority))
            item.setText(2, str(task.status))
            item.setText(3, str(task.command))

class WranglerQtGUI(QtGui.QWidget, WranglerGUI):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setup_gui()

    def setup_gui(self):
        self.setWindowTitle(self.window_title)
        self.setGeometry(640, 480, 640, 480)
        self.layout = QtGui.QHBoxLayout()
        #Setup Tabs
        self.tab_widget = QtGui.QTabWidget(self)

        #Stable 
        self.stable_table = JobTable()
        self.stable_table.refresh()
        self.tab_widget.addTab(self.stable_table, 'Stable')

        #Heard
        self.cattle_table = CattleTable()
        self.cattle_table.refresh()
        self.tab_widget.addTab(self.cattle_table, 'Heard')

        #Finalize Layout
        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)

def main():
    app = QtGui.QApplication(sys.argv)
    gui = WranglerQtGUI()
    gui.show()
    app.exec_()

if __name__ == '__main__':
    main()
from PyQt5 import QtGui
from PyQt5.QtWidgets import QTreeWidgetItem


class BuildTree():
    def __init__(self, root, text, content, icon = ''):
        self. root = root
        self.text = text
        self.content = content
        self.icon = icon

    def build(self):
        tree = QTreeWidgetItem(self.root)
        tree.setText(0, self.text)
        iicon = QtGui.QIcon()
        iicon.addPixmap(QtGui.QPixmap(self.icon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        tree.setIcon(0, iicon)

        for row in self.content:
            # print(row)
            child = QTreeWidgetItem(tree)
            itemindex = 0
            for item in row:
                if isinstance(item, list) and item !=[]:
                    for h in item:
                        cc = QTreeWidgetItem(child)
                        valindex = 0
                        for val in h:
                            cc.setText(valindex, val)
                            valindex = valindex+1
                elif not item:
                    continue
                else:
                    # print(item)
                    child.setText(itemindex, item)
                    itemindex = itemindex + 1

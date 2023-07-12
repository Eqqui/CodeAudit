from PyQt5.QtWidgets import QTreeWidgetItem


class BuildTree():
    def __init__(self, root, text, content):
        self. root = root
        self.text = text
        self.content = content

    def build(self):
        tree = QTreeWidgetItem(self.root)
        tree.setText(0, self.text)
        for row in self.content:
            # print(row)
            child = QTreeWidgetItem(tree)
            itemindex = 0
            for item in row:
                if isinstance(item, list) and item !=[]:
                    cc = QTreeWidgetItem(child)
                    for val in item:
                        valindex = 0
                        for i in val:
                            cc.setText(valindex, i)
                            valindex = valindex+1
                elif not item:
                    continue
                else:
                    print(item)
                    child.setText(itemindex, item)
                    itemindex = itemindex + 1
        tree.setExpanded(True)

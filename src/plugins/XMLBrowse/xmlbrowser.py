## 05/27/2001 - 18:11:58
##
## (C)2001 Romain Guy
## romain.guy@jext.org
## www.jext.org

##
## Jext & Java CLASSES
##
from org.jext import *
from org.jext.event import *
from java.lang import *
from java.awt import *
from javax.swing import *
from javax.swing.tree import *

##
## USED BY load() METHOD
##
import os
import string
import sys
import xmllib

# TREE NODES
class TagNode(DefaultMutableTreeNode):
  def __init__(self, name, parentNode):
    DefaultMutableTreeNode.__init__(self, name)
    self.name = name
    self.parentNode = parentNode

# BROWSER
class ClassBrowser(JPanel, JextListener, Runnable):
  def __init__(self):
    JPanel.__init__(self, BorderLayout())
    __jext__.addJextListener(self)
    self.browserTree = JTree()
    self.seeker = None

    renderer = DefaultTreeCellRenderer()
    renderer.setOpenIcon(Utilities.getIcon("images/tree_open.gif", __jext__.class))
    renderer.setLeafIcon(Utilities.getIcon("images/tree_leaf.gif", __jext__.class))
    renderer.setClosedIcon(Utilities.getIcon("images/tree_close.gif", __jext__.class))

    renderer.setTextSelectionColor(GUIUtilities.parseColor(Jext.getProperty("vf.selectionColor")))
    renderer.setBackgroundSelectionColor(self.browserTree.getBackground())
    renderer.setBorderSelectionColor(self.browserTree.getBackground())

    self.browserTree.setCellRenderer(renderer)
    self.browserTree.putClientProperty("JTree.lineStyle", "Angled")
    self.browserTree.setScrollsOnExpand(1);

    selectionModel = DefaultTreeSelectionModel();
    selectionModel.setSelectionMode(DefaultTreeSelectionModel.SINGLE_TREE_SELECTION);
    self.browserTree.setSelectionModel(selectionModel);

    self.load(__jext__.getTextArea())

    self.browserTree.expandRow(0)
    self.browserTree.setRootVisible(0)
    self.browserTree.setShowsRootHandles(1)

    self.add(JScrollPane(self.browserTree), BorderLayout.CENTER)

  # jext events
  def jextEventFired(self, evt):
    evtType = evt.getWhat()
    # on selection
    if evtType == JextEvent.TEXT_AREA_SELECTED or evtType == JextEvent.TEXT_AREA_OPENED:
      #if not evt.getJextFrame().getBatchMode():
      self.load(evt.getTextArea())
    # on textarea change
    elif evtType == JextEvent.CHANGED_UPDATE or evtType == JextEvent.REMOVE_UPDATE or evtType == JextEvent.INSERT_UPDATE:
      # threaded operation
      if not self.seeker is None:
        self.seeker.stop()
        self.seeker = None
      self.seeker = Thread(self)
      self.seeker.start()

  def run(self):
    try:
      Thread.sleep(400)
    except:
      pass
    self.load(__jext__.getTextArea())

  # browses the opened Python file and creates a list of classes and methods
  def load(self, textArea):
    # create tree root
    root = DefaultMutableTreeNode("root")
    browserTreeModel = DefaultTreeModel(root)

    if textArea is None:
      return
    # not a python file !
    if textArea.getColorizingMode() != "xml":
      root.add(TagNode("Not an XML file !", None))
      self.browserTree.setModel(browserTreeModel)
      return

    text = textArea.getText()

    parser = XMLTreeParser(root)
    parser.feed(text)
    parser.close()

    self.browserTree.setModel(browserTreeModel)

class XMLTreeParser(xmllib.XMLParser):
  def __init__(self, root):
    xmllib.XMLParser.__init__(self)
    self.root = root
    self.parentNode = self.root

  def unknown_endtag(self, tag):
    self.parentNode = self.parentNode.parentNode

  def unknown_starttag(self, tag, attributes):
    node = TagNode(tag, self.parentNode)
    for attr in attributes.keys():
      node.add(TagNode(attr + "=" + attributes[attr], node))
    self.parentNode.add(node)
    self.parentNode = node

# MAIN ENTRY POINT
def main():
  # if the tab already exists
  # we remove it then add it once more
  tPane = __jext__.getVerticalTabbedPane()
  if tPane.indexOfTab("XML Browser") == -1:
    tPane.addTab("XML Browser", ClassBrowser())
  else:
    __jext__.removeJextListener(tPane.getComponentAt(tPane.indexOfTab("XML Browser")))
    tPane.removeTabAt(tPane.indexOfTab("XML Browser"))

if __name__ == '__main__':
  main()

# End of classbrowser.py

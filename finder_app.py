import wx
import wx.stc
import subprocess

class FinderFrame(wx.Frame):

  def __init__(self, *args, **kwds):
    super().__init__(None, *args, **kwds)
    self.create_menubar()
    panel = FinderPanel(self)
    
    self.Show()

  def create_menubar(self):
    menu_bar= wx.MenuBar()

    file_menu = wx.Menu()
    index_item = file_menu.Append(wx.ID_ANY, '&Indexar archivos...\tCtrl+I', '')
    file_menu.AppendSeparator()
    quit_item = file_menu.Append(wx.ID_ANY, '&Salir\tCtrl+Q', '')

    menu_bar.Append(file_menu, "&Finder")

    self.Bind(wx.EVT_MENU, self.quit_item, quit_item)
    self.Bind(wx.EVT_MENU, self.create_index, index_item)

    self.SetMenuBar(menu_bar)

  def quit_item(self, event):
    self.Close()

  def create_index(self, event):
    with IndexDialog(self) as dlg:
      if dlg.ShowModal == wx.OK:
        pass


class IndexDialog(wx.Dialog):

  def __init__(self, parent, *args, **kwds):
    super().__init__(parent, title = 'Indexar archivos', *args, **kwds)
    panel = wx.Panel(self, wx.ID_ANY)
    
    
class FinderPanel(wx.Panel):

  def __init__(self, parent, *args, **kwds):
    super().__init__(parent, *args, **kwds)
    self.init_gui()
    
  def init_gui(self):
    splitter = wx.SplitterWindow(self)
    
    pan1 = wx.Panel(splitter, style = wx.BORDER_SUNKEN)
    tree = wx.TreeCtrl(pan1, wx.ID_ANY)
    pan1.SetBackgroundColour("yellow")

    pan2 = wx.Panel(splitter, style = wx.BORDER_SUNKEN)
    pan2.SetBackgroundColour("orange")
    stc = wx.stc.StyledTextCtrl(pan2, wx.ID_ANY)
    stc.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
    stc.SetMarginWidth(1, 40)
    stc.SetWrapMode(wx.stc.STC_WRAP_WORD)
    
    splitter.SplitVertically(pan1, pan2)
    
#    main_box = wx.BoxSizer(wx.HORIZONTAL)
#    main_box.Add(tree, 1,flag = wx.EXPAND|wx.ALL, border = 10)    
#    main_box.Add(stc, 3, flag = wx.EXPAND|wx.ALL, border = 10)
    
#    self.SetSizer(main_box)

  def About(self):
    pass
    
    
if __name__ == '__main__':
  app = wx.App()
  FinderFrame()
  app.MainLoop()

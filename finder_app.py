import wx

class FinderFrame(wx.Frame):
  
  def __init__(self, *args, **kwds):
    super().__init__(None, *args, **kwds)
    panel = FinderPanel(self)
    
    self.Show()
    
class FinderPanel(wx.Panel):

  def __init__(self, parent, *args, **kwds):
    super().__init__(parent, *args, **kwds)
    
    text = wx.TextCtrl(parent, style = wx.TE_MULTILINE)
    
    main_box = wx.BoxSizer(wx.VERTICAL)
    main_box.Add(text, 1, flag = wx.EXPAND)
    
if __name__ == '__main__':
  app = wx.App()
  FinderFrame()
  app.MainLoop()
  
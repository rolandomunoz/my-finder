import wx

class TextMultilineEntryDialog(wx.Dialog):

  def __init__(self, parent, *args, **kwds):
    super().__init__(parent, *args, **kwds)
    self.InitGUI()
    
  def InitGUI(self):
    # Widgets
    panel = wx.Panel(self)
    static_text = wx.StaticText(panel, wx.ID_ANY, 'Ingresa la lista de nombres de archivos que deseas buscar:')
    text_ctrl = wx.TextCtrl(panel, wx.ID_ANY, value = '', style= wx.TE_MULTILINE)
    
    #Layout
    main_box = wx.BoxSizer(wx.VERTICAL)
    main_box.Add(static_text, 0)
    main_box.Add(text_ctrl, 0)
    panel.SetSizer(main_box)
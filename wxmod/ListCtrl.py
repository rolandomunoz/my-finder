import wx

class ListCtrl(wx.ListCtrl):
  
  def GetColumnNames(self):
    column_names = list()
    n_columns = self.GetColumnCount()
    for index in range(n_columns):
      column_info = self.GetColumn(index)
      column_name = column_info.GetText()
      column_names.append(column_name)
    return column_names

  def GetSelectedItems(self):
    indexList = list()
    number_of_items = self.GetSelectedItemCount()
    item = self.GetFirstSelected()

    if item == -1:
      return []

    while not item == -1:
      indexList.append(item)
      item = self.GetNextSelected(item)
    return indexList

  def GetSelectedItemsText(self, column):
    item_list = list()
    number_of_items = self.GetSelectedItemCount()
    index = self.GetFirstSelected()

    if index == -1:
      return []

    while not index == -1:
      item_text = self.GetItemText(index, column)
      item_list.append(item_text)
      index = self.GetNextSelected(index)
    return item_list

  def GetAllItemsText(self, column):
    item_list = list()
    n_items = self.GetItemCount()
    for index in range(0, n_items):
      item = self.GetItemText(index, column)
      item_list.append(item)
    return item_list

  def SetSelectedItems(self, column, label):
    selected_items = self.GetSelectedItems()
    for index in selected_items:
      self.SetItem(index, column, label)

  def RemoveSelectedItems(self):
    selected_items = self.GetSelectedItems()
    selected_items.reverse()
    for item in selected_items:
      self.DeleteItem(item)

  def AppendRow(self, *args):
    last_index = self.GetItemCount()
    self.InsertItem(last_index, '')
    for column, value in enumerate(args):
      self.SetItem(last_index, column, str(value))

  def SetALLColumnsWidth(self, width):
    for col in range(self.GetColumnCount()):
      self.SetColumnWidth(col, width)

  def UnselectAll(self):
    indices = self.GetSelectedItems()
    for temp_index in indices:
      self.Select(temp_index, 0)
  
  def copy_to_clipboard(self, column_n, sep='\t'):
    '''
    Copy a column or all columns(table) to the clipboard.
    
    column_n (int): the column number to copy. If -1, then copy all columns. 
    '''
    if column_n > -1:
      item_list = self.GetAllItemsText(column_n)
      raw_text = '\n'.join(item_list)
    else:
      n_columns = self.GetColumnCount()
      column_names = self.GetColumnNames()

      table=list()
      for i_column in range(n_columns):
        column = self.GetAllItemsText(i_column)
        table.append(column)

      table = [sep.join(row) for row in zip(*table)]
      table.insert(0, sep.join(column_names))
      raw_text = '\n'.join(table)

    clipdata = wx.TextDataObject()
    clipdata.SetText(raw_text)
    wx.TheClipboard.Open()
    wx.TheClipboard.SetData(clipdata)
    wx.TheClipboard.Close()
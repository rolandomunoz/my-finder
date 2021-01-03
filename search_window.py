import wx
import wxmod
import finder
import os
import platform
import subprocess
import shutil
import dialogs

class SearchDialog(wx.Dialog):

  def __init__(self, parent, *args, **kwds):
    super().__init__(parent, size=(800,400), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, *args, **kwds)
    self.InitGUI()

  def InitGUI(self):
    # Widgets
    panel = wx.Panel(self)

    notebook = wx.Notebook(panel, style = wx.NB_FIXEDWIDTH)

    self.one_to_one_tab = FilesTab(notebook)
    notebook.AddPage(self.one_to_one_tab, 'Uno-a-uno')

    self.one_to_many_tab = FilesTab(notebook)
    notebook.AddPage(self.one_to_many_tab, 'Uno-a-varios')

    self.missing_files_tab = MissingFilesTab(notebook)
    notebook.AddPage(self.missing_files_tab, 'No encontrados')

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(notebook, 1, wx.ALL|wx.EXPAND, 5)
    panel.SetSizer(sizer)
    self.Layout()
    self.Show()

  def add_data(self, search_results):
    MISSING = 0
    ONE_TO_ONE = 1
    ONE_TO_MANY = 2
    missing_counter = 0
    one_to_one_counter = 0
    one_to_many_counter = 0

    for search_item in search_results:
      status = search_item.get_status()
      search_id = search_item.get_id()
      search_pattern = search_item.get_search_pattern()

      if status == MISSING:
        missing_counter+=1
        self.missing_files_tab.add_data(search_id, search_pattern, missing_counter)
        continue

      for filename, paths in search_item.result_items():
        for path in paths:
          if status == ONE_TO_ONE:
            one_to_one_counter+=1
            self.one_to_one_tab.add_data(search_id, search_pattern, one_to_one_counter, filename, path)
          elif status == ONE_TO_MANY:
            one_to_many_counter+=1
            self.one_to_many_tab.add_data(search_id, search_pattern, one_to_many_counter, filename, path)

      self.one_to_one_tab.report_duplicate_cases()
      self.one_to_one_tab.update_status_bar()

      self.one_to_many_tab.report_duplicate_cases()
      self.one_to_many_tab.update_status_bar()

class InverseSearchDialog(wx.Dialog):

  def __init__(self, parent, *args, **kwds):
    super().__init__(parent, size=(800,400), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, *args, **kwds)
    self.InitGUI()

  def InitGUI(self):
    # Widgets
    self.inverse_search_window = InverseFilesTab(self, ['ID', 'Nombre de archivo', 'Dirección'])
    self.Layout()

  def add_data(self, data):
    counter=0
    for filename, paths in data.items():
      for path in paths:
        counter+=1
        self.inverse_search_window.add_data(counter, filename, path)

class FilesTab(wx.Panel):
  '''
  A window containing all found files
  '''

  def __init__(self, parent, *args, **kwds):
    super().__init__(parent, *args, **kwds)
    self._COLUMN_NAMES = ['PatrónID', 'Patrón', 'ResultadoID', 'Nombre de archivo', 'Dirección']
    self._SEARCH_ID_COLUMN = 0
    self._PATTERN_COLUMN = 1
    self._RESULT_ID_COLUMN = 2
    self._FILENAME_COLUMN = 3
    self._PATH_COLUMN = 4

    self.InitGUI()

  def InitGUI(self):

    # Widgets
    self.list_ctrl = wxmod.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_HRULES)
    for index, column_name in enumerate(self._COLUMN_NAMES):
      self.list_ctrl.InsertColumn(index, column_name, width=wx.LIST_AUTOSIZE)

    self.tree_ctrl = wx.TreeCtrl(self, wx.ID_ANY)
    self.duplicate_root = self.tree_ctrl.AddRoot('Nombres duplicados (0)')

    clipboard_btn = wx.Button(self, wx.ID_ANY, 'Copiar tabla')
    self.copy_btn = wx.Button(self, wx.ID_ANY, 'Copiar')
    self.ecopy_btn = wx.Button(self, wx.ID_ANY, 'Copiar (e.)')
    self.ecopy_btn.Enable(False)
    self.move_btn = wx.Button(self, wx.ID_ANY, 'Mover')
    self.remove_btn = wx.Button(self, wx.ID_ANY, 'Eliminar')
    self.remove_btn.Enable(False)

    self.status_bar = wx.StatusBar(self, wx.ID_ANY)

    self.menu = wx.Menu()
    self.open_location_command = self.menu.Append(wx.ID_ANY, 'Abrir ubicación')

    # Binds
    self.Bind(wx.EVT_BUTTON, self.copy_to_clipboard, clipboard_btn)
    self.Bind(wx.EVT_BUTTON, self.copy_files, self.copy_btn)
    self.Bind(wx.EVT_BUTTON, self.move_files, self.move_btn)

    self.Bind(wx.EVT_MENU, self.open_location, self.open_location_command)
    self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_popup_menu)
    self.tree_ctrl.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.select_item)

    # Layout
    button_group1 = wx.StaticBoxSizer(wx.VERTICAL, self, 'Portapapeles:')
    button_group1.Add(clipboard_btn, 0, wx.EXPAND)

    button_group2 = wx.StaticBoxSizer(wx.VERTICAL, self, 'Archivos:')
    button_group2.Add(self.copy_btn, 0, wx.EXPAND)
    button_group2.Add(self.ecopy_btn, 0, wx.EXPAND)
    button_group2.Add(self.move_btn, 0, wx.EXPAND)
    button_group2.Add(self.remove_btn, 0, wx.EXPAND)

    right_panel = wx.BoxSizer(wx.VERTICAL)
    right_panel.Add(button_group1, 0, wx.EXPAND)
    right_panel.Add(button_group2, 0, wx.EXPAND)

    panel = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Resultados:')
    panel.Add(self.list_ctrl, 5, wx.ALL|wx.EXPAND, 1)
    panel.Add(right_panel, 1, wx.ALL|wx.EXPAND, 1)

    observation_panel = wx.StaticBoxSizer(wx.VERTICAL, self, 'Detalles:')
    observation_panel.Add(self.tree_ctrl, 1, wx.EXPAND)

    main_sizer= wx.BoxSizer(wx.VERTICAL)
    main_sizer.Add(panel, 2, wx.EXPAND)
    main_sizer.Add(observation_panel, 1, wx.EXPAND)
    main_sizer.Add(self.status_bar, 0, wx.EXPAND)
    self.SetSizer(main_sizer)

  def update_status_bar(self):
    n_items = self.list_ctrl.GetItemCount()
    self.status_bar.SetStatusText('Archivos encontrados: {}'.format(n_items))

  def add_data(self, *args):
    self.list_ctrl.AppendRow(*args)
    self.list_ctrl.SetALLColumnsWidth(wx.LIST_AUTOSIZE_USEHEADER)

  def show_popup_menu(self, event):
    number_of_items = self.list_ctrl.GetSelectedItemCount()
    enable_value = True if number_of_items == 1 else False
    self.open_location_command.Enable(enable_value)
    self.PopupMenu(self.menu)

  def open_location(self, event):
    index = self.list_ctrl.GetFirstSelected()
    fpath = self.list_ctrl.GetItemText(index, self._PATH_COLUMN)
    if platform.system() == 'Windows':
      fpath = os.path.normpath(fpath)
      subprocess.run(['explorer', '/select,', fpath])
    elif platform.system() == 'Linux':
      subprocess.run(['nautilus', fpath])

  def move_files(self, event):
    with wx.DirDialog(self, 'Selecciona la dirección donde deseas copiar tus archivos', "",
      wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST) as dlg:
      if not dlg.ShowModal() == wx.ID_OK:
        return

      new_path = dlg.GetPath()
      file_paths = self.list_ctrl.GetAllItemsText(self._PATH_COLUMN)

      # Duplicate behavior
      file_names = self.list_ctrl.GetAllItemsText(self._FILENAME_COLUMN)
      if self.is_any_duplicate(file_names):
        msg = 'Algunos archivos se sobrescribirán ya que comparten el mismo nombre'
        wx.MessageBox(msg, 'Mensaje', wx.OK|wx.ICON_INFORMATION)

      for fsrc in file_paths:
        shutil.move(fsrc, new_path)

  def ecopy_files(self, event):
    with wx.DirDialog(None, 'Selecciona la dirección donde deseas copiar tus archivos', "",
      wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST) as dlg:
      if not dlg.ShowModal() == wx.ID_OK:
        return

      new_path = dlg.GetPath()
      file_paths = self.list_ctrl.GetAllItemsText(self._PATH_COLUMN)
      search_ids = self.list_ctrl.GetAllItemsText(self._ID_COLUMN)
      for path, search_id in zip(file_paths, search_ids):
        pass

  def copy_files(self, event):
    with wx.DirDialog(None, 'Selecciona la dirección donde deseas copiar tus archivos', "",
      wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST) as dlg:
      if not dlg.ShowModal() == wx.ID_OK:
        return

      new_path = dlg.GetPath()
      file_paths = self.list_ctrl.GetAllItemsText(self._PATH_COLUMN)

      # Duplicate behavior
      file_names = self.list_ctrl.GetAllItemsText(self._FILENAME_COLUMN)
      if self.is_any_duplicate(file_names):
        msg = 'Algunos archivos se sobrescribirán ya que comparten el mismo nombre'
        wx.MessageBox(msg, 'Mensaje', wx.OK|wx.ICON_INFORMATION)

      for fsrc in file_paths:
        fname= os.path.basename(fsrc)
        fdst = os.path.join(new_path, fname)
        try:
          shutil.copy2(fsrc, fdst)
        except:
          shutil.copy(fsrc, fdst)

  def copy_to_clipboard(self, event):
    with dialogs.ClipboardDialog(self, title='Copiar al portapapeles',
    choices = [
    ('BúsquedaID', 0),
    ('Patrón', 1),
    ('ResultadoID', 2),
    ('Nombre de archivo', 3),
    ('Dirección', 4),
    ('Todas las columnas', -1)
    ]) as dlg:
      dlg.ShowModal()

  def is_any_duplicate(self, items):
    items_set = set()
    for item in items:
      if item in items_set:
        return True
      else:
        items_set.add(item)
    return False

  def report_duplicate_cases(self):
    filenames = self.list_ctrl.GetAllItemsText(self._FILENAME_COLUMN)
    items_set = set()
    duplicate_cases = dict()

    for item_id, filename in enumerate(filenames, start=1):
      if filename in items_set:
        if filename in duplicate_cases:
          duplicate_cases[filename].append(item_id)
        else:
          first_item_id = filenames.index(filename) + 1
          duplicate_cases[filename] = [first_item_id, item_id]
      else:
        items_set.add(filename)

    for filename, items_id in duplicate_cases.items():
      filename_item = self.tree_ctrl.AppendItem(self.duplicate_root, filename)
      for item_id in items_id:
        self.tree_ctrl.AppendItem(filename_item, str(item_id))

  def select_item(self, event):
    current_item_id = self.tree_ctrl.GetSelection()
    if not self.tree_ctrl.ItemHasChildren(current_item_id):
      item_value = int(self.tree_ctrl.GetItemText(current_item_id))

      # Deselect everything
      self.list_ctrl.UnselectAll()

      # Select only the index
      self.list_ctrl.Select(item_value-1, 1)
      self.list_ctrl.Focus(item_value-1)

class MissingFilesTab(wx.Panel):

  '''
  A window containing a list of missing files
  '''

  def __init__(self, parent, *args, **kwds):
    super().__init__(parent, *args, **kwds)
    self._COLUMN_NAMES = ['ID', 'Patrón', 'BúsquedaID']
    self.InitGUI()

  def InitGUI(self):

    # Widgets
    self.list_ctrl = wxmod.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_HRULES)
    for index, column_name in enumerate(self._COLUMN_NAMES):
      self.list_ctrl.InsertColumn(index, column_name, width=wx.LIST_AUTOSIZE)

    self.tree_ctrl = wx.TreeCtrl(self, wx.ID_ANY)
    self.duplicate_root = self.tree_ctrl.AddRoot('Nombres duplicados (0)')

    clipboard_btn = wx.Button(self, wx.ID_ANY, 'Copiar tabla')
    self.status_bar = wx.StatusBar(self, wx.ID_ANY)

    # Binds
    self.Bind(wx.EVT_BUTTON, self.copy_to_clipboard, clipboard_btn)
    #self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_popup_menu)

    # Layout
    button_group1 = wx.StaticBoxSizer(wx.VERTICAL, self, 'Portapapeles:')
    button_group1.Add(clipboard_btn, 0, wx.EXPAND)

    right_panel = wx.BoxSizer(wx.VERTICAL)
    right_panel.Add(button_group1, 0, wx.EXPAND)

    panel = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Resultados:')
    panel.Add(self.list_ctrl, 5, wx.ALL|wx.EXPAND, 1)
    panel.Add(right_panel, 1, wx.ALL|wx.EXPAND, 1)

    observation_panel = wx.StaticBoxSizer(wx.VERTICAL, self, 'Detalles:')
    observation_panel.Add(self.tree_ctrl, 1, wx.EXPAND)

    main_sizer= wx.BoxSizer(wx.VERTICAL)
    main_sizer.Add(panel, 2, wx.EXPAND)
    main_sizer.Add(observation_panel, 1, wx.EXPAND)
    main_sizer.Add(self.status_bar, 0, wx.EXPAND)
    self.SetSizer(main_sizer)

  def copy_to_clipboard(self, event):
    with dialogs.ClipboardDialog(self, title='Copiar al portapapeles',
    choices = [('PatrónID', 0), ('Patrón', 1),('BúsquedaID', 0), ('Todas las columnas', -1)]) as dlg:
      dlg.ShowModal()

  def add_data(self, *args):
  
    self.list_ctrl.AppendRow(*args)
    self.list_ctrl.SetALLColumnsWidth(wx.LIST_AUTOSIZE_USEHEADER)

class InverseFilesTab(wx.Panel):

  def __init__(self, parent, column_names, *args, **kwds):
    super().__init__(parent, *args, **kwds)
    _ID_COLUMN = 0
    self._FILENAME_COLUMN = 1
    self._PATH_COLUMN = 2
    self._COLUMN_NAMES = column_names
    self.InitGUI()

  def InitGUI(self):
    # Widgets
    self.list_ctrl = wxmod.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_HRULES)
    for index, column_name in enumerate(self._COLUMN_NAMES):
      self.list_ctrl.InsertColumn(index, column_name)
    self.list_ctrl.SetColumnWidth(0, 40)
    self.list_ctrl.SetColumnWidth(1, 200)

    self.copy_table_btn = wx.Button(self, wx.ID_ANY, 'Copiar tabla')
    self.copy_btn = wx.Button(self, wx.ID_ANY, 'Copiar')
    self.move_btn = wx.Button(self, wx.ID_ANY, 'Mover')
    self.remove_btn = wx.Button(self, wx.ID_ANY, 'Eliminar')

    self.tree_ctrl = wx.TreeCtrl(self, wx.ID_ANY)
    self.duplicate_root = self.tree_ctrl.AddRoot('Resultados duplicados')

    self.status_bar = wx.StatusBar(self, wx.ID_ANY)

    self.menu = wx.Menu()
    self.open_location_command = self.menu.Append(wx.ID_ANY, 'Abrir ubicación')

    # Bind
    self.Bind(wx.EVT_BUTTON, self.copy_to_clipboard, self.copy_table_btn)
    self.Bind(wx.EVT_BUTTON, self.copy_files, self.copy_btn)
    self.Bind(wx.EVT_BUTTON, self.move_files, self.move_btn)

    self.Bind(wx.EVT_MENU, self.open_location, self.open_location_command)
    self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_popup_menu)
    self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.select_item)

    # Layout
    button_group1 = wx.StaticBoxSizer(wx.VERTICAL, self, 'Portapapeles:')
    button_group1.Add(self.copy_table_btn, 0, wx.EXPAND)

    button_group2 = wx.StaticBoxSizer(wx.VERTICAL, self, 'Archivos:')
    button_group2.Add(self.copy_btn, 0, wx.EXPAND)
    button_group2.Add(self.move_btn, 0, wx.EXPAND)
    button_group2.Add(self.remove_btn, 0, wx.EXPAND)

    right_panel = wx.BoxSizer(wx.VERTICAL)
    right_panel.Add(button_group1, 0, wx.EXPAND)
    right_panel.Add(button_group2, 0, wx.EXPAND)

    panel = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Resultados:')
    panel.Add(self.list_ctrl, 5, wx.ALL|wx.EXPAND, 1)
    panel.Add(right_panel, 1, wx.ALL|wx.EXPAND, 1)

    observation_panel = wx.StaticBoxSizer(wx.VERTICAL, self, 'Detalles:')
    observation_panel.Add(self.tree_ctrl, 1, wx.EXPAND)

    main_sizer= wx.BoxSizer(wx.VERTICAL)
    main_sizer.Add(panel, 5, wx.EXPAND)
    main_sizer.Add(observation_panel, 1, wx.EXPAND)

    main_sizer.Add(self.status_bar, 0, wx.EXPAND)
    self.SetSizer(main_sizer)

  def add_data(self, *args):
    self.list_ctrl.AppendRow(*args)
    self.list_ctrl.SetALLColumnsWidth(wx.LIST_AUTOSIZE_USEHEADER)

  def show_popup_menu(self, event):
    number_of_items = self.list_ctrl.GetSelectedItemCount()
    enable_value = True if number_of_items == 1 else False
    self.open_location_command.Enable(enable_value)
    self.PopupMenu(self.menu)

  def open_location(self, event):
    index = self.list_ctrl.GetFirstSelected()
    fpath = self.list_ctrl.GetItemText(index, self._PATH_COLUMN)
    if platform.system() == 'Windows':
      fpath = os.path.normpath(fpath)
      subprocess.run(['explorer', '/select,', fpath])
    elif platform.system() == 'Linux':
      subprocess.run(['nautilus', fpath])

  def move_files(self, event):
    with wx.DirDialog(self, 'Selecciona la dirección donde deseas copiar tus archivos', "",
      wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST) as dlg:
      if dlg.ShowModal() == wx.ID_OK:
        new_path = dlg.GetPath()
        file_paths = self.list_ctrl.GetAllItemsText(self._FILENAME_COLUMN)
        for fsrc in file_paths:
          shutil.move(fsrc, new_path)

  def copy_files(self, event):
    with wx.DirDialog(self, 'Selecciona la dirección donde deseas copiar tus archivos', "",
      wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST) as dlg:
      if dlg.ShowModal() == wx.ID_OK:
        new_path = dlg.GetPath()

        file_paths = self.list_ctrl.GetAllItemsText(self._FILENAME_COLUMN)
        for fsrc in file_paths:
          fname= os.path.basename(fsrc)
          fdst = os.path.join(new_path, fname)
          try:
            shutil.copy2(fsrc, fdst)
          except:
            shutil.copy(fsrc, fdst)

  def copy_to_clipboard(self, event):
    with dialogs.ClipboardDialog(self, title='Copiar al portapapeles',
    choices = [('BúsquedaID', 0),('Nombre de archivo', 1), ('Dirección', 2), ('Todas las columnas', -1)]) as dlg:
      dlg.ShowModal()

  def select_item(self, event):
    pass
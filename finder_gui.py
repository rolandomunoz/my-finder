import wx
import wxmod
import finder
import os
import shutil
import fnmatch
import platform
import search_window
import dialogs

class FinderFrame(wx.Frame):

  def __init__(self, *args, **kwargs):
    super().__init__(None, title = 'BuscadorMP', size=(800,400), *args, **kwargs)

    index_obj = finder.Index()

    panel = wx.Panel(self)
    notebook = wx.Notebook(panel, style = wx.NB_FIXEDWIDTH)

    indexTab = IndexTab(notebook, index_obj)
    notebook.AddPage(indexTab, 'Índice')

    searchTab = SearchTab(notebook, index_obj)
    notebook.AddPage(searchTab, 'Búsqueda')

    self.SetIcon(wx.Icon(os.path.join('img', 'binoculars.ico')))

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(notebook, 1, wx.ALL|wx.EXPAND, 5)
    panel.SetSizer(sizer)
    self.Layout()
    self.Show()

class IndexTab(wx.Panel):

  def __init__(self, parent, index_obj, *args, **kwargs):
    super().__init__(parent)
    self.index_obj = index_obj
    self.init_GUI()

  def init_GUI(self):
    # Constants
    self._COLUMN_NAMES = ['ID', 'Dirección', 'Número de archivos']
    self._ID_COLUMN = 0
    self.PATH_COLUMN = 1
    self.COUNT_COLUMN = 2

    # widgets
    self.list_ctrl = wxmod.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_HRULES|wx.LC_VRULES)
    for index, column_name in enumerate(self._COLUMN_NAMES):
      self.list_ctrl.InsertColumn(index, column_name, width=wx.LIST_AUTOSIZE)

    self.add_btn = wx.Button(self, wx.ID_ANY, label = 'Agregar carpeta')
    self.update_btn = wx.Button(self, wx.ID_ANY, label='Actualizar')
    self.clear_all_btn = wx.Button(self, wx.ID_ANY, label = 'Borrar todo')

    summary_btn = wx.Button(self, wx.ID_ANY, label = 'Resumen')
    create_file_list_btn = wx.Button(self, wx.ID_ANY, label = 'Generar lista')
    check_sha256_btn = wx.Button(self, wx.ID_ANY, label='Validar SHA256')
    create_sha256_list_btn = wx.Button(self, wx.ID_ANY, 'Generar SHA256')
    
    self.status_bar = wx.StatusBar(self, wx.ID_ANY)

    # Binds
    self.Bind(wx.EVT_BUTTON, self.add_index_from_path, self.add_btn)
    self.Bind(wx.EVT_BUTTON, self.clear_all, self.clear_all_btn)
    self.Bind(wx.EVT_BUTTON, self.update, self.update_btn)
    self.Bind(wx.EVT_BUTTON, self.summary, summary_btn)
    self.Bind(wx.EVT_BUTTON, self.create_string_list, create_file_list_btn)   
    self.Bind(wx.EVT_BUTTON, self.check_sha256_files, check_sha256_btn)   
    self.Bind(wx.EVT_BUTTON, self.create_sha256_list, create_sha256_list_btn)   
    
    # Layout
    main_sizer = wx.BoxSizer(wx.VERTICAL)
    panel = wx.BoxSizer(wx.HORIZONTAL)

    manager_section = wx.StaticBoxSizer(wx.VERTICAL, self, 'Administrar lista:')
    manager_section.Add(self.add_btn, 0, wx.EXPAND)
    manager_section.Add(self.clear_all_btn, 0, wx.EXPAND)
    manager_section.Add(self.update_btn, 0, wx.EXPAND)

    analysis_section = wx.StaticBoxSizer(wx.VERTICAL, self, 'Analizar:')
    analysis_section.Add(summary_btn, 0, wx.EXPAND)
    analysis_section.Add(create_file_list_btn, 0, wx.EXPAND)
    analysis_section.Add(check_sha256_btn, 0, wx.EXPAND)
    analysis_section.Add(create_sha256_list_btn, 0, wx.EXPAND)

    right_panel = wx.BoxSizer(wx.VERTICAL)
    right_panel.Add(manager_section, 0, wx.EXPAND)
    right_panel.Add(analysis_section, 0, wx.EXPAND)

    panel.Add(self.list_ctrl, 5, wx.ALL|wx.EXPAND, 1)
    panel.Add(right_panel, 1, wx.ALL|wx.EXPAND, 1)

    main_sizer.Add(panel, 1, wx.ALL|wx.EXPAND)
    main_sizer.Add(self.status_bar, 0, wx.ALL|wx.EXPAND)
    self.SetSizer(main_sizer)

  def create_string_list(self, event):
    pass
 
  def create_sha256_list(self, event):
    pass

  def check_sha256_files(self, event):
    original_file_str = 'Archivos validados'
    modified_file_str = 'Archivos modificados'
    missing_pair_str = 'Archivos sin pareja'
  
    original_file_counter = 0
    modified_file_counter = 0
    missing_pair_counter = 0
    
    # Get the filenames with SHA256 extension
    pattern = '*SHA256'
    fnames = self.index_obj.index.keys()
    sha256_names = [fname for fname in fnames if fnmatch.fnmatchcase(fname, pattern)]
    
    # Check 
    for sha256_name in sha256_names:
      sha256_paths = self.index_obj.index[sha256_name]
      for sha256_path in sha256_paths:
        root, ext = os.path.splitext(sha256_path)
        if os.path.isfile(root):
          status = finder.check_sha256_file(sha256_path, root)
          if status:
            original_file_counter+=1
          else:
            modified_file_counter+=1
        else:
          missing_pair_counter+=1
            
    table = ((original_file_str, original_file_counter), (modified_file_str, modified_file_counter), (missing_pair_str, missing_pair_counter))

    with dialogs.TableInfoDialog(self, wx.ID_ANY, 'Validación de archivos SHA256', 'Resumen:', ['Concepto', 'Casos']) as dlg:
      dlg.add_data(table)
      dlg.ShowModal()
     
  def summary(self, event):
    extension_stat = dict()
    for filename, paths in self.index_obj.index.items():
      n_paths = len(paths)
      root, ext = os.path.splitext(filename)
      if ext in extension_stat:
        extension_stat[ext]+= n_paths
      else:
        extension_stat[ext] = n_paths

    dlg = dialogs.ExtensionSummary(self)
    dlg.add_data(extension_stat)
    dlg.Show()

  def get_folder(self):
    with wx.DirDialog(self, 'Selecciona la carpeta que deseas indexar', "",
      wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST) as dlg:
      if dlg.ShowModal() == wx.ID_OK:
        return dlg.GetPath()
      return

  def add_index_from_path(self, event):
    new_folder_path = self.get_folder()
    check = self.check_new_path(new_folder_path)
    if check:
      self.add_index(new_folder_path)

  def check_new_path(self, new_folder_path):
    message1 = 'La dirección seleccionada ya fue indexada anteriormente'
    message2 = 'La dirección seleccionada abarca al menos una dirección que ya ha sido indexada.\n¿Debería remplazarla?'
    message3 = 'La dirección seleccionada ya está incluida en otra dirección indexada.\n¿Debería eliminarla y solo considerar la dirección seleccionada?'

    window_title = 'Mensaje'
    if new_folder_path == None:
      return False

    folder_paths_list = self.list_ctrl.GetAllItemsText(self.PATH_COLUMN)

    # Check duplicates
    if new_folder_path in folder_paths_list:
      with wx.MessageDialog(None, message1, window_title, style=wx.ICON_EXCLAMATION) as dlg:
        if dlg.ShowModal():
          return False

    # Check if new_folder_path is included in folder_path
    remove_paths = [folder_path for folder_path in folder_paths_list if folder_path.startswith(new_folder_path)]
    if len(remove_paths):
      return self.check_dialog(message2, window_title, folder_paths_list, remove_paths)

    # Check if folder_path is included in new_folder_path
    remove_paths = [folder_path for folder_path in folder_paths_list if new_folder_path.startswith(folder_path)]
    if len(remove_paths):
      return self.check_dialog(message2, window_title, folder_paths_list, remove_paths)
    return True

  def check_dialog(self, message, window_title, items, remove_items):
    with wx.MessageDialog(None, message, window_title, style=wx.ICON_EXCLAMATION|wx.YES_NO) as dlg:
      if dlg.ShowModal() == wx.ID_YES:
        for remove_item in remove_items:
          items.remove(remove_item)
        self.clear_all(None)
        for item in items:
          self.add_index(item)
        return True
      return False

  def add_index(self, folder_path):
    n_files_old = self.index_obj.get_number_of_files()
    self.index_obj.append(folder_path)
    n_files_new = self.index_obj.get_number_of_files()

    n_files = n_files_new - n_files_old
    self.status_bar.SetStatusText('Archivos indexados: {}'.format(n_files_new))
    last_index = self.list_ctrl.GetItemCount()
    self.list_ctrl.AppendRow(last_index+1, folder_path, n_files)
    self.list_ctrl.SetALLColumnsWidth(wx.LIST_AUTOSIZE_USEHEADER)

  def clear_all(self, event):
    self.files = list()
    self.list_ctrl.DeleteAllItems()
    self.index_obj.clear()
    self.status_bar.SetStatusText('Archivos indexados: {}'.format(0))

  def update(self, event):
    folder_paths_list = self.list_ctrl.GetAllItemsText(self.PATH_COLUMN)
    self.clear_all(event)
    for folder_path in folder_paths_list:
      self.add_index(folder_path)

class SearchTab(wx.Panel):

  def __init__(self, parent, index_obj, *args, **kwargs):
    self.index_obj = index_obj
    super().__init__(parent)
    self.init_GUI()

  def init_GUI(self):
    # Constants
    self._COLUMN_NAMES = ['PatrónID', 'Patrón']
    self._ID_COLUMN = 0
    self._PATTERN_COLUMN = 1

    # Widgets
    self.list_ctrl = wxmod.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_HRULES)
    for index, column_name in enumerate(self._COLUMN_NAMES):
      self.list_ctrl.InsertColumn(index, column_name, width=wx.LIST_AUTOSIZE)

    self.tree_ctrl = wx.TreeCtrl(self, wx.ID_ANY)
    self.duplicate_root = self.tree_ctrl.AddRoot('Búsquedas que se repiten (0)')

    self.copy_to_clipboard_btn = wx.Button(self, wx.ID_ANY, label = 'Copiar &tabla')
    self.add_item_btn = wx.Button(self, wx.ID_ANY, label = '&Agregar')
    self.add_item_list_btn = wx.Button(self, wx.ID_ANY, label = 'Agregar &varios')
    self.clear_all_btn = wx.Button(self, wx.ID_ANY, label = 'Bo&rrar todo')
    search_and_replace_items_btn = wx.Button(self, wx.ID_ANY, label = 'Buscar y re&mplazar')

    self.search_all_btn = wx.Button(self, wx.ID_ANY, label = '&Buscar')
    self.isearch_all_btn = wx.Button(self, wx.ID_ANY, label = 'Buscar (&inverso)')

    self.search_all_btn.Enable(False)
    self.isearch_all_btn.Enable(False)

    self.status_bar = wx.StatusBar(self, wx.ID_ANY)

    self.menu = wx.Menu()
    self.mod_selected_command = self.menu.Append(wx.ID_ANY, 'Editar')
    self.remove_selected_command = self.menu.Append(wx.ID_ANY, 'Borrar')
    self.menu.AppendSeparator()
    self.search_selected_command = self.menu.Append(wx.ID_ANY, 'Buscar')

    # Binds
    self.Bind(wx.EVT_BUTTON, self.copy_to_clipboard, self.copy_to_clipboard_btn)
    self.Bind(wx.EVT_BUTTON, self.add_item, self.add_item_btn)
    self.Bind(wx.EVT_BUTTON, self.add_item_list, self.add_item_list_btn)
    self.Bind(wx.EVT_BUTTON, self.clear_all, self.clear_all_btn)
    self.Bind(wx.EVT_BUTTON, self.search_all, self.search_all_btn)
    self.Bind(wx.EVT_BUTTON, self.isearch_all, self.isearch_all_btn)
    self.Bind(wx.EVT_BUTTON, self.search_and_replace_items, search_and_replace_items_btn)

    self.Bind(wx.EVT_MENU, self.mod_selected_item, self.mod_selected_command)
    self.Bind(wx.EVT_MENU, self.remove_selected_items, self.remove_selected_command)
    self.Bind(wx.EVT_MENU, self.search_selected_items, self.search_selected_command)
    self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_popup_menu)
    self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.mod_selected_item)
    self.tree_ctrl.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.select_item)

    # Layout
    button_group0 = wx.StaticBoxSizer(wx.VERTICAL, self, 'Portapapeles:')
    button_group0.Add(self.copy_to_clipboard_btn, 0, wx.EXPAND)

    button_group1 = wx.StaticBoxSizer(wx.VERTICAL, self, 'Administrar lista:')
    button_group1.Add(self.add_item_btn, 0, wx.EXPAND)
    button_group1.Add(self.add_item_list_btn, 0, wx.EXPAND)
    button_group1.Add(self.clear_all_btn, 0, wx.EXPAND)
    button_group1.Add(search_and_replace_items_btn, 0, wx.EXPAND)

    button_group2 = wx.StaticBoxSizer(wx.VERTICAL, self, 'Búsqueda:')
    button_group2.Add(self.search_all_btn, 0, wx.EXPAND)
    button_group2.Add(self.isearch_all_btn, 0, wx.EXPAND)

    right_panel = wx.BoxSizer(wx.VERTICAL)
    right_panel.Add(button_group0, 0, wx.EXPAND)
    right_panel.Add(button_group1, 0, wx.EXPAND)
    right_panel.Add(button_group2, 0, wx.EXPAND)

    panel = wx.StaticBoxSizer(wx.HORIZONTAL, self, 'Lista de archivos a buscar:')
    panel.Add(self.list_ctrl, 5, wx.ALL|wx.EXPAND, 1)
    panel.Add(right_panel, 1, wx.ALL|wx.EXPAND, 1)

    main_sizer = wx.BoxSizer(wx.VERTICAL)
    main_sizer.Add(panel, 2, wx.ALL|wx.EXPAND)
    main_sizer.Add(self.tree_ctrl, 1, wx.EXPAND)
    main_sizer.Add(self.status_bar, 0, wx.EXPAND)

    self.SetSizer(main_sizer)

  def search_and_replace_items(self, event):
    dlg = dialogs.FindAndReplace(self, self._PATTERN_COLUMN)
    dlg.Show()

  def search_all(self, event):
    search_list = self.list_ctrl.GetAllItemsText(self._PATTERN_COLUMN)
    search_results = self.index_obj.search(search_list)
    with search_window.SearchDialog(self, title='Resultados de búsqueda') as dlg:
      dlg.add_data(search_results)
      dlg.ShowModal()

  def isearch_all(self, event):
    search_list = self.list_ctrl.GetAllItemsText(self._PATTERN_COLUMN)
    search_results = self.index_obj.inverse_search(search_list)
    with search_window.InverseSearchDialog(self, title='Resultados de búsqueda inversa') as dlg:
      dlg.add_data(search_results)
      dlg.ShowModal()

  def search_selected_items(self, event):
    search_list = self.list_ctrl.GetSelectedItemsText(self._PATTERN_COLUMN)
    search_results = self.index_obj.search(search_list)
    with search_window.SearchDialog(self, title='Resultados de búsqueda') as dlg:
      dlg.add_data(search_results)
      dlg.ShowModal()

  def add_item(self, event):
    with wx.TextEntryDialog(self, 'Agrega el nombre del archivo que deseas buscar. Puedes usar wildcards (* ? % [])', 'Agregar', '') as dlg:
      if dlg.ShowModal() == wx.ID_OK:
        item_list = dlg.GetValue()

        last_index = self.list_ctrl.GetItemCount()
        self.list_ctrl.AppendRow(last_index+1, item_list)
        self.list_ctrl.SetALLColumnsWidth(wx.LIST_AUTOSIZE_USEHEADER)
        self.search_all_btn.Enable(True)
        self.isearch_all_btn.Enable(True)
        self.status_bar.SetStatusText('Número de búsquedas: {}'.format(self.list_ctrl.GetItemCount()))
    self.check_items()

  def add_item_list(self, event):
    with wx.TextEntryDialog(self, 'Agrega los nombres de archivos que deseas buscar. Puedes usar wildcards (* ? % [])', 'Agregar varios', '', style= wx.TE_MULTILINE|wx.OK|wx.CANCEL) as dlg:
      if dlg.ShowModal() == wx.ID_OK:
        item_list = dlg.GetValue()
        for item in item_list.split('\n'):
          last_index = self.list_ctrl.GetItemCount()
          self.list_ctrl.AppendRow(last_index+1, item)
        self.list_ctrl.SetALLColumnsWidth(wx.LIST_AUTOSIZE_USEHEADER)
        self.search_all_btn.Enable(True)
        self.isearch_all_btn.Enable(True)
        self.status_bar.SetStatusText('Número de búsquedas: {}'.format(self.list_ctrl.GetItemCount()))
    self.check_items()

  def mod_selected_item(self, event):
    index = self.list_ctrl.GetFirstSelected()
    item_text = self.list_ctrl.GetItemText(index, 1)
    with wx.TextEntryDialog(self, 'Modificar item {}'.format(index+1), 'Modificar', item_text) as dlg:
      if dlg.ShowModal() == wx.ID_OK:
        new_item_text = dlg.GetValue()
        self.list_ctrl.SetItem(index, 1, new_item_text)
        self.check_items()

  def remove_selected_items(self, event):
    self.list_ctrl.RemoveSelectedItems()
    self.reset_id_count()
    self.check_items()

  def clear_all(self, event):
    self.files = list()
    self.list_ctrl.DeleteAllItems()
    self.check_items()
    self.search_all_btn.Enable(False)
    self.search_all_btn.Enable(False)
    self.status_bar.SetStatusText('Número de búsquedas: {}'.format(self.list_ctrl.GetItemCount()))

  def reset_id_count(self):
    # Reset items
    n_items = self.list_ctrl.GetItemCount()
    for index in range(0, n_items):
      item_id = index + 1
      self.list_ctrl.SetItem(index, 0, str(item_id))

  def check_items(self):
    item_list = self.list_ctrl.GetAllItemsText(self._PATTERN_COLUMN)
    duplicate_cases = self.check_duplicates(item_list)
    self.build_duplicate_cases_tree(duplicate_cases)

  def check_duplicates(self, item_list):
    # Count
    item_frequency = dict()
    report = list()

    for index, item in enumerate(item_list):
      if item in item_frequency:
        item_frequency[item][0] +=1
        item_frequency[item][1].append(index)
      else:
        item_frequency[item] = [1, [index]]

    for item, value in item_frequency.items():
      frequency, indices_list = value
      if frequency == 1:
        continue
      report.append((item, frequency, indices_list))

    return report

  def build_duplicate_cases_tree(self, duplicate_cases):
    n_duplicate_cases = len(duplicate_cases)
    self.tree_ctrl.CollapseAndReset(self.duplicate_root)
    self.tree_ctrl.SetItemText(self.duplicate_root, 'Búsquedas que se repiten ({})'.format(n_duplicate_cases))
    for case in duplicate_cases:
      search_pattern, frequency, id_list = case
      item_id = self.tree_ctrl.AppendItem(self.duplicate_root, search_pattern)
      for pattern_id in id_list:
        self.tree_ctrl.AppendItem(item_id, str(pattern_id+1))

  def select_item(self, event):
    item_id = self.tree_ctrl.GetSelection()
    item_value = int(self.tree_ctrl.GetItemText(item_id))
    if not self.tree_ctrl.ItemHasChildren(item_id):

      # Deselect everything
      indices = self.list_ctrl.GetSelectedItems()
      for temp_index in indices:
        self.list_ctrl.Select(temp_index, 0)

      # Select only the index
      self.list_ctrl.Select(item_value-1, 1)
      self.list_ctrl.Focus(item_value-1)

  def show_popup_menu(self, event):
    number_of_items = self.list_ctrl.GetSelectedItemCount()
    enable_value = True if number_of_items == 1 else False
    self.mod_selected_command.Enable(enable_value)
    self.PopupMenu(self.menu)

  def copy_to_clipboard(self, event):
    with dialogs.ClipboardDialog(self, title='Copiar al portapapeles', choices = [('Patrón', 1), ('Todas las columnas', -1)]) as dlg:
      dlg.ShowModal()

if __name__ == '__main__':
  app = wx.App()
  FinderFrame()
  app.MainLoop()
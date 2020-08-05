import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from tkinter import ttk
import subprocess
import csv
import shutil
import os
import glob
import fnmatch
import platform

class Finder(tk.Frame):
  
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    self.master = master
    self.app_config()
    self.create_widgets()
    
  def app_config(self):
    self.master.title('Finder-MP')
    if platform.system() == 'Windows':
      self.master.iconbitmap('img/mpfn.ico')
    #self.master.geometry('480x300')
    self.master.resizable(False, False)
  
  def create_widgets(self):
    # Notebook
    self.notebook = ttk.Notebook(self.master)
    self.notebook.pack(fill = tk.BOTH)
    
    ## Search Window
    searchWindow = tk.Frame(self.notebook)
    searchWindow.pack(fill = tk.BOTH)
    self.create_search_window(searchWindow)
    
    ## Index Window
    indexWindow = tk.Frame(self.notebook)
    indexWindow.pack(fill = tk.BOTH)
    self.create_index_window(indexWindow)

    ## About Window
    aboutWindow = tk.Frame(self.notebook)
    aboutWindow.pack(fill = tk.BOTH)
    self.create_about_window(aboutWindow)

    # Config Notebook
    self.notebook.add(indexWindow, text = 'Index')
    self.notebook.add(searchWindow, text = 'Search') 
    self.notebook.add(aboutWindow, text = 'About')
    
    self.notebook.tab(1, state="disabled")
    self.notebook.enable_traversal()

  def create_about_window(self, frame):
    text = tk.Text(frame, width = 60, height = 10, relief=tk.SUNKEN, border = 5, bg = '#f5f5f5')
    text.insert(tk.END, 'Ministerio Público - Oficina de Peritajes\n', ('title'))
    text.insert(tk.END, 'Área de Fonética y Acústica Forense\n\n', ('title'))
    text.insert(tk.END, 'Finder\n',('softwareName'))

    text.insert(tk.END, '\nCreado por Rolando Muñoz Aramburú (rolando.muar@gmail.com)\n', ('info'))    
    text.insert(tk.END, 'Fecha de creación: 10 de octubre de 2019\n', ('info'))
    text.insert(tk.END, 'Última actualización: 21 de marzo de 2020\n', ('info'))

    text.tag_configure('title', foreground='red', font =('Helvetica', 12), underline = True, justify = tk.CENTER)
    text.tag_configure('softwareName', foreground = 'blue', font =('Helvetica', 24), justify = tk.CENTER)
    text.tag_configure('info', justify = tk.CENTER)
    
    text.pack(fill = tk.BOTH)
    text.config(state = tk.DISABLED)
    
  def create_index_window(self, frame):
    buttonWidth = 10
    self.index_db = dict()
    self.index_path = tk.StringVar()
    self.index_deepSearch = tk.BooleanVar()
    self.index_fileSearch = tk.BooleanVar()
    self.index_folderSearch = tk.BooleanVar()
    self.index_exist = tk.StringVar()
    self.index_exist.set('Status: Unavailable')
    self.index_fileSearch.set(1)
    self.index_deepSearch.set(1)
    
    frame.grid_columnconfigure(0, weight= 1)  
    
    #Widgets
    labelField = tk.Label(frame, text = 'Create index from the following directory:')
    entryPath = tk.Entry(frame, width = 80, textvariable = self.index_path)
    buttonBrowse = tk.Button(frame, text = '...', width = int(buttonWidth*0.2), command = self._selectDirectory)
    checkDeepSearch = tk.Checkbutton(frame, text="Sub-folders as well", state = tk.DISABLED, variable= self.index_deepSearch)
    checkFileSearch = tk.Checkbutton(frame, text="Index file names", state = tk.DISABLED, variable= self.index_fileSearch)
    checkFolderSearch = tk.Checkbutton(frame, text="Index folder names", state = tk.DISABLED,variable= self.index_folderSearch)
    buttonCreateIndex = tk.Button(frame, text = 'Create Index', width = buttonWidth, command = self.createIndex)
    statusBar = tk.Label(frame, bd = 1, relief = tk.SUNKEN, textvariable = self.index_exist, anchor= tk.W)
    
    # Layout
    labelField.grid(column = 0, row = 0, sticky = tk.W)
    entryPath.grid(column = 0, row = 1, sticky = tk.W)
    buttonBrowse.grid(column = 1, row = 1, padx = 5, sticky = tk.W)
    checkDeepSearch.grid(column = 0, row = 2, sticky = tk.W)
    checkFileSearch.grid(column = 0, row = 3, sticky = tk.W)
    checkFolderSearch.grid(column = 0, row = 4, sticky = tk.W)
    buttonCreateIndex.grid(column = 0, row = 5)
    statusBar.grid(column = 0, columnspan = 2, row = 6, sticky = tk.W + tk.E)

    # Bind
    #frame.bind('<Control-i>', lambda event:self.run())
    
  def run(self):
    self.createIndex()
    
  def create_search_window(self, frame):
    buttonWidth = 10
    # Widgets
    label = tk.Label(frame, text = 'Search pattern:')
    self.searchWindow_text = tk.Text(frame, wrap = tk.NONE, height = 5, width = 60)
    self.searchWindow_button = tk.Button(frame, text = 'Find', width= buttonWidth, command = self.search)
 
    # Layout
    label.grid(column= 0, row = 0, sticky = tk.W)
    self.searchWindow_text.grid(column= 0, row = 1)
    self.searchWindow_button.grid(column=0, row = 2)
  
  def _selectDirectory(self):
    path = tk.filedialog.askdirectory()
    self.index_path.set(path)
  
  def _getQueryList(self):
    patternText = self.searchWindow_text.get('1.0', 'end-1c')
    return patternText.split('\n')
    
  def search(self):
    queryList= self._getQueryList()
    
    self.searchResults = list()
    for query in queryList:
      matchedKeyList = fnmatch.filter(self.index_db.keys(), query)
      fileList = [filePath for matchedKey in matchedKeyList for filePath in self.index_db[matchedKey]]        
      resultTuple = (query, fileList)
      self.searchResults.append(resultTuple)
      
    # Show results in View window
    viewWindows = ViewWindow(self.master, self.searchResults)
    
  def createIndex(self):
    path = self.index_path.get()
    deepSearch = self.index_deepSearch.get()
    fileSearch = self.index_fileSearch.get()
    folderSearch = self.index_folderSearch.get()

    folderName = os.path.basename(path)    
    path = os.path.join(path, '**') if deepSearch else os.path.join(path, '*')
    path = os.path.normpath(path)
  
    fileList = glob.glob(path, recursive = deepSearch)


    for f in fileList:
      fbasename = os.path.basename(f)
      isfile = os.path.isfile(f)
      
      if not isfile:
        continue
        
      if fbasename in self.index_db:
        self.index_db[fbasename].append(f)
      else:
        self.index_db[fbasename] = [f]

    self.index_exist.set('Status: created from ' + folderName)
    ## Actions
    # Active Search button
    self.notebook.tab(1, state = 'normal')
    
class ViewWindow(tk.Toplevel):
  
  def __init__(self, master, searchResults):
    # Variables
    self.searchResults = searchResults
    self.nQueries, self.nFoundQueries, self.nFoundItems, self.nDuplicates = self._stats(searchResults)

    # Windows
    self.top =  tk.Toplevel(master)
    self.app_config()
    self.create_widgets()

  def app_config(self):
    self.top.title('View')
    if platform.system() == 'Windows':
      self.top.iconbitmap('img/mpfn.ico')
    self.top.resizable(True, True)
    self.top.focus()
    
  def _stats(self, searchResults):
    nQueries = len(searchResults)
    nFoundQueries = 0
    nFoundItems = 0
    nDuplicates = 0
    fnameList = list()
    for query, fileList in searchResults:
      currentFnameList = [os.path.basename(f) for f in fileList]
      fnameList = fnameList + currentFnameList
  
      fileListLen = len(fileList)
      nFoundItems+= fileListLen
      if fileListLen > 0:
        nFoundQueries += 1
    nFiles = len(fnameList)
    nUniqueFiles = len(set(fnameList))
    nDuplicates = nFiles - nUniqueFiles
    return (nQueries, nFoundQueries, nFoundItems, nDuplicates)
    
  def create_widgets(self):
    frame_toolbar = tk.Frame(self.top, borderwidth = 2)
    frame_main = tk.Frame(self.top)
    frame_statusbar = tk.Frame(self.top, relief= tk.SUNKEN, bd=2)
    
    frame_toolbar.pack(side = tk.TOP, fill= tk.X)
    frame_main.pack(side = tk.TOP, fill= tk.BOTH, expand = True)
    frame_statusbar.pack(side = tk.TOP, fill =tk.X)
    
    self.create_toolbar(frame_toolbar)
    self.create_treeview_window(frame_main)
    self.create_statusbar(frame_statusbar)
    
    # Bind
    self.top.bind('<Control-w>', self.close_window)

  def create_toolbar(self, frame):
    buttonWidth = 15
    button1 = tk.Button(frame, text='Save Log', width = buttonWidth, relief = tk.RAISED, underline = 0, command = self.save_log)
    button2 = tk.Button(frame, text='Copy files', width = buttonWidth, relief = tk.RAISED, underline = 0, command = self.copy_files)
    button3 = tk.Button(frame, text='ECopy files', width = buttonWidth, relief = tk.RAISED, underline = 0, command = lambda: self.copy_files(fileEncapsulation = True))
    button4 = tk.Button(frame, text='Open Location', width = buttonWidth, relief = tk.RAISED, underline = 5, command = self.open_location)
    
    button1.pack(side=tk.LEFT, fill = tk.X, padx = 2, pady = 2)
    button2.pack(side=tk.LEFT, fill = tk.X, padx = 2, pady = 2)
    button3.pack(side=tk.LEFT, fill = tk.X, padx = 2, pady = 2)
    button4.pack(side=tk.LEFT, fill = tk.X, padx = 2, pady = 2)
    
  def create_treeview_window(self, frame):
    minwidth = 40
   # style = ttk.Style()
   # style.configure("mystyle.Treeview.Heading", font=('Calibri', 13,'bold'))
    self.tree = ttk.Treeview(frame, style="mystyle.Treeview")
    self.tree['columns'] = ('basename', 'fPath', 'query', 'queryID')
    
    self.tree.column('#0', minwidth = minwidth, stretch=True, anchor=tk.W)
    self.tree.column('basename', minwidth = minwidth, stretch =True)
    self.tree.column('fPath', minwidth = minwidth, stretch =True)
    self.tree.column('query', minwidth = minwidth, stretch =True)
    self.tree.column('queryID', minwidth = minwidth, stretch =True)
    
    self.tree.heading('#0', text = 'ItemID', anchor=tk.W)
    self.tree.heading('basename', text= 'Name', anchor=tk.W)
    self.tree.heading('fPath', text= 'Path', anchor=tk.W)
    self.tree.heading('query', text= 'Query', anchor=tk.W)
    self.tree.heading('queryID', text= 'QueryID', anchor=tk.W)


    itemID = 0
    queryID = 0
    for query, fileList in self.searchResults:
      queryID+=1
      if len(fileList) == 0:
        itemID+=1
        self.tree.insert('', 'end', text = itemID, values = ('', '', query, queryID), tags = ('red',))
        
      for fPath in fileList:
        itemID+=1
        basename = os.path.basename(fPath)
        self.tree.insert('', 'end', text = itemID, values = (basename, fPath, query, queryID), tags = ('green',))

    self.tree.tag_configure('red', background = "red")
    self.tree.tag_configure('green', background = "green")
    self.tree.pack(fill= tk.BOTH, expand = True, side= tk.LEFT, padx = (2,0), pady = 2)
    
    ## Add Scrollbar
    treeScrollBarY = ttk.Scrollbar(frame)
    treeScrollBarY.pack(fill= tk.Y, side=tk.LEFT)    
    self.tree.config(yscrollcommand=treeScrollBarY.set)
    treeScrollBarY.config(command=self.tree.yview)
    
    # Bind
    self.tree.bind('<Control-a>', self.shortcut_select_all)
    self.tree.bind('<Control-g>', self.shortcut_select_group)
    self.tree.bind('<Control-s>', lambda event:self.save_log())    
    self.tree.bind('<Control-c>', lambda event:self.copy_files(fileEncapsulation = False))
    self.tree.bind('<Control-e>', lambda event:self.copy_files(fileEncapsulation = True))
    self.tree.bind('<Control-l>', lambda event:self.open_location())

  def create_statusbar(self, frame):    
    ## Widgets
    label1 = tk.Label(frame, text = 'Queries: ')
    label2 = tk.Label(frame, text = 'Found queries: ')
    label3 = tk.Label(frame, text = 'Found items: ')
    label4 = tk.Label(frame, text = 'Duplicate names: ')
    
    stat1 = tk.Label(frame, text = '%d'%(self.nQueries))
    stat2 = tk.Label(frame, text = '%d'%(self.nFoundQueries))
    stat3 = tk.Label(frame, text = '%d'%(self.nFoundItems))
    stat4 = tk.Label(frame, text = '%d'%(self.nDuplicates))
    
    ## Layout
    label1.grid(row = 1, column = 0, sticky = tk.E)
    label2.grid(row = 2, column = 0, sticky = tk.E)
    label3.grid(row = 3, column = 0, sticky = tk.E)
    label4.grid(row = 4, column = 0, sticky = tk.E)
    
    stat1.grid(row = 1, column = 1, sticky = tk.E)
    stat2.grid(row = 2, column = 1, sticky = tk.E)
    stat3.grid(row = 3, column = 1, sticky = tk.E)
    stat4.grid(row = 4, column = 1, sticky = tk.E)
    
  def open_location(self):
    if platform.system() == 'Windows':
      for item in self.tree.selection():
        fpath = self.tree.item(item, 'values')[1]
        subprocess.run(['explorer', '/select,', fpath])

  def save_log(self):
    logPath = filedialog.asksaveasfilename(title = 'Save log', initialfile = 'log.csv', filetypes = (("csv files","*.csv"),("all files","*.*")))
    if logPath == '':
      return None
    with open(logPath, mode = 'w', newline='') as csvfile:
      spamwriter = csv.writer(csvfile, delimiter = ',')
      itemList = self._get_selection()
      spamwriter.writerow(('itemID', 'Name', 'Path', 'Query', 'queryID'))
      for itemValues in itemList:
        spamwriter.writerow(itemValues)
 
  def copy_files(self, fileEncapsulation = False):
    title = 'ECopy files' if fileEncapsulation else 'Copy files'
    dstPath = filedialog.askdirectory(title = title, parent = self.top)
    if dstPath == '':
      return None
    itemList = self._get_selection()
    for itemID, fname, fsrc, query, queryID in itemList:
      if fname == '':
        continue
      currentDstPath = dstPath
      if fileEncapsulation:
        currentDstPath = os.path.join(currentDstPath, str(itemID))
        if not os.path.isdir(currentDstPath):
          os.mkdir(currentDstPath)
      fdst = os.path.join(currentDstPath, fname)
      shutil.copy2(fsrc, fdst)
    messagebox.showinfo(title = 'Copy files', message = 'Copy File... Done!', parent = self.top)
      
  def _get_selection(self):
    resultList = list()
    for item in self.tree.selection():
      itemID = self.tree.item(item, option = 'text')
      basename, fPath, query, queryID = self.tree.item(item, option = 'values')
      result = (itemID, basename, fPath, query, queryID)
      resultList.append(result)
    return resultList
    
  # Events
  def shortcut_select_group(self, event):
    rootItemSet = set()
    for item in self.tree.selection():
      parentItem = self.tree.parent(item)
      parentItem = item if parentItem == '' else parentItem
      rootItemSet.add(parentItem)
    
    selectedItems = list()
    for rootItem in rootItemSet:
      rootList = self.tree.get_children(rootItem)
      selectedItems = selectedItems + list(rootList)
    self.tree.selection_set(selectedItems)
 
  def shortcut_select_all(self, event):
    selectedItems = self.tree.get_children()
    self.tree.selection_set(selectedItems)

  def close_window(self, event):
    self.top.destroy()
  
if __name__ == '__main__':
  root = tk.Tk()
  app = Finder(root)
  app.mainloop()
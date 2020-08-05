import os
import glob
import fnmatch

class FileIndex:

  def __init__(self):
    self.index = dict()
    self._number_of_files = 0

  def build_index(self, folder_path, recursive):
    self.index = self._create(folder_path, recursive = recursive)

  def __len__(self):
    return self._number_of_files
  
  def _create(self, folder_path, recursive = False):
    ''''Create an index of all files in a folder path

    Parameters:
    folder_path (string):The folder path where files are stored
    recursive (boolean):Search in subfolders as well
    
    Returns:
    dict:a dictionary containing filenames as keys and diretories as values

   '''
    index = dict()
    self._number_of_files = 0
    folder_name = os.path.basename(folder_path)
    wild_card = '**' if recursive else '*'
    path = os.path.join(folder_path, wild_card)

    fileList = glob.glob(path, recursive = recursive)
    for f in fileList:
      fbasename = os.path.basename(f)
      isfile = os.path.isfile(f)
      
      if not isfile:
        continue
      
      self._number_of_files+= 1
      if fbasename in index:
        index[fbasename].append(f)
      else:
        index[fbasename] = [f]
    return index

  def clear_index(self):
    self.index = dict()

  def find_paths_by_pattern_list(self, pattern_list):
    finder = Finder(self.index)
    return finder.find_paths_by_pattern_list(pattern_list)
    
class Finder:
  
  def __init__(self, dict_index):
    self.index = dict_index

  def find_paths_by_pattern_list(self, pattern_list):
    ''''Find paths given a pattern list where each item is a pattern

    Parameters:
    pattern_list (list):a list of pattern

    Returns:
    dict:a list containing a tuple where the first element is the query ande the second is a dictionary containing all filenames and their directories. If a query is not found, then an empty dictionary is returned.

   '''
    results = list()
    for pattern in pattern_list:
      fname_list = self._get_list_of_filenames(pattern)
      search_content = {fname:self._get_list_of_paths(fname) for fname in fname_list}
      results.append((pattern, search_content))
      
    return results
  
  def _get_list_of_paths(self, filename):
    ''''Given an index dictionary (filename:[paths]), get a path list based on a filename

    Parameters:
    filename (string):a filename

    Returns:
    list:a list of all paths where the filename is located

   '''
    return self.index[filename]

  def _get_list_of_filenames(self, pattern):
    ''''Given an index dictionary (filename:[paths]), get all filenames(keys) that match a pattern

    Parameters:
    filename (string):a filename. You can use wildcards * ? []

    Returns:
    list:a list of all 

   '''
    return fnmatch.filter(self.index.keys(), pattern)
    
if __name__ == '__main__':
  folder_path = '/home/rolando/Documents/Repositorio-ADLP/ADLP'
  recursive = True
  queryList = ['f1_ac_abrir_tierra_con_pico*', '*casa*', 'oeatoaeoatretao']
  
  index = FileIndex()
  index.build_index(folder_path, recursive)
  a = index.find_paths_by_pattern_list(queryList)
  print(a)

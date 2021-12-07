import os
import pathlib
import glob
import fnmatch

class Index:

    def __init__(self):
        self.index = {}
        self.number_of_files = 0

    def __len__(self):
        return self.number_of_files

    def get_number_of_files(self):
        return len(self)

    def create(self, dir_, recursive= True, initialize= True):
        """
        Create an index of all files in a folder path

        Parameters
        ----------
        dir_ : pathlib.Path
            The path of the folder where files are stored.
        recursive : bool
            Search in subfolders as well.

        Returns
        -------
        dict:A dictionary containing filenames as keys and diretories as values
        """
        if initialize:
            self.clear()
        folder_path = pathlib.Path(dir_)
        folder_name = os.path.basename(folder_path)
        wild_card = '**' if recursive else '*'
        path = os.path.join(folder_path, wild_card)

        fileList = glob.glob(path, recursive = recursive)
        for f in fileList:
            fbasename = os.path.basename(f)
            isfile = os.path.isfile(f)

            if not isfile:
                continue

            self.number_of_files+= 1
            if fbasename in self.index:
                self.index[fbasename].append(f)
            else:
                self.index[fbasename] = [f]

    def append(self, folder_path, recursive= True):
        ''''Append the files from a folder to an existing index

        Parameters:
        folder_path (string):The folder path where files are stored
        recursive (boolean):Search in subfolders as well

        Returns:
        dict:A dictionary containing filenames as keys and diretories as values

        '''
        self.create(folder_path, recursive= recursive, initialize=False)

    def clear(self):
        self.index = {}
        self.number_of_files = 0

    def search(self, search_list):
        finder = Finder(self.index)
        return finder.search_by_list(search_list)

    def inverse_search(self, search_list):
        finder = Finder(self.index)
        return finder.inverse_search_by_list(search_list)

class Finder:

    def __init__(self, index):
        self.index = index

    def inverse_search_by_list(self, pattern_list):
        """
        Given a patterns list, find all paths that do not match that list

        Parameters
        ----------
        pattern_list : list
            A list of pattern

        Returns
        -------
        dict
            A dictionary containing the unmatched paths {filename}
        """
        new_index = self.index.copy()
        for pattern in pattern_list:
            fname_list = self.get_filenames(pattern)
            for fname in fname_list:
                new_index.pop(fname)
        return new_index

    def search_by_list(self, pattern_list):
        """
        Find paths given a pattern list

        Parameters
        ----------
        pattern_list:list
            A list of pattern

        Returns
        -------
        dict
            A list of tuples where [(pattern, {filename1:[path1, path2, path3]}), ...] or (pattern, {})

        """
        search_results = SearchResults()
        for pattern in pattern_list:
            fname_list = self.get_filenames(pattern)
            results = {fname:self.get_paths(fname) for fname in fname_list}
            search_item = SearchItem(pattern, results)
            search_results.append(search_item)
        return search_results

    def get_paths(self, filename):
        """
        Given an index dictionary list (filename:[paths]), get a path list based on a filename

        Parameters
        ----------
        filename : string
            A filename

        Returns
        -------
        list
            A list of all paths where the filename is located

        """
        if filename in self.index:
            return self.index[filename]
        return []

    def get_filenames(self, pattern):
        """
        Given an index dictionary list (filename:[paths]), get all filenames(keys)
        that match a pattern

        Parameters
        ----------
        filename : str
            A filename. You can use wildcards * ? []

        Returns
        -------
        list
            A list of all
        """
        return fnmatch.filter(self.index.keys(), pattern)

class SearchItem:
    """
    pattern -> filename1
                    -> path1
            -> filename2
                    -> path2
                    -> path3
            -> filename3
                    -> path4
    """
    def __init__(self, search_pattern = '', search_results = {}):
        self._search_pattern = search_pattern
        self._search_results = search_results
        self._search_id = None
        self._status = self.update_status()

    def __iter__(self):
        return iter(self._search_results)

    def paths(self):
        return iter(self._search_results.values())

    def filenames(self):
        return iter(self._search_results.keys())

    def result_items(self):
        return iter(zip(self.filenames(), self.paths()))

    def update_status(self):
        MISSING = 0
        ONE_TO_ONE = 1
        ONE_TO_MANY = 2

        results_len = len(self._search_results)

        if results_len == 0:
            return MISSING
        elif results_len == 1:
            return ONE_TO_ONE
        elif results_len > 1:
            return ONE_TO_MANY

    def set_id(self, search_id):
        self._search_id = search_id

    def set_search_item(self, pattern, search_results):
        self._pattern = pattern
        self._search_results = search_results
        self._status = self.update_status()

    def get_total_number_of_paths(self):
        paths_counter = 0
        for filename, paths in self.result_items():
            for path in paths:
                paths_counter+=1
        return paths_counter

    def get_number_of_filenames(self):
        return len(self._search_results)

    def get_all_paths(self):
        paths = list()
        for filename, temp_paths in self.result_items():
            paths.extend(temp_paths)
        return paths

    def get_paths(self, filename):
        try:
            return self._search_results[filename]
        except:
            return []

    def get_filenames(self):
        filenames = list()
        for filename, paths in self.result_items():
            filenames.append(filename)
        return filenames

    def get_search_pattern(self):
        return self._search_pattern

    def get_status(self):
        return self._status

    def get_id(self):
        return self._search_id

    def get_duplicates(self):
        duplicate_cases = list()
        for filename, paths in self.result_items():
            if len(paths) > 1:
                duplicate_cases.append((self._search_id, filename))
        return duplicate_cases

class SearchResults:

    def __init__(self):
        self._results = list()
        self._count = 0

    def __iter__(self):
        return iter(self._results)

    def append(self, search_item_obj):
        self._count+= 1
        search_item_obj.set_id(self._count)
        self._results.append(search_item_obj)

    def duplicate_cases(self):
        pass

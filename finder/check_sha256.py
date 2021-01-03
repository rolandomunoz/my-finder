'''
  Written by Rolando Muñoz (2019-10-24)
  Description: Compare SHA256
'''
import os
import argparse
import hashlib

def check_sha256_file(sha256_path, path):
  freader = SHA256FileReader(sha256_path)
  sha256 = freader.get_sha256()

  fcalc = SHA256Calculator(path)
  sha256_calc = fcalc.get_sha256()
  
  if sha256 == sha256_calc:
   return True
  else:
    return False

class SHA256Calculator:

  def __init__(self, path):
    self.calculate(path)
  
  def calculate(self, path):
    sha256_hash = hashlib.sha256()
    
    with open(path, "rb") as f:
      for byte_block in iter(lambda: f.read(4096), b""):
        sha256_hash.update(byte_block)
      self.sha256 = sha256_hash.hexdigest()
   
  def get_sha256(self):
    return self.sha256
    
class SHA256FileReader:
  
  def __init__(self, path):
    self.parse(path)
  
  def parse(self, path, normalize=True):
    with open(path, "r") as f:
      hash_str = f.readline()
      hash_str = hash_str.rstrip()

      if not hash_str.index(' '):
        hash_str = hash_str + ' '

      self.sha256, self.fname = hash_str.split(' ', 1)
      if normalize:
        self.sha256 = self.sha256.lower()

  def get_sha256(self):
    return self.sha256
    
  def get_filename(self):
    return self.fname

#!/usr/bin/env python

from csv import reader
from argparse import ArgumentParser

# call with a csv iterator that returns rows as lists
def get_csv_rows(csv_iter):
  header_row = None
  for row in csv_iter:
    if header_row is None:
      # first line
      header_row = row
    else:
      # build a hash
      for i in range(len(header_row)):
        if (i < 
    


if __name__=='__main__':
  parser = ArgumentParser(description='Count devices from an FA pullsheet')
  parser.add_argument('file', dest='file', help='the pullsheet')
  

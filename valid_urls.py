import csv

"""
  valid_urls.csv

  A list of urls that are valid for the 2nd pass of the algorithm
  where we allow directory listings (i.e. urls with a path containing multiple folders)
"""

def get_valid_urls():
  ls = []
  with open('overrides/valid_urls.csv', newline='') as csvfile:
    url_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    header = True
    for row in url_reader:
      if header:
        header = False
      else:
        item = ''.join(row)
        ls.append(item)
  return ls


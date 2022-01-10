import csv


def get_overriden_entities():
  map = {}
  with open('overrides/overriden_entities.csv', newline='') as csvfile:
    url_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    header = True
    for row in url_reader:
      if header:
        header = False
      else:
        map[row[0]] = row[1]
  return map


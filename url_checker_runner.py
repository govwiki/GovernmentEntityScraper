from url_checker import getUrlResults


""" Check urls of the Texas local governments spreadsheet """
results = getUrlResults('Texas Local Governments.xlsx', 'A', 'Y', debug=True)
print(results)

import csv


timestamp_file = open('Y:/DATA/derivatives/eyetracking/header.csv')
time_reader = csv.reader(timestamp_file)
headers = list(time_reader)
print(headers)

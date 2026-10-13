import csv

with open('evaluation_dataset.csv','r',newline='',) as csv_file:

    reader = csv.DictReader(csv_file,delimiter='|')
    print(type(reader))
    for row in reader:
        print(row)
        print()
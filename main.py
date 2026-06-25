import csv

config = "./input/config.csv"

with open(config) as config_file:
    config_reader = csv.reader(config_file)
    next(config_reader)  # skip header
    for row in config_reader:
        print(row)

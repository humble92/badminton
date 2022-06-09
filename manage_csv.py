import csv


def save_csv(filename, json):
    filepath = f'data/output/csv/{filename}.csv'
    file = open(filepath, mode="w")
    writer = csv.writer(file)
    writer.writerow(["location", "day", "timeslot", "age", "url"])
    for o in json:
        writer.writerow(o.values())
    return

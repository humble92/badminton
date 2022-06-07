import csv

def save_csv(filename, json):
    filepath = f'programs_data/csv/{filename}.csv'
    file = open(filepath, mode="w")
    writer = csv.writer(file)
    writer.writerow(["location", "day", "timeslot", "age", "url"])
    for o in json:
        writer.writerow(o.values()) #list(o.values())
    return

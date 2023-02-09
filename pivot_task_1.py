import csv


res_data = []

with open('revenue.csv', 'r') as csv_read:
    csv_reader = csv.reader(csv_read, delimiter=',')
    header = next(csv_reader)

    for item in csv_reader:
        for index, val in enumerate(item):
            if index == 0:
                continue

            res_data.append(
                {
                    'opportunityId': item[0],
                    'date': header[index],
                    'revenue': val
                }
            )

with open('revenue_new.csv', 'w', newline="") as new_csv:
    fieldnames = ['opportunityId', 'date', 'revenue']
    csvwriter = csv.DictWriter(new_csv, fieldnames=fieldnames)
    csvwriter.writeheader()
    csvwriter.writerows(res_data)

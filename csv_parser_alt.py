import csv
import sys

domain_col_name = "Value"

with open("subjects.csv", "r") as f:
    domain_list = []

    data = csv.DictReader(f)
    for row in data:
        domain_list.append(row[domain_col_name].strip())

    print(domain_list)

    print(f"Total subjects parsed: {len(domain_list)}")

    with open("subjects.txt", "w") as s:
        for item in domain_list:
            s.write(item.strip())
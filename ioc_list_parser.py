import csv

domain_col_name = "Value"
domain_list = []

with open("alternate.csv", "r") as f:
  data = csv.DictReader(f)
  for row in data:
      domain_list.append(row[domain_col_name].strip())
  
  print(domain_list)
    
  print(f"Total items to process: {len(domain_list)}")
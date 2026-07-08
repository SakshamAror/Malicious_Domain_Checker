import csv
import sys

domain_col_name = "email ID"
file = "emails.csv"

def valid(sub):
    if '.' in sub:
        return True
    
    for char in sub:
        if ((ord(char) <= 57 and ord(char) >= 48) or 
                (ord(char) >= 65 and ord(char) <= 90) or 
                (ord(char) >= 97 and ord(char) <= 122)):
            return True
    
    return False

def main():
    with open(file, "r") as f:
        domain_list = []
        rejected_list = []

        data = csv.DictReader(f)
        for row in data:
            for dom in row[domain_col_name].split(";"):
                split = dom.strip().split("@")
                if len(split) == 2 and split[1] not in domain_list:
                    if valid(split[1]): 
                        domain_list.append(split[1])
                    else:
                        rejected_list.append(split[1])
                elif len(split) == 1 and split[0] not in domain_list:
                    if valid(split[0]): 
                        domain_list.append(split[0])
                    else:
                        rejected_list.append(split[0])

        print(f"Total subjects rejected: {len(rejected_list)}")
        print(rejected_list)
        print()
        print(f"Total subjects parsed: {len(domain_list)}")
        print(domain_list)

        with open("subjects.txt", "w") as s:
            for item in domain_list:
                s.write(item.strip() + "\n")

def cla(): # Command line arguments
    if len(sys.argv) < 1:
        print("File to parse not entered as command line argument")
        print("Usage: python csv_parser_emails.py (filepath to a subjects.csv containing emails with suspicious domains) (col name)")
        quit()
    
    file_path = sys.argv[1]
    
    if not file_path.lower().endswith(".csv"):
        print(f"Error: '{file_path}' is not a .csv file")
        print("Usage: python csv_parser_emails.py (filepath to a subjects.csv containing emails with suspicious domains) (col name)")
        quit()
    
    global file
    file = file_path

    if len(sys.argv) < 2:
        print("Column name to parse not inputted")
        print("Usage: python csv_parser_emails.py (filepath to a subjects.csv containing emails with suspicious domains) (col name)")

    global domain_col_name
    domain_col_name = sys.argv[2]



cla()
main()
import re
import csv
from pathlib import Path
import FreeSimpleGUI as sg
import os 

def crate_dict():
    types = []
    dict_file = Path("columns.txt")
    if dict_file.is_file():
        with open("columns.txt", "r", encoding="utf-8") as f:
            for line in f:
                types.append(line.strip('\n'))
    else:
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Due"]
        with open("data.txt", "r", encoding="utf-8") as f:
            with open("columns.txt", "w", encoding="utf-8") as col_file:
                for line in f:
                    line = line.strip("\r\n")
                    if re.search(r"(\d{1,2}\.\d{1,2}\.\d{4})", line) is None:
                        if line.split(' ')[0] in months:
                            continue  
                        type = line.split('—')[0].rstrip()
                        types.append(type)
                types = list(set(types))
                for i in types:
                    col_file.write(i + '\n')
    # print(types)
    return types

def test():
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Due"]
    with open("data.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip("\r\n")
            if re.search(r"(\d{1,2}\.\d{1,2}\.\d{4})", line) is None:
                if line.split(' ')[0] in months:
                    continue 
                x = re.search(r"[0-9]+", line)
                line = x.group()
                print(line)

def create_csv(file_path: str):
    with open(file_path, "r", encoding="utf-8", newline='') as in_file:
        with open("out.csv", "w", encoding="utf-8", newline='') as csvfile:
            fieldnames = crate_dict()
            fieldnames.insert(0, "Date")
            fieldnames = [n.rstrip() for n in fieldnames]


            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval = 0, dialect='excel')
            writer.writeheader()
            new_row = {}
            months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Due"]
            for line in in_file:
                line = line.strip("\r\n")
                if re.search(r"(\d{1,2}\.\d{1,2}\.\d{4})", line):
                    if new_row:
                        print(new_row)
                        writer.writerow(new_row)
                        new_row = {}
                    # new_row.append({"Date": line})
                    new_row["Date"] = line
                else:
                    if line.split(' ')[0] in months:
                        continue
                    if line.split('—')[0].rstrip() not in fieldnames:
                        print("New type of loss appeared: " + line.split('—')[0].rstrip() + "\n Ask the dev for futher guidance on how to proceed.")
                    # new_row.append({line.split('—') [0]: line})
                    x = re.search(r"[0-9]+", line)
                    number = x.group()
                    new_row[line.split('—')[0].rstrip()] = number
            writer.writerow(new_row)
        cwd = os.getcwd()
        return cwd + "\\out.csv"
        # sg.save_to_disk("out.csv")

def main():
    # columns = crate_dict()
    # crate_dict()
    # create_csv()
    # test()

    sg.theme('DarkAmber')
    layout = [  [sg.Text('Choose an input file:'), sg.FileBrowse(file_types=(("Text files", "*.txt"),))],
                [sg.Button('Ok'), sg.Button('Cancel')],
                 [sg.Output(size=(80, 10))] ]

    window = sg.Window('RusMinus .csv creator', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
            break
        if event == 'Ok':
            # print('You entered ', values['Browse'])
            path = create_csv(values['Browse'])
            print('File created: ' + path)
    window.close()


if __name__ == "__main__":
    main()

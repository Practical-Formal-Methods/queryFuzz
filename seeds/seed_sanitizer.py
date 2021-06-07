
import os
from termcolor import colored
from queryfuzz.utils.file_operations import create_file, read_file

def get_all_dl_files(path):
    all_files = list()
    for r,d,f in os.walk(path):
        for file in f:
            if file.find(".dl") != -1:
                all_files.append(os.path.join(r,file))
    return all_files

def sanitize(file_path):
    print(colored("sanitizing file: " + file_path, "green",  attrs=["bold"]))
    file_lines = read_file(file_path)
    new_file = []
    line_pointer1 = 0
    line_pointer2 = 0

    while True:
        if line_pointer1 >= len(file_lines):
            break
        new_line = ""
        if file_lines[line_pointer1] == "":
            new_file.append(file_lines[line_pointer1])
            line_pointer1 += 1
            continue
        if file_lines[line_pointer1][-1] == "," or file_lines[line_pointer1][-1] == "-":
            new_line = file_lines[line_pointer1]
            line_pointer2 = line_pointer1 + 1
            while True:
                if line_pointer2 == len(file_lines):
                    break
                new_line += " " + file_lines[line_pointer2]
                if file_lines[line_pointer2][-1] == ".":
                    line_pointer2 += 1
                    break
                line_pointer2 += 1
            new_file.append(new_line)
            line_pointer1 = line_pointer2
        else:
            new_file.append(file_lines[line_pointer1])
            line_pointer1 += 1
    for i in new_file:
        print(i)
    file_string = ""
    for i in new_file:
        file_string += i + "\n"
    create_file(file_string, file_path)



def sanitize_all_souffle_seeds():
    path_to_seeds = os.path.join(os.path.dirname(os.path.realpath(__file__)), "souffle")

    files = get_all_dl_files(path_to_seeds)
    for i in files:
        sanitize(i)

        


sanitize_all_souffle_seeds()

import re
import numpy as np
from numpy.linalg import inv
import math
import csv

bvh_file = "Product_Dance.bvh"

def identifier(scanner, token):  return "IDENT", token
def operator(scanner, token):    return "OPERATOR", token
def digit(scanner, token):       return "DIGIT", token
def open_brace(scanner, token):  return "OPEN_BRACE", token
def close_brace(scanner, token): return "CLOSE_BRACE", token
def column(scanner, token):  return "COLUMN", token
def space(scanner, token): return "SPACE", token

reserved      = [ "HIERARCHY", "ROOT", "OFFSET", "CHANNELS", "MOTION" ]
channel_names = [ "Xposition", "Yposition", "Zposition",  "Zrotation", "Xrotation",  "Yrotation" ]

scanner = re.Scanner([
    (r"[a-zA-Z_]\w*", identifier),
    (r"-*[0-9]+(\.[0-9]+)?", digit),
    (r"}", close_brace),
    (r"{", open_brace),
    (r":", column),
    (r"\s+", space),
    ])

def read_data(bvh):

    CSV_DATA = []
    current_token = 0

    while (bvh[current_token] != ("IDENT", "Time")):
        current_token = current_token + 1

    current_token = current_token + 5

    while (current_token<len(bvh)):
        Frame_Data = []
        while ("\n" not in bvh[current_token][1]):
            if (bvh[current_token][0] == "DIGIT"):
                Frame_Data = Frame_Data + [bvh[current_token][1]]
            current_token = current_token + 1
        CSV_DATA = CSV_DATA + [Frame_Data]
        current_token = current_token + 1

    with open('data.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='excel')
        csvwriter.writerow([])
        for x in CSV_DATA:
        	csvwriter.writerow(x)


if __name__ == "__main__":
    bvh_read = open(bvh_file, "r")
    bvh = bvh_read.read()
    bvh_read.close()

    tokens, remainder = scanner.scan(bvh)

    read_data(tokens)


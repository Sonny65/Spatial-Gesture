import re
import numpy as np
from numpy.linalg import inv
import math

bvh_file = "Product_Dance.bvh"
bvh_out_file = "Dance_Skeleton.bvh"

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

# write out Abdomen first
def write_abdomen(bvh, bvh_out):

    # control the writing flow
    current_token = 0

    # write out the hip
    while (bvh[current_token] != ("IDENT", "Zrotation")):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    
    # write out Zrotation
    bvh_out.write(bvh[current_token][1])
    current_token = current_token + 1

    # skip the thighs
    while (bvh[current_token] != ("IDENT", "Abdomen")):
        current_token = current_token + 1

    # back to the joints
    current_token = current_token - 3

    # write out Abdomen
    bvh_out.write(bvh[current_token][1])
    current_token = current_token + 1

    # write the left hand
    while (bvh[current_token+2] != ("IDENT", "L2ProxPhalanx")):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    current_token = organize_finger(bvh,bvh_out,current_token)

    # write the right hand
    while (bvh[current_token+2] != ("IDENT", "R2ProxPhalanx")):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    current_token = organize_finger(bvh,bvh_out,current_token)

    # write out closing brace

    for x in range(0, 4):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1
        x

# reorganize fingers
def organize_finger(bvh,bvh_out,token):

    # control the parsing flow
    current_token = token

    # thumb first
    while ("1ProxPhalanx" not in bvh[current_token+2][1]):
        current_token = current_token + 1

    # write out the thumb

    while (bvh[current_token] != ("IDENT", "Site")):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    # write out closing brace

    brace_count = current_token

    while (current_token < brace_count + 20):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    bvh_out.write("    ")

    # keep track of the brace position

    brace_count = current_token - 1

    # write out rest of the fingers

    current_token = token

    while ("1ProxPhalanx" not in bvh[current_token+3][1]):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    # write out closing brace

    current_token = brace_count

    while (current_token < brace_count+8):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    return current_token


# write out thighs
def write_thighs(bvh, bvh_out):

    current_token = 0

    # go to thighs

    while (bvh[current_token] != ("IDENT", "JOINT")):
        current_token = current_token + 1

    current_token = current_token - 1

    # write thigh

    while (bvh[current_token + 3] != ("IDENT", "Abdomen")):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

# write out motion data



if __name__ == "__main__":
    bvh_file = open(bvh_file, "r")
    bvh = bvh_file.read()
    bvh_file.close()

    tokens, remainder = scanner.scan(bvh)

    bvh_out = open(bvh_out_file, "w")

    write_abdomen(tokens,bvh_out)

    write_thighs(tokens,bvh_out)

    # write out last brace

    bvh_out.write("\n}")

    bvh_out.close()

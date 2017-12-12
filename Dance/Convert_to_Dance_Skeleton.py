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

    prox = False

    while (bvh[current_token] != ("IDENT", "Site")):

        # change the order of the rotations

        if ("Prox" in bvh[current_token][1]):
            prox = True

        if (bvh[current_token+4] == ("IDENT", "Xrotation") and prox):
            bvh_out.write("CHANNELS 3 Yrotation Zrotation Xrotation")
            current_token = current_token + 9
            prox = False
        elif (bvh[current_token+4] == ("IDENT", "Xrotation")):
            bvh_out.write("CHANNELS 1 Zrotation")
            current_token = current_token + 9
            prox = False

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

    prox = False

    while ("1ProxPhalanx" not in bvh[current_token+3][1]):

        # change the order of the rotations

        if ("Prox" in bvh[current_token][1]):
            prox = True

        if (bvh[current_token+4] == ("IDENT", "Zrotation") and prox):
            bvh_out.write("CHANNELS 2 Yrotation Zrotation")
            current_token = current_token + 9
            prox = False
        elif (bvh[current_token+4] == ("IDENT", "Xrotation")):
            bvh_out.write("CHANNELS 1 Zrotation")
            current_token = current_token + 9
            prox = False

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

    # control the parsing flow

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
def write_motion(bvh, bvh_out):

    # control the parsing flow

    current_token = 0

    # write legend

    while (bvh[current_token] != ("IDENT", "MOTION")):
        current_token = current_token + 1

    while (bvh[current_token] != ("IDENT", "Time")):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    for x in range(0, 4):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1
        x

    write_frames(bvh, bvh_out, current_token)

def write_frames(bvh, hvh_out, token):

    # control the parsing flow

    current_token = token + 1

    frames = []

    # read frames

    while (current_token < len(bvh)):
        frame = []
        while ("\n" not in bvh[current_token][1]):
            if (bvh[current_token][0] == "DIGIT"):
                frame = frame + [bvh[current_token][1]]
            current_token = current_token + 1
        current_token = current_token + 1
        frames = frames + [frame]

    bvh_out.write("\n")

    for frame in frames:
        # print len(frame)
        write_single_frame(frame)
        bvh_out.write("\n")

def write_single_frame(frame):

    # write out hip

    for x in range(0, 6):
        bvh_out.write(frame[x])
        bvh_out.write(" ")
        x

    # write out abdomen

    for x in range(20, 41):
        bvh_out.write(frame[x])
        bvh_out.write(" ")
        x

    # write out left thumb:

    bvh_out.write(frame[78])
    bvh_out.write(" ")

    bvh_out.write(frame[79])
    bvh_out.write(" ")

    bvh_out.write(frame[77])
    bvh_out.write(" ")

    bvh_out.write(frame[82])
    bvh_out.write(" ")

    bvh_out.write(frame[85])
    bvh_out.write(" ")

    # write out rest of the fingers

    # L2

    bvh_out.write(frame[42])
    bvh_out.write(" ")

    bvh_out.write(frame[43])
    bvh_out.write(" ")

    bvh_out.write(frame[46])
    bvh_out.write(" ")

    bvh_out.write(frame[49])
    bvh_out.write(" ")

    # L3

    bvh_out.write(frame[51])
    bvh_out.write(" ")

    bvh_out.write(frame[52])
    bvh_out.write(" ")

    bvh_out.write(frame[55])
    bvh_out.write(" ")

    bvh_out.write(frame[58])
    bvh_out.write(" ")

    # L4

    bvh_out.write(frame[60])
    bvh_out.write(" ")

    bvh_out.write(frame[61])
    bvh_out.write(" ")

    bvh_out.write(frame[64])
    bvh_out.write(" ")

    bvh_out.write(frame[67])
    bvh_out.write(" ")

    # L5

    bvh_out.write(frame[69])
    bvh_out.write(" ")

    bvh_out.write(frame[70])
    bvh_out.write(" ")

    bvh_out.write(frame[73])
    bvh_out.write(" ")

    bvh_out.write(frame[76])
    bvh_out.write(" ")

    # write out right hand

    for x in range(86, 95):
        bvh_out.write(frame[x])
        bvh_out.write(" ")
        x

    # write out right thumb:

    bvh_out.write(frame[132])
    bvh_out.write(" ")

    bvh_out.write(frame[133])
    bvh_out.write(" ")

    bvh_out.write(frame[131])
    bvh_out.write(" ")

    bvh_out.write(frame[136])
    bvh_out.write(" ")

    bvh_out.write(frame[139])
    bvh_out.write(" ")

    # write out rest of the fingers

    # R2

    bvh_out.write(frame[96])
    bvh_out.write(" ")

    bvh_out.write(frame[97])
    bvh_out.write(" ")

    bvh_out.write(frame[100])
    bvh_out.write(" ")

    bvh_out.write(frame[103])
    bvh_out.write(" ")

    # R3

    bvh_out.write(frame[105])
    bvh_out.write(" ")

    bvh_out.write(frame[106])
    bvh_out.write(" ")

    bvh_out.write(frame[109])
    bvh_out.write(" ")

    bvh_out.write(frame[112])
    bvh_out.write(" ")

    # R4

    bvh_out.write(frame[114])
    bvh_out.write(" ")

    bvh_out.write(frame[115])
    bvh_out.write(" ")

    bvh_out.write(frame[118])
    bvh_out.write(" ")

    bvh_out.write(frame[121])
    bvh_out.write(" ")

    # R5

    bvh_out.write(frame[123])
    bvh_out.write(" ")

    bvh_out.write(frame[124])
    bvh_out.write(" ")

    bvh_out.write(frame[127])
    bvh_out.write(" ")

    bvh_out.write(frame[130])
    bvh_out.write(" ")

    # write out thighs

    for x in range(6, 20):
        bvh_out.write(frame[x])
        bvh_out.write(" ")
        x

if __name__ == "__main__":
    bvh_file = open(bvh_file, "r")
    bvh = bvh_file.read()
    bvh_file.close()

    tokens, remainder = scanner.scan(bvh)

    bvh_out = open(bvh_out_file, "w")

    write_abdomen(tokens,bvh_out)

    write_thighs(tokens,bvh_out)

    # write out last brace

    bvh_out.write("\n}\n")

    # write frames

    write_motion(tokens, bvh_out)

    bvh_out.close()

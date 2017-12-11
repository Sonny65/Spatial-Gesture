import re
import numpy as np
from numpy.linalg import inv
import math

bvh_file_body = "Sentences_1_variations - Body Solve.bvh"
bvh_file_left = "Sentences_1_variations - Left Hand Solve.bvh"
bvh_file_right = "Sentences_1_variations - Right Hand Solve.bvh"
bvh_out_file = "Product.bvh"
bvh_file = "Product.bvh"
bvh_out_file_assembled = "Product_Dance.bvh"

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

# print out hierachy

def print_hierarchy(bvh,bvh_l,bvh_r, bvh_out):

    # tokens to keep track of writting flow

    current_token = 0
    current_token_left = 0
    current_token_right = 0

    # print out orginal hierarchy

    while (bvh[current_token] != ("IDENT", "L_Wrist")):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    # using the lewrist from body

    while (bvh[current_token] != ("IDENT", "End")):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    # Left Hand

    left_space = bvh[current_token-1][1]
    bvh_out.write("JOINT ")

    while (bvh_l[current_token_left] != ("IDENT", "LeIndexMP")):
        current_token_left = current_token_left + 1

    # calculate the space

    bvh_out.write(bvh_l[current_token_left][1])
    current_token_left = current_token_left + 1
    left_space = left_space.replace(bvh_l[current_token_left][1], '')

    while (bvh_l[current_token_left] != ("IDENT", "MOTION")):
        bvh_out.write(bvh_l[current_token_left][1])
        if "\n" in bvh_l[current_token_left][1]:
            bvh_out.write(left_space)
        if bvh_l[current_token_left+2] == ("IDENT", "MOTION"):
            break
        current_token_left = current_token_left + 1

    current_token_left = current_token_left + 1

    while (bvh[current_token][0] != "CLOSE_BRACE"):
        current_token = current_token + 1
    current_token = current_token + 1

    while (bvh[current_token][0] != "CLOSE_BRACE"):
        current_token = current_token + 1
    current_token = current_token + 1

    while (bvh[current_token][0] != "CLOSE_BRACE"):
        current_token = current_token + 1
    current_token = current_token + 1

    # END OF LEFT HAND
    # RIGHT HAND

    while (bvh[current_token] != ("IDENT", "R_Wrist")):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    while (bvh[current_token] != ("IDENT", "End")):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    # calculate the space

    right_space = bvh[current_token-1][1]
    bvh_out.write("JOINT ")

    while (bvh_r[current_token_right] != ("IDENT", "RiIndexMP")):
        current_token_right = current_token_right + 1

    bvh_out.write(bvh_r[current_token_right][1])
    current_token_right = current_token_right + 1
    right_space = right_space.replace(bvh_r[current_token_right][1], '')

    while (bvh_r[current_token_right] != ("IDENT", "MOTION")):
        bvh_out.write(bvh_r[current_token_right][1])
        if "\n" in bvh_r[current_token_right][1]:
            bvh_out.write(right_space)
        if bvh_r[current_token_right+2] == ("IDENT", "MOTION"):
            break
        current_token_right = current_token_right + 1

    while (bvh[current_token][0] != "CLOSE_BRACE"):
        current_token = current_token + 1
    current_token = current_token + 1

    while (bvh[current_token][0] != "CLOSE_BRACE"):
        current_token = current_token + 1
    current_token = current_token + 1

    while (bvh[current_token][0] != "CLOSE_BRACE"):
        current_token = current_token + 1
    current_token = current_token + 1

    # finish the body

    while (bvh[current_token] != ("IDENT", "Time")):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    while ("\n" not in bvh[current_token][1]):
        bvh_out.write(bvh[current_token][1])
        current_token = current_token + 1

    bvh_out.write(bvh[current_token][1])

def analyse_hierarchy(bvh,bvh_l,bvh_r):

    # tokens to keep track of parsing flow

    current_token = 0
    current_token_left = 0
    current_token_right = 0

    data_index = 0
    data_index_mid = 0
    data_index_left = 0
    data_index_right = 0

    # Calculate the index in body

    while (bvh[current_token] != ("IDENT", "L_Wrist")):
        if "rotation" in bvh[current_token][1]:
            data_index = data_index + 1
        current_token = current_token + 1

    while (bvh[current_token] != ("IDENT", "End")):
        if "rotation" in bvh[current_token][1]:
            data_index = data_index + 1
        current_token = current_token + 1

    while (bvh[current_token] != ("IDENT", "R_Wrist")):
        if "rotation" in bvh[current_token][1]:
            data_index_mid = data_index_mid + 1
        current_token = current_token + 1

    while (bvh[current_token] != ("IDENT", "End")):
        if "rotation" in bvh[current_token][1]:
            data_index_mid = data_index_mid + 1
        current_token = current_token + 1

    # Calculate the left wrists

    while (bvh_l[current_token_left] != ("IDENT", "leHand")):
        current_token_left = current_token_left + 1

    while (bvh_l[current_token_left] != ("IDENT", "MOTION")):
        if "rotation" in bvh_l[current_token_left][1]:
            data_index_left = data_index_left + 1
        current_token_left = current_token_left + 1

    # Calculate the right wrists

    while (bvh_r[current_token_right] != ("IDENT", "riHand")):
        current_token_right = current_token_right + 1

    while (bvh_r[current_token_right] != ("IDENT", "MOTION")):
        if "rotation" in bvh_r[current_token_right][1]:
            data_index_right = data_index_right + 1
        current_token_right = current_token_right + 1

    return data_index, data_index_mid, data_index_left, data_index_right

def organize_frames(bvh,bvh_l,bvh_r):

    # store the frames

    body_frames = []
    left_frames = []
    right_frames = []

    body_frame = []
    left_frame = []
    right_frame = []

    # tokens to keep track of parsing flow

    current_token = 0
    current_token_left = 0
    current_token_right = 0

    # getting to data

    while (bvh[current_token] != ("IDENT", "Frame")):
        current_token = current_token + 1

    while ("\n" not in bvh[current_token][1]):
        current_token = current_token + 1

    while (bvh_l[current_token_left] != ("IDENT", "Frame")):
        current_token_left = current_token_left + 1

    while ("\n" not in bvh_l[current_token_left][1]):
        current_token_left = current_token_left + 1

    while (bvh_r[current_token_right] != ("IDENT", "Frame")):
        current_token_right = current_token_right + 1

    while ("\n" not in bvh_r[current_token_right][1]):
        current_token_right = current_token_right + 1

    # go to the first line of frames

    current_token = current_token + 1
    current_token_left = current_token_left + 1
    current_token_right = current_token_right + 1

    # creating the new frames

    while (current_token+1<len(bvh)):
        body_frame = []
        while ("\n" not in bvh[current_token][1]):
            if (bvh[current_token][0] == "DIGIT"):
                body_frame = body_frame + [float(bvh[current_token][1])]
            current_token = current_token + 1
        body_frames = body_frames + [body_frame]
        current_token = current_token + 1

    while (current_token_left+1<len(bvh_l)):
        left_frame = []
        while ("\n" not in bvh_l[current_token_left][1]):
            if (bvh_l[current_token_left][0] == "DIGIT"):
                left_frame = left_frame + [float(bvh_l[current_token_left][1])]
            current_token_left = current_token_left + 1
        left_frames = left_frames + [left_frame]
        current_token_left = current_token_left + 1

    while (current_token_right+1<len(bvh_r)):
        right_frame = []
        while ("\n" not in bvh_r[current_token_right][1]):
            if (bvh_r[current_token_right][0] == "DIGIT"):
                right_frame = right_frame + [float(bvh_r[current_token_right][1])]
            current_token_right = current_token_right + 1
        right_frames = right_frames + [right_frame]
        current_token_right = current_token_right + 1

    return body_frames, right_frames, left_frames

def parent_rotation(bvh, body_frames, right_frames, left_frames):

    # copy frames

    bf = []
    rf = []
    lf = []

    # get rid of positions from frames

    for x in body_frames:
        bf = bf + [x[3:]]

    for x in right_frames:
        rf = rf + [x[3:]]

    for x in left_frames:
        lf = lf + [x[3:]]

    # tokens to keep track of parsing flow
    
    current_token = 0
    joint = []

    # create parent

    # single frame

    body = []
    parent_left = []
    parent_right = []

    # all the frames

    body_all = []
    parent_left_all = []
    parent_right_all = []

    # creating parent from body file

    for frame in bf:

        current_token = 0

        body = []
        parent_left = []
        parent_right = []

        # root is a special case

        while (bvh[current_token] != ("IDENT", "L_Femur")):
            if "rotation" in bvh[current_token][1]:
                joint = joint + [bvh[current_token][1]]
                joint = joint + [frame.pop(0)]
            current_token = current_token + 1

        body = body + [joint]

        # skip legs

        while (bvh[current_token] != ("IDENT", "LowerBack")):
            if "rotation" in bvh[current_token][1]:
                frame.pop(0)
            current_token = current_token + 1

        current_token = current_token - 2

        # rest of the body

        while (bvh[current_token] != ("IDENT", "Neck")):
            if ("JOINT" in bvh[current_token][1] and "Neck" not in bvh[current_token+2][1]):
                joint = []
                current_token = current_token + 1
                while ("JOINT" not in bvh[current_token][1] and "Neck" not in bvh[current_token][1]):
                    if "rotation" in bvh[current_token][1]:
                        joint = joint + [bvh[current_token][1]]
                        joint = joint + [frame.pop(0)]
                    current_token = current_token + 1
                body = body + [joint]

            else:
                current_token = current_token + 1

        # skip head

        while (bvh[current_token] != ("IDENT", "End")):
            if "rotation" in bvh[current_token][1]:
                frame.pop(0)
            current_token = current_token + 1

        # Skip the "End"

        current_token = current_token + 1

        # left hand

        parent_left = parent_left + body

        while (bvh[current_token] != ("IDENT", "End")):
            if "JOINT" in bvh[current_token][1]:
                joint = []
                current_token = current_token + 1
                while ("JOINT" not in bvh[current_token][1] and "End" not in bvh[current_token][1]):
                    if "rotation" in bvh[current_token][1]:
                        joint = joint + [bvh[current_token][1]]
                        joint = joint + [frame.pop(0)]
                    current_token = current_token + 1
                parent_left = parent_left + [joint]

            else:
                current_token = current_token + 1

        # Skip the "End"

        current_token = current_token + 1

        # right hand

        parent_right = parent_right + body

        while (bvh[current_token] != ("IDENT", "End")):
            if "JOINT" in bvh[current_token][1]:
                joint = []
                current_token = current_token + 1
                while ("JOINT" not in bvh[current_token][1] and "End" not in bvh[current_token][1]):
                    if "rotation" in bvh[current_token][1]:
                        joint = joint + [bvh[current_token][1]]
                        joint = joint + [frame.pop(0)]
                    current_token = current_token + 1
                parent_right = parent_right + [joint]

            else:
                current_token = current_token + 1

        # Skip the "End"

        current_token = current_token + 1

        # put into all

        body_all = body_all + [body]

        parent_left_all = parent_left_all + [parent_left]

        parent_right_all = parent_right_all + [parent_right]

        return parent_left_all, parent_right_all

def transpose(bvh, body_frames):

    transpose_root = []

    body_transpose = []

    left_transpose = []

    right_transpose = []

    current_token = 0

    joint = []

    # root is a special case

    for x in body_frames:
        transpose_root = transpose_root + [x[:3]]

    # skip the legs

    while (bvh[current_token] != ("IDENT", "LowerBack")):
        current_token = current_token + 1

    # get body transpose

    while (bvh[current_token] != ("IDENT", "Neck")):
        joint = []
        if "OFFSET" in bvh[current_token][1]:
            while ("\n" not in bvh[current_token][1]):
                if (bvh[current_token][0] == "DIGIT"):
                    joint = joint + [bvh[current_token][1]]
                current_token = current_token + 1
            body_transpose = body_transpose + [joint]
        else:
            current_token = current_token + 1

    # skip the head

    while (bvh[current_token] != ("IDENT", "L_Collar")):
        current_token = current_token + 1

    # left hand

    left_transpose = left_transpose + body_transpose

    while (bvh[current_token] != ("IDENT", "R_Collar")):
        joint = []
        if "OFFSET" in bvh[current_token][1]:
            while ("\n" not in bvh[current_token][1]):
                if (bvh[current_token][0] == "DIGIT"):
                    joint = joint + [bvh[current_token][1]]
                current_token = current_token + 1
            left_transpose = left_transpose + [joint]
        else:
            current_token = current_token + 1

    # right hand

    right_transpose = right_transpose + body_transpose

    while (bvh[current_token] != ("IDENT", "MOTION")):
        joint = []
        if "OFFSET" in bvh[current_token][1]:
            while ("\n" not in bvh[current_token][1]):
                if (bvh[current_token][0] == "DIGIT"):
                    joint = joint + [bvh[current_token][1]]
                current_token = current_token + 1
            right_transpose = right_transpose + [joint]
        else:
            current_token = current_token + 1

    return transpose_root, left_transpose, right_transpose

def write_data(body_frames, left_frames, right_frames, data_index, data_index_mid, data_index_left, data_index_right, bvh_out):
    # print len(body_frames)
    for index in range(0,len(body_frames)):

        i = 0
        
        # write down xyz position of the root

        while (i < 3):
            bvh_out.write(str(body_frames[index].pop(0)))
            bvh_out.write(" ")
            i = i + 1

        # write down body

        i = 0

        while (i<(data_index-2)):
            bvh_out.write(str(body_frames[index].pop(0)))
            bvh_out.write(" ")
            i = i + 1

        i = 0

        while (i<2):
            bvh_out.write(str(body_frames[index].pop(0)-90))
            bvh_out.write(" ")
            i = i + 1

        # write down left hand

        i = 0

        while (i<9):
            left_frames[index].pop(0)
            i = i + 1

        while (left_frames[index]):
            bvh_out.write(str(left_frames[index].pop(0)))
            bvh_out.write(" ")
            i = i + 1

        # write down mid

        i = 0

        while (i<(data_index_mid-2)):
            bvh_out.write(str(body_frames[index].pop(0)))
            bvh_out.write(" ")
            i = i + 1

        i = 0

        while (i<2):
            bvh_out.write(str(body_frames[index].pop(0)+90))
            bvh_out.write(" ")
            i = i + 1

        # write down right hand

        i = 0

        while (i<9):
            right_frames[index].pop(0)
            i = i + 1

        while (right_frames[index]):
            bvh_out.write(str(right_frames[index].pop(0)))
            bvh_out.write(" ")
            i = i + 1
        
        bvh_out.write("\n")

# replace the joint names
def replace(bvh, bvh_out):
    
    # keep track of the parsing flow
    file_len = len(bvh)
    current_token = 0

    # start replacing
    while (current_token < file_len):
        # print(bvh(current_token))
        joint = new_joint_name(bvh[current_token][1])
        bvh_out.write(joint)
        current_token = current_token + 1

# create a dictionary for joint replacement
def new_joint_name(joint):
    return {
        'Root': 'Hip',
        'LowerBack': 'Abdomen',
        'Thorax': 'Chest',
        'Head': 'Head_comp',
        'L_Collar': 'Left_Collar',
        'L_Humerus': 'Left_Shoulder',
        'L_Elbow': 'Left_Forearm',
        'L_Wrist': 'Left_Hand',
        'R_Collar': 'Right_Collar',
        'R_Humerus': 'Right_Shoulder',
        'R_Elbow': 'Right_Forearm',
        'R_Wrist': 'Right_Hand',
        'L_Femur': 'Left_Thigh',
        'L_Tibia': 'Left_Shin',
        'L_Foot': 'Left_Foot',
        'L_Toe': 'Left_Toe',
        'R_Femur': 'Right_Thigh',
        'R_Tibia': 'Right_Shin',
        'R_Foot': 'Right_Foot',
        'R_Toe': 'Right_Toe',
        'LeIndexMP': 'L2ProxPhalanx',
        'LeIndexPIP': 'L2MidPhalanx',
        'LeIndexDIP': 'L2DistPhalanx',
        'LeMiddleMP': 'L3ProxPhalanx',
        'LeMiddlePIP': 'L3MidPhalanx',
        'LeMiddleDIP': 'L3DistPhalanx',
        'LeRingMP': 'L4ProxPhalanx',
        'LeRingPIP': 'L4MidPhalanx',
        'LeRingDIP': 'L4DistPhalanx',
        'LePinkyMP': 'L5ProxPhalanx',
        'LePinkyPIP': 'L5MidPhalanx',
        'LePinkyDIP': 'L5DistPhalanx',
        'LeThumbCMC': 'L1ProxPhalanx',
        'LeThumbMP': 'L1MidPhalanx',
        'LeThumbIP': 'L1DistPhalanx',
        'RiIndexMP': 'R2ProxPhalanx',
        'RiIndexPIP': 'R2MidPhalanx',
        'RiIndexDIP': 'R2DistPhalanx',
        'RiMiddleMP': 'R3ProxPhalanx',
        'RiMiddlePIP': 'R3MidPhalanx',
        'RiMiddleDIP': 'R3DistPhalanx',
        'RiRingMP': 'R4ProxPhalanx',
        'RiRingPIP': 'R4MidPhalanx',
        'RiRingDIP': 'R4DistPhalanx',
        'RiPinkyMP': 'R5ProxPhalanx',
        'RiPinkyPIP': 'R5MidPhalanx',
        'RiPinkyDIP': 'R5DistPhalanx',
        'RiThumbCMC': 'R1ProxPhalanx',
        'RiThumbMP': 'R1MidPhalanx',
        'RiThumbIP': 'R1DistPhalanx'
    }.get(joint, joint)

if __name__ == "__main__":
    bvh_file_body = open(bvh_file_body, "r")
    bvh_body = bvh_file_body.read()
    bvh_file_body.close()

    bvh_file_left = open(bvh_file_left, "r")
    bvh_left = bvh_file_left.read()
    bvh_file_left.close()

    bvh_file_right = open(bvh_file_right, "r")
    bvh_right = bvh_file_right.read()
    bvh_file_right.close()

    tokens_body, remainder = scanner.scan(bvh_body)
    tokens_left, remainder = scanner.scan(bvh_left)
    tokens_right, remainder = scanner.scan(bvh_right)

    bvh_out = open(bvh_out_file, "w")

    # print out hierachy

    print_hierarchy(tokens_body,tokens_left, tokens_right, bvh_out)

    # get the index

    data_index, data_index_mid, data_index_left, data_index_right = analyse_hierarchy(tokens_body,tokens_left, tokens_right)

    # extract frames

    body_frames, right_frames, left_frames = organize_frames(tokens_body,tokens_left, tokens_right)

    # get the wrist rotation

    parent_left_all, parent_right_all = parent_rotation(tokens_body, body_frames, right_frames, left_frames)

    # transpose

    transpose_root, left_transpose, right_transpose = transpose(tokens_body, body_frames)

    # write down transpose

    write_data(body_frames, left_frames, right_frames, data_index, data_index_mid, data_index_left, data_index_right, bvh_out)

    bvh_out.close()

    # change the name of the file

    bvh_file = open(bvh_file, "r")
    bvh = bvh_file.read()
    bvh_file.close()

    tokens, remainder = scanner.scan(bvh)

    bvh_out = open(bvh_out_file_assembled, "w")

    replace(tokens,bvh_out)

    bvh_out.close()

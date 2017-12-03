import re
import numpy as np
from numpy.linalg import inv
import math

bvh_file = "Product.bvh"
bvh_out_file = "Product_Dance.bvh"

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
        'LeIndexMP': 'L1ProxPhalanx',
        'LeIndexPIP': 'L1MidPhalanx',
        'LeIndexDIP': 'L1DistPhalanx',
        'LeMiddleMP': 'L2ProxPhalanx',
        'LeMiddlePIP': 'L2MidPhalanx',
        'LeMiddleDIP': 'L2DistPhalanx',
        'LeRingMP': 'L3ProxPhalanx',
        'LeRingPIP': 'L3MidPhalanx',
        'LeRingDIP': 'L3DistPhalanx',
        'LePinkyMP': 'L4ProxPhalanx',
        'LePinkyPIP': 'L4MidPhalanx',
        'LePinkyDIP': 'L4DistPhalanx',
        'LeThumbCMC': 'L5ProxPhalanx',
        'LeThumbMP': 'L5MidPhalanx',
        'LeThumbIP': 'L5DistPhalanx',
        'RiIndexMP': 'R1ProxPhalanx',
        'RiIndexPIP': 'R1MidPhalanx',
        'RiIndexDIP': 'R1DistPhalanx',
        'RiMiddleMP': 'R2ProxPhalanx',
        'RiMiddlePIP': 'R2MidPhalanx',
        'RiMiddleDIP': 'R2DistPhalanx',
        'RiRingMP': 'R3ProxPhalanx',
        'RiRingPIP': 'R3MidPhalanx',
        'RiRingDIP': 'R3DistPhalanx',
        'RiPinkyMP': 'R4ProxPhalanx',
        'RiPinkyPIP': 'R4MidPhalanx',
        'RiPinkyDIP': 'R4DistPhalanx',
        'RiThumbCMC': 'R5ProxPhalanx',
        'RiThumbMP': 'R5MidPhalanx',
        'RiThumbIP': 'R5DistPhalanx'
    }.get(joint, joint)
#define Neck "Neck"

if __name__ == "__main__":
	bvh_file = open(bvh_file, "r")
	bvh = bvh_file.read()
	bvh_file.close()

	tokens, remainder = scanner.scan(bvh)

	bvh_out = open(bvh_out_file, "w")

	replace(tokens,bvh_out)

	bvh_out.close()

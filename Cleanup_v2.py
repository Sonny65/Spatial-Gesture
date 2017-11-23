import re
import numpy as np
from numpy.linalg import inv
import math

bvh_file_body = "Sentences_1_variations - Body Solve.bvh"
bvh_file_left = "Sentences_1_variations - Left Hand Solve.bvh"
bvh_file_right = "Sentences_1_variations - Right Hand Solve.bvh"
bvh_out_file = "Product.bvh"

def identifier(scanner, token):  return "IDENT", token
def operator(scanner, token):    return "OPERATOR", token
def digit(scanner, token):       return "DIGIT", token
def open_brace(scanner, token):  return "OPEN_BRACE", token
def close_brace(scanner, token): return "CLOSE_BRACE", token
def colon(scanner, token):  return "COLON", token
def space(scanner, token): return "SPACE", token

reserved      = [ "HIERARCHY", "ROOT", "OFFSET", "CHANNELS", "MOTION" ]
channel_names = [ "Xposition", "Yposition", "Zposition",  "Zrotation", "Xrotation",  "Yrotation" ]

scanner = re.Scanner([
    (r"[a-zA-Z_]\w*", identifier),
    (r"-*[0-9]+(\.[0-9]+)?", digit),
	(r"}", close_brace),
	(r"{", open_brace),
	(r":", None),
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

	while (bvh_l[current_token_left] != ("IDENT", "leHand")):
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

	while (bvh_r[current_token_right] != ("IDENT", "riHand")):
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

def wrist_rotation(bvh, body_frames, right_frames, left_frames):

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

	# create parent

	body = []
	parent_left = []
	parent_right = []

	# creating parent from body file

	# root is a special case

	while (bvh[current_token] != ("IDENT", "L_Femur")):
		if "rotation" in bvh[current_token][1]:
			body = body + [bvh[current_token][1]]
		current_token = current_token + 1


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

	# calculate the wrist rotation

	print len(body_frames[0])

	wrist_rotation(tokens_body, body_frames, right_frames, left_frames)

	print len(body_frames[0])

	bvh_out.close()

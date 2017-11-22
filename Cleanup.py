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

def isRotationMatrix(R) :
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype = R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6

def rotationMatrixToEulerAngles(R) :
 
    assert(isRotationMatrix(R))
     
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
     
    singular = sy < 1e-6
 
    if  not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0
 
    return np.array([x, y, z])

def getRotationMatrix(parent_matrix, child_matrix):
	# parent = np.array([[1,0,0,parent_matrix[0]],[0,1,0,parent_matrix[1]],[0,0,1,parent_matrix[2]],[0,0,0,1]])
	# child = np.array([[1,0,0,child_matrix[0]],[0,1,0,child_matrix[1]],[0,0,1,child_matrix[2]],[0,0,0,1]])
	parent = np.array([parent_matrix[0],parent_matrix[1],parent_matrix[2],1])
	child = np.array([child_matrix[0],child_matrix[1],child_matrix[2],1])
	R = parent.dot(np.transpose(child))

	return R

def translation(translation, position):
	# translation = np.array([[1,0,0,translation[0]],[0,1,0,translation[1]],[0,0,1,translation[2]],[0,0,0,1]])
	position = np.array([position[0], position[1], position[2], 1])
	position = translation.dot(position)
	position = np.array([position[0], position[1], position[2]])
	return position

def rotation(rotationx, rotationy, rotationz, transpose):
	# transpose = np.array([transpose[0], transpose[1], transpose[2], 1])
	transpose = np.array([[1,0,0,transpose[0]],[0,1,0,transpose[1]],[0,0,1,transpose[2]],[0,0,0,1]])
	rotationx = math.radians(rotationx[0])
	rotationy = math.radians(rotationy[1])
	rotationz = math.radians(rotationz[2])

	# rotationx = rotationx[0]
	# rotationy = rotationy[0]
	# rotationz = rotationz[2]

	rotationx = np.array([[1, 0, 0, 0], [0, math.cos(rotationx), -math.sin(rotationx), 0], [0, math.sin(rotationx), math.cos(rotationx), 0], [0, 0, 0, 1]])
	rotationy = np.array([[math.cos(rotationy), 0, math.sin(rotationy), 0], [0, 1, 0, 0], [-math.sin(rotationy), 0, math.cos(rotationy), 0], [0, 0, 0, 1]])
	rotationz = np.array([[math.cos(rotationz), -math.sin(rotationz), 0, 0], [math.sin(rotationz), math.cos(rotationz), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
	
	# transpose = transpose.dot(rotationx)
	# transpose = transpose.dot(rotationy)
	# transpose = transpose.dot(rotationz)
	transpose = rotationx.dot(transpose)
	transpose = rotationy.dot(transpose)
	transpose = rotationz.dot(transpose)
	# transpose = rotationx.dot(transpose)
	# print transpose
	# print rotationy
	# transpose = rotationy.dot(transpose)
	# print transpose
	# transpose = rotationz.dot(transpose)
	return transpose

def parentlocal_transpose(transpose_list, Rotation_list):
	local_transpose = np.array([0, 0, 0])
	global_position = transpose_list.pop(0)
	Xrotation = Rotation_list.pop(0)
	Yrotation = Rotation_list.pop(0)
	Zrotation = Rotation_list.pop(0)
	for transpose in transpose_list:
		print global_position
		Xrotation = Rotation_list.pop(0)
		Yrotation = Rotation_list.pop(0)
		Zrotation = Rotation_list.pop(0)
		# local_transpose = translation(transpose_list.pop(), local_transpose)
		local_transpose = rotation(Xrotation, Yrotation, Zrotation, transpose_list.pop(0))
		global_position = translation(local_transpose, global_position)
	return local_transpose

def transpose(bvh, current_token):
	Transpose_List = []

	while (bvh[current_token] != ("IDENT", "LowerBack")):
		current_token = current_token + 1

	while (bvh[current_token] != ("IDENT", "OFFSET")):
		current_token = current_token + 1

	x = np.array([float(bvh[current_token+2][1]), float(bvh[current_token+4][1]), float(bvh[current_token+6][1])])

	current_token = current_token + 1

	Transpose_List.append(x)

	while (bvh[current_token] != ("IDENT", "Neck")):
		if (bvh[current_token] == ("IDENT", "End")):
			current_token = current_token + 12
		if (bvh[current_token] == ("IDENT", "OFFSET")):
			x = np.array([float(bvh[current_token+2][1]), float(bvh[current_token+4][1]), float(bvh[current_token+6][1])])
			Transpose_List.append(x)
		current_token = current_token + 1

	while (bvh[current_token] != ("IDENT", "L_Collar")):
		current_token = current_token + 1

	# Deal with Left and Right Wrists
	Transpose_List_Left = list(Transpose_List)
	Transpose_List_Right = list(Transpose_List)

	while (bvh[current_token] != ("IDENT", "Site")):
		if (bvh[current_token] == ("IDENT", "OFFSET")):
			x = np.array([float(bvh[current_token+2][1]), float(bvh[current_token+4][1]), float(bvh[current_token+6][1])])
			Transpose_List_Left.append(x)
		current_token = current_token + 1

	while (bvh[current_token] != ("IDENT", "R_Collar")):
		current_token = current_token + 1

	while (bvh[current_token] != ("IDENT", "Site")):
		if (bvh[current_token] == ("IDENT", "OFFSET")):
			x = np.array([float(bvh[current_token+2][1]), float(bvh[current_token+4][1]), float(bvh[current_token+6][1])])
			Transpose_List_Right.append(x)
		current_token = current_token + 1

	return Transpose_List_Left, Transpose_List_Right, Transpose_List

# get the local transform for the first frame
def worldtolocal(bvh,bvh_l,bvh_r,bvh_out, current_token, current_token_left, current_token_right, transpose_left, transpose_right, transpose_body):

	Rotation_list = []

	count = 0

	while (bvh[current_token] != ("IDENT", "Time")):
		current_token = current_token + 1

	current_token = current_token + 1
	current_token = current_token + 1
	current_token = current_token + 1
	current_token = current_token + 1

	while ("\n" not in bvh[current_token][1]):
		if (bvh[current_token][0] != "DIGIT"):
			count = count + 1
		current_token = current_token + 1
		if (count == 3):
			break

	# Getting Transpose
	x = np.array([float(bvh[current_token-6][1]), float(bvh[current_token-4][1]), float(bvh[current_token-2][1])])
	transpose_left = [x] + transpose_left
	transpose_right = [x] + transpose_right

	count = 0

	# Constructing new Matrix and get Rotations
	while ("\n" not in bvh[current_token][1]):
		if (bvh[current_token][0] == "DIGIT"):
			count = count + 1
		else:
			current_token = current_token + 1
			continue

		if (count == 1):
			x = np.array([float(bvh[current_token][1]),0,0])
			Rotation_list.append(x)
			current_token = current_token + 1
		if (count == 2):
			x = np.array([0,float(bvh[current_token][1]),0])
			Rotation_list.append(x)
			current_token = current_token + 1
		if (count == 3):
			x = np.array([0,0,float(bvh[current_token][1])])
			Rotation_list.append(x)
			current_token = current_token + 1
			count = 0

		if (len(Rotation_list) == 48):
			break

	while ("\n" not in bvh[current_token][1]):
		current_token = current_token + 1
	current_token = current_token + 1

	# Left Hand
	while (bvh_l[current_token_left][0] != "DIGIT"):
		current_token_left = current_token_left + 1

	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1

	left_parent_global_transpose = parentlocal_transpose(transpose_left, Rotation_list)
	left_global_transpose = np.array([float(bvh_l[current_token_left-6][1]), float(bvh_l[current_token_left-4][1]), float(bvh_l[current_token_left-2][1])])
	left_matrix = np.array([float(bvh_l[current_token_left][1]), float(bvh_l[current_token_left+2][1]), float(bvh_l[current_token_left+4][1])])
	left_parent = translation(transpose_body[-1], parentlocal_transpose(transpose_left, Rotation_list))
	getRotationMatrix(left_global_transpose, left_parent)

	while ("\n" not in bvh_l[current_token_left][1]):
		current_token_left = current_token_left + 1

	current_token_left = current_token_left + 1

	# right Hand
	while (bvh_r[current_token_right][0] != "DIGIT"):
		current_token_right = current_token_right + 1

	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1

	right_global_transpose = np.array([float(bvh_l[current_token_right-6][1]), float(bvh_l[current_token_right-4][1]), float(bvh_l[current_token_right-2][1])])
	right_matrix = np.array([float(bvh_r[current_token_right][1]), float(bvh_r[current_token_right+2][1]), float(bvh_r[current_token_right+4][1])])
	right_parent = translation(transpose_body[-1], parentlocal_transpose(transpose_right, Rotation_list))

	while ("\n" not in bvh_r[current_token_right][1]):
		current_token_right = current_token_right + 1

	current_token_right = current_token_right + 1

	return left_matrix, right_matrix, current_token, current_token_left, current_token_right

# get the local transform for other frames
def worldtolocalnext(bvh,bvh_l,bvh_r,bvh_out, current_token, current_token_left, current_token_right, transpose_left, transpose_right):
	Rotation_list = []

	count = 0

	while ("\n" not in bvh[current_token][1]):
		if (bvh[current_token][0] != "DIGIT"):
			count = count + 1
		current_token = current_token + 1
		if (count == 3):
			break

	count = 0
	
	# Constructing new Matrix and get Rotations
	while ("\n" not in bvh[current_token][1]):

		if (bvh[current_token][0] == "DIGIT"):
			count = count + 1
		else:
			current_token = current_token + 1
			continue

		if (count == 1):
			x = np.array([[1, 0, 0], [0, math.cos(float(bvh[current_token][1])), -math.sin(float(bvh[current_token][1]))], [0, math.sin(float(bvh[current_token][1])), math.cos(float(bvh[current_token][1]))]])
			Rotation_list.append(inv(x))
			current_token = current_token + 1
		if (count == 2):
			x = np.array([[math.cos(float(bvh[current_token][1])), 0, math.sin(float(bvh[current_token][1]))], [0, 1, 0], [-math.sin(float(bvh[current_token][1])), 0, math.cos(float(bvh[current_token][1]))]])
			Rotation_list.append(inv(x))
			current_token = current_token + 1
		if (count == 3):
			x = np.array([[math.cos(float(bvh[current_token][1])), -math.sin(float(bvh[current_token][1])), 0], [math.sin(float(bvh[current_token][1])), math.cos(float(bvh[current_token][1])), 0], [0, 0, 1]])
			Rotation_list.append(inv(x))
			current_token = current_token + 1
			count = 0

		if (len(Rotation_list) == 48):
			break

	while ("\n" not in bvh[current_token][1]):
		current_token = current_token + 1
	current_token = current_token + 1

	# Left Hand
	while (bvh_l[current_token_left][0] != "DIGIT"):
		current_token_left = current_token_left + 1

	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1
	current_token_left = current_token_left + 1

	left_matrix = np.array([float(bvh_l[current_token_left][1]), float(bvh_l[current_token_left+2][1]), float(bvh_l[current_token_left+4][1])])

	for inverse in Rotation_list:
		left_matrix = left_matrix.dot(inverse)

	while ("\n" not in bvh_l[current_token_left][1]):
		current_token_left = current_token_left + 1

	current_token_left = current_token_left + 1

	# right Hand
	while (bvh_r[current_token_right][0] != "DIGIT"):
		current_token_right = current_token_right + 1

	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1
	current_token_right = current_token_right + 1

	right_matrix = np.array([float(bvh_r[current_token_right][1]), float(bvh_r[current_token_right+2][1]), float(bvh_r[current_token_right+4][1])])

	for inverse in Rotation_list:
		right_matrix = right_matrix.dot(inverse)

	while ("\n" not in bvh_r[current_token_right][1]):
		current_token_right = current_token_right + 1

	current_token_right = current_token_right + 1

	return left_matrix, right_matrix, current_token, current_token_left, current_token_right

def parse_data(bvh,bvh_l,bvh_r,bvh_out, current_token, current_token_left, current_token_right, transpose_left, transpose_right, transpose_body):

	# Caculate the Local Postion of Wrists

	left_matrix, right_matrix, main_index, left_index, right_index = worldtolocal(bvh,bvh_l,bvh_r,bvh_out, current_token, current_token_left, current_token_right, transpose_left, transpose_right, transpose_body)

	# Parsing Legends Body

	while (bvh[current_token] != ("IDENT", "Time")):
		bvh_out.write(bvh[current_token][1])
		if bvh[current_token][1] == "Frames":
			bvh_out.write(":")
		current_token = current_token + 1

	bvh_out.write(bvh[current_token][1])
	bvh_out.write(":")
	current_token = current_token + 1

	bvh_out.write(bvh[current_token][1])
	current_token = current_token + 1

	bvh_out.write(bvh[current_token][1])
	current_token = current_token + 1

	bvh_out.write(bvh[current_token][1])
	current_token = current_token + 1

	# Parsing Legends Left

	while (bvh_l[current_token_left] != ("IDENT", "Time")):
		current_token_left = current_token_left + 1

	current_token_left = current_token_left + 1

	current_token_left = current_token_left + 1

	current_token_left = current_token_left + 1

	current_token_left = current_token_left + 1

	# Parsing Legends Right

	while (bvh_r[current_token_right] != ("IDENT", "Time")):
		current_token_right = current_token_right + 1

	current_token_right = current_token_right + 1

	current_token_right = current_token_right + 1

	current_token_right = current_token_right + 1

	current_token_right = current_token_right + 1

	# Parsing Data

	while (current_token != len(bvh)):
		count = 0
		l_count = 0
		r_count = 0
		m_count = 0

		while ("\n" not in bvh[current_token][1]):
			if (bvh[current_token][0] != "DIGIT"):
				count = count + 1
			if (count == 51):
				break
			bvh_out.write(bvh[current_token][1])
			current_token = current_token + 1

		bvh_out.write(bvh[current_token][1])

		# Left Hand

		# bvh_out.write("Comment")

		# Get Rid of Extra Degrees

		current_token_left = current_token_left + 1
		current_token_left = current_token_left + 1
		current_token_left = current_token_left + 1
		current_token_left = current_token_left + 1
		current_token_left = current_token_left + 1
		current_token_left = current_token_left + 1

		while ("\n" not in bvh_l[current_token_left][1]):
			if (bvh_l[current_token_left][0] != "DIGIT"):
				l_count = l_count + 1
			if (l_count == 3):
				break
			if (bvh_l[current_token_left][0] == "DIGIT"):
				bvh_out.write(str(left_matrix[l_count]))
			else:
				bvh_out.write(bvh_l[current_token_left][1])
			current_token_left = current_token_left + 1

		while ("\n" not in bvh_l[current_token_left][1]):
			bvh_out.write(bvh_l[current_token_left][1])
			current_token_left = current_token_left + 1

		current_token_left = current_token_left + 1

		# bvh_out.write("Comment")

		# Finish the R_Collar

		bvh_out.write(bvh[current_token][1])
		current_token = current_token + 1

		while ("\n" not in bvh[current_token][1]):
			if (bvh[current_token][0] != "DIGIT"):
				m_count = m_count + 1
			if (m_count == 3):
				break
			current_token = current_token + 1

		# bvh_out.write("Comment")

		current_token = current_token + 1

		m_count = 0

		while ("\n" not in bvh[current_token][1]):
			if (bvh[current_token][0] != "DIGIT"):
				m_count = m_count + 1
			if (m_count == 9):
				break
			bvh_out.write(bvh[current_token][1])
			current_token = current_token + 1

		bvh_out.write(bvh[current_token][1])


		# Right Hand
		
		# Get Rid of Extra Degrees

		current_token_right = current_token_right + 1
		current_token_right = current_token_right + 1
		current_token_right = current_token_right + 1
		current_token_right = current_token_right + 1
		current_token_right = current_token_right + 1
		current_token_right = current_token_right + 1

		while ("\n" not in bvh_r[current_token_right][1]):
			if (bvh_r[current_token_right][0] != "DIGIT"):
				r_count = r_count + 1
			if (r_count == 3):
				break
			if (bvh_r[current_token_right][0] == "DIGIT"):
				bvh_out.write(str(right_matrix[r_count]))
			else:
				bvh_out.write(bvh_r[current_token_right][1])
			current_token_right = current_token_right + 1


		while ("\n" not in bvh_r[current_token_right][1]):
			bvh_out.write(bvh_r[current_token_right][1])
			current_token_right = current_token_right + 1


		current_token_right = current_token_right + 1

		# Transfer to New Frame
		while ("\n" not in bvh[current_token][1]):
			current_token = current_token + 1

		bvh_out.write(bvh[current_token][1])
		current_token = current_token + 1
		if (current_token != len(bvh)):
			left_matrix, right_matrix, main_index, left_index, right_index = worldtolocalnext(bvh,bvh_l,bvh_r,bvh_out, main_index, left_index, right_index, transpose_left, transpose_right)


def parse_hierarchy(bvh,bvh_l,bvh_r):

	bvh_out = open(bvh_out_file, "w")

	global current_token
	global current_token_left

	current_token = 0
	current_token_left = 0
	current_token_right = 0

	# Get the Transpose
	transpose_left, transpose_right, transpose_body = transpose(bvh, current_token)


	while (bvh[current_token] != ("IDENT", "L_Wrist")):
		bvh_out.write(bvh[current_token][1])
		current_token = current_token + 1

	# bvh_out.write(bvh[current_token][1])

	# Left Hand

	while (bvh[current_token] != ("IDENT", "L_Wrist")):
		bvh_out.write(bvh[current_token][1])
		current_token = current_token + 1

	while (bvh[current_token] != ("IDENT", "End")):
		bvh_out.write(bvh[current_token][1])
		current_token = current_token + 1

	left_space = bvh[current_token-1][1]
	bvh_out.write("JOINT ")

	while (bvh_l[current_token_left] != ("IDENT", "leHand")):
		current_token_left = current_token_left + 1

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

	current_token_right = current_token_right + 1

	while (bvh[current_token][0] != "CLOSE_BRACE"):
		current_token = current_token + 1
	current_token = current_token + 1

	while (bvh[current_token][0] != "CLOSE_BRACE"):
		current_token = current_token + 1
	current_token = current_token + 1

	#END OF RIGHT HAND
	while (bvh_l[current_token_left] != ("IDENT", "Time")):
		current_token_left = current_token_left + 1

	while (bvh_r[current_token_right] != ("IDENT", "Time")):
		current_token_right = current_token_right + 1

	while (bvh[current_token] != ("IDENT", "MOTION")):
		bvh_out.write(bvh[current_token][1])
		current_token = current_token + 1

	# PARSING DATA
	parse_data(bvh,bvh_l,bvh_r,bvh_out, current_token, current_token_left, current_token_right, transpose_left, transpose_right, transpose_body)

	bvh_out.close()

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

	parse_hierarchy(tokens_body,tokens_left, tokens_right)

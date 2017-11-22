import re

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

def parse_data(bvh,bvh_l,bvh_r,bvh_out, current_token, current_token_left, current_token_right):

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

		while ("\n" not in bvh_l[current_token_left][1]):
			bvh_out.write(bvh_l[current_token_left][1])
			current_token_left = current_token_left + 1

		while ("\n" not in bvh_l[current_token_left][1]):
			current_token_left = current_token_left + 1

		current_token_left = current_token_left + 1

		m_count = 0


		# Finish Right Collar

		bvh_out.write(bvh[current_token][1])

		while ("\n" not in bvh[current_token][1]):
			if (bvh[current_token][0] != "DIGIT"):
				m_count = m_count + 1
			if (m_count == 4):
				break
			current_token = current_token + 1

		current_token = current_token + 1

		m_count = 0

		while ("\n" not in bvh[current_token][1]):
			if (bvh[current_token][0] != "DIGIT"):
				m_count = m_count + 1
			if (m_count == 9):
				break
			bvh_out.write(bvh[current_token][1])
			current_token = current_token + 1

		# Right Hand

		# Get Rid of Extra Degrees

		bvh_out.write(bvh[current_token][1])

		while ("\n" not in bvh_r[current_token_right][1]):
			bvh_out.write(bvh_r[current_token_right][1])
			current_token_right = current_token_right + 1

		while ("\n" not in bvh_r[current_token_right][1]):
			current_token_right = current_token_right + 1

		current_token_right = current_token_right + 1

		# Transfer to New Frame

		while ("\n" not in bvh[current_token][1]):
			# bvh_out.write(bvh[current_token][1])
			current_token = current_token + 1

		bvh_out.write(bvh[current_token][1])
		current_token = current_token + 1


def parse_hierarchy(bvh,bvh_l,bvh_r):
	bvh_out = open(bvh_out_file, "w")

	global current_token
	global current_token_left

	current_token = 0
	current_token_left = 0
	current_token_right = 0


	while (bvh[current_token-1] != ("IDENT", "L_Wrist")):
		bvh_out.write(bvh[current_token][1])
		current_token = current_token + 1

	# Left Hand

	while (bvh[current_token] != ("IDENT", "End")):
		# bvh_out.write(bvh[current_token][1])
		current_token = current_token + 1

	left_space = bvh[current_token-1][1]

	while (bvh_l[current_token_left] != ("IDENT", "leWrist")):
		current_token_left = current_token_left + 1

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

	bvh_out.write(bvh[current_token][1])

	while (bvh[current_token] != ("IDENT", "End")):
		# bvh_out.write(bvh[current_token][1])
		current_token = current_token + 1

	right_space = bvh[current_token-1][1]

	while (bvh_r[current_token_right] != ("IDENT", "wrist")):
		current_token_right = current_token_right + 1

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
	parse_data(bvh,bvh_l,bvh_r,bvh_out, current_token, current_token_left, current_token_right)

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

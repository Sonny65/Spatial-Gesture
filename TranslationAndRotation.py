import re
import numpy as np
from numpy.linalg import inv
import math

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

rotationx = [0,0,0]
rotationy = [0,0,0]
rotationz = [0,0,180]
transpose = np.array([1,1,1])
position = [0,0,0]
print translation(rotation(rotationx, rotationy, rotationz, transpose), position)
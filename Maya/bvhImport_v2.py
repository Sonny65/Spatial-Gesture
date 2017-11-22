# BVH to maya importer.

import fileinput

import maya.cmds as mc

class BVHData:

	def __init__(self):
		# the names of the joints
		self.jointNames = []

		# the parent index for each joint
		self.jointParents = []

		# a 3 tuple containing the joint offset
		self.jointOffset = []

		# the rotational degrees of freedom for this joint
		self.rotDOF = []

		# the rotation order of this joint
		#note that Maya uses fixed axes (i.e. the axes don't move, so an XYZ rotation
		#in a rotating frame bvh becomes an ZYX rotation in a fixed frame scheme)
		self.rotOrder = []

		# the names of all channels in the file
		self.channelNames = []

		# the current parent joint index
		self.parentStack = []

		# the current joint index
		self.currentJoint = -1

		# the number of frames
		self.numFrames = 0

		# the frames per second
		self.fps = 30

		# the actual frame data
		self.frames = []

	def reset(self):
		self.jointNames = []
		self.jointParents = []
		self.jointOffset = []
		self.rotDOF = []
		self.rotOrder = []

		self.channelNames = []
		self.parentStack = []

		self.numFrames = 0
		self.fps = 0
		self.frames = 0
	
	def parseHierarchy(self, currentLine):
		ret = True
		words = self.processLine(currentLine)
		
		if(words[0] == "ROOT" or words[0] == "JOINT" or words[0] == "End"):
			# ignore the word Site after End in 'End Site <name>'
			if(words[0] == "End"):
				words.pop(1)

			# get the joint name
			if(len(words) > 1):
				self.jointNames.append(words[1])

			else:
				self.jointNames.append('')

			# the joint parent
			if(len(self.parentStack) == 0):
				self.jointParents.append(-1)

			else:
				self.jointParents.append(self.parentStack[-1])

			self.currentJoint = len(self.jointNames) - 1

		elif(words[0] == '{'):
			self.parentStack.append(self.currentJoint)

		elif(words[0] == '}'):
			if(not len(self.rotDOF) == len(self.jointNames)):
				self.rotDOF.append('xyz')
				self.rotOrder.append('zyx')

			self.parentStack.pop()

		elif(words[0] == 'OFFSET'):
			self.jointOffset.append( \
					[float(words[1]), float(words[2]), float(words[3])] \
							)

		elif(words[0] == 'CHANNELS'):
			numChannels = int(words[1])

			if(len(words) - 2 == numChannels):
				ro = ''

				for c in words[2:]:
					if(c == 'Xrotation'):
						attr = 'rx'
						ro += 'x'

					elif(c == 'Yrotation'):
						attr = 'ry'
						ro += 'y'

					elif(c == 'Zrotation'):
						attr = 'rz'
						ro += 'z'

					elif(c == 'Xposition'):
						attr = 'tx'

					elif(c == 'Yposition'):
						attr = 'ty'

					elif(c == 'Zposition'):
						attr = 'tz'

					else:
						print 'Unknown channel type! ', c

					self.channelNames.append( \
							[self.jointNames[self.currentJoint], attr] \
							)

				self.rotDOF.append(ro)

				#print 'found rotations ', ro

				order = ''
				if(ro[0] == 'x'):
					if(len(ro) < 2):
						order = 'zyx'
					elif(ro[1] == 'y'):
						order = 'zyx'
					elif(ro[1] == 'z'):
						order = 'yzx'
				elif(ro[0] == 'y'):
					if(len(ro) < 2):
						order = 'zxy'
					elif(ro[1] == 'x'):
						order = 'zxy'
					elif(ro[1] == 'z'):
						order = 'xzy'
				elif(ro[0] == 'z'):
					if(len(ro) < 2):
						order = 'xyz'
					elif(ro[1] == 'x'):
						order = 'yxz'
					elif(ro[1] == 'y'):
						order = 'xyz'
				else:
					print 'Unrecognized channel order: ', ro

				self.rotOrder.append(order)

				#print 'joint order: ', order

			else:
				print 'Incorrect number of channels listed!'

		elif(words[0] == 'MOTION'):
			ret = False

		else:
			print 'Syntax Error on line ', currentLine
	
		return ret
	
	# removes tabs and spurious characters from a line of input, and breaks
	# it up into tokens.
	def processLine(self, line):
		return filter(lambda x: not x == '', line.strip('\t\r\n').split(' '))

	# parses the motion data and stores it.
	def parseMotion(self, line):
		words = self.processLine(line)

		if(words[0] == 'MOTION'):
			pass	# ignore this line, we're ok

		elif(words[0] == 'Frames:'):
			self.numFrames = int(words[1])

		elif(words[0] == 'Frame' and words[1] == 'Time:'):
			self.fps = int(1.0/float(words[2]))

		else:
			# must be a data frame.
			if(not len(words) == len(self.channelNames)):
				print 'Unrecognized line: ', line

			else:
				# convert to floats and store.
				try:
					flist = map(float, words)
			
				except ValueError:
					print 'Error converting values to float.'
					raise

				else:
					self.frames.append(flist)


# does the initial file parsing and returns the fileinput structure
# and the parsed hierarchy data.
def parseFile(filename):
	data = BVHData()
	f = fileinput.input(filename)

	# first line should be the HIERARCHY marcher.
	words = data.processLine(f.readline())

	if(not words[0] == 'HIERARCHY'):
		print 'Syntax error: does not appear to be a BVH file.'
		return

	else:
		# parse the hierarchy marker
		line = f.readline()
		keepGoing = data.parseHierarchy(line)

		while(keepGoing):
			line = f.readline()
			keepGoing = data.parseHierarchy(line)

		# now parse the motion data
		data.parseMotion(line)

		for line in f:
			data.parseMotion(line)

		f.close()
		return data

# builds the skeleton in maya given the parsed skeleton data.
def buildMayaSkeleton(bvh):
	# first, clear the selection.
	mc.select(cl=True)

	# create a transform node for the new hierarchy.
	mc.group(empty=True, name='bvhImport', world=True)

	# create the joints.
	for i in range(0, len(bvh.jointNames)):
		parent = ''

		if(bvh.jointParents[i] == -1):
			parent = 'bvhImport'

		else:
			parent = bvh.jointNames[bvh.jointParents[i]]

		# joint must be selected to become the parent.
		mc.select(parent, r=True)

		mc.joint( name = bvh.jointNames[i] \
				  , position = bvh.jointOffset[i] \
				  , relative = True \
				  , rotationOrder = bvh.rotOrder[i] \
				  , dof = bvh.rotDOF[i] \
				 )

# sets the key frames from the motion data
def applyFrameData(bvh):
	# for each frame
	for f in range(0, bvh.numFrames):
		ftime = f+1
		frame = bvh.frames[f]

		# for each channel
		for c in range(0, len(frame)):
			mc.setKeyframe( bvh.channelNames[c][0] \
						  , at = bvh.channelNames[c][1] \
						  , time = ftime \
						  , value = frame[c] \
					)

# the main script
filename = mc.fileDialog(directoryMask = '*.bvh')

if(not filename == ''):
	fileinput.close()

	bvh = parseFile(filename)
	buildMayaSkeleton(bvh)
	applyFrameData(bvh)

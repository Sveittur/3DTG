import numpy as np

class ObjLoader:
	def __init__(self):
		self.v = []
		self.vt = []
		self.vn = []

		self.vIndex = []
		self.vtIndex = []
		self.vnIndex = []

		self.position = []
		self.normal = []
		self.model = []

	def loadModel(self,file):
		for line in open(file, 'r'):
			if line.startswith('#'): continue
			values = line.split(" ")
			if not values: continue

			if values[0] == 'v':
				values[3] = values[3].strip("\n")
				self.v.append(values[1:4])

			if values[0] == 'vt':
				self.vt.append(values[1:3])

			if values[0] == 'vn':
				values[3] = values[3].strip("\n")
				self.vn.append(values[1:4])

			if values[0] == 'f':
				face_i = []
				text_i = []
				norm_i = []

				for v in values[1:4]:
					w = v.split("/")
					face_i.append(int(w[0])-1)
					text_i.append(int(w[1])-1)
					norm_i.append(int(w[2])-1) 
				self.vIndex.append(face_i)
				self.vtIndex.append(text_i)
				self.vnIndex.append(norm_i)

		self.vIndex = [y for x in self.vIndex for y in x]
		self.vtIndex = [y for x in self.vtIndex for y in x]
		self.vnIndex = [y for x in self.vnIndex for y in x]

		for i in self.vIndex:
			self.model.extend(self.v[i])

		for i in self.vtIndex:
		 	self.model.extend(self.vt[i])

		for i in self.vnIndex:
		 	self.model.extend(self.vn[i])

		self.model = np.array(self.model,dtype='float32')

		
					








		
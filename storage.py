class Storage():
	def __init__(self):
		self.storage = []

	def get(self, k):
		return self.storage[k]

	def set(self, k, v):
		self.storage[k] = v

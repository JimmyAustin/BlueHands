class Storage():
	def __init__(self):
		self.storage = {}

	def get(self, k):
        # I'm not sure if it should default to returning 0x0, but seems as good as an
		return self.storage.get(k, bytes(32))

	def set(self, k, v):
		self.storage[k] = v

class EwChef:
	cooking = False
	serve = False
	done = False
	chef_id = 0
	prompts = 0
	reward = 0
	def stop(self):
		self.fishing = False
		self.serve = False
		self.done = False
		self.chef_id = 0
		self.prompts = 0
		self.reward = 0
		
chefs = {}

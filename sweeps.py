
class Sweeper:


	def __init__(self, params):
		self.params = params


	def full_sweep(self):
		return self.sweep_helper(self.params)


	def sweep_helper(self, param_list):
		if len(param_list) > 1:
			first, rest = param_list[0], param_list[1:]
			settings = self.sweep_helper(rest)
		else:
			first = param_list[0]
			settings = [{}]
		for setting in settings:		
			for v in range(int(first.min_val * 10), int(first.max_val * 10) + 1, 1):
				v = v / 10
				z = {**setting, **{first.name : v}}
				yield z


	def tied_sweep(self, tied_params):
		pass


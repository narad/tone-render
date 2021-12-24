from typing import Dict, List
import yaml

from param import Param


class VSTConfig:

	def __init__(self, filename) -> None:
		self.read(filename)


	def read(self, filename) -> None:
	   with open(filename) as infile:
	        info = yaml.load(infile)
	   self.vst_name = info['vst']
	   self.params = [Param(p['name'], p['min'], p['max']) for p in info['params']]
	   self.default_value_dict = { p['name']: p['value'] for p in info['defaults']}


	def tunable_parameters(self) -> List[Param]:
		return self.params


	def default_values(self) -> Dict[str, float]:
		return self.default_value_dict
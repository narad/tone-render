from typing import Dict, List
#from param import Param
import yaml
from pathlib import Path


class SweepInfo:

    def __init__(self, comment, params):
        self.comment = comment
        self.params = params


class ParamSweep:

    def __init__(self, names, min_val, max_val, step):
        self.names = names
        self.min_val = min_val
        self.max_val = max_val
        self.step = step


class Sweeper:


    def __init__(self, config):
        self.config = config        
        self.sweeps = [(sw.comment, list(self.sweep_helper(sw.params))) for sw in config.sweeps]


    def sweep_helper(self, param_list: List[ParamSweep]):
        if len(param_list) > 1:
            first, rest = param_list[0], param_list[1:]
            settings = self.sweep_helper(rest) #, tied_params)
        else:
            first = param_list[0]
            settings = [{}]

        for setting in settings:
            for v in range(int(first.min_val * 10), int(first.max_val * 10) + 1, int(first.step*10)):
                v = v / 10
                z = {**setting, **{pname : v for pname in first.names}}
                yield z


    def write(self, out_file: Path, di_file: Path):
        with open(out_file, "w") as settings_file:
            settings_file.write(f"di_file: {di_file.name}\n")
            settings_file.write("files:\n")
            i = 0
            for sweep_name, sweep in self.sweeps:
                print("outer sweep: ", sweep_name)
                print(sweep)
                for setting in sweep:
            # for i, setting in enumerate(sweeps):
                    settings_file.write(f"  - filename: {i:08d}.wav\n" +
                                        "    settings:\n")
                    for param_name, param_val in setting.items():
                        settings_file.write(f"    - {param_name}: {param_val}\n")
                    i += 1
            settings_file.write("- defaults:\n")
            for param_name, param_val in self.config.default_values().items():
                settings_file.write(f"  - name: {param_name}\n")
                settings_file.write(f"    value: {param_val}\n")


    # @staticmethod
    # def load()



class SweepConfig:

    def __init__(self, filename) -> None:
        self.read(filename)


    def read(self, filename) -> None:
        with open(filename) as infile:
            info = yaml.load(infile)
        self.vst_name = info['vst']
        self.sweeps = [self.parse_sweep(sd) for sd in info['sweeps']]
        self.default_value_dict = { p['name']: p['value'] for p in info['defaults']}


    def parse_sweep(self, sweep_dict):
        params = [ParamSweep(p['name'], p['min'], p['max'], p['step']) for p in sweep_dict['params']]
        return SweepInfo(comment=sweep_dict['comment'], 
                         params=params)


    def flatten(self, l):
        return [x for row in l for x in l]


    def tunable_parameters(self) -> List[str]:
        return self.flatten(self.sweeps[0].params)

    def sweeps(self):
        return self.sweeps


    def default_values(self) -> Dict[str, float]:
        return self.default_value_dict



# old code from when sweeps had to stay as generators
# #from itertools import chain

# def chain(*iterables): 
#   for iterable in iterables: yield from iterable 

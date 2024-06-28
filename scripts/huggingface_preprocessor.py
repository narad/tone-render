# Takes a data directory and creates a data.csv file as used in HuggingFace Datasets

import os
import sys
import yaml
from pathlib import Path
import subprocess
import argparse

def process_info(yaml_data, verbose=False):
    # print(yaml_data.keys())
    # global_keys = ['vst_name', 'device', 'di_file']
    local_keys = ['files', 'defaults']
    global_keys = [k for k in yaml_data.keys() if k not in local_keys]
    for f in yaml_data['files']:
        d = dict()
        for k in global_keys:
            d[k] = yaml_data[k]
        d['filename'] = f['filename']
        # Set the default values
        for pdict in yaml_data['defaults']:
            k,v = list(pdict.items())[0]
            d[k] = v
        # Set the sweep values
        for tup in f['settings']:
            for k,v in tup.items():
                d[k] = v
        yield d


def convert2huggingface(base_dir, verbose = False):
    infos = []
    for p in base_dir.rglob("*"):
        if p.suffix == '.yaml':
            if verbose:
                print(f"Processing {p}...")
            with open(str(p)) as infile:
                for info in process_info(yaml.safe_load(infile), verbose):
                    root_path = p.relative_to(base_dir.parent)
                    info['di_file'] = str(root_path.parent / info['di_file'])
                    info['filename'] = str(root_path.parent / info['filename'])
                    infos.append(info)

    all_keys = set()
    for info in infos:
        for k in info.keys():
            all_keys.add(k)

    key_list = list(all_keys)
    print(key_list)
    print(len(infos))

    # Write CSV file
    # if make_zip:
    #     output_csv_file = base_dir / "data.csv"
    # else:

    output_csv_file = base_dir / "data.csv"
    print(output_csv_file)
    with open(output_csv_file, "w") as out:
        out.write(",".join(key_list) + "\n")
        for info in infos:
            out.write(",".join([str(info.get(k, "0")) for k in key_list]) + "\n")

    # # Make .zip, then delete the csv from the original data folder
    # print(str(base_dir))
    # if make_zip:
    #     process = subprocess.run(["cp",
    #                               "-r",
    #                               str(base_dir),
    #                               "./"],
    #                              stdout=subprocess.PIPE,
    #                              universal_newlines=True)
    #     # process = subprocess.run(["zip",
        #                           "-vr",
        #                           "data.zip",
        #                           str(base_dir),
        #                           "-x",
        #                           "\"*.DS_Store\""],
        #                          stdout=subprocess.PIPE,
        #                          universal_newlines=True)
        # os.remove(output_csv_file)


#       cmd = f"zip -vr data.zip FM3\ -\ Axe-FX\ 5150\ Block/ -x "*.DS_Store""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Options for VST rendering.')
    parser.add_argument('--input_dir', type=Path, required=True,
                        help='the input directory, which should be the device name folder.')
    # parser.add_argument('--output_dir', type=Path, default='./', required=False,
    #                     help='the input directory, which should be the device name folder.')
    # parser.add_argument('--make_zip', type=bool, default=False,
    #                     help='will run extra shell commands to package the complete zip for upload (mac only)')
    args = parser.parse_args()


    convert2huggingface(base_dir=args.input_dir, 
                        # output_dir=args.output_dir,
                        # make_zip=args.make_zip,
                        verbose=True)


#!/usr/bin/env python3
import json
import yaml
import csv
from cookiecutter.main import cookiecutter
import os
import argparse


def read_yaml_file(filename, load_all=False):
    with open(filename, mode='r') as f:
        if not load_all:
            yaml_data = yaml.load(f, Loader=yaml.FullLoader)
        else:
            # convert generator to list before returning
            yaml_data = list(yaml.load_all(f, Loader=yaml.FullLoader))
    return yaml_data


def read_csv_file(filename):
    with open(filename, mode='r') as csv_file:
        csv_row_dict_list = list()
        for row in csv.DictReader(csv_file):
            updated_row_dict = dict()
            for k,v in row.items():
                # remove potential spaces left and right
                k = k.strip()
                if v:
                    v = v.strip()
                updated_row_dict.update({k:v})
            csv_row_dict_list.append(updated_row_dict)

    return csv_row_dict_list


if __name__ == "__main__":

    # Get cookiecutter output_directory from CLI argument or default
    parser = argparse.ArgumentParser(
        prog="AVD Cookiecutter",
        description="This script will create AVD repository based on data proved in CSVs directory.")
    parser.add_argument(
        '-out', '--output_directory', default='./avd-cookiecutter-output',
        help='Directory to keep the AVD repository produced by cookiecutter'
    )
    args = parser.parse_args()
    cookiecutter_output_dir = args.output_directory

    # find cookiecutter templates location
    cookiecutter_template_directory = os.path.join(
        os.getcwd(), '.cookiecutters/avd-cookiecutter')

    cookiecutter_json = {
        '_jinja2_env_vars': {'lstrip_blocks': True, 'trim_blocks': True},
        'csv': {
            # load inventory
            'inventory': read_csv_file('CSVs/inventory.csv'),
            # load cabling plan
            'cabling_plan': read_csv_file('CSVs/cabling_plan.csv'),
            # load server connections
            'server_list': read_csv_file('CSVs/servers.csv'),
            # load server port profiles
            'server_port_profiles': read_csv_file('CSVs/server_port_profiles.csv'),
            # load tenants and vrfs
            'tenants_vrfs': read_csv_file('CSVs/tenants_and_vrfs.csv'),
            # load vlans and svis
            'vlans_svis': read_csv_file('CSVs/vlans_and_svis.csv')
        }

    }

    # load general parameters and update cookiecutter.json
    cookiecutter_json.update(read_yaml_file('CSVs/general_parameters.yml'))

    # write cookiecutter.json
    cookiecutter_json_filename = os.path.join(
        cookiecutter_template_directory, 'cookiecutter.json'
    )
    with open(cookiecutter_json_filename, 'w') as cc_json_file:
        json.dump(cookiecutter_json, cc_json_file, indent=4)

    # generate AVD project
    cookiecutter(cookiecutter_template_directory, no_input=True, overwrite_if_exists=True, output_dir=cookiecutter_output_dir)

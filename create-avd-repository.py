#!/usr/bin/env python3
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
        csv_row_list = list(csv.DictReader(csv_file))
    return csv_row_list


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

    # load inventory
    inventory_list = [ row for row in read_csv_file('CSVs/inventory.csv') ]
    # load cabling plan
    cabling_plan_list = [ row for row in read_csv_file('CSVs/cabling_plan.csv') ]
    # load general parameters
    general_parameters_dict = read_yaml_file('CSVs/general_parameters.yml')
    # load server connections
    server_list = [ row for row in read_csv_file('CSVs/servers.csv') ]
    # load server port profiles
    server_port_profile_list = [ row for row in read_csv_file('CSVs/server_port_profiles.csv') ]
    # load tenants and vrfs
    tenant_and_vrf_list = [ row for row in read_csv_file('CSVs/tenants_and_vrfs.csv') ]
    # load vlans and svis
    vlan_and_svi_list = [ row for row in read_csv_file('CSVs/vlans_and_svis.csv') ]

    # start building cookiecutter.json
    cookiecutter_json = dict()

    print(

    )

    # cookiecutter(cookiecutter_template_directory, no_input=True, overwrite_if_exists=True, output_dir=cookiecutter_output_dir)

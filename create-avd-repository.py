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

    # load inventory
    # inventory_list = [ row for row in read_csv_file('CSVs/inventory.csv') ]
    inventory_list = read_csv_file('CSVs/inventory.csv')
    # load cabling plan
    cabling_plan_list = read_csv_file('CSVs/cabling_plan.csv')
    # load general parameters
    general_parameters_dict = read_yaml_file('CSVs/general_parameters.yml')
    # load server connections
    server_list =  read_csv_file('CSVs/servers.csv')
    # load server port profiles
    server_port_profile_list = read_csv_file('CSVs/server_port_profiles.csv')
    # load tenants and vrfs
    tenant_and_vrf_list = read_csv_file('CSVs/tenants_and_vrfs.csv')
    # load vlans and svis
    vlan_and_svi_list = read_csv_file('CSVs/vlans_and_svis.csv')

    # start building cookiecutter.json
    cookiecutter_json = dict()
    # set AVD repository name
    cookiecutter_json.update({
        'avd_repository_name': general_parameters_dict['AVD Repository Name']
    })
    # set AVD fabric name
    cookiecutter_json.update({
        'fabric_name': general_parameters_dict['Fabric Name']
    })

    # write cookiecutter.json
    cookiecutter_json_filename = os.path.join(
        cookiecutter_template_directory, 'cookiecutter.json'
    )
    with open(cookiecutter_json_filename, 'w') as cc_json_file:
        json.dump(cookiecutter_json, cc_json_file, indent=4)

    print(
        
    )

    cookiecutter(cookiecutter_template_directory, no_input=True, overwrite_if_exists=True, output_dir=cookiecutter_output_dir)

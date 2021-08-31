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
            for k, v in row.items():
                # remove potential spaces left and right
                k = k.strip()
                if v:
                    v = v.strip()
                updated_row_dict.update({k: v})
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
        # _jinja2_env_vars was added in attempt to fix whitespace control
        # doesn't work as expected, more testing required
        # but doesn't hurt either =), keeping it here for reference
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
    cookiecutter_json.update({
        'general': read_yaml_file('CSVs/general_parameters.yml')
    })

    # build fabric variables
    cookiecutter_json.update({
        'fabric': {
            'spine_list': list(),
            'l3leaf_list': list(),
            'pod_list': list()
        }
    })

    # calculate leaf and spine IDs
    spine_id = 1
    l3leaf_id = 1
    for a_switch in cookiecutter_json['csv']['inventory']:

        if a_switch['type'] == 'spine':
            a_spine = dict()
            # update spine dict with known parameters
            a_spine.update(a_switch)
            # set spine id and increment it
            a_spine.update({
                'id': spine_id
            })
            spine_id += 1

            cookiecutter_json['fabric']['spine_list'].append(a_spine)

        if a_switch['type'] == 'l3leaf':
            a_leaf = dict()
            # update leaf dict with known parameters
            a_leaf.update(a_switch)
            # set leaf id and increment it
            a_leaf.update({
                'id': l3leaf_id
            })
            l3leaf_id += 1

            # build leaf to spine connections
            spine_list = list()
            uplink_to_spine_interfaces = list()  # l3leaf uplinks to spines
            spine_interfaces = list()  # spine connections to l3leaf

            for a_link in cookiecutter_json['csv']['cabling_plan']:
                if a_link['local_switch'] == a_switch['hostname']:
                    for a_spine in cookiecutter_json['fabric']['spine_list']:
                        if a_link['remote_switch'] == a_spine['hostname']:
                            spine_list.append(a_spine['hostname'])
                            uplink_to_spine_interfaces.append(
                                a_link['local_interface'])
                            spine_interfaces.append(a_link['remote_interface'])
                if a_link['remote_switch'] == a_switch['hostname']:
                    for a_spine in cookiecutter_json['fabric']['spine_list']:
                        if a_link['local_switch'] == a_spine['hostname']:
                            spine_list.append(a_spine['hostname'])
                            uplink_to_spine_interfaces.append(
                                a_link['remote_interface'])
                            spine_interfaces.append(a_link['local_interface'])

            a_leaf.update({
                'spines': spine_list,
                'uplink_to_spine_interfaces': uplink_to_spine_interfaces,
                'spine_interfaces': spine_interfaces
            })

            cookiecutter_json['fabric']['l3leaf_list'].append(a_leaf)

    # build pods and MLAG connections
    pod_number = 0
    # l3leaf_list_copy = cookiecutter_json['fabric']['l3leaf_list'].copy()
    l3leaf_list_sorted_copy = sorted(
        cookiecutter_json['fabric']['l3leaf_list'], key=lambda leaf: leaf['id']
    )
    while l3leaf_list_sorted_copy:
        bgp_start_asn = int(
            cookiecutter_json['general']['leaf_as_range'].split('-')[0])
        bgp_end_asn = int(
            cookiecutter_json['general']['leaf_as_range'].split('-')[-1])
        bgp_asn_list = list(range(bgp_start_asn, bgp_end_asn))
        a_pod = {
            'name': f'pod{pod_number}',
            'asn': bgp_asn_list[pod_number],
            'leafs': list()
        }
        pod_number += 1  # increment for next cycle
        a_leaf = l3leaf_list_sorted_copy.pop(0)
        a_pod['leafs'].append(a_leaf)
        for a_link in cookiecutter_json['csv']['cabling_plan']:
            if a_link['local_switch'] == a_leaf['hostname']:
                for index, another_leaf in enumerate(l3leaf_list_sorted_copy):
                    if a_link['remote_switch'] == another_leaf['hostname']:
                        a_pod['leafs'].append(
                            l3leaf_list_sorted_copy.pop(index))
            elif a_link['remote_switch'] == a_leaf['hostname']:
                for index, another_leaf in enumerate(l3leaf_list_sorted_copy):
                    if a_link['local_switch'] == another_leaf['hostname']:
                        a_pod['leafs'].append(
                            l3leaf_list_sorted_copy.pop(index))
        cookiecutter_json['fabric']['pod_list'].append(a_pod)

    # write cookiecutter.json
    cookiecutter_json_filename = os.path.join(
        cookiecutter_template_directory, 'cookiecutter.json'
    )
    with open(cookiecutter_json_filename, 'w') as cc_json_file:
        json.dump(cookiecutter_json, cc_json_file, indent=4)

    # generate AVD project
    cookiecutter(cookiecutter_template_directory, no_input=True,
                 overwrite_if_exists=True, output_dir=cookiecutter_output_dir)

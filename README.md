# WARNING: avd-cookiecutter repository is now obsolete
> ***
> Please check [AVD Quickstart Containerlab](https://github.com/arista-netdevops-community/avd-quickstart-containerlab) that is a newer version of this repository with additional features.
> ***

> This repository will be deleted in future.

AVD Cookiecutter project helps to build AVD inventory quickly by building all required variables from simple CSV files.

## Required Input

Following data is required to generate AVD inventory:

- inventory.csv - list of switches in the AVD fabric
- cabling_plan.csv - connections between these switches
- general_parameters.yml - IP pools to build fabric and other general general_parameters
- server_port_profiles.csv - profiles to be referenced from servers.csv
- servers.csv - list of server-to-switch connections
- tenants_and_vrs.csv - list of tenants and IP VRFs to be created
- vlans_and_svis.csv - L2-only VLANs and SVIs for every tenant

Sometimes it's fine to skip certain parameters in CSVs to keep the entry short. For example, missing parameters for the entries with the same hostname will be completed from the first one:

```csv
server_name,description,rack_name,switch_hostname,switch_port,profile,port_channel_mode
host1,leaf1_to_host1,pod1,leaf1,Ethernet4,TENANT_A,active
host1,,,leaf1,Ethernet5,,
host1,,,leaf2,Ethernet4,,
host1,,,leaf2,Ethernet5,,
```

Feel free to experiment with the CSV files and share your feedback.

## How to Run the Script

- Clone this repository.
- Create Python virtual environment: `python3 -m venv .venv`
- Activate the virtual environment. Or set `"python.pythonPath"` in `.vscode/settings.json` accordingly
- Install requirements: `pip install -r requirements.txt`
- Run the script. `.create-avd-repository.py` will create an inventory in the current repository. `.create-avd-repository.py -o ~` will create a dedicated repository in your home directory (assuming you are on Linux or MacOS). It's possible to specify any other directory as the destination.
- Open AVD inventory in VSCode. If Docker is installed on your machine, VSCode will build a devcontainer and you are ready to go.
- It is recommended to `git init` the AVD inventory.

> NOTE: If devcontainer is not starting automatically, for example, when using Remote-SSH, you can start it manually:
> `docker run --rm -it --mount type=bind,source="$(pwd)",target=/home/avd/projects avdteam/avd-all-in-one:latest`
> Check [avd-all-in-one container documents](https://github.com/arista-netdevops-community/avd-all-in-one-container) for additional details if you have issues.

## Caveats

- Windows machines have path length limit. To avoid breaking git cone for AVD cookiecutter, cookiecutter directory names were shortened.

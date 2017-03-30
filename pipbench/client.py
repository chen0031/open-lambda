import argparse
import requests
import json
import os
import tarfile
import shutil


'''
PipBench client
Triggers the backend to create a package with the provided parameters, which is added to a local
PyPi compatible cache, and retrieves the name of the created package. It also generates a handler
that uses the packages, and uploads it to the store. 
'''

def generate_packages(imports_mean, imports_scale):
    num_imports = 5
    packages = []
    for i in range(0, num_imports):
        new_package_name = generate_package(5, 5, 5, 5, 5, 5)
        packages.append(new_package_name)
    return packages

def generate_package(num_assets, asset_size, install_cpu, install_mem, import_cpu, import_mem):
    headers = {'Content-Type': 'application/json'}
    r = requests.post('http://localhost:9198/package', headers=headers, data=json.dumps({
        "numAssets": num_assets,
        "assetSize": asset_size,
        "installCpu": install_cpu,
        "installMem": install_mem,
        "importCpu": import_cpu,
        "importMem": import_mem
    }))
    if r.status_code != 200:
        raise Exception('PipBench server failed to create package ' + r.json())
    else:
        package_name = r.json()['packageName']
        return package_name

def generate_handler_file(handler_name, packages):
    # todo this needs to actually upload the handler to the store
    handler_contents = ''
    for p in packages:
        handler_contents += 'import ' + p + '\n'
    f = open(handler_name + '/lambda_func.py', 'w')
    f.write(handler_contents)
    f.close()

def generate_requirements(handler_name, packages):
    # todo this needs to actually upload the handler to the store
    handler_contents = ''
    for p in packages:
        handler_contents += p + '\n'
    f = open(handler_name + '/' + 'requirements.txt', 'w')
    f.write(handler_contents)
    f.close()

def zip(handler_name):
    tar = tarfile.open(handler_name + ".tar.gz", "w:gz")
    tar.add(handler_name)
    tar.close()

def cleanup(handler_name):
    shutil.rmtree(handler_name)

parser = argparse.ArgumentParser(description='Generate a handler')
parser.add_argument('-imports-mean', default=10)
parser.add_argument('-imports-scale', default=1)
parser.add_argument('-handler-name', default='pip_bench_handler')
args = parser.parse_args()

if not os.path.exists(args.handler_name):
    os.makedirs(args.handler_name)

packages = generate_packages(args.imports_mean, args.imports_scale)
generate_handler_file(args.handler_name, packages)
generate_requirements(args.handler_name, packages)
zip(args.handler_name)
cleanup(args.handler_name)
print('Created handler zip ' + args.handler_name + ' successfully')


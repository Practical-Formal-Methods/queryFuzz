from setuptools import setup, find_packages
import json
import os

# Set home link in parameters file
query_fuzz_home = os.path.dirname(os.path.realpath(__file__))
path_to_souffle_engine = os.path.join(query_fuzz_home, "souffle_installations", "souffle_master", "bin", "souffle")
if os.path.exists(path_to_souffle_engine):
    print("######## souffle.... FOUND")
else:
    path_to_souffle_engine = ""
    print("######## souffle.... NOT FOUND")

# Create a params.json file at home directory location. Copy everything from default_params.py
default_parameters = os.path.join(query_fuzz_home, "queryfuzz", "default_params.json")
with open(default_parameters) as f:
    data = json.load(f)
    json_dump = json.dumps(data, indent=4)


# Create params.json at home
data["path_to_souffle_engine"] = path_to_souffle_engine
data["query_fuzz_home"] = query_fuzz_home
file=open(os.path.join(query_fuzz_home, "params.json"),"w")
file.write("")
file.close()
with open(os.path.join(query_fuzz_home, "params.json"), "w") as outfile:
    json.dump(data, outfile, indent=4)

# create get_home()
home_path_data = "def get_home():\n\treturn'" + query_fuzz_home + "'\n"
file = open(os.path.join(query_fuzz_home, "queryfuzz", "home.py"), "w")
file.write(home_path_data)
file.close()

setup(
    name='queryfuzz',
    version='1.0',
    description='Fuzzing Datalog program using the theory of conjunctive queries',
    author='Numair Mansur',
    author_email='numair@mpi-sws.org',
    url='https://numairmansur.github.io/',
    keywords='fuzzing, Datalog',
    packages=find_packages(),
    install_requires=['termcolor', 'pyfiglet'],
    entry_points={
        'console_scripts': ['queryfuzz = queryfuzz.__main__:main']
    }
)

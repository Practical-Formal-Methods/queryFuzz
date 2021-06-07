import os
from queryfuzz.home import get_home
import shutil
from termcolor import colored


SOUFFLE_GIT = "https://github.com/souffle-lang/souffle.git"


"""
queryfuzz
    |
    |
    |
    souffle_installations
        |
        |
        |
        --- souffle_master
        |
        |
        | 
        --- souffle_s34k34
        |
        |
        | 
        --- souffle_a5g111
"""

def create_souffle_dir():
    if not os.path.exists(os.path.join(get_home(), "souffle_installations")):
        os.mkdir(os.path.join(get_home(), "souffle_installations"))

def install_souffle(revision):
    print("Installing Souffle...")
    create_souffle_dir()
    SOUFFLE_INSTALLATIONS_DIR = os.path.join(get_home(), "souffle_installations")
    # Download the Souffle project if it is not there
    if not os.path.exists(os.path.join(get_home(), "souffle_installations", "souffle")):
        print(colored("Downloading Souffle...", "cyan", attrs=["bold"]))
        os.system("cd " + SOUFFLE_INSTALLATIONS_DIR + " && " + "git clone " + SOUFFLE_GIT)
    else:
        print(colored("Found a downloaded Souffle", "green", attrs=["bold"]))
        os.system("cd " + SOUFFLE_INSTALLATIONS_DIR + " && " + "git pull")
    # Check out to the revision we want to install
    print(colored("Checking out to revision... " + revision, "cyan", attrs=["bold"]))
    if revision == "master": os.system("cd " + os.path.join(SOUFFLE_INSTALLATIONS_DIR, "souffle") + " && " + "git checkout -f " + revision + " && git pull")
    else: os.system("cd " + os.path.join(SOUFFLE_INSTALLATIONS_DIR, "souffle") + " && " + "git checkout -f " + revision)
    INSTALLATION_PREFIX = os.path.join(SOUFFLE_INSTALLATIONS_DIR, "souffle_" + revision[:6])
    if revision == "master" : print("Installing Master")
    # if revision is masters then delete master installation and re-install
    if revision == "master" and os.path.exists(os.path.join("souffle_installations", "souffle_master", "bin", "souffle")): shutil.rmtree(INSTALLATION_PREFIX)
    # Start installation
    if not os.path.exists(INSTALLATION_PREFIX):
        print(colored("Begin installation for revision " + revision, "green", attrs=["bold"]))
        os.system("cd " + os.path.join(SOUFFLE_INSTALLATIONS_DIR, "souffle") + \
            " && sh ./bootstrap && ./configure --prefix=" + INSTALLATION_PREFIX + \
                " && make && make install")
    else: 
        print(colored("This version is already installed... " + revision, "red", attrs=["bold"]))
    return os.path.join(INSTALLATION_PREFIX, "bin", "souffle")
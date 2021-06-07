"""
    FSE'21 replication manager
"""
import os, json, time, multiprocessing
from queryfuzz.home import get_home
from queryfuzz.utils.souffle_installer import install_souffle
from termcolor import colored
from queryfuzz.utils.file_operations import create_server_directory, create_core_directory, export_errored_out_instance
from queryfuzz.utils.file_operations import export_buggy_instance_for_soundness, pick_seed_program, load_parameters
from queryfuzz.utils.file_operations import export_buggy_instance_for_soundness
from queryfuzz.utils.randomness import Randomness
from queryfuzz.utils.statistics import Statistics
from queryfuzz.engines.souffle.souffle import SouffleProgram
from queryfuzz.runner.souffle_runner import SouffleRunner
import pyfiglet
from queryfuzz.transformations.manager import TransformationManager
from queryfuzz.runner.compare_results import compare_results
import shutil
from queryfuzz.engines.z3.z3 import Z3Program
from queryfuzz.runner.z3_runner import Z3Runner
from queryfuzz.engines.ddlog.ddlog import DDlogProgram
from queryfuzz.runner.ddlog_runner import DDlogRunner


def load_bug_parameters(bug_path):
    with open(os.path.join(bug_path, "parameters.json")) as f:
        data = json.load(f)
    return data


def export_bug(program_path, bug_path):
    temp_directory = os.path.join(bug_path, "temp")
    if not os.path.exists(temp_directory): os.mkdir(temp_directory)
    number_of_directories = 0
    for r,d,f in os.walk(temp_directory):
        number_of_directories = len(d)
        break
    shutil.copytree(program_path, os.path.join(temp_directory, "bug" + str(number_of_directories)), copy_function=shutil.copy)


def merge_parameters(bug_parameters, default_parameters):
    for key in default_parameters.keys():
        if key not in bug_parameters.keys(): bug_parameters[key] = default_parameters[key]



def run(core, local_seed, wait, bug_path):
    time.sleep(wait)
    core_dir_path = create_core_directory(os.path.join(HOME, "temp"), SERVER, core) # Create the core directory
    stats = Statistics(server=SERVER, core=core, core_dir=core_dir_path)    # Create statistics object
    randomness = Randomness(local_seed) # Initialize randomness
    seed_folder = os.path.join(HOME, "seeds", ENGINE)   # Path to seed directory
    i = 0
    while True:
        i+=1
        program = None
        path_to_engine = None
        program_runner = None
        engine_options = None
        if SEED_FILE == "unknown": seed_program = None
        else: seed_program = os.path.join(seed_folder, SEED_FILE)
        if SEED_FILE != "unknown": print(colored("SEED PROGRAM: ", "magenta", attrs=["bold"]) + seed_program)
        if ENGINE == "souffle": 
            program = SouffleProgram(params=PARAMS, verbose=VERBOSE, randomness=randomness, program_number=i, seed_program=seed_program)
            program.enrich_program()
            path_to_engine = PATH_TO_BUGGY_VERSION
            program_runner = SouffleRunner(params=PARAMS, program=program, stats=stats)
        elif ENGINE == "z3":
            program = Z3Program(params=PARAMS, verbose=VERBOSE, randomness=randomness, program_number=i, seed_program=seed_program)
            program.enrich_program()
            path_to_engine = PATH_TO_BUGGY_VERSION
            program_runner = Z3Runner(params=PARAMS, program=program, stats=stats)
        elif ENGINE == "ddlog":
            program = DDlogProgram(params=PARAMS, verbose=VERBOSE, randomness=randomness, program_number=i, seed_program=seed_program)
            program.enrich_program()
            path_to_engine = PATH_TO_BUGGY_VERSION
            program_runner = DDlogRunner(params=PARAMS, program=program, stats=stats)
            program_runner.set_program_name("orig_rules")
        else:
            print(colored("This engine is currently not supported", "red", attrs=["bold"]))
            return 1        
        
        
        print("----- Prog # " + str(i)+ " ------------ SEED PROGRAM: " + str(seed_program) )
        if VERBOSE: program.pretty_print_program()
        program.create_program_string()
        program.export_program_string(core_dir_path)
        if SEED_FILE != "unknown": program.copy_fact_file_for_seed_program() # Copy fact files to the exported program location
        program.dump_program_log_file()
        signal = program_runner.run_original(engine_options=ORIG_ENGINE_OPTIONS)
        program.add_log_text("\tLocal Seed: " + local_seed)
        program.add_log_text("\tRunner signal = " + str(signal))
        if signal != 0: 
            print(colored("error", "red", attrs=["bold"]))
            stats.inc_total_orig_programs()
            shutil.rmtree(program.get_program_path())
            stats.dump_data()
            continue

        print(colored("ok", "green", attrs=["bold"]))
        # Everything looks good. We can start transformations
        # Start transformations
        for j in range(PARAMS["number_of_transformations"]):
            print(">>>> Prog. " + str(i)+ "  ->  Transf. " + str(j) + "  ", end="")            
            transformation_manager = TransformationManager(randomness=randomness, program=program, params=PARAMS, verbose=VERBOSE, engine=ENGINE)
            oracle = transformation_manager.get_chosen_transformation_type()
            new_program = transformation_manager.generate_transformation()
            new_program.add_transformation_information(oracle=oracle)
            new_program.create_program_string()
            new_program.export_transformed_program_string(transformation_number=j)
            new_program.dump_program_log_file()
            if (  (PARAMS["i"] != "unknown" and i != PARAMS["i"]) or  (PARAMS["j"] != "unknown" and j != PARAMS["j"]) ):
                os.remove(new_program.get_program_file_path()) 
                os.remove(new_program.get_log_file_path())
                continue
            transformation_signal = 0
            if ENGINE == "souffle":
                transformed_program_runner = SouffleRunner(params=PARAMS, program=new_program, stats=stats)
                transformation_signal = transformed_program_runner.run_transformed(transformation_number=j, engine_options=TRANS_ENGINE_OPTIONS)
                new_program.dump_program_log_file()
            if ENGINE == "z3":
                transformed_program_runner = Z3Runner(params=PARAMS, program=new_program, stats=stats)
                transformation_signal = transformed_program_runner.run_transformed(transformation_number=j, engine_options=TRANS_ENGINE_OPTIONS)
                new_program.dump_program_log_file()
            if ENGINE == "ddlog":
                transformed_program_runner = DDlogRunner(params=PARAMS, program=new_program, stats=stats)
                transformed_program_runner.set_program_name("transformed_rules_" + str(j))
                transformation_signal = transformed_program_runner.run_transformed(transformation_number=j, engine_options=TRANS_ENGINE_OPTIONS)
                new_program.dump_program_log_file()
            if transformation_signal == 3: 
                os.remove(new_program.get_program_file_path())
                continue # We do not care about this one bit
            if transformation_signal != 0:
                print(colored("error", "red", attrs=["bold"]))
                continue
            # Compare results
            comp_signal = compare_results(program.get_output_result_file_path(), 
                            new_program.get_output_result_file_path(),
                            oracle,
                            VERBOSE,
                            PARAMS, 
                            False, 
                            program.get_output_relation(),
                            program.get_program_path(),
                            j, 
                            SEED, 
                            new_program,
                            stats, 
                            ENGINE)
            if comp_signal == 1:
                # Export the soundness bug to a temp folder in bug_path
                export_buggy_instance_for_soundness(program.get_program_path(), HOME + "/temp")
                export_bug(program_path=program.get_program_path(), bug_path=bug_path)
                return 1
            stats.inc_total_transformations()
            os.remove(new_program.get_program_file_path())  # Remove transformed program file.
            os.remove(new_program.get_output_result_file_path())  # Remove ouput for T.
            os.remove(new_program.get_log_file_path())  # Remove log file for T.
            print(colored("ok ", "green", attrs=["bold"]))
        stats.inc_total_orig_programs()
        shutil.rmtree(program.get_program_path())
        stats.dump_data()


def reproduce(bug, server, cores, params, verbose):
    os.system("clear")
    initial_text = pyfiglet.figlet_format("queryFuzz")
    print(colored(initial_text , "yellow", attrs=["bold"]))
    initial_text = pyfiglet.figlet_format("FSE_REPL")
    print(colored(initial_text , "red", attrs=["bold"]), end="")
    initial_text = pyfiglet.figlet_format(bug)
    print(colored(initial_text , "green", attrs=["bold"]))
    bug_path = os.path.join(get_home(), "queryfuzz", "fse_repl", bug)
    if not os.path.exists(bug_path): 
        print(colored("Wrong bug number", "red", attrs=["bold"]))
        return 1
    bug_parameters = load_bug_parameters(bug_path)
    merge_parameters(bug_parameters, params)
    
    buggy_version = ""
    #  Install the buggy version but only for Souffle
    #if bug_parameters["engine"] == "souffle":
        #buggy_version = install_souffle(bug_parameters["buggy_version"])    
        #buggy_version = bug_parameters["path_to_souffle_engine"]
    #if bug_parameters["engine"] == "z3": 
        #buggy_version = bug_parameters["path_to_z3_engine"]
    #if bug_parameters["engine"] == "ddlog":
         #buggy_version = bug_parameters["path_to_ddlog_engine"]



    # update path_to_souffle_engine in the params
    if bug_parameters["engine"] == "souffle": buggy_version = bug_parameters["path_to_souffle_engine"]
    if bug_parameters["engine"] == "ddlog": buggy_version = bug_parameters["path_to_ddlog_engine"]
    if bug_parameters["engine"] == "z3": buggy_version = bug_parameters["path_to_z3_engine"]    
    if buggy_version == "": 
        print(colored("Please enter path to the buggy engine in the parameters.json file and try again", "red", attrs=["bold"]))
        return 1
    if bug_parameters["engine"] == "ddlog" and bug_parameters["path_to_ddlog_home_dir"] == "":
        print(colored("Please enter path to ddlog home directory and try again", "red", attrs=["bold"]))
        return 1
    # Start fuzzing on the buggy version
    global SEED         # Randomness seed for the run() instance
    global HOME         # queryfuzz home (retrieved from params.py)
    global SERVER       # server name
    global VERBOSE      # Verbose mode (We will print a lot of stuff + we won't handle errors and just stop)
    global PARAMS       # Tunable parameters
    global ENGINE       # Datalog engine
    global ANIMATE      # Cool transformation animations
    global CORES        # Number of cores
    global SEED_FILE     # Seed fuzzing
    global PATH_TO_BUGGY_VERSION
    global ORIG_ENGINE_OPTIONS  
    global TRANS_ENGINE_OPTIONS

    HOME = get_home()
    SERVER = server
    CORES = cores
    SEED = str(int(time.time())) if bug_parameters["seed"] == "unknown" else bug_parameters["seed"]
    ENGINE = bug_parameters["engine"]
    SEED_FILE = bug_parameters["seed_file"]
    PARAMS = bug_parameters
    VERBOSE = verbose    
    PATH_TO_BUGGY_VERSION = buggy_version
    ORIG_ENGINE_OPTIONS = bug_parameters["orig_engine_options"]
    TRANS_ENGINE_OPTIONS = bug_parameters["trans_engine_options"]

    create_server_directory(os.path.join(HOME, "temp"), SERVER) # Create server directory in temp
    if CORES is not None:
        for i in range(int(CORES)):
            core = i
            wait = int(CORES)
            local_seed = str(int(SEED) + core)
            process = multiprocessing.Process(target=run, args=(core, local_seed, wait, bug_path))
            process.start()
            # pin the process to a specific CPU
            os.system("taskset -p -c " + str(i) + " " + str(process.pid))
    else:
        run(core=0, local_seed=SEED, wait=0, bug_path=bug_path)
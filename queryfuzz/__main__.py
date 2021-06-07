import os
import json
import multiprocessing
import time
import shutil
from termcolor import colored
import argparse
import pyfiglet
from queryfuzz.parsers.argument_parser import MainArgumentParser
from queryfuzz.utils.file_operations import create_server_directory, create_core_directory, export_errored_out_instance
from queryfuzz.utils.file_operations import export_buggy_instance_for_soundness, pick_seed_program, load_parameters
from queryfuzz.utils.statistics import Statistics
from queryfuzz.engines.souffle.souffle import SouffleProgram
from queryfuzz.engines.z3.z3 import Z3Program
from queryfuzz.engines.ddlog.ddlog import DDlogProgram
from queryfuzz.utils.randomness import Randomness
from queryfuzz.runner.souffle_runner import SouffleRunner
from queryfuzz.runner.ddlog_runner import DDlogRunner
from queryfuzz.runner.z3_runner import Z3Runner
from queryfuzz.transformations.manager import TransformationManager
from queryfuzz.runner.compare_results import compare_results
from queryfuzz.utils.statistics import print_live_statistics
from queryfuzz.home import get_home
from queryfuzz.utils.souffle_installer import install_souffle
from queryfuzz.fse_repl.manager import reproduce

def run(core, local_seed, wait):
    time.sleep(wait)
    print("\nGlobal Variables:")
    print(colored("\tHOME = ", attrs=["bold"]) + colored(HOME, "cyan", attrs=["bold"]))
    print(colored("\tGLOBAL SEED = ", attrs=["bold"]) + colored(SEED, "cyan", attrs=["bold"]))
    print(colored("\tSERVER = ", attrs=["bold"]) + colored(SERVER, "cyan", attrs=["bold"]))
    print(colored("\tENGINE = ", attrs=["bold"]) + colored(ENGINE, "cyan", attrs=["bold"]))
    print(colored("\tVERBOSE = ", attrs=["bold"]) + colored(VERBOSE, "cyan", attrs=["bold"]))
    print("\nLocal Variables:")
    print(colored("\n\tcore number = ", attrs=["bold"]) + colored(core, "cyan", attrs=["bold"]))
    print(colored("\tlocal seed = ", attrs=["bold"]) + colored(local_seed, "cyan", attrs=["bold"]))
        
    core_dir_path = create_core_directory(os.path.join(HOME, "temp"), SERVER, core) # Create the core directory
    stats = Statistics(server=SERVER, core=core, core_dir=core_dir_path)    # Create statistics object
    randomness = Randomness(local_seed) # Initialize randomness
    seed_folder = os.path.join(HOME, "seeds", ENGINE)   # Path to seed directory
    
    for i in range(PARAMS["number_of_programs"]):
        program = None
        path_to_engine = None
        program_runner = None
        engine_options = None
        if SEEDFUZZ: seed_program = pick_seed_program(randomness=randomness, path_to_engine_seed_folder=seed_folder)
        else: seed_program = None
        if ENGINE == "souffle": 
            program = SouffleProgram(params=PARAMS, verbose=VERBOSE, randomness=randomness, program_number=i, seed_program=seed_program)
            program.enrich_program()
            path_to_engine = PARAMS["path_to_souffle_engine"]
            program_runner = SouffleRunner(params=PARAMS, program=program, stats=stats)
            engine_options = randomness.random_choice(PARAMS["souffle_options"])
        elif ENGINE == "z3":
            program = Z3Program(params=PARAMS, verbose=VERBOSE, randomness=randomness, program_number=i, seed_program=seed_program)
            program.enrich_program()
            path_to_engine = PARAMS["path_to_z3_engine"]
            program_runner = Z3Runner(params=PARAMS, program=program, stats=stats)
            engine_options = ""
        elif ENGINE == "ddlog":
            # /home/numair/ddlog_build/ddlog TODO: REMOVE THIS FROM default_params.json
            print(colored("ENGINE: DDLOG", "magenta", attrs=["bold"]))
            program = DDlogProgram(params=PARAMS, verbose=VERBOSE, randomness=randomness, program_number=i, seed_program=seed_program)
            program.enrich_program()           
            path_to_engine = PARAMS["path_to_ddlog_engine"]
            program_runner = DDlogRunner(params=PARAMS, program=program, stats=stats)
            program_runner.set_program_name("orig_rules")
            engine_options = ""
        else:
            print(colored("This engine is currently not supported", "red", attrs=["bold"]))
            return 1
        print("----- Prog # " + str(i)+ " ------------ SEED PROGRAM: " + str(seed_program) )
        
        # export Program
        if VERBOSE: program.pretty_print_program()
        program.create_program_string()
        program.export_program_string(core_dir_path)
        if SEEDFUZZ: program.copy_fact_file_for_seed_program() # Copy fact files to the exported program location

        # run the original program
        signal = program_runner.run_original(engine_options=engine_options)
        if signal == 3: 
            # We do not care about this one bit
            shutil.rmtree(program.get_program_path())
            continue 

        if signal != 0:
            print(colored("Signal = " + str(signal), "red", attrs=["bold"]))
            print(colored("SOMETHING WENT WRONG. Check it out please", "red", attrs=["bold"]))            
            program.add_log_text("XXXXX SOMETHING WENT WRONG. PLEASE CHECK IT OUT. XXXXXX")
            program.dump_program_log_file()
            program.pretty_print_program()
            export_errored_out_instance(program.get_program_path(), HOME, False)    # Move the file to the errors folder.
            stats.dump_data()
            break   # TODO: Change this to continue at some point
        print(colored("ok", "green", attrs=["bold"]))

        # Let's start with the transfromations
        transformation_signal = 0
        for j in range(PARAMS["number_of_transformations"]):
            if ANIMATE: time.sleep(0.1)
            if ANIMATE: os.system("clear")
            print(">>>> Prog. " + str(i)+ "  ->  Transf. " + str(j) + "  ", end="")
            transformation_manager = TransformationManager(randomness=randomness, program=program, params=PARAMS, verbose=VERBOSE, engine=ENGINE)
            oracle = transformation_manager.get_chosen_transformation_type()
            
            # Transform the original program
            new_program = transformation_manager.generate_transformation()
            
            # Export the transformed program
            new_program.add_transformation_information(oracle=oracle)
            new_program.create_program_string()
            new_program.export_transformed_program_string(transformation_number=j)
            new_program.dump_program_log_file()

            # run the transformed program
            transformation_signal = 0
            if ENGINE == "souffle":
                transformed_program_runner = SouffleRunner(params=PARAMS, program=new_program, stats=stats)
                transformation_signal = transformed_program_runner.run_transformed(transformation_number=j, engine_options=engine_options)
                new_program.dump_program_log_file()

            if ENGINE == "z3":
                transformed_program_runner = Z3Runner(params=PARAMS, program=new_program, stats=stats)
                transformation_signal = transformed_program_runner.run_transformed(transformation_number=j, engine_options=engine_options)
                new_program.dump_program_log_file()

            if ENGINE == "ddlog":
                transformed_program_runner = DDlogRunner(params=PARAMS, program=new_program, stats=stats)
                transformed_program_runner.set_program_name("transformed_rules_" + str(j))
                transformation_signal = transformed_program_runner.run_transformed(transformation_number=j, engine_options=engine_options)
                new_program.dump_program_log_file()
                
            if transformation_signal == 3: 
                print(colored("We do not care about this error"))
                os.remove(new_program.get_program_file_path())
                continue # We do not care about this one bit
                   
            if transformation_signal != 0:
                print(colored("Signal = " + str(transformation_signal), "red", attrs=["bold"]))
                print(colored("SOMETHING WENT WRONG. Check it out please", "red", attrs=["bold"]))
                new_program.pretty_print_program()
                
                # Export errored out instance
                export_errored_out_instance(new_program.get_program_path(), HOME, True)
                stats.dump_data()
                break   #TODO: Change to continue at some point
            
            new_program.add_log_text("\tRunning successful. Result file produced.")
            # compare results
            comp_signal = compare_results(program.get_output_result_file_path(), 
                            new_program.get_output_result_file_path(),
                            oracle,
                            VERBOSE,
                            PARAMS, 
                            ANIMATE, 
                            program.get_output_relation(),
                            program.get_program_path(),
                            j, 
                            SEED, 
                            new_program,
                            stats, 
                            ENGINE)

            if comp_signal == 1:
                # Soundness bug
                new_program.dump_program_log_file()
                stats.dump_data()
                # Export soundness bug file
                export_buggy_instance_for_soundness(program.get_program_path(), HOME + "/temp")
                # TODO: For now we will stop if a soundness bug is detected
                return 1    # TODO: Remove this return statement at some point
            
            # Increment the total number of transformations
            stats.inc_total_transformations()

            # If everything is ok, then delete this transformed program T , the result file and the log file. 
            os.remove(new_program.get_program_file_path())  # Remove transformed program file.
            os.remove(new_program.get_output_result_file_path())    # Remove ouput for T.
            os.remove(new_program.get_log_file_path())  # Remove log file for T.
            print(colored("ok ", "green", attrs=["bold"]), end="")
            print(str(randomness.get_random_integer(1,100)))

        # TODO: This is temporaray. No need to break the cycle.  
        if transformation_signal == 1 or transformation_signal == 2:
            break
        # Increment the total number of programs generated
        stats.inc_total_orig_programs()
        # Delete the program
        shutil.rmtree(program.get_program_path())
        # Export statistics data
        stats.dump_data()



def main():
    global SEED         # Randomness seed for the run() instance
    global HOME         # queryfuzz home (retrieved from params.py)
    global SERVER       # server name
    global VERBOSE      # Verbose mode (We will print a lot of stuff + we won't handle errors and just stop)
    global PARAMS       # Tunable parameters
    global ENGINE       # Datalog engine
    global ANIMATE      # Cool transformation animations
    global CORES        # Number of cores
    global SEEDFUZZ     # Seed fuzzing
    os.system("clear")
    initial_text = pyfiglet.figlet_format("queryFuzz")
    print(colored(initial_text , "yellow", attrs=["bold"]))
    # Parse arguments
    arguments = MainArgumentParser()
    arguments.parse_arguments(argparse.ArgumentParser())
    parsedArguments = arguments.get_arguments()
    VERBOSE = parsedArguments["verbose"]
    SEED = parsedArguments["seed"]
    HOME = get_home()
    SERVER = parsedArguments["server"]
    CORES = parsedArguments["cores"]
    PARAMS = load_parameters(HOME)
    ENGINE = parsedArguments["engine"]
    ANIMATE = parsedArguments["animate"]
    PRINT_STATS = parsedArguments["stats"]
    SEEDFUZZ = parsedArguments["seedfuzz"]

    # PRINT STATS --------------------------------------------------------------------------------------
    if PRINT_STATS: # Print stats and exit
        print_live_statistics(HOME, Statistics("", "", "").get_data_points())
        return 0
    
    # REPRODUCE  --------------------------------------------------------------------------------------
    if parsedArguments["reproduce"] is not None:
        reproduce(parsedArguments["reproduce"], SERVER, CORES, PARAMS, VERBOSE)
        return 0

    # INSTALL SOUFFLE IF IT IS NOT FOUND -----------------------------------------------------------
    if PARAMS["path_to_souffle_engine"] == "" or not os.path.exists(os.path.join(HOME, "souffle_installations", "souffle_master", "bin", "souffle")):
        install_souffle("master")
        # Add souffle path in params.json
        with open(os.path.join(HOME, "params.json")) as f: data = json.load(f)
        data["path_to_souffle_engine"] = os.path.join(HOME, "souffle_installations", "souffle_master", "bin", "souffle")
        with open(os.path.join(HOME, "params.json"), "w") as f: json.dump(data, f, indent=4)
        # Reload PARAMS
        PARAMS = load_parameters(HOME)  

    # INSTALL SOUFFLE ------------------------------------------------------------------------------
    if parsedArguments["installsouffle"] is not False:
        if parsedArguments["installsouffle"] == True: install_souffle("master")
        else: install_souffle(parsedArguments["installsouffle"])
        return 0

    # SOUFFLE NOT FOUND ----------------------------------------------------------------------------
    if PARAMS["path_to_souffle_engine"] == "": # If we don't know where Souffle is
        not_valid_path = True
        while not_valid_path:
            path_to_souffle = input(colored("Please provide full path to souffle binary (/soffle/src/souffle): ", "red", attrs=["bold"]))
            if os.path.exists(path_to_souffle) and path_to_souffle.find("/souffle/src/souffle") != -1:
                print(colored("Provided path: " + path_to_souffle, "green", attrs=["bold"]))
                not_valid_path = False
                with open(os.path.join(HOME, "params.json")) as f:  # Add souffle path in params.json
                    data = json.load(f)
                data["path_to_souffle_engine"] = path_to_souffle
                with open(os.path.join(HOME, "params.json"), "w") as f:
                    json.dump(data, f, indent=4)
            else:
                print("This is not a valid path: " + path_to_souffle)
        PARAMS = load_parameters(HOME)  # Reload PARAMS

    # Z3 not found
    if ENGINE == "z3" and PARAMS["path_to_z3_engine"] == "":
        print(colored("Please provide path to z3 binary in " + HOME + "/params.json and run again", "red", attrs=["bold"]))
        return 1

    # DDLOG not found
    # Z3 not found
    if ENGINE == "ddlog" and PARAMS["path_to_ddlog_engine"] == "" and PARAMS["path_to_ddlog_home_dir"] == "":
        print(colored("Please provide path to ddlog binary and ddlog home directory in " + HOME + "/params.json and run again", "red", attrs=["bold"]))
        return 1


    # START FUZZING ------------------------------------------------------------------------------------
    print("\nGlobal Variables:")
    print(colored("\tHOME = ", attrs=["bold"]) + colored(HOME, "cyan", attrs=["bold"]))
    print(colored("\tGLOBAL SEED = ", attrs=["bold"]) + colored(SEED, "cyan", attrs=["bold"]))
    print(colored("\tSERVER = ", attrs=["bold"]) + colored(SERVER, "cyan", attrs=["bold"]))
    print(colored("\tCORES = ", attrs=["bold"]) + colored(CORES, "cyan", attrs=["bold"]))
    print(colored("\tENGINE = ", attrs=["bold"]) + colored(ENGINE, "cyan", attrs=["bold"]))
    print(colored("\tVERBOSE = ", attrs=["bold"]) + colored(VERBOSE, "cyan", attrs=["bold"]))
    print(colored("\tANIMATE = ", attrs=["bold"]) + colored(ANIMATE, "cyan", attrs=["bold"]))
    print(colored("\tSEEDFUZZ = ", attrs=["bold"]) + colored(SEEDFUZZ, "cyan", attrs=["bold"]))
    letsgo = input(colored("\nAre you happy with the global parameters you are seeing? (y/n) ", attrs=["bold"]))
    create_server_directory(os.path.join(HOME, "temp"), SERVER) # Create server directory in temp
    if letsgo == "y":
        os.system("clear")
        try:
            if CORES is not None:
                for i in range(int(CORES)):
                    core = i
                    wait = int(CORES)
                    local_seed = str(int(SEED) + core)
                    process = multiprocessing.Process(target=run, args=(core, local_seed, wait))
                    process.start()
                    # pin the process to a specific CPU
                    os.system("taskset -p -c " + str(i) + " " + str(process.pid))
            else:
                run(core=0, local_seed=SEED, wait=0)        
        except (KeyboardInterrupt, SystemExit):
            print("\nGood Bye!\n")
    else:
        print(colored("\nSeems like you are not happy with the global parameters\n", "red", attrs=["bold"]))

if __name__ == '__main__':
    signal = main()

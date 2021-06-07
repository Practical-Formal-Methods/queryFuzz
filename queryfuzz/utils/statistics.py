"""
    Statistics class for progress reporting    
    Numbers we keep track of: 
        - Total number of program
        - Total number of transformation
        - Timeouts
        - Number of segfaults
        - Assertion failures
        - Unknown errors
        - Uninteresting errors
        - Inline errors
        - Soundness errors
"""
import os
import json
from queryfuzz.utils.file_operations import get_dir_names
from termcolor import colored
from copy import deepcopy

class Statistics(object):
    def __init__(self, server, core, core_dir):
        self.server = server
        self.core = core
        self.stats_file_path = os.path.join(core_dir, "stats.json") # should it be a json format

        # Initialize 
        self.stats_data = dict()
        self.performance_data = dict()
        self.stats_data["total_orig_programs"] = 0
        self.stats_data["total_transformations"] = 0
        
        self.stats_data["total_orig_timeouts"] = 0
        self.stats_data["total_trans_timeouts"] = 0
        
        self.stats_data["total_orig_syntax_errors"] = 0
        self.stats_data["total_trans_syntax_errors"] = 0
        
        self.stats_data["total_orig_segmentation_faults"] = 0
        self.stats_data["total_trans_segmentation_faults"] = 0

        self.stats_data["total_orig_assertion_failures"] = 0
        self.stats_data["total_trans_assertion_failures"] = 0 

        self.stats_data["total_orig_known_assertion_failures"] = 0
        self.stats_data["total_trans_known_assertion_failures"] = 0 

        self.stats_data["total_orig_unknown_errors"] = 0
        self.stats_data["total_trans_unknown_errors"] = 0

        self.stats_data["total_orig_uninteresting_errors"] = 0
        self.stats_data["total_trans_uninteresting_errors"] = 0

        self.stats_data["total_orig_floating_point_exceptions"] = 0
        self.stats_data["total_trans_floating_point_exceptions"] = 0

        self.stats_data["total_orig_inline_errors"] = 0
        self.stats_data["total_trans_inline_errors"] = 0

        self.stats_data["total_trans_soundness_errors"] = 0

        self.dump_data()


    def dump_data(self):
        with open(self.stats_file_path, 'w') as outfile:
            json.dump(self.stats_data, outfile, sort_keys=True)

    def get_data_points(self):
        return self.stats_data.keys()

    def get_performance_numbers(self):
        return self.performance_data

    # Increment methods ---------------------------------------
    def inc_total_orig_programs(self):
        self.stats_data["total_orig_programs"] += 1
    def inc_total_transformations(self):
        self.stats_data["total_transformations"] += 1

    def inc_total_orig_timeouts(self):
        self.stats_data["total_orig_timeouts"] += 1
    def inc_total_trans_timeouts(self):
        self.stats_data["total_trans_timeouts"] += 1

    def inc_total_orig_syntax_errors(self):
        self.stats_data["total_orig_syntax_errors"] += 1
    def inc_total_trans_syntax_errors(self):
        self.stats_data["total_trans_syntax_errors"] += 1

    def inc_total_orig_seg_faults(self):
        self.stats_data["total_orig_segmentation_faults"] += 1
    def inc_total_trans_seg_faults(self): 
        self.stats_data["total_trans_segmentation_faults"] += 1

    def inc_total_orig_assertion_failures(self):
        self.stats_data["total_orig_assertion_failures"] += 1
    def inc_total_trans_assertion_failures(self):
        self.stats_data["total_trans_assertion_failures"] += 1

    def inc_total_orig_known_assertion_failures(self):
        self.stats_data["total_orig_known_assertion_failures"] += 1
    def inc_total_trans_known_assertion_failures(self):
        self.stats_data["total_trans_known_assertion_failures"] += 1

    def inc_total_orig_unknown_errors(self):
        self.stats_data["total_orig_unknown_errors"] += 1
    def inc_total_trans_unknown_errors(self):
        self.stats_data["total_trans_unknown_errors"] += 1

    def inc_total_orig_uninteresting_errors(self):
        self.stats_data["total_orig_uninteresting_errors"] += 1
    def inc_total_trans_uninteresting_errors(self): 
        self.stats_data["total_trans_uninteresting_errors"] += 1

    def inc_total_orig_inline_errors(self):
        self.stats_data["total_orig_inline_errors"] += 1
    def inc_total_trans_inline_errors(self): 
        self.stats_data["total_trans_inline_errors"] += 1

    def inc_total_orig_floating_point_exceptions(self):
        self.stats_data["total_orig_floating_point_exceptions"] += 1
    def inc_total_trans_floating_point_exceptions(self): 
        self.stats_data["total_trans_floating_point_exceptions"] += 1

    def inc_total_trans_soundness_errors(self):
        self.stats_data["total_trans_soundness_errors"] += 1

    def print_stats(self):
        with open(self.stats_file_path) as f:
            data = json.load(f)
            json_dump = json.dumps(data, indent=4)
        print(json_dump)




def print_live_statistics(home_path, data_points):
    
    def get_sum_over_all_servers(parameter):
        # Sigma stats_i,j(parameter) for  core_0 < i < core_32 AND server_1 < j < server_n 
        _sum = 0
        for core in range(CORES):
            for server in server_names:
                server_path = os.path.join(temp_dir_path, server)
                core_path = os.path.join(server_path, "core_" + str(core))
                json_file_path = os.path.join(core_path, "stats.json")
                # import json at location core_path
                if not os.path.exists(json_file_path):
                    # If no json file found at this path then ignore
                    continue
                with open(json_file_path) as f:
                    data = json.load(f)
                _sum += data[parameter]
        return _sum

    def print_sum_per_server():
        print(colored("Total", "yellow", attrs=["bold"]), end="")
        for server in server_names:
            _server_sum = 0
            server_path = os.path.join(temp_dir_path, server)
            for core in range(CORES):
                core_path = os.path.join(server_path, "core_" + str(core))
                json_file_path = os.path.join(core_path, "stats.json")
                if not os.path.exists(json_file_path):
                    # If no json file found at this path then ignore
                    continue
                with open(json_file_path) as f:
                    data = json.load(f)                    
                _server_sum += data["total_orig_programs"]
            print(" \t\t\t" + str(_server_sum), end="")

    temp_dir_path = os.path.join(home_path, "temp")
    CORES = 50
    CRITICAL_DATA_POINTS = ["assertion", "segmentation", "soundness", "unknown"]

    os.system("clear")
    # see what server names we have in the temp folder
    server_names = get_dir_names(temp_dir_path)
    if server_names is None: return 1
    
    # Print server names
    for server in server_names:
        print("\t\t\t" + colored(server, "yellow", attrs=["bold"]), end="")
    print("\n")
    for core in range(CORES):
        print(colored("core_" + str(core), "yellow", attrs=["bold"] ), end="")
        # Get the total_programs from stats folder in this core and this server
        for server in server_names:
            server_path = os.path.join(temp_dir_path, server)
            core_path = os.path.join(server_path, "core_" + str(core))
            json_file_path = os.path.join(core_path, "stats.json")
            # import json at location core_path
            if not os.path.exists(json_file_path):
                # If no json file found at this path then ignore
                print("\t\t\t", end="")
                continue
            with open(json_file_path) as f:
                data = json.load(f)
            print("\t\t\t" + str(data["total_orig_programs"]), end="")
        print("")
    print("")
    
    # Print the total in a server
    print("")
    print_sum_per_server()
    
    for _type in ["orig", "trans"]:
        print("\n\n----- " + _type + " ----- \n")
        for data_point in data_points:
            if data_point.find(_type) != -1:
                _sum = get_sum_over_all_servers(data_point)
                if _sum > 0 and len([i for i in CRITICAL_DATA_POINTS if data_point.find(i) != -1]) > 0:
                    # If it is a critical data point and greater than zero. Then print in red
                    print(data_point + " : " + colored(str(_sum), "white", "on_red", attrs=["bold"]))
                elif _sum == 0 and len([i for i in CRITICAL_DATA_POINTS if data_point.find(i) != -1]) > 0:
                    # If it is a critical data point and equal to zero. Then print in green
                    print(data_point + " : " + colored(" " + str(_sum) + " ", "green", attrs=["bold"]))
                else: 
                    # We dont care about the color here
                    print(data_point + " : " + colored(" " + str(_sum) + " ", "cyan", attrs=["bold"]))
    print("")


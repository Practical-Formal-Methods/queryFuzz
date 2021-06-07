from termcolor import colored
import time

class MainArgumentParser(object):
    def __init__(self):
        self.parsed_arguments = dict()
        self.verbose = None
        self.seed = None
        self.server = None
        self.engine = None
        self.animate = None
        self.stats = None
        self.cores = None
        self.seedfuzz = None
        self.reproduce = None
        self.installsouffle = None

    def parse_arguments(self, parser):
        parser.add_argument("--verbose", nargs='?', const=True, default=False, help="Verbose mode")
        parser.add_argument("--animate", nargs='?', const=True, default=False, help="cool animation")
        parser.add_argument("--seed", help="Seed for the randomness class")
        parser.add_argument("--server", help="server name")
        parser.add_argument("--cores", help="Number of cores")
        parser.add_argument("--engine", help="Data log engine to test")
        parser.add_argument("--stats", nargs='?', const=True, default=False, help="Show live statistics")
        parser.add_argument("--seedfuzz", nargs='?', const=True, default=False, help="Seed Fuzz")
        parser.add_argument("--reproduce", help="Reproduce")
        parser.add_argument("--installsouffle", nargs='?', const=True, default=False, help="Install Souffle")

        arguments = vars(parser.parse_args())
        self.verbose = arguments["verbose"]
        self.animate = arguments["animate"]
        self.seed = arguments["seed"]
        self.server = arguments["server"] if arguments["server"] is not None else "local"
        self.engine = arguments["engine"] if arguments["engine"] is not None else "souffle"
        self.stats = arguments["stats"]
        self.cores = arguments["cores"]
        self.seedfuzz = arguments["seedfuzz"]
        self.reproduce = arguments["reproduce"]
        self.installsouffle = arguments["installsouffle"]

    def get_arguments(self):
        self.parsed_arguments["verbose"] = self.verbose
        self.parsed_arguments["animate"] = self.animate
        self.parsed_arguments["server"] = self.server
        self.parsed_arguments["engine"] = self.engine
        self.parsed_arguments["stats"] = self.stats
        self.parsed_arguments["cores"] = self.cores
        self.parsed_arguments["seedfuzz"] = self.seedfuzz
        self.parsed_arguments["reproduce"] = self.reproduce
        self.parsed_arguments["installsouffle"] = self.installsouffle
        # Use Unix time as seed in case no seed is provided
        if self.seed is None: 
            self.seed = str(int(time.time()))
        self.parsed_arguments["seed"] = self.seed
        # print arguments
        print("Parsed Arguments:")
        for key in sorted(self.parsed_arguments.keys()):
            print("\t" + colored(key, attrs=["bold"]) + " : " + colored(str(self.parsed_arguments[key]), "cyan", attrs=["bold"]))
        return self.parsed_arguments
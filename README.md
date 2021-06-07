[![Python package](https://github.com/numairmansur/queryFuzz/actions/workflows/python-package.yml/badge.svg)](https://github.com/numairmansur/queryFuzz/actions/workflows/python-package.yml) 
[![Python application](https://github.com/numairmansur/queryFuzz/actions/workflows/python-app.yml/badge.svg)](https://github.com/numairmansur/queryFuzz/actions/workflows/python-app.yml)


<img src="https://numairmansur.github.io/queryfuzz.png" width="400" height="220" />


Datalog is a popular query language with applications in several domains. 
Like any complex piece of software, Datalog engines may contain bugs. 
The most critical ones manifest as incorrect results when evaluating queries (query bugs).
Given the wide applicability of the language, query bugs may have detrimental consequences, 
for instance, by compromising the soundness of a program analysis that is implemented 
and formalized in Datalog. 

QueryFuzz implements the metamorphic testing approach for Datalog engines described in:
```
M. N. Mansur, M. Christakis, V. Wüstholz - Metamorphic Testing of Datalog Engines -
In Proceedings of the 29th Joint European Software Engineering Conference and Symposium on 
the Foundations of Software Engineering (ESEC/FSE'21).
```

# Installation:

## Ubuntu/Debian:
Support for C++17 is required, which is supported in g++ 7/clang++ 7 on.
```
sudo apt-get install autoconf automake bison build-essential clang doxygen flex g++ git libffi-dev libncurses5-dev libtool libsqlite3-dev make mcpp python sqlite zlib1g-dev
git clone https://github.com/numairmansur/queryFuzz
virtualenv --python=/usr/bin/python3.7 venv
source venv/bin/activate
cd queryFuzz
python setup.py install
```

# Usage:

## Testing `Soufflé`:
You can immediately start testing `Soufflé` by just typing the following command:
```
queryfuzz
```
When you run this command for the first time, it will download and install Soufflé. We use 
`Soufflé` as our backend tool to compare and find discrepancies in the results of two Datalog programs.
After successfully installing `Soufflé`, the above command will start the fuzzing procedure 
on the latest revision of `Soufflé`.

If you want to test a different version of `Soufflé`, please build and install that version 
and paste the path to `Soufflé` executable in the `path_to_souffle_engine` field in file
`/path/to/queryFuzz/params.json`. 


## Testing `µZ`:
If you want to run queryFuzz on `µZ`, please first build and install the appropriate version of `z3`. 
Then paste the path to `z3` executable in the `path_to_z3_engine` field in file `/path/to/queryFuzz/params.json`.
You can then begin the fuzzing procedure by running: 
```
queryfuzz --engine=z3
```

## Testing `DDlog`:
If you want to run queryFuzz on `DDlog`, please first build and install the appropriate version of `DDlog`. 
Then paste the path to `DDlog` executable in the `path_to_ddlog_engine` field in file `/path/to/queryFuzz/params.json`.
You would also have to add path to `DDlog` home directory in the `path_to_ddlog_home_dir` field in `/path/to/queryFuzz/params.json`.
You can then begin the fuzzing procedure by running: 
```
queryfuzz --engine=ddlog
```

## Want to test your own Datalog engine?
If you want to use QueryFuzz to test your own Datalog engine, please get in touch at <numair@mpi-sws.org>.

## Running on multiple cores:

If you wish to run parallel instances of Queryfuzz on `n` cores, use the `--cores` flag. For example: 
```
queryfuzz --cores=n
```

# Reproducing query bugs reported in our ESEC/FSE'21 paper:
Please follow the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz/tree/master/queryfuzz/fse_repl). 


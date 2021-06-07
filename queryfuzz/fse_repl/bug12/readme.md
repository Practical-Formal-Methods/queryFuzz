## bug12

Engine: `µZ`<br>
Version: `7fe829847938627ad880d3781fc81ac8dfd96cb3`<br>
Issue link: [#4893](https://github.com/Z3Prover/z3/issues/4893)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `z3` at version `7fe829847938627ad880d3781fc81ac8dfd96cb3`.
After installation, add the path to `z3` executable in the `path_to_z3_engine` field in `parameters.json`.
Then type

```
queryfuzz --reproduce=bug12
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_32.dl` using `EQU` transformation(s). 
The tranformation log can be seen in `transformed_rules_32.log`.
 
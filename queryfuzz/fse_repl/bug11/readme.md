## bug11

Engine: `µZ`<br>
Version: `fae9481308040ba84fe0e081e142cb9cd3e86cb9`<br>
Issue link: [#4879](https://github.com/Z3Prover/z3/issues/4879)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `z3` at version `fae9481308040ba84fe0e081e142cb9cd3e86cb9`.
After installation, add the path to `z3` executable in the `path_to_z3_engine` field in `parameters.json`.
Then type

```
queryfuzz --reproduce=bug11
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_8.dl` using `EQU` transformation(s). 
The tranformation log can be seen in `transformed_rules_8.log`.

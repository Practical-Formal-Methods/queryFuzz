## bug6

Engine: `Soufflé`<br>
Version: `934f7e36fe23f1046b4c511cb8114c62d0ba4674`<br>
Issue link: [#1738](https://github.com/souffle-lang/souffle/issues/1738)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `Soufflé` at version `934f7e36fe23f1046b4c511cb8114c62d0ba4674`.
After installation, add the path to `Soufflé` executable in the `path_to_souffle_engine` field in `parameters.json`. 
Then type

```
queryfuzz --reproduce=bug6
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_0.dl` using `EXP` transformation(s). 
The tranformation log can be seen in `transformed_rules_0.log`.

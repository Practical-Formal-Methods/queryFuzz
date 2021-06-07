## bug5

Engine: `Soufflé`<br>
Version: `fbb4c4b967bf58cccb7aca58e3d200a799218d98`<br>
Issue link: [#1732](https://github.com/souffle-lang/souffle/issues/1732)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `Soufflé` at version `fbb4c4b967bf58cccb7aca58e3d200a799218d98`.
After installation, add the path to `Soufflé` executable in the `path_to_souffle_engine` field in `parameters.json`. 
Then type

```
queryfuzz --reproduce=bug5
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_12.dl` using `EQU` transformation(s). 
The tranformation log can be seen in `transformed_rules_12.log`.

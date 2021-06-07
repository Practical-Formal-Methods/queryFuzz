 ## bug2

Engine: `Soufflé`<br>
Version: `20d76ce2124d40e6636c3cc5a956116cf984d16a`<br>
Issue link: [#1463](https://github.com/souffle-lang/souffle/issues/1463)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `Soufflé` at version `20d76ce2124d40e6636c3cc5a956116cf984d16a`.
After installation, add the path to `Soufflé` executable in the `path_to_souffle_engine` field in `parameters.json`. 
Then type

```
queryfuzz --reproduce=bug2
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_21.dl` using `EXP` transformation(s). 
The tranformation log can be seen in `transformed_rules_21.log`.

## bug4

Engine: `Soufflé`<br>
Version: `2995ff775ccb23342b06b457835662b03c5bc1f5`<br>
Issue link: [#1679](https://github.com/souffle-lang/souffle/issues/1679)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `Soufflé` at version `2995ff775ccb23342b06b457835662b03c5bc1f5`.
After installation, add the path to `Soufflé` executable in the `path_to_souffle_engine` field in `parameters.json`. 
Then type

```
queryfuzz --reproduce=bug4
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_70.dl` using `EQU` transformation(s). 
The tranformation log can be seen in `transformed_rules_70.log`.

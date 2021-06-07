## bug1

Engine: `Soufflé`<br>
Version: `4b6b17fe322eb1ed12aa1f945df6da4c9925002d`<br>
Issue link: [#1453](https://github.com/souffle-lang/souffle/issues/1453)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `Soufflé` at version `4b6b17fe322eb1ed12aa1f945df6da4c9925002d`.
After installation, add the path to `Soufflé` executable in the `path_to_souffle_engine` field in `parameters.json`. 
Then type

```
queryfuzz --reproduce=bug1
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_63.dl` using `CON` transformation(s). 
The tranformation log can be seen in `transformed_rules_63.log`.

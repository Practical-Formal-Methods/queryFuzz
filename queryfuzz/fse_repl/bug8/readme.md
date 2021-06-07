## bug8

Engine: `Soufflé`<br>
Version: `4bf6d1ceba23693d3e4a2e8bda3b86fec86f93a2`<br>
Issue link: [#1848](https://github.com/souffle-lang/souffle/issues/1848)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `Soufflé` at version `4bf6d1ceba23693d3e4a2e8bda3b86fec86f93a2`.
After installation, add the path to `Soufflé` executable in the `path_to_souffle_engine` field in `parameters.json`. 
Then type

```
queryfuzz --reproduce=bug8
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_0.dl` using `CON` transformation(s). 
The tranformation log can be seen in `transformed_rules_0.log`.

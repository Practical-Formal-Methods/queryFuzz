## bug3

Engine: `Soufflé`<br>
Version: `a9ac3cbf2aad1b3bf8dfd335192e7a9328ec4b4d`<br>
Issue link: [#1467](https://github.com/souffle-lang/souffle/issues/1467)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `Soufflé` at version `a9ac3cbf2aad1b3bf8dfd335192e7a9328ec4b4d`.
After installation, add the path to `Soufflé` executable in the `path_to_souffle_engine` field in `parameters.json`. 
Then type

```
queryfuzz --reproduce=bug3
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_1.dl` using `EXP` transformation(s). 
The tranformation log can be seen in `transformed_rules_1.log`.

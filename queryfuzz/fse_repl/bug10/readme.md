## bug10

Engine: `µZ`<br>
Version: `7089610bbd45fc51651ba8caac925cabb479092f`<br>
Issue link: [#4870](https://github.com/Z3Prover/z3/issues/4870)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `z3` at version `7089610bbd45fc51651ba8caac925cabb479092f`.
After installation, add the path to `z3` executable in the `path_to_z3_engine` field in `parameters.json`.
Then type

```
queryfuzz --reproduce=bug10
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_28.dl` using `CON` transformation(s). 
The tranformation log can be seen in `transformed_rules_28.log`.

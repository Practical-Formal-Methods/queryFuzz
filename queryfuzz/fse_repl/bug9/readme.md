## bug9

Engine: `µZ`<br>
Version: `6d427d9dae4f374107297b5bf0dd0fa5651c0d1b`<br>
Issue link: [#4844](https://github.com/Z3Prover/z3/issues/4844)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `z3` at version `6d427d9dae4f374107297b5bf0dd0fa5651c0d1b`.
After installation, add the path to `z3` executable in the `path_to_z3_engine` field in `parameters.json`.
Then type

```
queryfuzz --reproduce=bug9
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_9.dl` using `CON` transformation(s). 
The tranformation log can be seen in `transformed_rules_9.log`.

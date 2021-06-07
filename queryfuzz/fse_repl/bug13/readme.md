## bug13

Engine: `DDlog`<br>
Version: `00899b18b06816b1e84b84411e09aacfe4240a65`<br>
Issue link: [#878](https://github.com/vmware/differential-datalog/issues/878)

### Steps:
Install QueryFuzz by following the instructions [here](https://github.com/Practical-Formal-Methods/queryFuzz).
Download and install `DDlog` at version `00899b18b06816b1e84b84411e09aacfe4240a65`.
After installation, add the path to `DDlog` executable in the `path_to_ddlog_engine` field in `parameters.json`.
You would also need to add path to DDlog home directory in the `path_to_ddlog_home_dir` field in `parameters.json`
Then type

```
queryfuzz --reproduce=bug13
```

This will create a `temp` folder in this directory. In the `temp/bug0`, you will find 
`orig_rules.dl` which was transformed to `transformed_rules_30.dl` using `EQU` transformation(s). 
The tranformation log can be seen in `transformed_rules_30.log`.
 
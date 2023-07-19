# CodeAudit

```
token_func:[[filepath, name, line, val_type, [[name, line, val_type], [name, line, val_type]....]],
			[name, line, val_type, [[name, line, val_type], [name, line, val_type]....]]...... ]
token_val:[[filepath, name, line, val_type, [[name, line, val_type], [name, line, val_type]....]], 
           [name, line, val_type, [[name, line, val_type], [name, line, val_type]....]]......]
danger:[[filepath, line, function_name, risk, solve],
        [filepath, line, function_name, risk, solve].......]
invalidfunc:[[filepath, line, name], 
             [filepath, line, name]......]
invalidval:[[filepath, line, name],
            [filepath, line, name]......]
```

全为str

token list 中的最后一项可能为空。

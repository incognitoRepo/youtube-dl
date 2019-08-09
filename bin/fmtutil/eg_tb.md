```python
Traceback (most recent call last):
  File "fmt.py", line 67, in <module>
    literate_style = fud.write_literate_style_df(aggdf,color=False)
  File "/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/fmtutil/dataframe.py", line 189, in entry
    return write_literate_style_df(df,color=color)
  File "/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/fmtutil/dataframe.py", line 198, in write_literate_style_df
    ca_str,sn_itrr = dtacels_itrr = format_call_datacell(r.call_data,r.event_kind), format_snoop_datacell(r.snoop_data);1/0
ZeroDivisionError: division by zero
```

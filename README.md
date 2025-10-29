# oth-scrape-tool
Some simple python utilities to interact with the OTH-Website.

## Blackboard
Can scrape the current blackboard from the IM-Faculty of the OTH.
Will either print it to the terminal or save into a markdown file.
```bash
# print blackboard to terminal
python3 oth_tool.py black

# print as markdown
python3 oth_tool.py b -m
```

A few aliases for `blackboard` are supported.

## Mensaplan
Receive the mensaplan for the current week (or any calendar week).
```python
# print to console
python3 oth_tool.py mensaplan

# print as markdown
python3 oth_tool.py m -m
```
This also supports a few aliases.

### Options
- `-m` prints the output as markdown and embeds links to the images
- `-d` day of the week (e.g. monday/montag, dienstag, ...)
- `-w` calendar week to view
- `-t` print today's mensaplan

Weekdays also support a few aliases.

## Planned features
- html output support

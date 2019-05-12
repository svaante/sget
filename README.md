# SGET

[![asciicast](https://asciinema.org/a/tphk9GPW0ZDGMrKLzoGqbhZYE.png)](https://asciinema.org/a/tphk9GPW0ZDGMrKLzoGqbhZYE?speed=3)

## INSTALL
```bash
git clone git@github.com:ONordander/sget.git
cd sget
pip install -e .
```

## USAGE
```bash
# Add a snippet
sget add "grep -r "sget" *" --name grep_sget --description "simple grep" --groups unix

# Add many snippets from a .toml file
sget install defaults/bash.toml

# Get a snippet from search prompt
sget

# Get a snippet by name
sget get grep_sget

# Remove snippet by name (leaving the name blank will start a search prompt)
sget rm grep_sget

# List all snippets (with optional group)
sget list -g unix

# Clear all snippets
sget clear

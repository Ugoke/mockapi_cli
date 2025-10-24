# 🖥️ MockAPI CLI Commands

## The MockAPI CLI provides convenient commands for managing mock servers without manually writing Django views and URLs.
## Below is a complete reference of all commands, options, and examples.

### 📚 General syntax
```bash
python -m mockapi <command> [options] [arguments]
```
---
### MockAPI CLI
```bash
python -m mockapi
```
---
### Add
#### Adds a JSON file with mocks to local storage for later execution without specifying a path.
#### If the file is in the current folder
```bash
python -m mockapi add main.json
```
#### If you need to specify an absolute path
```bash
python -m mockapi add C:\Users\username\Desktop\test_mockapi\main.json
```
---
### Add Settings
#### Adds a JSON file with settings to local storage
```bash
python -m mockapi add-settings settings.json
```
#### If you need to specify an absolute path
```bash
python -m mockapi add-settings C:\Users\username\Desktop\test_mockapi\settings.json
```
---
### Start
```bash
python -m mockapi start
```
The server automatically uses the built-in JSON file and deploys all routes.
Starting with a separate JSON file
If you want to use a different JSON file without adding it to the system, specify the path to the file:
```bash
# Absolute path to the file
python -m mockapi start C:\Users\username\Desktop\test_mockapi\main.json

# Relative path
python -m mockapi start ./main.json
```
#### Once launched, the server will be accessible at http://127.0.0.1:8000, and all JSON routes will return the specified responses.
---
### Help
```bash
python -m mockapi --help
```
#### Or
```bash
python -m mockapi <command> --help
```
#### For a specific command
---
### Set Default
Restores default JSON configuration files (```settings.json``` and/or ```mocks.json```) from example templates.
Use this command if you want to reset your MockAPI configuration to its default state.
```bash
python -m mockapi set-default
```
#### Options:
Option:
```--file-name```, ```-f```
Description:
Specify which file to reset - ```"settings"``` or ```"mocks"```. If not specified, both will be reset.
---
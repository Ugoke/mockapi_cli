# 🚀 Quick Start

## This section will help you set up your first Django mock server in 2-3 minutes using the MockAPI CLI.

### 🛠️ 1. Create a mock file
### Create a mocks.json file and add a minimal example:

```json
[
   {
    "path": "/api/goods/1",
    "method": "GET",
    "status": 200,
    "response": [
        {
        "id": 1,
        "name": "car"
        }
      ]
    }
]
```

### ⚡ 2. Launch the server
### In the same directory, run:

```bash
# If the file is in the current folder
python -m mockapi add main.json

# If you need to specify an absolute path
python -m mockapi add C:\Users\username\Desktop\test_mockapi\main.json
```

### 🚀 3. Starting the MockAPI Server
### Once the JSON file has been added, you can start the server and begin serving mock endpoints.
### Starting with an embedded JSON file
### If you've already added the JSON file using the add command, you can simply start the server:

```bash
python -m mockapi start
```

## That's it! You've launched the server.
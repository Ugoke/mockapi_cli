# ⚙️ Settings Configuration
## This file describes the basic settings of the local server.
```json
{
  "host": "127.0.0.1",
  "port": "8000",
  "append_slash": true
}
```
## Description of parameters:
- ```host``` - Local IP address (localhost). The server will only be accessible from this machine.
- ```port``` - The port on which the server runs.
- ```append_slash``` - If enabled, the server automatically adds a forward slash (/) to the end of the URL if it is missing.
  For example: a request to ```/about``` will be redirected to ```/about/```.
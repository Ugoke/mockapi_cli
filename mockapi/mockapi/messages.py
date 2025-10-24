import sys
import django
import click

from . import settings


HELP_TEXT_FOR_ADD_COMMAND = """
Add mocks from a user JSON file into the local mocks.json file.

Usage:
    python -m mockapi add <user_file>

Arguments:
    user_file   Path to the user JSON file containing mocks.

Description:
    This command copies all mocks from the specified user JSON file into the
    local mocks.json file used by the server. The JSON file must contain
    an array of objects, where each object represents a mock with the fields:
        - path: the API endpoint (e.g., /api/product)
        - method: HTTP method (GET, POST, etc.)
        - status: HTTP status code to return
        - response: JSON response to return"""


HELP_TEXT_FOR_ADD_SETTINGS_COMMAND = """
Adds a JSON file with settings to local storage.

Usage:
    python -m mockapi add <user_file>

Arguments:
    user_file   Path to the user JSON file containing settings.
"""


HELP_TEXT_FOR_START_COMMAND = """
Start the local Django server to serve mocks.

Usage:
    python -m mockapi start [OPTIONS]

Options:
    --file PATH JSON file containing mocks (default: mocks.json)"""


class Hello:
    def __get_version(self) -> str:
        return settings.VERSION

    def __get_python_version(self) -> str:
        return sys.version

    def __get_requirements_version(self) -> str:
        return f"Djnago: {django.get_version()}, Click: {click.__version__}, ..."

    def show(self) -> str:
      return rf"""                                                                                                                                          
 .                                                __  __         _      _   ___ ___    ___ _    ___ 
  ...                                            |  \/  |___  __| |__  /_\ | _ \_ _|  / __| |  |_ _|     
   ....                                          | |\/| / _ \/ _| / / / _ \|  _/| |  | (__| |__ | | 
     .''.                                ....    |_|  |_\___/\__|_\_\/_/ \_\_| |___|  \___|____|___|
      ..;;,'.                          ......    
        .';cl;.                     ........     Version: {self.__get_version()}
           .:dxc.                ..',,''....     Python: {self.__get_python_version()}
             'lkkl'... .........,;;;;;,....      Requirements version: {self.__get_requirements_version()}
               'o00xl:,;;:coolcllc:;''....       
                .c0Xk,    .;xOdc::;,......       
                .,c;.      .ldc;;;'.....         
                .c:       ;dxl:,......           
               .,do.   .,okd:'......             
                'oOd;;lddl;'......               
                ,dOxodoc;........                
              .'cll:::,'...........              
             .,:;,,,........   ..''..            
           ..',''....... ..      ..,;..          
         ...'.......   ...         ..''.         
       ...........   ..               ....       
      ...........                       ....     
    ......                                ...    
   .......                                       
  . .. ..                                     
 """
    

HELP_TEXT_FOR_SET_DEFAULT = """Set default data JSON files (settings, mocks, or both)."""
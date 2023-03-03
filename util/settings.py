import os, json
from typing import Any, Callable, Dict, List, Optional, cast

from util.debug import catch

class Settings():
    '''Handles configuration data.'''
    
    _data: Dict[str, Any]
    _callback: Optional[Callable[[str], Any]]
    
    def __init__(self,
                 data: Dict[str, Any],
                 callback: Optional[Callable[[str], Any]] = None):
        self._data = data
        self._callback = callback
    
    def get(self, setting: str, default: object = None) -> Optional[Any]:
        '''Returns the value of the specified setting or the provided default.'''
        
        # try to pull from the dictionary first
        obj = self._data.get(setting)
        
        # use the callback fallback
        if obj is None and self._callback is not None:
            try:
                obj = self._callback(setting)
            except:
                pass
        
        return obj if obj is not None else default
    
    def keys(self) -> List[str]:
        '''Returns list of all keys.'''
        
        return list(self._data.keys())
    
    def __getitem__(self, setting: str) -> Any:
        '''Returns the value of the specified setting.'''
        
        # throws on failure
        value = self.get(setting)
        if value is None:
            raise KeyError(setting)
        else:
            return value


def json_settings(filename: str) -> Settings:
    '''Loads configuration settings stored as JSON data.'''
    
    with catch((json.decoder.JSONDecodeError, FileNotFoundError),
               f'Settings :: Failed to load JSON data from {filename}!'):
        
        with open(filename, encoding='utf8') as file:
            obj = json.loads(file.read())
            
            # force result to be a dictionary
            if isinstance(obj, dict):
                return Settings(cast(Dict[str, Any], obj))
            else:
                return Settings({'_data': obj})


def env_settings(filename: str) -> Settings:
    '''Loads configuration settings stored in key=value format.'''
    
    obj: Dict[str, str] = {}
    with catch(FileNotFoundError,
               f'Settings :: Failed to load ENV data from {filename}!'):
        
        with open(filename) as file:
            
            # attempts to parse each line in key=value format
            for line in file.readlines():
                with catch(ValueError,
                           f'Settings :: Failed to parse ENV line "{line}"'):
                    key, value = line.split('=', 1)
                    obj[key] = value.rstrip('\r\n')
    
    return Settings(obj, callback=os.getenv)

Config = json_settings('config.jason')
Env = env_settings('.env')

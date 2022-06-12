import os, json
from abc import ABC, abstractmethod
from typing import Any, Dict, TextIO, cast, List
from util.debug import catch

class Settings(ABC):
    '''Handles configuration data.'''

    _data: Dict[str, Any] = {}
    
    @property
    @classmethod
    @abstractmethod
    def SETTINGS_FILE(self) -> str: ...
    
    @classmethod
    @abstractmethod
    def load(cls) -> None:
        '''Initializes the configuration data from the default file.'''

        try:
            with open(cast(str, cls.SETTINGS_FILE), 'r') as file:
                cls.load_file(file)
        except FileNotFoundError:
            cls._data = {}

    @classmethod
    @abstractmethod
    def load_file(cls, file: TextIO) -> None:
        '''Initializes the configuration data from the specified file.'''

    @classmethod
    def get(cls, setting: str, default: object = None) -> object:
        '''Returns the value of the specified setting or the provided default.'''
        
        return cls._data.get(setting, default)

    @classmethod
    def keys(cls) -> List[str]:
        '''Returns list of all keys.'''

        return list(cls._data.keys())

    def __class_getitem__(cls, setting: str) -> object:
        '''Returns the value of the specified setting.'''

        # throws on failure
        value = cls.get(setting)
        if value is None:
            raise KeyError(setting)
        else:
            return value


class Config(Settings):
    '''Handles configuration data pulled from a public file.'''
    
    SETTINGS_FILE: str = 'config.jason'
    
    @classmethod
    def load_file(cls, file: TextIO) -> None:
        '''Initializes the configuration data from the configuration JSON file.'''

        cls._data = {}
        
        # attempts to load as a json object
        with catch(json.decoder.JSONDecodeError, 'Settings :: Failed to load configuration data!'):
            obj = json.loads(file.read())
            if isinstance(obj, dict):
                cls._data = obj



class Env(Settings):
    '''Handles sensitive or secret configuration data pulled from environment variables.'''
    
    SETTINGS_FILE: str = '.env'
    
    @classmethod
    def load_file(cls, file: TextIO) -> None:
        '''Initializes the configuration data from the secrets file.'''
        
        cls._data = {}
        
        # attempts to parse each line in key=value format
        for line in file.readlines():
            with catch(ValueError, f'Settings :: Failed to parse line "{line}"'):
                key, value = line.split('=', 1)
                cls._data[key] = value.rstrip('\r\n')
        
    @classmethod
    def get(cls, setting: str, default: object = None) -> str:
        '''Returns the value of the specified setting or the provided default.'''

        # defaults to os environment variables with the loaded data as fallback
        return os.getenv(setting, cls._data.get(setting, default))

class TalkConfig(Settings):
    '''Handles loading the talk Markov chain data.'''

    SETTINGS_FILE: str = 'markov.jason'

    @classmethod
    def load_file(cls, file: TextIO) -> None:
        '''Initializes the configuration data from the configuration JSON file.'''

        cls._data = {}
        
        # attempts to load as a json object
        with catch(json.decoder.JSONDecodeError, 'Settings :: Failed to load talk configuration data!'):
            obj = json.loads(file.read())
            if isinstance(obj, dict):
                cls._data = obj

Config.load()
Env.load()
TalkConfig.load()
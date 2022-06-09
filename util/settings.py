import os, json
from abc import ABC, abstractmethod
from typing import Any, Dict, TextIO
from util.debug import error

class Settings(ABC):
    '''Handles configuration data.'''

    _data: Dict[str, Any] = {}
    
    @property
    @abstractmethod
    def SETTINGS_FILE(self) -> str: ...

    @classmethod
    @abstractmethod
    def load(cls) -> None:
        '''Initializes the configuration data from the default file.'''

        try:
            with open(cls.SETTINGS_FILE, 'r') as file:
                cls.load_file(file)
        except FileNotFoundError:
            cls._data = {}

    @classmethod
    @abstractmethod
    def load_file(cls, file: TextIO) -> None:
        '''Initializes the configuration data from the specified file.'''

    @classmethod
    def get(cls, setting: str, default: str = None) -> object:
        '''Returns the value of the specified setting or the provided default.'''
        
        return cls._data.get(setting, default)


    def __class_getitem__(cls, setting: str) -> str:
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
        try:
            obj = json.loads(file.read())
            if isinstance(obj, dict):
                cls._data = obj
        except json.decoder.JSONDecodeError as e:
            error(e, 'Failed to load configuration data!')



class Env(Settings):
    '''Handles sensitive or secret configuration data pulled from environment variables.'''
    
    SETTINGS_FILE: str = '.env'
    
    @classmethod
    def load_file(cls, file: TextIO) -> None:
        '''Initializes the configuration data from the secrets file.'''
        
        cls._data = {}
        
        # attempts to parse each line in key=value format
        for line in file.readlines():
            try:
                key, value = line.split('=', 1)
                cls._data[key] = value.rstrip('\r\n')
            except ValueError:
                pass
        
    @classmethod
    def get(cls, setting: str, default: str = None) -> str:
        '''Returns the value of the specified setting or the provided default.'''

        # defaults to os environment variables with the loaded data as fallback
        return os.getenv(setting, cls._data.get(setting, default))


Config.load()
Env.load()
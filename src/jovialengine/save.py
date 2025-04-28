import sys
import os
import json
from types import ModuleType
from collections import deque

import pygame.math

from . import gamebuilder
from .saveable import Saveable


_KEY_COLLECTION = 'COLLECTION'
_COLLECTION_DEQUE = 'DEQUE'
_COLLECTION_SET = 'SET'
_COLLECTION_VECTOR2 = 'VECTOR2'
_COLLECTION_VECTOR3 = 'VECTOR3'
_KEY_ELEMENTS = 'ELEMENTS'
_KEY_MAXLEN = 'MAXLEN'
_KEY_MODULE = 'MODULE'
_KEY_CLASS = 'CLASS'
_KEY_SAVEABLE = 'SAVEABLE'
_SAVE_EXT = '.sav'
_save_directory: str | None = None
_mode_module: ModuleType


def init(save_directory: str, mode_module: ModuleType):
    global _save_directory
    global _mode_module
    if _save_directory:
        raise RuntimeError("error: _save_directory is already set")
    _save_directory = save_directory
    _mode_module = mode_module


class _SaveableJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, deque):
            return {
                _KEY_COLLECTION: _COLLECTION_DEQUE,
                _KEY_ELEMENTS: list(o),
                _KEY_MAXLEN: o.maxlen,
            }
        elif isinstance(o, set):
            return {
                _KEY_COLLECTION: _COLLECTION_SET,
                _KEY_ELEMENTS: list(o),
            }
        elif isinstance(o, pygame.math.Vector2):
            return {
                _KEY_COLLECTION: _COLLECTION_VECTOR2,
                _KEY_ELEMENTS: list(o),
            }
        elif isinstance(o, pygame.math.Vector3):
            return {
                _KEY_COLLECTION: _COLLECTION_VECTOR3,
                _KEY_ELEMENTS: list(o),
            }
        elif isinstance(o, type):
            return {
                _KEY_MODULE: o.__module__,
                _KEY_CLASS: o.__qualname__,
            }
        elif isinstance(o, Saveable):
            return {
                _KEY_MODULE: type(o).__module__,
                _KEY_CLASS: type(o).__qualname__,
                _KEY_SAVEABLE: o.save(),
            }
        return super().default(o)


def _get_class(dct: dict):
    attr = sys.modules[dct[_KEY_MODULE]]
    for name in dct[_KEY_CLASS].split('.'):
        attr = getattr(attr, name)
    return attr


def _decode_saveable(dct: dict):
    if _KEY_COLLECTION in dct:
        if dct[_KEY_COLLECTION] == _COLLECTION_DEQUE:
            return deque(dct[_KEY_ELEMENTS], dct[_KEY_MAXLEN])
        elif dct[_KEY_COLLECTION] == _COLLECTION_SET:
            return set(dct[_KEY_ELEMENTS])
        elif dct[_KEY_COLLECTION] == _COLLECTION_VECTOR2:
            return pygame.math.Vector2(dct[_KEY_ELEMENTS])
        elif dct[_KEY_COLLECTION] == _COLLECTION_VECTOR3:
            return pygame.math.Vector3(dct[_KEY_ELEMENTS])
    elif {_KEY_MODULE, _KEY_CLASS} == dct.keys():
        return _get_class(dct)
    elif {_KEY_MODULE, _KEY_CLASS, _KEY_SAVEABLE} == dct.keys():
        saveable_class = _get_class(dct)
        return saveable_class.load(dct[_KEY_SAVEABLE])
    return dct


class Save(object):
    __slots__ = (
        'save_name',
        '_mode_name',
        '_mode_data',
        '_shared_data',
    )

    def __init__(self, save_name: str, mode_name: str, mode_data, shared_data):
        self.save_name = save_name
        self._mode_name = mode_name
        self._mode_data = mode_data
        self._shared_data = shared_data

    @staticmethod
    def will_overwrite(save_name: str):
        return os.path.exists(
            Save._get_file_path_from_file_name(save_name + _SAVE_EXT)
        )

    @staticmethod
    def _get_save_files():
        if not os.path.isdir(_save_directory):
            return ()
        return (
            file_name
            for file_name
            in os.listdir(_save_directory)
            if os.path.isfile(
                Save._get_file_path_from_file_name(file_name)
            )
            and file_name.endswith(_SAVE_EXT)
        )

    @staticmethod
    def _get_file_path_from_file_name(file_name):
        return os.path.join(_save_directory, file_name)

    def _get_file_path(self):
        return self._get_file_path_from_file_name(self.save_name + _SAVE_EXT)

    @classmethod
    def get_all_from_files(cls):
        return sorted(
            (
                save
                for save
                in (
                    cls._get_from_file(file)
                    for file
                    in cls._get_save_files()
                )
                if save is not None
            ),
            key=lambda s: (s.save_name.lower(), s.save_name)
        )

    @classmethod
    def _get_from_file(cls, file_name: str):
        file_path = cls._get_file_path_from_file_name(file_name)
        try:
            with open(file_path, 'r') as file:
                save_object = json.load(file, object_hook=_decode_saveable)
                return cls(
                    file_name[:-len(_SAVE_EXT)],
                    save_object['mode_name'],
                    save_object['mode_data'],
                    save_object['shared_data']
                )
        except (IOError, json.decoder.JSONDecodeError):
            return None

    @classmethod
    def get_from_mode(cls, save_name: str, from_mode: Saveable):
        return cls(
            save_name,
            type(from_mode).__name__,
            from_mode.save(),
            gamebuilder.get_state().save()
        )

    def save(self):
        try:
            os.mkdir(_save_directory)
        except FileExistsError:
            pass
        save_object = {
            'mode_name': self._mode_name,
            'mode_data': self._mode_data,
            'shared_data': self._shared_data,
        }
        file_path = self._get_file_path()
        try:
            with open(file_path, 'w') as file:
                json.dump(save_object, file, cls=_SaveableJSONEncoder)
            return True
        except IOError:
            return False

    def load(self):
        gamebuilder.set_state(self._shared_data)
        mode_cls = getattr(_mode_module, self._mode_name)
        new_mode = mode_cls.load(self._mode_data)
        return new_mode

    def load_state(self):
        gamebuilder.set_state(self._shared_data)

    def delete(self):
        file_path = self._get_file_path()
        os.remove(file_path)

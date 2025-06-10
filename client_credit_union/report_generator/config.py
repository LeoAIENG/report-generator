from pathlib import Path
import yaml
from types import SimpleNamespace

config_file_path = Path().cwd() / 'config.yaml'

def _convert_dict_to_namespace(_dict):
    if isinstance(_dict, dict):
        namespace = SimpleNamespace()
        setattr(namespace, 'config', _dict)
        for key, value in _dict.items():
            if isinstance(value, dict):
                setattr(namespace, key, _convert_dict_to_namespace(value))
            else:
                setattr(namespace, key, value)
        return namespace
    return _dict

def _set_initial_paths(config):
    base_path = Path().cwd()
    config.path.src = base_path / config.path.src
    config.path.data = config.path.src / config.path.data
    config.path.templates = config.path.data / config.path.templates
    config.path.input = config.path.data / config.path.input
    config.path.output = config.path.data / config.path.output
    config.path.images = config.path.data / config.path.images
    config.path.loan_json = config.path.input/ config.path.loan_json_file
    config.path.credit_excel = config.path.input / config.path.credit_excel_file
    return config

def _set_globals(config):
    for key, value in config.__dict__.items():
        globals()[key] = value

def load_config():
    with open(config_file_path, 'r') as file:
        config_dict = yaml.safe_load(file)
        config = _convert_dict_to_namespace(config_dict)
        config = _set_initial_paths(config)
        _set_globals(config)
        return config

config = load_config()
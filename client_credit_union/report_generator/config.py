from pathlib import Path
import yaml
from types import SimpleNamespace
import os
import dotenv

dotenv.load_dotenv()

config_path = Path().cwd() / 'config'


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

def _set_paths(config):
    base_path = Path().cwd()
    config.path.credentials = base_path /config.path.credentials_file
    config.path.data = base_path / config.path.data
    config.path.templates = config.path.data / config.path.templates
    config.path.input = config.path.data / config.path.input
    config.path.output = config.path.data / config.path.output
    config.path.images = config.path.data / config.path.images
    config.path.loan_json = config.path.input / config.path.loan_json_file
    config.path.credit_excel = config.path.input / config.path.credit_excel_file
    
    return config

def _set_credentials(config):
    config.app.secrets.encompass.username = os.getenv("ENCOMPASS_USERNAME")
    config.app.secrets.encompass.password = os.getenv("ENCOMPASS_PASSWORD")
    config.app.secrets.encompass.client_id = os.getenv("ENCOMPASS_CLIENT_ID")
    config.app.secrets.encompass.client_secret = os.getenv("ENCOMPASS_CLIENT_SECRET")
    return config

def _set_globals(config):
    for key, value in config.__dict__.items():
        globals()[key] = value

def load_config():
    config = {
        path.stem: yaml.safe_load(path.read_text())
        for path in config_path.glob('*.yaml')
    }
    config = _convert_dict_to_namespace(config)
    config = _set_paths(config)
    config = _set_credentials(config)
    _set_globals(config)
    return config

config = load_config()
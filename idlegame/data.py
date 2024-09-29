import os
import pickle
import getpass
from . import config
import logging

def load(filename: str = config.save_file) -> dict:
    """Load data from a pickle file.

    Args:
        filename (str): The path to the pickle file to load data from.

    Returns:
        dict: The data loaded from the file, or an empty dictionary if the file does not exist or an error occurs.
    """
    if os.path.exists(filename):
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except (pickle.UnpicklingError, EOFError, FileNotFoundError) as e:
            logging.error(f"Error loading data from {filename}: {e}")
            return {}
    else:
        logging.warning(f"File {filename} does not exist. Returning empty dictionary.")
    return {}

def save(data: dict, filename: str = config.save_file) -> None:
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

class AutosavedPlayer():
    DEFAULT_ATTRIBUTES: dict[str, int, dict] = {
        'tree_health': 100,
        'gold': 0,
        'last_claim_timestamp': None,
        'settings': {},
        'aliases': {},
        'nano_cores': {'normal': 0, 'miner': 0, 'fighter': 0, 'super': 0, 'warper': 0},
        'nanos': [],
        'system_complexity': 0.0,
        'warps': 0,
    }

    def __init__(self, override_directory=None) -> None:
        self.username = getpass.getuser()  # Automatically use the current system user
        self._data = self.load(override_directory if override_directory else config.save_file)
        self.override_save_dir = override_directory if override_directory else False
        self.automigrate()

        for key, value in self._data.items():
            setattr(self, key, value)

    def load(self, filename: str = config.save_file) -> dict:
        if os.path.exists(filename):
            return(load(filename))
        print("Welcome to idlegame, the pip & play Python game!")
        print("idlegame emulates a zsh command line to play. Get started: `man idlegame` / `man commands`")
        print("© 2024 Ben Boonstra MIT License.")
        return {}

    def save(self, filename: str = config.save_file) -> None:
        save(self._data, self.override_save_dir if self.override_save_dir else filename)

    def __getattr__(self, attr: str) -> int:
        if attr == 'system_complexity':
            self.update_complexity()
            return self._data.get('system_complexity', 0.0)
        if attr in self._data:
            return self._data[attr]
        raise AttributeError(f"{attr} not found")


    def __setattr__(self, attr: str, value: int) -> None:
        if attr in ['username', '_data']:
            super().__setattr__(attr, value)
        else:
            self._data[attr] = value
            self.save()

    def automigrate(self) -> None:
        for attr, default_value in self.DEFAULT_ATTRIBUTES.items():
            if attr not in self._data:
                self._data[attr] = default_value
        for bot in self.nanos:
            bot.update_complexity()
        self.update_complexity()

    def update_complexity(self) -> None:
        self.system_complexity = sum(bot.complexity for bot in self.nanos) + (len(self.aliases) / 10)

def handle_login() -> AutosavedPlayer:
    """Automatically login as the current system user."""
    username = getpass.getuser()
    print(f"Logged in as: {username}")

    return AutosavedPlayer()
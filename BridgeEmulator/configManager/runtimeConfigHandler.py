from dataclasses import dataclass, field
from typing import Dict, Any
from configManager.argumentHandler import parse_arguments

@dataclass
class Config:
    newLights: Dict[str, Any] = field(default_factory=dict)
    arg: Dict[str, Any] = field(default_factory=dict)

    def populate(self) -> None:
        """
        Populate the configuration with parsed arguments.

        Args:
            None

        Returns:
            None
        """
        self.newLights.clear()
        self.arg.update(parse_arguments())

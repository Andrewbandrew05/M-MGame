import json
from dataclasses import dataclass, asdict, field
from typing import List, Dict


# Available energy types
ENERGY_TYPES = ["Power", "Fire", "Toxic", "Shadow", "Water"]


@dataclass
class Attack:
    """Represents an attack that a creature can perform."""
    name: str
    damage: int
    description: str = ""
    energy_costs: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize energy_costs with all energy types if not provided."""
        if not self.energy_costs:
            self.energy_costs = {energy_type: 0 for energy_type in ENERGY_TYPES}

    def to_dict(self):
        return {
            "name": self.name,
            "damage": self.damage,
            "description": self.description,
            "energy_costs": self.energy_costs
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Attack':
        """Create an Attack from a dictionary."""
        return Attack(
            name=data["name"],
            damage=data["damage"],
            description=data.get("description", ""),
            energy_costs=data.get("energy_costs", {energy_type: 0 for energy_type in ENERGY_TYPES})
        )


@dataclass
class CreatureCard:
    """Represents a creature card with combat and stat information."""
    name: str
    description: str
    health: int
    type: str
    creature_class: str
    is_titan: bool = False
    image_path: str = ""
    attacks: List[Attack] = field(default_factory=list)

    def to_dict(self):
        """Convert the creature card to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "health": self.health,
            "type": self.type,
            "creature_class": self.creature_class,
            "is_titan": self.is_titan,
            "image_path": self.image_path,
            "attacks": [attack.to_dict() for attack in self.attacks]
        }

    def to_json(self) -> str:
        """Convert the creature card to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @staticmethod
    def from_dict(data: dict) -> 'CreatureCard':
        """Create a CreatureCard from a dictionary."""
        attacks = [Attack.from_dict(attack) for attack in data.get("attacks", [])]
        return CreatureCard(
            name=data["name"],
            description=data["description"],
            health=data["health"],
            type=data["type"],
            creature_class=data["creature_class"],
            is_titan=data.get("is_titan", False),
            image_path=data.get("image_path", ""),
            attacks=attacks
        )

    @staticmethod
    def from_json(json_string: str) -> 'CreatureCard':
        """Create a CreatureCard from a JSON string."""
        data = json.loads(json_string)
        return CreatureCard.from_dict(data)

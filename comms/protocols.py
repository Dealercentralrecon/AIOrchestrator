from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TaskDefinition:
    requirements: List[str]
    dependencies: List[str]
    success_criteria: Dict[str, float]
    resource_constraints: Dict[str, str]
    priority: int = 1


class ProtocolValidator:
    @staticmethod
    def validate_task(task: dict) -> bool:
        required_fields = {
            "requirements",
            "dependencies",
            "success_criteria",
            "resource_constraints",
        }
        return all(field in task for field in required_fields)

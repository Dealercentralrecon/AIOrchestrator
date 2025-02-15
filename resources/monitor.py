from typing import Dict

import psutil

from utils.logger import setup_logger


class ResourceMonitor:
    def __init__(self):
        self.logger = setup_logger(name="ResourceMonitor")
        self.agent_resources: Dict[str, Dict] = {}

    def track_agent(self, agent_id: str):
        process = psutil.Process()
        self.agent_resources[agent_id] = {
            "memory": process.memory_info().rss,
            "cpu": process.cpu_percent(),
            "threads": process.num_threads(),
        }

    def enforce_limits(self, max_memory="2GB", max_cpu=80):
        max_mem_bytes = self._parse_memory(max_memory)
        for agent_id, usage in self.agent_resources.items():
            if usage["memory"] > max_mem_bytes:
                self._handle_over_limit(agent_id, "memory")
            if usage["cpu"] > max_cpu:
                self._handle_over_limit(agent_id, "cpu")

    def _parse_memory(self, memory_str: str) -> int:
        units = {"GB": 1024**3, "MB": 1024**2, "KB": 1024}
        value = int(memory_str[:-2])
        unit = memory_str[-2:]
        return value * units[unit]

    def _handle_over_limit(self, agent_id: str, resource: str):
        self.logger.warning(f"Agent {agent_id} exceeded {resource} limit")
        # TODO: Implement actual mitigation

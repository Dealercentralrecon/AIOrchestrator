class GenesisBlock:
    REQUIRED_CONSTRAINTS = {
        'max_memory_mb': (int, 1, 4096),
        'network_access': (bool, False),
        'allowed_imports': (list, ['math', 'datetime', 'json']),
        'max_code_size_kb': (int, 1, 100)
    }

    def validate_blueprint(self, blueprint):
        return all(
            isinstance(blueprint.get(key), typ) and 
            (min_val <= blueprint[key] <= max_val if isinstance(min_val, int) else blueprint[key] == min_val)
            for key, (typ, min_val, max_val) in self.REQUIRED_CONSTRAINTS.items()
        )

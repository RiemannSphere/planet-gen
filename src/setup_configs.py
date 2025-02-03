from db_manager import TerrainDB
from models import TerrainConfig

def setup_initial_configs():
    db = TerrainDB()
    
    # Define base configurations
    configs = [
        TerrainConfig(
            name='baseline_smooth',
            sigma=90.0,
            sea_level=0.4,
            use_power_function=True,
            continent_factor=2.0,
            description='Our baseline model with smooth terrain features'
        ),
        # ... other configs ...
    ]
    
    # Save configs only if they don't exist
    for config in configs:
        if not db.config_exists(config.name):
            try:
                db.save_config(config)
                print(f"Added configuration: {config.name}")
            except Exception as e:
                print(f"Error saving configuration '{config.name}': {e}")
        else:
            print(f"Configuration '{config.name}' already exists, skipping.")

def remove_configs(config_names: list[str]) -> None:
    """Remove specified configurations from the database.
    
    Args:
        config_names: List of configuration names to remove
    """
    db = TerrainDB()
    
    for name in config_names:
        try:
            if db.config_exists(name):
                db.delete_config(name)
                print(f"Removed configuration: {name}")
            else:
                print(f"Configuration '{name}' not found, skipping.")
        except Exception as e:
            print(f"Error removing configuration '{name}': {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--remove":
        # Remove specified configs
        configs_to_remove = sys.argv[2:]
        if not configs_to_remove:
            print("Please specify configuration names to remove.")
            print("Usage: python setup_configs.py --remove config1 config2 ...")
            sys.exit(1)
        remove_configs(configs_to_remove)
    else:
        # Add initial configs
        setup_initial_configs() 
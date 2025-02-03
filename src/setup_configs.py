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

if __name__ == "__main__":
    setup_initial_configs() 
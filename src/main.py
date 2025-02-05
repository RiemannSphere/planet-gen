import os  # Add import at top
from generators.simple_generator import SimpleGenerator, SimpleParameters
from noise.random_noise import SphericalRandomNoiseStrategy
from utils.projections import ProjectionType

def main():
    # Define output directory
    output_dir = "output"  # or whatever your output directory path is
    
    # Clear existing image files in output directory
    for file in os.listdir(output_dir):
        if file.endswith(('.png', '.jpg', '.jpeg')):
            os.remove(os.path.join(output_dir, file))
            
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
            
    # Create a list of different parameter configurations
    configurations = [
        {"name": "terrain_1", "scale": 1.0, "noise_scale": 1.0},
        {"name": "terrain_2", "scale": 1.5, "noise_scale": 1.5},
        {"name": "terrain_3", "scale": 2.0, "noise_scale": 2.0},
        {"name": "terrain_4", "scale": 2.5, "noise_scale": 1.0},
        {"name": "terrain_5", "scale": 1.0, "noise_scale": 2.5},
        {"name": "terrain_6", "scale": 3.0, "noise_scale": 1.5},
        {"name": "terrain_7", "scale": 1.5, "noise_scale": 3.0},
        {"name": "terrain_8", "scale": 2.0, "noise_scale": 2.5},
        {"name": "terrain_9", "scale": 2.5, "noise_scale": 2.0},
        {"name": "terrain_10", "scale": 3.0, "noise_scale": 3.0},
    ]
    
    # Generate terrain for each configuration
    for config in configurations:
        print(f"Generating terrain for {config['name']}...")
        
        # Set up parameters for this configuration
        params = SimpleParameters(
            name=config['name'],
            scale=config['scale']
        )
        
        # Create noise strategy
        noise = SphericalRandomNoiseStrategy(
            scale=config['noise_scale']
        )
        
        # Create generator
        generator = SimpleGenerator(
            shape=(180, 360),  # 1-degree resolution
            parameters=params,
            noise=noise
        )
        
        # First create the displacement map
        generator.create_displacement_map()
        
        # Then generate and save the visualization
        generator.save_terrain_visualization(
            projection_type=ProjectionType.EQUIRECTANGULAR,
            suffix=f"_{config['name']}"
        )

if __name__ == "__main__":
    main() 
from generators.simple_generator import SimpleGenerator, SimpleParameters
from noise.perlin_noise import PerlinNoiseStrategy
from noise.random_noise import SimpleRandomNoiseStrategy
from utils.projections import ProjectionType

def main():
    # Set up base parameters
    base_params = SimpleParameters(
        name="simple_terrain",
        scale=2.0  # Adjust scale factor for more pronounced features
    )
    
    # Create both noise strategies
    random_noise = SimpleRandomNoiseStrategy(
        seed=42,
        sigma=2.0  # Adjust for smoother/rougher terrain
    )
    
    perlin_noise = PerlinNoiseStrategy(
        seed=42,
        frequency=3.0  # Higher frequency = more detailed terrain
    )
    
    # Generate terrain with random noise (simpler approach)
    print("Generating terrain with simple random noise...")
    random_generator = SimpleGenerator(
        shape=(180, 360),  # 1-degree resolution
        parameters=base_params,
        noise=random_noise
    )
    random_generator.run(projection_type=ProjectionType.EQUIRECTANGULAR, suffix="_random_noise")
    
    # Generate terrain with Perlin noise (more complex approach)
    print("Generating terrain with Perlin noise...")
    perlin_generator = SimpleGenerator(
        shape=(180, 360),  # 1-degree resolution
        parameters=base_params,
        noise=perlin_noise
    )
    perlin_generator.run(projection_type=ProjectionType.EQUIRECTANGULAR, suffix="_perlin_noise")

if __name__ == "__main__":
    main() 
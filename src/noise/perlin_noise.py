from opensimplex import OpenSimplex
import numpy as np
from numpy.typing import NDArray

from .noise_strategy import NoiseStrategy

class PerlinNoiseStrategy(NoiseStrategy):
    """Generates Perlin-like noise using OpenSimplex."""
    
    def __init__(self, seed: int = 42, frequency: float = 1.0):
        """Initialize the noise generator.
        
        Args:
            seed: Random seed for noise generation
            frequency: Base frequency of the noise
        """
        self.generator = OpenSimplex(seed=seed)
        self.frequency = frequency
    
    def generate(self, shape: tuple[int, int]) -> NDArray[np.float64]:
        """Generate a noise map with the given shape.
        
        Args:
            shape: Tuple of (lat_points, lon_points) for the noise map
            
        Returns:
            Generated noise map in latitude/longitude format
        """
        height, width = shape
        noise_map = np.zeros(shape)
        
        # Generate noise values
        for i in range(height):
            lat = (i / height - 0.5) * 2  # Map to [-1, 1]
            for j in range(width):
                lon = (j / width - 0.5) * 2  # Map to [-1, 1]
                noise_map[i, j] = self.generator.noise2(
                    lat * self.frequency,
                    lon * self.frequency
                )
        
        # Normalize to [0, 1] range
        noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
        return noise_map 
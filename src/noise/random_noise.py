import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import gaussian_filter

from .noise_strategy import NoiseStrategy

class SimpleRandomNoiseStrategy(NoiseStrategy):
    """Generates simple random noise using numpy's random generator."""
    
    def __init__(self, seed: int = 42, sigma: float = 2.0):
        """Initialize the noise generator.
        
        Args:
            seed: Random seed for noise generation
            sigma: Standard deviation for Gaussian smoothing
        """
        self.rng = np.random.RandomState(seed)
        self.sigma = sigma
    
    def generate(self, shape: tuple[int, int]) -> NDArray[np.float64]:
        """Generate a noise map with the given shape.
        
        Args:
            shape: Tuple of (lat_points, lon_points) for the noise map
            
        Returns:
            Generated noise map in latitude/longitude format
        """
        # Generate two scales of noise like in the terrain generator
        noise1 = self.rng.rand(*shape)
        noise2 = self.rng.rand(*shape)
        
        # Apply Gaussian smoothing at two scales
        smoothed1 = gaussian_filter(noise1, sigma=self.sigma)
        smoothed2 = gaussian_filter(noise2, sigma=self.sigma/2)
        
        # Combine the two scales
        combined = smoothed1 * 0.7 + smoothed2 * 0.3
        
        # Normalize to [0, 1] range
        noise_map = (combined - combined.min()) / (combined.max() - combined.min())
        return noise_map 
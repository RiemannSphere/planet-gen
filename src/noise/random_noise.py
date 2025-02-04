import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import gaussian_filter

from .noise_strategy import NoiseStrategy

class SimpleRandomNoiseStrategy(NoiseStrategy):
    """Generates simple random noise appropriate for spherical coordinates."""
    
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
        height, width = shape
        
        # Generate base noise
        noise = self.rng.rand(*shape)
        
        # Scale noise by latitude to prevent polar distortion
        lats = np.linspace(-90, 90, height)
        lat_weights = np.cos(np.radians(lats))
        noise = noise * lat_weights[:, np.newaxis]
        
        # Apply light smoothing
        smoothed = gaussian_filter(noise, sigma=self.sigma)
        
        # Normalize to [0, 1] range
        noise_map = (smoothed - smoothed.min()) / (smoothed.max() - smoothed.min())
        return noise_map 
import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import gaussian_filter
from opensimplex import OpenSimplex
from typing import Tuple

from .noise_strategy import NoiseStrategy

class SphericalRandomNoiseStrategy(NoiseStrategy):
    """Generates smooth noise appropriate for spherical coordinates using OpenSimplex noise."""
    
    def __init__(self, seed: int | None = None, scale: float = 3.0):
        """Initialize the noise generator.
        
        Args:
            seed: Random seed for noise generation. If None, a random seed will be used.
            scale: Scale factor for noise input coordinates.
        """
        if seed is None:
            seed = np.random.randint(0, 2**32 - 1)
        self.noise_gen = OpenSimplex(seed=seed)
        self.scale = scale
    
    def _spherical_to_cartesian(self, theta: np.ndarray, phi: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Convert spherical coordinates to Cartesian.
        
        Args:
            theta: Latitude angles in radians.
            phi: Longitude angles in radians.
        
        Returns:
            x, y, z Cartesian coordinates.
        """
        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)
        return x, y, z
    
    def _spherical_noise(self, x: float, y: float, z: float) -> float:
        """Generate OpenSimplex noise for given Cartesian coordinates.
        
        Args:
            x, y, z: Cartesian coordinates on the unit sphere.
        
        Returns:
            Noise value at the given point.
        """
        return self.noise_gen.noise3(self.scale * x, self.scale * y, self.scale * z)
    
    def generate(self, shape: Tuple[int, int]) -> np.ndarray:
        """Generate a noise map with the given shape using spherical coordinates.
        
        Args:
            shape: Tuple of (lat_points, lon_points) defining the grid resolution.
        
        Returns:
            Generated noise map in latitude/longitude format.
        """
        lat_points, lon_points = shape
        theta = np.linspace(0, np.pi, lat_points)  # Latitude
        phi = np.linspace(0, 2 * np.pi, lon_points)  # Longitude
        
        # Create a meshgrid for the spherical coordinates
        Theta, Phi = np.meshgrid(theta, phi, indexing='ij')
        x, y, z = self._spherical_to_cartesian(Theta, Phi)
        
        # Generate noise values
        noise_map = np.vectorize(self._spherical_noise)(x, y, z)
        
        return noise_map
import numpy as np
from numpy.typing import NDArray
from opensimplex import OpenSimplex
from typing import Tuple

from .noise_strategy import NoiseStrategy

class SphericalFBMNoiseStrategy(NoiseStrategy):
    """Generates fractal Brownian motion noise appropriate for spherical coordinates using OpenSimplex noise."""
    
    def __init__(self, 
                 seed: int | None = None, 
                 scale: float = 3.0,
                 octaves: int = 6,
                 persistence: float = 0.5,
                 lacunarity: float = 2.0):
        """Initialize the fBm noise generator.
        
        Args:
            seed: Random seed for noise generation. If None, a random seed will be used.
            scale: Base scale factor for noise input coordinates.
            octaves: Number of noise layers to combine.
            persistence: How much each octave contributes to the final result.
                       Controls amplitude decrease (0-1). Higher values = more detail.
            lacunarity: How much the frequency increases each octave.
                       Higher values = more high-frequency variation.
        """
        if seed is None:
            seed = np.random.randint(0, 2**31 - 1)
        
        # Create separate noise generators for each octave
        self.noise_gens = [OpenSimplex(seed=seed + i) for i in range(octaves)]
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
    
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
        """Generate fBm noise for given Cartesian coordinates by combining multiple octaves.
        
        Args:
            x, y, z: Cartesian coordinates on the unit sphere.
        
        Returns:
            Combined noise value at the given point.
        """
        total = 0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0  # Used for normalization
        
        for noise_gen in self.noise_gens:
            # Add noise at current frequency and amplitude
            total += amplitude * noise_gen.noise3(
                frequency * self.scale * x,
                frequency * self.scale * y,
                frequency * self.scale * z
            )
            
            max_value += amplitude
            amplitude *= self.persistence  # Decrease amplitude for each octave
            frequency *= self.lacunarity  # Increase frequency for each octave
        
        # Normalize to [-1, 1] range
        return total / max_value
    
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
from typing import Optional
from pydantic import Field
import numpy as np
from numpy.typing import NDArray
from scipy import ndimage

from models.base_parameters import BaseParameters
from generators.base_generator import BaseGenerator

class AdvancedParameters(BaseParameters):
    """Parameters for the advanced terrain generator."""
    base_scale: float = Field(1.0, description="Base scale factor for the noise map")
    sharpness: float = Field(2.0, description="Controls how sharp terrain features are")
    erosion_iterations: int = Field(4, description="Number of erosion simulation iterations")
    roughness: float = Field(0.4, description="Terrain roughness factor (0-1)")
    noise_scale: float = Field(2.0, description="Scale factor for the noise generation")

class AdvancedGenerator(BaseGenerator[AdvancedParameters]):
    """An advanced terrain generator that creates more realistic features."""
    
    def _create_terrain_features(self, height_map: NDArray) -> NDArray:
        """Transform the height map to create terrain features."""
        # Store the original range
        min_val = np.min(height_map)
        max_val = np.max(height_map)
        
        # Normalize to [0, 1] range
        normalized = (height_map - min_val) / (max_val - min_val)
        
        # Apply power transformation (safe now as all values are between 0 and 1)
        features = np.power(normalized, self.parameters.sharpness)
        
        # Scale back to original range
        features = features * (max_val - min_val) + min_val
        
        return features
    
    def _simulate_erosion(self, height_map: NDArray) -> NDArray:
        """Simulate simple erosion effects."""
        eroded = height_map.copy()
        
        for _ in range(self.parameters.erosion_iterations):
            # Apply diffusion to simulate erosion
            eroded = ndimage.gaussian_filter(eroded, sigma=0.5)
            
            # Add some roughness back to maintain detail
            roughness = np.random.rand(*eroded.shape) * self.parameters.roughness
            eroded = eroded * (1 - self.parameters.roughness) + roughness
            
            # Ensure valleys remain lower than peaks
            eroded = np.minimum(eroded, height_map)
        
        return eroded
    
    def create_displacement_map(self) -> None:
        """Create a spherical displacement map with advanced terrain features."""
        # Start with the base noise map
        height_map = self.noise_map * self.parameters.base_scale
        
        # Create terrain features
        height_map = self._create_terrain_features(height_map)
        
        # Simulate erosion
        height_map = self._simulate_erosion(height_map)
        
        # Store the final displacement map
        self.displacement_map = height_map 
from abc import ABC, abstractmethod
from numpy.typing import NDArray
import numpy as np

class NoiseStrategy(ABC):
    """Interface for noise generation strategies."""
    
    @abstractmethod
    def generate(self, shape: tuple[int, int]) -> NDArray[np.float64]:
        """Generate a noise map with the given shape.
        
        Args:
            shape: Tuple of (lat_points, lon_points) for the noise map
            
        Returns:
            Generated noise map in latitude/longitude format
        """
        pass 
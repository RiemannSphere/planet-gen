from typing import Optional
from pydantic import Field
import numpy as np
from numpy.typing import NDArray

from models.base_parameters import BaseParameters
from generators.base_generator import BaseGenerator

class SimpleParameters(BaseParameters):
    """Parameters for the simple generator."""
    scale: float = Field(1.0, description="Scale factor to apply to the noise map")

class SimpleGenerator(BaseGenerator[SimpleParameters]):
    """A simple generator that directly uses the noise map as displacement."""
    
    def create_displacement_map(self) -> None:
        """Create a spherical displacement map by simply scaling the noise map.
        
        Returns:
            Displacement map in lat/lon format (values represent radial displacement)
        """
        # Simply scale the noise map by the scale factor and store it
        self.displacement_map = self.noise_map * self.parameters.scale
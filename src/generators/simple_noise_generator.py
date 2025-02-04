from typing import Optional
import numpy as np
from numpy.typing import NDArray
from pydantic import Field

from .base_generator import BaseGenerator
from ..models.base_parameters import BaseParameters
from ..noise.noise_strategy import NoiseStrategy
from ..utils.projections import ProjectionType

class SimpleNoiseParameters(BaseParameters):
    """Parameters for the simple noise terrain generator."""
    amplitude: float = Field(
        default=1.0,
        description="Global scaling factor for terrain height",
        gt=0
    )
    frequency_scale: float = Field(
        default=1.0,
        description="Scaling factor for noise frequency",
        gt=0
    )
    base_height: float = Field(
        default=0.5,
        description="Base height offset for the terrain",
        ge=0,
        le=1
    )

class SimpleNoiseGenerator(BaseGenerator[SimpleNoiseParameters]):
    """A simple terrain generator that creates height maps from noise."""
    
    def __init__(self, output_dir: str = "output", 
                 noise_strategy: Optional[NoiseStrategy] = None,
                 projection_type: ProjectionType = ProjectionType.EQUIRECTANGULAR):
        """Initialize the generator.
        
        Args:
            output_dir: Directory to save output files
            noise_strategy: Strategy for generating noise maps
            projection_type: Type of projection to use for 2D visualization
        """
        super().__init__(output_dir, noise_strategy)
        self.projection_type = projection_type
    
    def set_projection_type(self, projection_type: ProjectionType) -> None:
        """Set the projection type for 2D visualization.
        
        Args:
            projection_type: Type of projection to use
        """
        self.projection_type = projection_type
    
    def project_to_2d(self, displacement_map: NDArray[np.float64], 
                     parameters: SimpleNoiseParameters) -> NDArray[np.float64]:
        """Override project_to_2d to use the generator's projection type.
        
        Args:
            displacement_map: Spherical displacement map in lat/lon format
            parameters: Parameters for displacement map generation
            
        Returns:
            2D projected map
        """
        return self.projector.project_to_2d(displacement_map, self.projection_type)
    
    def create_displacement_map(self, noise_map: NDArray[np.float64], 
                              parameters: SimpleNoiseParameters) -> NDArray[np.float64]:
        """Create a spherical displacement map from the noise map.
        
        This implementation creates a simple height map by:
        1. Scaling the noise values to [0,1]
        2. Applying frequency scaling
        3. Adding base height
        4. Scaling by amplitude
        
        Args:
            noise_map: Input noise map in lat/lon format
            parameters: Parameters for displacement map generation
            
        Returns:
            Displacement map in lat/lon format (values represent radial displacement)
        """
        # Normalize noise to [0,1]
        normalized = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
        
        # Apply frequency scaling by interpolating
        if parameters.frequency_scale != 1.0:
            rows, cols = noise_map.shape
            y = np.linspace(0, 1, rows)
            x = np.linspace(0, 1, cols)
            X, Y = np.meshgrid(x, y)
            
            scaled_x = X * parameters.frequency_scale
            scaled_y = Y * parameters.frequency_scale
            
            # Clip to ensure we stay within [0,1]
            scaled_x = np.clip(scaled_x, 0, 1)
            scaled_y = np.clip(scaled_y, 0, 1)
            
            normalized = np.interp(scaled_x.flatten(), x, normalized[0, :]).reshape(rows, cols)
            normalized = np.interp(scaled_y.flatten(), y, normalized[:, 0]).reshape(rows, cols)
        
        # Add base height and scale by amplitude
        displacement = parameters.base_height + normalized * parameters.amplitude
        
        return displacement 
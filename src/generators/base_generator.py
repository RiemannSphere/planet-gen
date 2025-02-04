from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar, Generic, Union, Tuple
import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt
import os
from datetime import datetime

from models.base_parameters import BaseParameters
from utils.projections import MapProjector, ProjectionType
from noise.noise_strategy import NoiseStrategy

NoiseMap = NDArray[np.float64]
# Generic type for parameters that extend BaseParameters
Param = TypeVar('Param', bound=BaseParameters)

class BaseGenerator(ABC, Generic[Param]):
    """Abstract base class for terrain generators."""
    
    def __init__(self, shape: tuple[int, int], parameters: Param, noise: Union[NoiseMap, NoiseStrategy], output_dir: str = "output"):
        """Initialize the generator.
        
        Args:
            shape: Tuple of (lat_points, lon_points) for the terrain
            parameters: Parameters for terrain generation
            noise: Noise map or strategy for generating noise maps
            output_dir: Directory to save output files
        """
        self.shape = shape
        self.output_dir = output_dir
        self.parameters = parameters

        if isinstance(noise, NoiseStrategy):
            self.noise_map = noise.generate(self.shape)
        else:
            self.noise_map = noise
            
        self.projector = MapProjector()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    @abstractmethod
    def create_displacement_map(self) -> None:
        """Create a spherical displacement map from the noise map.
  
        Returns:
            Displacement map in lat/lon format (values represent radial displacement)
        """
        pass
    
    def save_2d_projection(self, projection_type: ProjectionType, suffix: str = "") -> None:
        """Project spherical displacement map to 2D using specified projection and save to file.
        
        Args: 
            projection_type: Type of map projection to use
            suffix: Optional suffix to add to the filename
            
        Raises:
            RuntimeError: If displacement_map hasn't been generated yet
        """
        if not hasattr(self, 'displacement_map'):
            raise RuntimeError("Displacement map hasn't been generated. Call create_displacement_map() first.")
            
        # Get the projected map
        projected_map = self.projector.project_to_2d(self.displacement_map, projection_type)
        
        # Create visualization and save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.figure(figsize=(12, 6))
        plt.imshow(projected_map, cmap='terrain')
        plt.colorbar(label='Displacement')
        plt.title(f"2D Projection ({projection_type.value}) - {self.parameters.name}")
        
        filename = f"projected_map_{self.parameters.name}{suffix}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def save_equatorial_cross_section(self, save: bool = True) -> None:
        """Create a cross-section plot along the equator of the spherical displacement map.
        
        Args:
            save: Whether to save the plot to file
            
        Raises:
            RuntimeError: If displacement_map hasn't been generated yet
        """
        if not hasattr(self, 'displacement_map'):
            raise RuntimeError("Displacement map hasn't been generated. Call create_displacement_map() first.")
            
        # Get the equatorial cross section
        equator_idx = self.displacement_map.shape[0] // 2
        cross_section = self.displacement_map[equator_idx, :]
        
        # Create longitude values for x-axis
        lons = np.linspace(-180, 180, len(cross_section))
        
        plt.figure(figsize=(12, 6))
        plt.plot(lons, cross_section, color='blue', linewidth=1)
        plt.title(f"Equatorial Cross Section - {self.parameters.name}")
        plt.xlabel('Longitude (degrees)')
        plt.ylabel('Radial Displacement')
        plt.grid(True, alpha=0.3)
        
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"equatorial_section_{self.parameters.name}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
        
        plt.close()

    def run(self, projection_type: ProjectionType = ProjectionType.EQUIRECTANGULAR, suffix: str = "") -> None:
        """Run the generator and save both 2D projection and cross section visualizations.
        
        Args:
            projection_type: Type of map projection to use (default: EQUIRECTANGULAR)
            suffix: Optional suffix to add to the filename
        """
        self.create_displacement_map()
        self.save_2d_projection(projection_type, suffix)
        self.save_equatorial_cross_section()
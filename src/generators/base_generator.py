from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar, Generic, Union, Tuple
import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt
import os
from datetime import datetime

from ..models.base_parameters import BaseParameters
from ..utils.projections import MapProjector, ProjectionType
from ..noise.noise_strategy import NoiseStrategy

# Generic type for parameters that extend BaseParameters
P = TypeVar('P', bound=BaseParameters)

class BaseGenerator(ABC, Generic[P]):
    """Abstract base class for terrain generators."""
    
    def __init__(self, output_dir: str = "output", noise_strategy: Optional[NoiseStrategy] = None):
        """Initialize the generator.
        
        Args:
            output_dir: Directory to save output files
            noise_strategy: Strategy for generating noise maps
        """
        self.output_dir = output_dir
        self.parameters: Optional[Union[P, List[P]]] = None
        self.noise_map: Optional[NDArray[np.float64]] = None
        self.projector = MapProjector()
        self.noise_strategy = noise_strategy
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def set_parameters(self, parameters: Union[P, List[P]]) -> None:
        """Set the parameters for terrain generation.
        
        Args:
            parameters: Single parameter set or list of parameter sets
        """
        self.parameters = parameters

    def set_noise_strategy(self, noise_strategy: NoiseStrategy) -> None:
        """Set the noise generation strategy.
        
        Args:
            noise_strategy: Strategy for generating noise maps
        """
        self.noise_strategy = noise_strategy

    def generate_noise(self, shape: tuple[int, int]) -> NDArray[np.float64]:
        """Generate noise map using the current noise strategy.
        
        Args:
            shape: Tuple of (lat_points, lon_points) for the noise map
            
        Returns:
            Generated noise map in latitude/longitude format
        
        Raises:
            ValueError: If no noise strategy has been set
        """
        if self.noise_strategy is None:
            raise ValueError("No noise strategy has been set")
        return self.noise_strategy.generate(shape)
    
    def set_noise_map(self, noise_map: NDArray[np.float64]) -> None:
        """Set an external noise map for terrain generation.
        
        Args:
            noise_map: Pre-generated noise map in lat/lon format
        """
        self.noise_map = noise_map
    
    @abstractmethod
    def create_displacement_map(self, noise_map: NDArray[np.float64], 
                              parameters: P) -> NDArray[np.float64]:
        """Create a spherical displacement map from the noise map.
        
        Args:
            noise_map: Input noise map in lat/lon format
            parameters: Parameters for displacement map generation
            
        Returns:
            Displacement map in lat/lon format (values represent radial displacement)
        """
        pass
    
    def project_to_2d(self, displacement_map: NDArray[np.float64], 
                     parameters: P) -> NDArray[np.float64]:
        """Project spherical displacement map to 2D using specified projection.
        
        Args:
            displacement_map: Spherical displacement map in lat/lon format
            parameters: Parameters containing projection type
            
        Returns:
            2D projected map
        """
        return self.projector.project_to_2d(displacement_map, parameters.projection_type)
    
    def plot_equatorial_cross_section(self, displacement_map: NDArray[np.float64], 
                                    parameters: P,
                                    save: bool = True) -> None:
        """Create a cross-section plot along the equator of the spherical displacement map.
        
        Args:
            displacement_map: Spherical displacement map in lat/lon format
            parameters: Parameters used to generate the displacement map
            save: Whether to save the plot to file
        """
        # Get the equatorial cross section
        equator_idx = displacement_map.shape[0] // 2
        cross_section = displacement_map[equator_idx, :]
        
        # Create longitude values for x-axis
        lons = np.linspace(-180, 180, len(cross_section))
        
        plt.figure(figsize=(12, 6))
        plt.plot(lons, cross_section, color='blue', linewidth=1)
        plt.title(f"Equatorial Cross Section - {parameters.name}")
        plt.xlabel('Longitude (degrees)')
        plt.ylabel('Radial Displacement')
        plt.grid(True, alpha=0.3)
        
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"equatorial_section_{parameters.name}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def save_displacement_map(self, displacement_map: NDArray[np.float64], 
                            parameters: P,
                            suffix: str = "") -> None:
        """Save both the spherical displacement map and its 2D projection.
        
        Args:
            displacement_map: Spherical displacement map in lat/lon format
            parameters: Parameters used to generate the map
            suffix: Optional suffix to add to the filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save spherical displacement map visualization
        plt.figure(figsize=(12, 6))
        plt.imshow(displacement_map, cmap='terrain')
        plt.colorbar(label='Radial Displacement')
        plt.title(f"Spherical Displacement Map - {parameters.name}")
        
        filename = f"spherical_map_{parameters.name}{suffix}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save 2D projection
        projected_map = self.project_to_2d(displacement_map, parameters)
        plt.figure(figsize=(12, 6))
        plt.imshow(projected_map, cmap='terrain')
        plt.colorbar(label='Displacement')
        plt.title(f"2D Projection ({parameters.projection_type.value}) - {parameters.name}")
        
        filename = f"projected_map_{parameters.name}{suffix}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def run(self, shape: tuple[int, int]) -> None:
        """Run the terrain generation process.
        
        Args:
            shape: Tuple of (lat_points, lon_points) for the terrain
            
        Raises:
            ValueError: If parameters are not set or if neither noise_map nor noise_strategy is available
        """
        if self.parameters is None:
            raise ValueError("Parameters must be set before running generation")
            
        # Handle both single parameter set and list of parameter sets
        parameter_sets = (
            [self.parameters] if not isinstance(self.parameters, list) 
            else self.parameters
        )
        
        # Check if we have either a noise map or a strategy to generate one
        if self.noise_map is None and self.noise_strategy is None:
            raise ValueError(
                "Either set_noise_map() must be called with a pre-generated noise map "
                "or set_noise_strategy() must be called with a noise generation strategy"
            )
        
        # Generate noise map if needed
        if self.noise_map is None:
            self.noise_map = self.generate_noise(shape)
        
        # Process each parameter set
        for params in parameter_sets:
            # Generate displacement map
            displacement_map = self.create_displacement_map(self.noise_map, params)
            
            # Save outputs
            self.save_displacement_map(displacement_map, params)
            self.plot_equatorial_cross_section(displacement_map, params) 
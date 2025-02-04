from enum import Enum
import numpy as np
from numpy.typing import NDArray

class ProjectionType(Enum):
    """Available map projection types."""
    EQUIRECTANGULAR = "equirectangular"
    MERCATOR = "mercator"
    SINUSOIDAL = "sinusoidal"

class MapProjector:
    """Handles conversions between spherical and projected coordinates."""
    
    @staticmethod
    def to_spherical(lat: NDArray[np.float64], lon: NDArray[np.float64]) -> tuple[NDArray[np.float64], ...]:
        """Convert latitude and longitude to spherical coordinates (r=1).
        
        Args:
            lat: Latitude in radians (-π/2 to π/2)
            lon: Longitude in radians (-π to π)
            
        Returns:
            Tuple of (x, y, z) coordinates on unit sphere
        """
        x = np.cos(lat) * np.cos(lon)
        y = np.cos(lat) * np.sin(lon)
        z = np.sin(lat)
        return x, y, z
    
    @staticmethod
    def project_to_2d(displacement_map: NDArray[np.float64], 
                     projection: ProjectionType = ProjectionType.EQUIRECTANGULAR) -> NDArray[np.float64]:
        """Project spherical displacement map to 2D using specified projection.
        
        Args:
            displacement_map: Displacement values in lat/lon format
            projection: Type of projection to use
            
        Returns:
            2D projected map
        """
        if projection == ProjectionType.EQUIRECTANGULAR:
            return displacement_map  # Simple lat/lon projection
        
        elif projection == ProjectionType.MERCATOR:
            height, width = displacement_map.shape
            lats = np.linspace(-np.pi/2, np.pi/2, height)
            
            # Mercator projection scaling factor
            scale = np.cos(lats)[:, np.newaxis]
            return displacement_map * scale
        
        elif projection == ProjectionType.SINUSOIDAL:
            height, width = displacement_map.shape
            lats = np.linspace(-np.pi/2, np.pi/2, height)
            lons = np.linspace(-np.pi, np.pi, width)
            
            # Sinusoidal projection scaling
            scale = np.cos(lats)[:, np.newaxis]
            return displacement_map * scale
        
        else:
            raise ValueError(f"Unsupported projection type: {projection}") 
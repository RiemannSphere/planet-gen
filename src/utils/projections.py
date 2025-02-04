from enum import Enum
import numpy as np
from numpy.typing import NDArray

class ProjectionType(Enum):
    """Types of map projections."""
    EQUIRECTANGULAR = "equirectangular"
    MERCATOR = "mercator"
    SINUSOIDAL = "sinusoidal"

class MapProjector:
    """Handles projecting spherical maps to different 2D projections."""
    
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
    
    def project_to_2d(self, spherical_map: NDArray[np.float64], projection_type: ProjectionType) -> NDArray[np.float64]:
        """Project a spherical map to 2D using the specified projection.
        
        Args:
            spherical_map: Input map in spherical coordinates
            projection_type: Type of projection to use
            
        Returns:
            The projected 2D map
        """
        if projection_type == ProjectionType.EQUIRECTANGULAR:
            return spherical_map  # Equirectangular is already in lat/lon format
        elif projection_type == ProjectionType.MERCATOR:
            return self._mercator_projection(spherical_map)
        elif projection_type == ProjectionType.SINUSOIDAL:
            height, width = spherical_map.shape
            lats = np.linspace(-np.pi/2, np.pi/2, height)
            lons = np.linspace(-np.pi, np.pi, width)
            
            # Sinusoidal projection scaling
            scale = np.cos(lats)[:, np.newaxis]
            return spherical_map * scale
        else:
            raise ValueError(f"Unsupported projection type: {projection_type}")
    
    def _mercator_projection(self, spherical_map: NDArray[np.float64]) -> NDArray[np.float64]:
        """Convert spherical map to Mercator projection.
        
        Args:
            spherical_map: Input map in spherical coordinates
            
        Returns:
            Map in Mercator projection
        """
        height, width = spherical_map.shape
        
        # Create latitude array (in radians)
        lats = np.linspace(-np.pi/2, np.pi/2, height)
        
        # Apply Mercator transformation
        mercator = np.zeros_like(spherical_map)
        for i, lat in enumerate(lats):
            if abs(lat) < np.pi/2:  # Exclude poles
                mercator[i, :] = spherical_map[i, :] / np.cos(lat)
        
        return mercator 
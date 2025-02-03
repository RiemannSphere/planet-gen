from typing import Optional, Tuple, Union
import numpy as np
from numpy.typing import NDArray
from PIL import Image
import cv2
from scipy.ndimage import gaussian_filter

class TerrainGenerator:
    def __init__(self, width: int = 1024, height: int = 1024) -> None:
        """Initialize the terrain generator with given dimensions.
        
        Args:
            width (int): Width of the terrain map in pixels
            height (int): Height of the terrain map in pixels
        """
        self.width: int = width
        self.height: int = height
        
    def generate_base_noise(self) -> NDArray[np.float64]:
        """Generate base noise for the terrain.
        
        Returns:
            NDArray[np.float64]: 2D array of random noise values between 0 and 1
        """
        return np.random.rand(self.height, self.width)
        
    def create_height_map(self, sigma: float = 5.0) -> NDArray[np.uint8]:
        """Create a basic height map for the planet's terrain.
        
        Args:
            sigma (float): Standard deviation for Gaussian filter
            
        Returns:
            NDArray[np.uint8]: 2D array representing the height map with values 0-255
        """
        noise: NDArray[np.float64] = self.generate_base_noise()
        # Apply Gaussian smoothing
        smoothed: NDArray[np.float64] = gaussian_filter(noise, sigma=sigma)
        # Normalize to 0-255 range
        height_map: NDArray[np.uint8] = ((smoothed - smoothed.min()) * 255 / 
                     (smoothed.max() - smoothed.min())).astype(np.uint8)
        return height_map
    
    def save_height_map(self, height_map: NDArray[np.uint8], filename: str = "terrain.png") -> None:
        """Save the height map as an image.
        
        Args:
            height_map (NDArray[np.uint8]): The height map to save
            filename (str): Output filename
        """
        img: Image.Image = Image.fromarray(height_map)
        img.save(filename)

if __name__ == "__main__":
    # Example usage
    generator: TerrainGenerator = TerrainGenerator(width=1024, height=1024)
    terrain: NDArray[np.uint8] = generator.create_height_map()
    generator.save_height_map(terrain) 
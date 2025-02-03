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
        
    def create_height_map(self, sigma: float = 50.0, sea_level: float = 0.35, continent_factor: float = 1.5) -> NDArray[np.uint8]:
        """Create a height map for the planet's terrain with large continent-like features.
        
        Args:
            sigma (float): Standard deviation for Gaussian filter
            sea_level (float): Threshold for water (0.0 to 1.0), lower values mean more land
            continent_factor (float): Power factor to create more distinct continents
            
        Returns:
            NDArray[np.uint8]: 2D array representing the height map with values 0-255
        """
        # Generate noise at a larger scale
        noise1: NDArray[np.float64] = self.generate_base_noise()
        noise2: NDArray[np.float64] = self.generate_base_noise()
        
        # Combine two scales of noise
        smoothed1: NDArray[np.float64] = gaussian_filter(noise1, sigma=sigma)
        smoothed2: NDArray[np.float64] = gaussian_filter(noise2, sigma=sigma/2)
        smoothed: NDArray[np.float64] = smoothed1 * 0.7 + smoothed2 * 0.3
        
        # Normalize to 0-1 range
        normalized: NDArray[np.float64] = ((smoothed - smoothed.min()) / 
                                         (smoothed.max() - smoothed.min()))
        
        # Apply gentle power function
        continents: NDArray[np.float64] = np.power(normalized, continent_factor)
        
        # Adjust the levels to create more land
        continents = np.clip(continents + 0.2, 0, 1)
        
        # Create sharp transition for water
        continents[continents < sea_level] = sea_level * 0.5
        
        # Convert to 0-255 range
        height_map: NDArray[np.uint8] = (continents * 255).astype(np.uint8)
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
    generator: TerrainGenerator = TerrainGenerator(width=2048, height=1024)

    # Version 1: Default large continents
    terrain1 = generator.create_height_map(
        sigma=50.0, 
        sea_level=0.35, 
        continent_factor=1.5
    )
    generator.save_height_map(terrain1, "terrain_default.png")

    # Version 2: Huge continents
    terrain2 = generator.create_height_map(
        sigma=80.0, 
        sea_level=0.3, 
        continent_factor=1.2
    )
    generator.save_height_map(terrain2, "terrain_huge.png")

    # Version 3: Pangaea-like (very large connected landmasses)
    terrain3 = generator.create_height_map(
        sigma=100.0, 
        sea_level=0.25, 
        continent_factor=1.8
    )
    generator.save_height_map(terrain3, "terrain_pangaea.png")

    # Version 4: Archipelago (many smaller islands)
    terrain4 = generator.create_height_map(
        sigma=20.0, 
        sea_level=0.4, 
        continent_factor=2.0
    )
    generator.save_height_map(terrain4, "terrain_archipelago.png")

    # Version 5: Balanced mix
    terrain5 = generator.create_height_map(
        sigma=60.0, 
        sea_level=0.32, 
        continent_factor=1.6
    )
    generator.save_height_map(terrain5, "terrain_balanced.png") 
from typing import Optional, Tuple, Union
import numpy as np
from numpy.typing import NDArray
from PIL import Image
import cv2
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
import os
import shutil

class TerrainGenerator:
    def __init__(self, width: int = 1024, height: int = 1024, output_dir: str = "output") -> None:
        """Initialize the terrain generator with given dimensions.
        
        Args:
            width (int): Width of the terrain map in pixels
            height (int): Height of the terrain map in pixels
            output_dir (str): Directory to save output files
        """
        self.width: int = width
        self.height: int = height
        self.output_dir: str = output_dir
        self.noise1: Optional[NDArray[np.float64]] = None
        self.noise2: Optional[NDArray[np.float64]] = None
        
        # Remove the output directory if it exists and create a fresh one
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

    def generate_noise(self) -> None:
        """Generate and store base noise for the terrain."""
        self.noise1 = np.random.rand(self.height, self.width)
        self.noise2 = np.random.rand(self.height, self.width)
        
    def create_height_map(self, sigma: float = 50.0, sea_level: float = 0.35, 
                         use_power_function: bool = True, continent_factor: float = 1.5) -> NDArray[np.uint8]:
        """Create a height map for the planet's terrain with large continent-like features.
        
        Args:
            sigma (float): Standard deviation for Gaussian filter
            sea_level (float): Threshold for water (0.0 to 1.0), lower values mean more land
            use_power_function (bool): Whether to apply the power function for continent formation
            continent_factor (float): Power factor to create more distinct continents
            
        Returns:
            NDArray[np.uint8]: 2D array representing the height map with values 0-255
        """
        if self.noise1 is None or self.noise2 is None:
            self.generate_noise()
            
        # Combine two scales of noise
        smoothed1: NDArray[np.float64] = gaussian_filter(self.noise1, sigma=sigma)
        smoothed2: NDArray[np.float64] = gaussian_filter(self.noise2, sigma=sigma/2)
        smoothed: NDArray[np.float64] = smoothed1 * 0.7 + smoothed2 * 0.3
        
        # Normalize to 0-1 range
        normalized: NDArray[np.float64] = ((smoothed - smoothed.min()) / 
                                         (smoothed.max() - smoothed.min()))
        
        # Apply power function if enabled
        continents: NDArray[np.float64] = (np.power(normalized, continent_factor) 
                                          if use_power_function else normalized)
        
        # Adjust the levels to create more land
        continents = np.clip(continents + 0.2, 0, 1)
        
        # Create sharp transition for water
        continents[continents < sea_level] = sea_level * 0.5
        
        # Convert to 0-255 range
        height_map: NDArray[np.uint8] = (continents * 255).astype(np.uint8)
        return height_map
    
    def save_height_map(self, height_map: NDArray[np.uint8], filename: str, params: Optional[dict] = None) -> None:
        """Save the height map as an image with optional parameter information.
        
        Args:
            height_map: The height map array to save
            filename: Name of the output file
            params: Dictionary of parameters used to generate this height map
        """
        # Calculate figure height based on image dimensions and text size
        img_height = height_map.shape[0]
        img_width = height_map.shape[1]
        aspect_ratio = img_width / img_height
        
        # Base figure width of 12 inches
        fig_width = 12
        # Calculate figure height based on image aspect ratio plus small space for text
        fig_height = (fig_width / aspect_ratio) + 0.8  # 0.8 inches for text
        
        fig = plt.figure(figsize=(fig_width, fig_height))
        
        # Create grid with minimal space for text
        gs = plt.GridSpec(2, 1, height_ratios=[img_height, 40], hspace=0.05)
        
        # Add terrain image
        ax_image = fig.add_subplot(gs[0])
        ax_image.imshow(height_map, cmap='terrain')
        ax_image.axis('off')
        
        # Add parameter text if provided
        if params:
            ax_text = fig.add_subplot(gs[1])
            param_text = " | ".join([f"{k}: {v}" for k, v in params.items()])
            ax_text.text(0.5, 0.5, param_text, 
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontfamily='monospace',
                        fontsize=8)
            ax_text.axis('off')
        
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', pad_inches=0.1)
        plt.close()

    def plot_height_map_cross_section(self, height_map: NDArray[np.uint8], filename: str = "terrain_cross_section.png") -> None:
        """Save a horizontal cross-section plot of the height map through the middle.
        
        Args:
            height_map (NDArray[np.uint8]): The height map to analyze
            filename (str): Output filename for the plot
        """
        # Get the middle row of the height map
        middle_row = height_map[height_map.shape[0]//2, :]
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(middle_row, color='blue', linewidth=1)
        plt.title("Height Map Cross Section")
        plt.xlabel('X Position')
        plt.ylabel('Height')
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 255)
        
        # Save the plot to the output directory
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to free memory

    def create_multiple_terrains(self, configs: list[dict]) -> None:
        """Create multiple terrain maps from different parameter configurations.
        
        Args:
            configs: List of dictionaries containing parameters for create_height_map.
                    Each dict should also include a 'name' key for the output filename.
                    Example:
                    {
                        'name': 'mountainous',
                        'sigma': 50.0,
                        'sea_level': 0.35,
                        'use_power_function': True,
                        'continent_factor': 1.5
                    }
        """
        if self.noise1 is None or self.noise2 is None:
            self.generate_noise()
            
        # Generate all height maps
        height_maps = []
        for config in configs:
            name = config.pop('name')  # Remove name from config before passing to create_height_map
            height_map = self.create_height_map(**config)
            self.save_height_map(height_map, f"terrain_{name}.png", config)
            height_maps.append((name, height_map))
            
        # Create combined cross-section plot
        plt.figure(figsize=(15, 8))
        
        # Plot all cross sections on the same chart
        for name, height_map in height_maps:
            middle_row = height_map[height_map.shape[0]//2, :]
            plt.plot(middle_row, label=name, linewidth=1.5, alpha=0.8)
        
        plt.title("Height Map Cross Sections Comparison")
        plt.xlabel('X Position')
        plt.ylabel('Height')
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 255)
        plt.legend()
        
        filepath = os.path.join(self.output_dir, "terrain_cross_sections_comparison.png")
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    generator: TerrainGenerator = TerrainGenerator(width=2048, height=1024)
    generator.generate_noise()

    # Define different parameter configurations
    configs = [
        {
            'name': 'mountainous',
            'sigma': 50.0,
            'sea_level': 0.35,
            'use_power_function': True,
            'continent_factor': 1.5
        },
        {
            'name': 'smooth',
            'sigma': 75.0,
            'sea_level': 0.4,
            'use_power_function': False,
            'continent_factor': 1.0
        },
        {
            'name': 'archipelago',
            'sigma': 40.0,
            'sea_level': 0.6,
            'use_power_function': True,
            'continent_factor': 2.0
        }
    ]

    # Generate all terrains with their cross sections
    generator.create_multiple_terrains(configs)
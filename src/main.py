import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from generators.simple_generator import SimpleGenerator, SimpleParameters
from generators.advanced_generator import AdvancedGenerator, AdvancedParameters
from noise.random_noise import SphericalRandomNoiseStrategy
from noise.fbm_noise import SphericalFBMNoiseStrategy
from utils.projections import ProjectionType

def get_valid_parameters(generator_type: str) -> list:
    """Get list of valid parameters for a generator type."""
    if generator_type == 'simple':
        return ['scale']
    else:  # advanced
        return ['base_scale']

def get_default_advanced_parameters() -> dict:
    """Get default parameters for advanced generator."""
    return {
        'base_scale': 0.8,         # Reduced from 1.2
        'sharpness': 0.8,          # Reduced from 1.1
        'erosion_iterations': 6,    # Increased from 4
        'roughness': 0.2,          # Reduced from 0.4
        'noise_scale': 2.0         # Kept the same
    }

def get_parameter_range(param_name: str, n_models: int) -> np.ndarray:
    """Get the range for a specific parameter."""
    ranges = {
        # Simple generator parameters
        'scale': (0.1, 10.0),
        
        # Advanced generator parameters
        'base_scale': (0.1, 1.0)
    }
    
    if param_name not in ranges:
        raise ValueError(f"Unknown parameter: {param_name}")
    
    start, end = ranges[param_name]
    return np.linspace(start, end, n_models)

def save_combined_cross_sections(generators: list, output_dir: str, title: str = "Combined Cross Sections"):
    """Create a single plot with cross sections from all generators.
    
    Args:
        generators: List of tuples (generator, name) containing all generators and their names
        output_dir: Directory to save the plot
        title: Title for the plot
    """
    print(f"\nSaving combined cross section plot: {title}")
    
    plt.figure(figsize=(12, 8))  # Made figure slightly taller for footer
    
    # Create longitude values for x-axis
    lons = np.linspace(-180, 180, generators[0][0].displacement_map.shape[1])
    
    # Plot each cross section with a different color
    for generator, name in generators:
        equator_idx = generator.displacement_map.shape[0] // 2
        cross_section = generator.displacement_map[equator_idx, :]
        plt.plot(lons, cross_section, label=name, linewidth=1)
    
    plt.title(title)
    plt.xlabel('Longitude (degrees)')
    plt.ylabel('Radial Displacement')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Extract parameter name from title
    param_name = title.split("Varying ")[-1] if "Varying " in title else "unknown_param"
    
    # Get fixed parameters from the first generator
    params = generators[0][0].parameters
    fixed_params = {
        'noise_scale': 2.0,
        'erosion_iterations': 4,
        'roughness': 0.4
    }
    
    if isinstance(params, AdvancedParameters):
        if param_name != 'base_scale':
            fixed_params['base_scale'] = params.base_scale
    
    # Create footer text
    footer_text = "Fixed parameters: " + ", ".join([f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}" 
                                                  for k, v in fixed_params.items()])
    
    # Add footer
    plt.figtext(0.5, 0.02, footer_text, ha='center', va='bottom', fontsize=8,
                bbox=dict(facecolor='white', alpha=0.8, pad=3))
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"combined_cross_sections_{param_name}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Saved to: {filepath}")
    plt.close()

def generate_all_parameter_variations(n_models: int, output_dir: str, map_types: list, generator_type: str):
    """Generate models varying each parameter one at a time."""
    print(f"\nGenerating variations for all parameters of {generator_type.capitalize()} Generator...")
    
    # Get list of parameters to vary
    parameters = get_valid_parameters(generator_type)
    
    # Generate noise map once to use for all variations
    noise = SphericalFBMNoiseStrategy(scale=2.0, octaves=6, persistence=0.5, lacunarity=2.0)
    noise_map = noise.generate((180, 360))
    
    # Generate variations for each parameter
    for param in parameters:
        print(f"\nVarying parameter: {param}")
        param_values = get_parameter_range(param, n_models)
        generators = []
        
        for i in range(n_models):
            name = f"{generator_type}_{param}_{i+1}"
            print(f"Generating terrain: {name}...")
            
            if generator_type == 'simple':
                params = SimpleParameters(
                    name=name,
                    scale=param_values[i] if param == 'scale' else 2.0
                )
                
                generator = SimpleGenerator(
                    shape=(180, 360),
                    parameters=params,
                    noise=noise_map,
                    output_dir=output_dir
                )
                
            else:  # advanced generator
                # Get default parameters and update the one we're varying
                params_dict = get_default_advanced_parameters()
                params_dict[param] = param_values[i]
                
                # Create parameters object with name and updated values
                params = AdvancedParameters(
                    name=name,
                    **params_dict
                )
                
                generator = AdvancedGenerator(
                    shape=(180, 360),
                    parameters=params,
                    noise=noise_map,
                    output_dir=output_dir
                )
            
            generator.create_displacement_map()
            generators.append((generator, f"{param}={param_values[i]:.2f}"))
            
            if 'terrain' in map_types:
                generator.save_terrain_visualization(
                    projection_type=ProjectionType.EQUIRECTANGULAR,
                    suffix=f"_{name}"
                )
            
            if 'projection' in map_types:
                generator.save_2d_projection(
                    projection_type=ProjectionType.EQUIRECTANGULAR,
                    suffix=f"_{name}"
                )
        
        # Create combined cross section plot for this parameter
        if 'cross_section' in map_types:
            save_combined_cross_sections(
                generators,
                output_dir,
                f"Combined Cross Sections - Varying {param}"
            )

def generate_with_varied_parameter(n_models: int, output_dir: str, map_types: list, generator_type: str, param_to_vary: str):
    """Generate models varying only one parameter while keeping others fixed."""
    print(f"\nGenerating {n_models} terrains using {generator_type.capitalize()} Generator...")
    print(f"Varying parameter: {param_to_vary}")
    
    # Get the range for the parameter to vary
    param_values = get_parameter_range(param_to_vary, n_models)
    
    # Generate noise map once
    noise = SphericalFBMNoiseStrategy(scale=2.0, octaves=6, persistence=0.5, lacunarity=2.0)
    noise_map = noise.generate((180, 360))
    
    # Store generators for combined cross section
    generators = []
    
    for i in range(n_models):
        name = f"{generator_type}_{param_to_vary}_{i+1}"
        print(f"Generating terrain: {name}...")
        
        if generator_type == 'simple':
            # Set up simple generator parameters
            params = SimpleParameters(
                name=name,
                scale=param_values[i] if param_to_vary == 'scale' else 2.0
            )
            
            generator = SimpleGenerator(
                shape=(180, 360),
                parameters=params,
                noise=noise_map,
                output_dir=output_dir
            )
            
        else:  # advanced generator
            # Get default parameters
            default_params = get_default_advanced_parameters()
            
            # Update the parameter to vary
            if param_to_vary != 'noise_scale':
                default_params[param_to_vary] = param_values[i]
            
            params = AdvancedParameters(
                name=name,
                **default_params
            )
            
            generator = AdvancedGenerator(
                shape=(180, 360),
                parameters=params,
                noise=noise_map,
                output_dir=output_dir
            )
        
        # Generate maps
        generator.create_displacement_map()
        
        # Store generator for combined cross section
        generators.append((generator, f"{param_to_vary}={param_values[i]:.2f}"))
        
        if 'terrain' in map_types:
            generator.save_terrain_visualization(
                projection_type=ProjectionType.EQUIRECTANGULAR,
                suffix=f"_{name}"
            )
        
        if 'projection' in map_types:
            generator.save_2d_projection(
                projection_type=ProjectionType.EQUIRECTANGULAR,
                suffix=f"_{name}"
            )
            
        if 'cross_section' in map_types:
            generator.save_equatorial_cross_section()
            
        if '3d' in map_types:
            generator.view_3d_terrain(water_level=0.0)
    
    # Create combined cross section plot if requested
    if 'cross_section' in map_types:
        save_combined_cross_sections(
            generators,
            output_dir,
            f"Combined Cross Sections - Varying {param_to_vary}"
        )

def generate_simple_terrains(n_models: int, output_dir: str, map_types: list):
    """Generate n_models using the simple generator with varied parameters."""
    print(f"\nGenerating {n_models} terrains using Simple Generator...")
    
    # Create base scale and noise scale ranges
    scales = np.linspace(1.0, 3.0, n_models)
    
    # Generate noise map once
    noise = SphericalFBMNoiseStrategy(scale=2.0, octaves=6, persistence=0.5, lacunarity=2.0)
    noise_map = noise.generate((180, 360))
    
    for i in range(n_models):
        name = f"simple_{i+1}"
        print(f"Generating simple terrain: {name}...")
        
        params = SimpleParameters(
            name=name,
            scale=scales[i]
        )
        
        generator = SimpleGenerator(
            shape=(180, 360),
            parameters=params,
            noise=noise_map,  # Pass the pre-generated noise map
            output_dir=output_dir
        )
        
        generator.create_displacement_map()
        
        if 'terrain' in map_types:
            generator.save_terrain_visualization(
                projection_type=ProjectionType.EQUIRECTANGULAR,
                suffix=f"_{name}"
            )
        
        if 'projection' in map_types:
            generator.save_2d_projection(
                projection_type=ProjectionType.EQUIRECTANGULAR,
                suffix=f"_{name}"
            )
            
        if 'cross_section' in map_types:
            generator.save_equatorial_cross_section()
            
        if '3d' in map_types:
            generator.view_3d_terrain(water_level=0.0)

def generate_advanced_terrains(n_models: int, output_dir: str, map_types: list):
    """Generate n_models using the advanced generator with varied parameters."""
    print(f"\nGenerating {n_models} terrains using Advanced Generator...")
    
    # Create parameter ranges
    base_scales = np.linspace(0.8, 1.5, n_models)
    
    # Generate noise map once
    noise = SphericalFBMNoiseStrategy(scale=2.0, octaves=6, persistence=0.5, lacunarity=2.0)
    noise_map = noise.generate((180, 360))
    
    for i in range(n_models):
        name = f"advanced_{i+1}"
        print(f"Generating advanced terrain: {name}...")
        
        params = AdvancedParameters(
            name=name,
            base_scale=base_scales[i],
            erosion_iterations=4,    # Fixed value
            roughness=0.4,          # Fixed value
            noise_scale=2.0         # Fixed value
        )
        
        generator = AdvancedGenerator(
            shape=(180, 360),
            parameters=params,
            noise=noise_map,  # Pass the pre-generated noise map
            output_dir=output_dir
        )
        
        generator.create_displacement_map()
        
        if 'terrain' in map_types:
            generator.save_terrain_visualization(
                projection_type=ProjectionType.EQUIRECTANGULAR,
                suffix=f"_{name}"
            )
        
        if 'projection' in map_types:
            generator.save_2d_projection(
                projection_type=ProjectionType.EQUIRECTANGULAR,
                suffix=f"_{name}"
            )
            
        if 'cross_section' in map_types:
            generator.save_equatorial_cross_section()
            
        if '3d' in map_types:
            generator.view_3d_terrain(water_level=0.0)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate terrain maps using simple or advanced generator.')
    parser.add_argument('-g', '--generator', 
                       choices=['simple', 'advanced'],
                       required=True,
                       help='Type of generator to use (simple or advanced)')
    parser.add_argument('-n', '--num_models',
                       type=int,
                       required=True,
                       help='Number of models to generate')
    parser.add_argument('-m', '--map_type',
                       nargs='+',
                       choices=['terrain', 'projection', 'cross_section', '3d'],
                       default=['terrain', 'projection'],
                       help='Type of maps to generate (terrain, projection, cross_section, and/or 3d)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--variate',
                      help='Parameter to vary while keeping others fixed. For simple generator: scale, noise_scale. '
                           'For advanced generator: base_scale, erosion_iterations, roughness, noise_scale')
    group.add_argument('-va', '--vary_all',
                      action='store_true',
                      help='Generate variations for all parameters of the selected generator')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate parameter to vary based on generator type
    if args.variate:
        valid_params = get_valid_parameters(args.generator)
        if args.variate not in valid_params:
            parser.error(f"Invalid parameter for {args.generator} generator. Choose from: {', '.join(valid_params)}")
    
    # Define output directory
    output_dir = "output"
    
    # Clear existing image files in output directory
    for file in os.listdir(output_dir):
        if file.endswith(('.png', '.jpg', '.jpeg')):
            os.remove(os.path.join(output_dir, file))
            
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate terrains based on selected generator and variation mode
    if args.vary_all:
        generate_all_parameter_variations(args.num_models, output_dir, args.map_type, args.generator)
    elif args.variate:
        generate_with_varied_parameter(args.num_models, output_dir, args.map_type, args.generator, args.variate)
    else:
        if args.generator == 'simple':
            generate_simple_terrains(args.num_models, output_dir, args.map_type)
        else:
            generate_advanced_terrains(args.num_models, output_dir, args.map_type)

if __name__ == "__main__":
    main() 
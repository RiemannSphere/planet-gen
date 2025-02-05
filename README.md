# Planet Generator

A Python project for procedurally generating images of foreign planets. The project uses various image processing and mathematical techniques to create realistic-looking planetary terrain maps.

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
.\venv\Scripts\Activate.ps1  # On Windows PowerShell
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Database Setup and Configuration

The project uses SQLite to store terrain generation configurations. To set up and manage configurations:

1. First, ensure the database is initialized by running the migrations:
```bash
alembic upgrade head
```

2. Initialize default terrain configurations:
```bash
python src/setup_configs.py
```

3. To add new configurations, edit `src/setup_configs.py`. Each configuration should include:
   - `name`: Unique identifier for the configuration
   - `sigma`: Controls terrain smoothness
   - `sea_level`: Water level threshold (0.0 to 1.0)
   - `use_power_function`: Boolean for continent formation
   - `continent_factor`: Factor affecting continent distinctness
   - `description`: Human-readable description of the configuration

4. To remove configurations from the database:
```bash
python src/setup_configs.py --remove config1 config2 ...
```
Replace `config1 config2 ...` with the names of the configurations you want to remove. You can specify multiple configurations to remove at once.

Example configuration:
```python
TerrainConfig(
    name='mountainous',
    sigma=50.0,
    sea_level=0.35,
    use_power_function=True,
    continent_factor=2.5,
    description='Terrain with prominent mountain ranges'
)
```

## Database Migrations

The project uses SQLAlchemy with Alembic for database migrations. To manage database schema changes:

1. After modifying models in `src/models.py`, create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

2. Review the generated migration file in `src/migrations/versions/`

3. Apply the migration:
```bash
alembic upgrade head
```

To revert a migration:
```bash
alembic downgrade -1  # Go back one version
# or
alembic downgrade base  # Revert all migrations
```

## Running the Project

The project can be run with various command-line arguments to control the terrain generation process. Here's the basic syntax:

```bash
python src/main.py -g <generator_type> -n <number_of_models> [options]
```

### Command Line Arguments

- `-g, --generator`: Type of generator to use (Required)
  - Options: `simple`, `advanced`
- `-n, --num_models`: Number of models to generate (Required)
- `-m, --map_type`: Types of maps to generate (Optional)
  - Options: `terrain`, `projection`, `cross_section`
  - Multiple types can be specified: `-m terrain projection cross_section`
  - Default: `terrain projection`
- `-v, --variate`: Parameter to vary while keeping others fixed (Optional)
  - For simple generator: `scale`
  - For advanced generator: `base_scale`
- `-va, --vary_all`: Generate variations for all parameters of the selected generator (Optional)

### Example Usage Scenarios

1. Generate a single terrain using the simple generator:
```bash
python src/main.py -g simple -n 1
```

2. Generate multiple terrains using the advanced generator:
```bash
python src/main.py -g advanced -n 5
```

3. Generate terrains with all map types (terrain, projection, and cross-section):
```bash
python src/main.py -g advanced -n 3 -m terrain projection cross_section
```

4. Generate variations by varying a specific parameter:
```bash
# Vary scale parameter for simple generator
python src/main.py -g simple -n 5 -v scale

# Vary base_scale parameter for advanced generator
python src/main.py -g advanced -n 5 -v base_scale
```

5. Generate variations for all parameters:
```bash
python src/main.py -g advanced -n 3 -va
```

The generated files will be saved in the `output` directory. Each run clears previous output files to maintain a clean workspace.

## Features (Planned)
- 2D terrain map generation
- Height map visualization
- Procedural texture generation
- Atmospheric effects
- Surface features (craters, mountains, etc.)

## Project Structure
```
planet-gen/
├── requirements.txt    # Project dependencies
├── README.md          # This file
└── src/              # Source code directory
``` 
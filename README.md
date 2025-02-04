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
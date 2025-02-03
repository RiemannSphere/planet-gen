from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Optional
from models import TerrainConfig
import os

# Create base class for SQLAlchemy models
Base = declarative_base()
metadata = MetaData()

class TerrainConfigDB(Base):
    """SQLAlchemy model for terrain configurations."""
    __tablename__ = 'terrain_configs'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    sigma = Column(Float, nullable=False)
    sea_level = Column(Float, nullable=False)
    use_power_function = Column(Boolean, nullable=False)
    continent_factor = Column(Float, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class TerrainDB:
    def __init__(self, db_path: str = "terrain_configs.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables - in production, this should be handled by migrations
        Base.metadata.create_all(self.engine)
    
    def save_config(self, config: TerrainConfig) -> None:
        """Save a validated terrain configuration to the database.
        
        Args:
            config: Pydantic TerrainConfig model instance
        """
        with self.SessionLocal() as session:
            db_config = TerrainConfigDB(**config.model_dump(exclude={'created_at'}))
            session.add(db_config)
            session.commit()
    
    def get_all_configs(self) -> List[TerrainConfig]:
        """Retrieve all terrain configurations from the database.
        
        Returns:
            List of TerrainConfig instances
        """
        with self.SessionLocal() as session:
            db_configs = session.query(TerrainConfigDB).order_by(TerrainConfigDB.created_at.desc()).all()
            return [TerrainConfig.model_validate(config) for config in db_configs]

    def get_config_by_name(self, name: str) -> Optional[TerrainConfig]:
        """Retrieve a terrain configuration by name.
        
        Args:
            name: Name of the configuration to retrieve
            
        Returns:
            TerrainConfig if found, None otherwise
        """
        with self.SessionLocal() as session:
            db_config = session.query(TerrainConfigDB).filter(TerrainConfigDB.name == name).first()
            return TerrainConfig.model_validate(db_config) if db_config else None

    def config_exists(self, name: str) -> bool:
        """Check if a configuration with the given name exists.
        
        Args:
            name: Name of the configuration to check
            
        Returns:
            bool: True if configuration exists, False otherwise
        """
        with self.SessionLocal() as session:
            return session.query(TerrainConfigDB).filter(TerrainConfigDB.name == name).count() > 0 
from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base, get_db
from ..services.ships import ShipService
from ..plugins.manager import PluginManager
from ..plugins.scout_ship import ScoutShipPlugin
from ..logging.logger import setup_logging
from ..events.event_bus import EventBus

class Container(containers.DeclarativeContainer):
    # Контейнер зависимостей
    
    config = providers.Configuration()
    
    # Logging
    logger = providers.Singleton(
        setup_logging,
        log_level=config.log_level,
        log_file=config.log_file,
        elasticsearch_host=config.elasticsearch_host,
        elasticsearch_port=config.elasticsearch_port,
        elasticsearch_index=config.elasticsearch_index
    )
    
    # Event Bus
    event_bus = providers.Singleton(
        EventBus,
        logger=logger
    )
    
    # Database
    engine = providers.Singleton(
        create_engine,
        config.database.url
    )
    
    session_factory = providers.Singleton(
        sessionmaker,
        engine,
        autocommit=False,
        autoflush=False
    )
    
    db = providers.Resource(
        get_db,
        session_factory
    )
    
    # Plugins
    plugin_manager = providers.Singleton(
        PluginManager
    )
    
    scout_ship_plugin = providers.Singleton(
        ScoutShipPlugin
    )
    
    # Services
    ship_service = providers.Singleton(
        ShipService,
        plugin_manager=plugin_manager,
        logger=logger,
        event_bus=event_bus
    ) 
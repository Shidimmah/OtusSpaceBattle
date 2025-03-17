from .game import router as game_router
from .player import router as player_router
from .analytics import router as analytics_router
from .ships import router as ships_router

__all__ = ['game_router', 'player_router', 'analytics_router', 'ships_router'] 
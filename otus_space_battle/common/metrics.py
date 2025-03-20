from prometheus_client import Counter, Histogram, Gauge
from typing import Dict
from .metric_utils import create_counter, create_histogram, create_gauge

class ServiceMetrics:
    """Базовый класс для метрик сервисов"""
    def __init__(self, service_name: str):
        self.service_name = service_name
        
        # Общие метрики для всех сервисов
        self.request_count = create_counter(
            'request_count_total',
            'Total number of requests',
            ['service', 'endpoint', 'method'],
            service_name=service_name
        )
        
        self.request_latency = create_histogram(
            'request_latency_seconds',
            'Request latency in seconds',
            ['service', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
            service_name=service_name
        )
        
        self.error_count = create_counter(
            'error_count_total',
            'Total number of errors',
            ['service', 'error_type'],
            service_name=service_name
        )
        
        self.active_connections = create_gauge(
            'active_connections',
            'Number of active connections',
            ['service'],
            service_name=service_name
        )

class BattleMechanicsMetrics(ServiceMetrics):
    """Метрики для сервиса боевой механики"""
    def __init__(self):
        super().__init__("battle_mechanics")
        
        # Специфичные метрики
        self.movement_count = create_counter(
            'movement_commands_total',
            'Total number of movement commands',
            ['result'],  # success/failure
            service_name=self.service_name
        )
        
        self.rotation_count = create_counter(
            'rotation_commands_total',
            'Total number of rotation commands',
            ['result'],
            service_name=self.service_name
        )
        
        self.fire_count = create_counter(
            'fire_commands_total',
            'Total number of fire commands',
            ['result'],
            service_name=self.service_name
        )
        
        self.collision_count = create_counter(
            'collision_checks_total',
            'Total number of collision checks',
            ['result'],
            service_name=self.service_name
        )

class ResourceManagementMetrics(ServiceMetrics):
    """Метрики для сервиса управления ресурсами"""
    def __init__(self):
        super().__init__("resource_management")
        
        # Специфичные метрики
        self.fuel_usage = create_counter(
            'fuel_usage_total',
            'Total amount of fuel used',
            ['ship_id'],
            service_name=self.service_name
        )
        
        self.torpedo_usage = create_counter(
            'torpedo_usage_total',
            'Total number of torpedoes used',
            ['ship_id'],
            service_name=self.service_name
        )
        
        self.resource_check_count = create_counter(
            'resource_checks_total',
            'Total number of resource availability checks',
            ['resource_type', 'result'],
            service_name=self.service_name
        )
        
        self.active_ships = create_gauge(
            'active_ships',
            'Number of active ships',
            ['game_id'],
            service_name=self.service_name
        )

class RankingMetrics(ServiceMetrics):
    """Метрики для сервиса рейтинга"""
    def __init__(self):
        super().__init__("ranking")
        
        # Специфичные метрики
        self.rank_updates = create_counter(
            'rank_updates_total',
            'Total number of rank updates',
            ['result_type'],  # win/loss/draw
            service_name=self.service_name
        )
        
        self.points_awarded = create_counter(
            'points_awarded_total',
            'Total number of ranking points awarded',
            ['points_type'],  # gained/lost
            service_name=self.service_name
        )
        
        self.leaderboard_queries = create_counter(
            'leaderboard_queries_total',
            'Total number of leaderboard queries',
            service_name=self.service_name
        )
        
        self.active_players = create_gauge(
            'active_players',
            'Number of active players in the ranking system',
            service_name=self.service_name
        )

class AnalyticsMetrics(ServiceMetrics):
    """Метрики для сервиса аналитики"""
    def __init__(self):
        super().__init__("analytics")
        
        # Специфичные метрики
        self.events_processed = create_counter(
            'events_processed_total',
            'Total number of game events processed',
            ['event_type'],
            service_name=self.service_name
        )
        
        self.stats_queries = create_counter(
            'stats_queries_total',
            'Total number of statistics queries',
            ['query_type'],  # game/player
            service_name=self.service_name
        )
        
        self.event_processing_time = create_histogram(
            'event_processing_seconds',
            'Time spent processing events',
            ['event_type'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1],
            service_name=self.service_name
        )
        
        self.stored_events = create_gauge(
            'stored_events',
            'Number of events stored in the system',
            ['game_id'],
            service_name=self.service_name
        )

class ApiGatewayMetrics(ServiceMetrics):
    """Метрики для API Gateway"""
    def __init__(self):
        super().__init__("api_gateway")
        
        # Специфичные метрики
        self.upstream_latency = create_histogram(
            'upstream_latency_seconds',
            'Latency of upstream service calls',
            ['upstream_service'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
            service_name=self.service_name
        )
        
        self.upstream_errors = create_counter(
            'upstream_errors_total',
            'Number of upstream service errors',
            ['upstream_service', 'error_type'],
            service_name=self.service_name
        )
        
        self.active_games = create_gauge(
            'active_games',
            'Number of active games',
            service_name=self.service_name
        )
        
        self.api_key_validations = create_counter(
            'api_key_validations_total',
            'Number of API key validations',
            ['result'],  # success/failure
            service_name=self.service_name
        )

# Глобальные счетчики игровых событий (с использованием функций создания метрик)
game_events_total = create_counter(
    'game_events_total',
    'Total number of game events',
    ['event_type']
)

# Счетчики активных игроков
active_players = create_gauge(
    'active_players',
    'Number of active players',
    ['status']
)

# Гистограмма длительности матчей
match_duration_seconds = create_histogram(
    'match_duration_seconds',
    'Duration of matches in seconds',
    buckets=[30, 60, 120, 300, 600, 1200, 1800, 3600]
)

# Счетчики использования ресурсов
resource_usage_bytes = create_gauge(
    'resource_usage_bytes',
    'Resource usage in bytes',
    ['resource_type']
)

# Счетчики API запросов
api_requests_total = create_counter(
    'api_requests_total',
    'Total number of API requests',
    ['endpoint', 'method', 'status']
)

# Гистограмма длительности API запросов
api_request_duration_seconds = create_histogram(
    'api_request_duration_seconds',
    'Duration of API requests in seconds',
    ['endpoint', 'method'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Счетчики ошибок
error_total = create_counter(
    'error_total',
    'Total number of errors',
    ['error_type']
)

# Счетчики рейтинга игроков
player_rating = create_gauge(
    'player_rating',
    'Player rating',
    ['player_id']
) 
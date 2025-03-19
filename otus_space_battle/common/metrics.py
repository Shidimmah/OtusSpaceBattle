from prometheus_client import Counter, Histogram, Gauge
from typing import Dict

class ServiceMetrics:
    """Базовый класс для метрик сервисов"""
    def __init__(self, service_name: str):
        self.service_name = service_name
        
        # Общие метрики для всех сервисов
        self.request_count = Counter(
            'request_count_total',
            'Total number of requests',
            ['service', 'endpoint', 'method']
        )
        
        self.request_latency = Histogram(
            'request_latency_seconds',
            'Request latency in seconds',
            ['service', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        self.error_count = Counter(
            'error_count_total',
            'Total number of errors',
            ['service', 'error_type']
        )
        
        self.active_connections = Gauge(
            'active_connections',
            'Number of active connections',
            ['service']
        )

class BattleMechanicsMetrics(ServiceMetrics):
    """Метрики для сервиса боевой механики"""
    def __init__(self):
        super().__init__("battle_mechanics")
        
        # Специфичные метрики
        self.movement_count = Counter(
            'movement_commands_total',
            'Total number of movement commands',
            ['result']  # success/failure
        )
        
        self.rotation_count = Counter(
            'rotation_commands_total',
            'Total number of rotation commands',
            ['result']
        )
        
        self.fire_count = Counter(
            'fire_commands_total',
            'Total number of fire commands',
            ['result']
        )
        
        self.collision_count = Counter(
            'collision_checks_total',
            'Total number of collision checks',
            ['result']
        )

class ResourceManagementMetrics(ServiceMetrics):
    """Метрики для сервиса управления ресурсами"""
    def __init__(self):
        super().__init__("resource_management")
        
        # Специфичные метрики
        self.fuel_usage = Counter(
            'fuel_usage_total',
            'Total amount of fuel used',
            ['ship_id']
        )
        
        self.torpedo_usage = Counter(
            'torpedo_usage_total',
            'Total number of torpedoes used',
            ['ship_id']
        )
        
        self.resource_check_count = Counter(
            'resource_checks_total',
            'Total number of resource availability checks',
            ['resource_type', 'result']
        )
        
        self.active_ships = Gauge(
            'active_ships',
            'Number of active ships',
            ['game_id']
        )

class RankingMetrics(ServiceMetrics):
    """Метрики для сервиса рейтинга"""
    def __init__(self):
        super().__init__("ranking")
        
        # Специфичные метрики
        self.rank_updates = Counter(
            'rank_updates_total',
            'Total number of rank updates',
            ['result_type']  # win/loss/draw
        )
        
        self.points_awarded = Counter(
            'points_awarded_total',
            'Total number of ranking points awarded',
            ['points_type']  # gained/lost
        )
        
        self.leaderboard_queries = Counter(
            'leaderboard_queries_total',
            'Total number of leaderboard queries'
        )
        
        self.active_players = Gauge(
            'active_players',
            'Number of active players in the ranking system'
        )

class AnalyticsMetrics(ServiceMetrics):
    """Метрики для сервиса аналитики"""
    def __init__(self):
        super().__init__("analytics")
        
        # Специфичные метрики
        self.events_processed = Counter(
            'events_processed_total',
            'Total number of game events processed',
            ['event_type']
        )
        
        self.stats_queries = Counter(
            'stats_queries_total',
            'Total number of statistics queries',
            ['query_type']  # game/player
        )
        
        self.event_processing_time = Histogram(
            'event_processing_seconds',
            'Time spent processing events',
            ['event_type'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1]
        )
        
        self.stored_events = Gauge(
            'stored_events',
            'Number of events stored in the system',
            ['game_id']
        )

class ApiGatewayMetrics(ServiceMetrics):
    """Метрики для API Gateway"""
    def __init__(self):
        super().__init__("api_gateway")
        
        # Специфичные метрики
        self.upstream_latency = Histogram(
            'upstream_latency_seconds',
            'Latency of upstream service calls',
            ['upstream_service'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        self.upstream_errors = Counter(
            'upstream_errors_total',
            'Number of upstream service errors',
            ['upstream_service', 'error_type']
        )
        
        self.active_games = Gauge(
            'active_games',
            'Number of active games'
        )
        
        self.api_key_validations = Counter(
            'api_key_validations_total',
            'Number of API key validations',
            ['result']  # success/failure
        )

# Счетчики игровых событий
game_events_total = Counter(
    'game_events_total',
    'Total number of game events',
    ['event_type']
)

# Счетчики активных игроков
active_players = Gauge(
    'active_players',
    'Number of active players',
    ['status']
)

# Гистограмма длительности матчей
match_duration_seconds = Histogram(
    'match_duration_seconds',
    'Duration of matches in seconds',
    buckets=[30, 60, 120, 300, 600, 1200, 1800, 3600]
)

# Счетчики использования ресурсов
resource_usage_bytes = Gauge(
    'resource_usage_bytes',
    'Resource usage in bytes',
    ['resource_type']
)

# Счетчики API запросов
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['endpoint', 'method', 'status']
)

# Гистограмма длительности API запросов
api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'Duration of API requests in seconds',
    ['endpoint', 'method'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Счетчики ошибок
error_total = Counter(
    'error_total',
    'Total number of errors',
    ['error_type']
)

# Счетчики рейтинга игроков
player_rating = Gauge(
    'player_rating',
    'Player rating',
    ['player_id']
) 
import pytest
from prometheus_client import REGISTRY, Counter, Gauge, Histogram
from common.metrics import (
    ServiceMetrics,
    BattleMechanicsMetrics,
    ResourceManagementMetrics,
    RankingMetrics,
    AnalyticsMetrics,
    ApiGatewayMetrics,
    game_events_total,
    active_players,
    match_duration_seconds,
    resource_usage_bytes,
    api_requests_total,
    api_request_duration_seconds,
    error_total,
    player_rating
)

@pytest.mark.unit
class TestMetrics:
    
    @pytest.fixture(autouse=True)
    def clear_registry(self):
        """Очищаем реестр Prometheus перед каждым тестом"""
        collectors = list(REGISTRY._collector_to_names.keys())
        for collector in collectors:
            REGISTRY.unregister(collector)
        yield
    
    def test_game_events_counter(self):
        """Тест счетчика игровых событий"""
        # Проверяем, что счетчик существует
        assert isinstance(game_events_total, Counter)
        
        # Инкрементируем счетчик
        game_events_total.labels(event_type='move').inc()
        game_events_total.labels(event_type='fire').inc(2)
        
        # Проверяем значения
        assert game_events_total.labels(event_type='move')._value.get() == 1
        assert game_events_total.labels(event_type='fire')._value.get() == 2
    
    def test_active_players_gauge(self):
        """Тест счетчика активных игроков"""
        # Проверяем, что счетчик существует
        assert isinstance(active_players, Gauge)
        
        # Устанавливаем и изменяем значения
        active_players.labels(status='online').set(10)
        active_players.labels(status='in_battle').set(5)
        
        # Инкрементируем и декрементируем
        active_players.labels(status='online').inc(2)
        active_players.labels(status='in_battle').dec()
        
        # Проверяем значения
        assert active_players.labels(status='online')._value.get() == 12
        assert active_players.labels(status='in_battle')._value.get() == 4
    
    def test_match_duration_histogram(self):
        """Тест гистограммы длительности матчей"""
        # Проверяем, что гистограмма существует
        assert isinstance(match_duration_seconds, Histogram)
        
        # Записываем значения
        match_duration_seconds.observe(45)  # 45 секунд
        match_duration_seconds.observe(150)  # 2.5 минуты
        match_duration_seconds.observe(360)  # 6 минут
        
        # Проверяем, что значения записаны
        assert match_duration_seconds._sum.get() == 45 + 150 + 360
        
        # Получаем счетчик вызовов через sample_count
        histogram_samples = REGISTRY.get_sample_values(
            'match_duration_seconds_count'
        )
        assert len(histogram_samples) > 0
        
        # Альтернативный вариант проверки - через сумму всех bucket samples
        bucket_samples = REGISTRY.get_sample_values(
            'match_duration_seconds_bucket'
        )
        assert len(bucket_samples) > 0
    
    def test_resource_usage_bytes(self):
        """Тест счетчика использования ресурсов"""
        # Проверяем, что счетчик существует
        assert isinstance(resource_usage_bytes, Gauge)
        
        # Устанавливаем значения
        resource_usage_bytes.labels(resource_type='memory').set(1024 * 1024)  # 1 MB
        resource_usage_bytes.labels(resource_type='disk').set(1024 * 1024 * 100)  # 100 MB
        
        # Проверяем значения
        assert resource_usage_bytes.labels(resource_type='memory')._value.get() == 1024 * 1024
        assert resource_usage_bytes.labels(resource_type='disk')._value.get() == 1024 * 1024 * 100
    
    def test_api_requests_counter(self):
        """Тест счетчика API запросов"""
        # Проверяем, что счетчик существует
        assert isinstance(api_requests_total, Counter)
        
        # Инкрементируем счетчик
        api_requests_total.labels(endpoint='/api/v1/battles', method='GET', status='200').inc()
        api_requests_total.labels(endpoint='/api/v1/users', method='POST', status='201').inc(2)
        
        # Проверяем значения
        assert api_requests_total.labels(endpoint='/api/v1/battles', method='GET', status='200')._value.get() == 1
        assert api_requests_total.labels(endpoint='/api/v1/users', method='POST', status='201')._value.get() == 2
    
    def test_api_request_duration(self):
        """Тест гистограммы длительности API запросов"""
        # Проверяем, что гистограмма существует
        assert isinstance(api_request_duration_seconds, Histogram)
        
        # Записываем значения
        api_request_duration_seconds.labels(endpoint='/api/v1/battles', method='GET').observe(0.2)
        api_request_duration_seconds.labels(endpoint='/api/v1/users', method='POST').observe(1.5)
        
        # Проверяем, что значения записаны
        assert api_request_duration_seconds.labels(endpoint='/api/v1/battles', method='GET')._sum.get() == 0.2
        assert api_request_duration_seconds.labels(endpoint='/api/v1/users', method='POST')._sum.get() == 1.5
    
    def test_error_counter(self):
        """Тест счетчика ошибок"""
        # Проверяем, что счетчик существует
        assert isinstance(error_total, Counter)
        
        # Инкрементируем счетчик
        error_total.labels(error_type='ValueError').inc()
        error_total.labels(error_type='ConnectionError').inc(3)
        
        # Проверяем значения
        assert error_total.labels(error_type='ValueError')._value.get() == 1
        assert error_total.labels(error_type='ConnectionError')._value.get() == 3
    
    def test_player_rating_gauge(self):
        """Тест счетчика рейтинга игроков"""
        # Проверяем, что счетчик существует
        assert isinstance(player_rating, Gauge)
        
        # Устанавливаем значения
        player_rating.labels(player_id='player1').set(1500)
        player_rating.labels(player_id='player2').set(1800)
        
        # Проверяем значения
        assert player_rating.labels(player_id='player1')._value.get() == 1500
        assert player_rating.labels(player_id='player2')._value.get() == 1800
    
    def test_service_metrics_base_class(self):
        """Тест базового класса метрик сервиса"""
        # Создаем экземпляр базового класса
        metrics = ServiceMetrics("test_service")
        
        # Проверяем, что все базовые метрики созданы
        assert hasattr(metrics, 'request_count')
        assert hasattr(metrics, 'request_latency')
        assert hasattr(metrics, 'error_count')
        assert hasattr(metrics, 'active_connections')
        
        # Проверяем, что service_name установлен правильно
        assert metrics.service_name == "test_service"
        
        # Инкрементируем счетчики и проверяем значения
        metrics.request_count.labels(service="test_service", endpoint="/test", method="GET").inc()
        metrics.error_count.labels(service="test_service", error_type="ValueError").inc(2)
        
        assert metrics.request_count.labels(service="test_service", endpoint="/test", method="GET")._value.get() == 1
        assert metrics.error_count.labels(service="test_service", error_type="ValueError")._value.get() == 2
        
    def test_battle_mechanics_metrics(self):
        """Тест метрик сервиса боевой механики"""
        # Создаем экземпляр метрик боевой механики
        metrics = BattleMechanicsMetrics()
        
        # Проверяем, что service_name установлен правильно
        assert metrics.service_name == "battle_mechanics"
        
        # Проверяем, что все специфичные метрики созданы
        assert hasattr(metrics, 'movement_count')
        assert hasattr(metrics, 'rotation_count')
        assert hasattr(metrics, 'fire_count')
        assert hasattr(metrics, 'collision_count')
        
        # Инкрементируем счетчики и проверяем значения
        metrics.movement_count.labels(result="success").inc(5)
        metrics.fire_count.labels(result="failure").inc(2)
        
        assert metrics.movement_count.labels(result="success")._value.get() == 5
        assert metrics.fire_count.labels(result="failure")._value.get() == 2
        
    def test_resource_management_metrics(self):
        """Тест метрик сервиса управления ресурсами"""
        # Создаем экземпляр метрик управления ресурсами
        metrics = ResourceManagementMetrics()
        
        # Проверяем, что service_name установлен правильно
        assert metrics.service_name == "resource_management"
        
        # Проверяем, что все специфичные метрики созданы
        assert hasattr(metrics, 'fuel_usage')
        assert hasattr(metrics, 'torpedo_usage')
        assert hasattr(metrics, 'resource_check_count')
        assert hasattr(metrics, 'active_ships')
        
        # Инкрементируем счетчики и проверяем значения
        metrics.fuel_usage.labels(ship_id="ship_1").inc(100)
        metrics.torpedo_usage.labels(ship_id="ship_1").inc(3)
        metrics.active_ships.labels(game_id="game_1").set(5)
        
        assert metrics.fuel_usage.labels(ship_id="ship_1")._value.get() == 100
        assert metrics.torpedo_usage.labels(ship_id="ship_1")._value.get() == 3
        assert metrics.active_ships.labels(game_id="game_1")._value.get() == 5
        
    def test_ranking_metrics(self):
        """Тест метрик сервиса рейтинга"""
        # Создаем экземпляр метрик рейтинга
        metrics = RankingMetrics()
        
        # Проверяем, что service_name установлен правильно
        assert metrics.service_name == "ranking"
        
        # Проверяем, что все специфичные метрики созданы
        assert hasattr(metrics, 'rank_updates')
        assert hasattr(metrics, 'points_awarded')
        assert hasattr(metrics, 'leaderboard_queries')
        assert hasattr(metrics, 'active_players')
        
        # Инкрементируем счетчики и проверяем значения
        metrics.rank_updates.labels(result_type="win").inc(10)
        metrics.points_awarded.labels(points_type="gained").inc(150)
        metrics.leaderboard_queries.inc(3)
        
        assert metrics.rank_updates.labels(result_type="win")._value.get() == 10
        assert metrics.points_awarded.labels(points_type="gained")._value.get() == 150
        assert metrics.leaderboard_queries._value.get() == 3
        
    def test_analytics_metrics(self):
        """Тест метрик сервиса аналитики"""
        # Создаем экземпляр метрик аналитики
        metrics = AnalyticsMetrics()
        
        # Проверяем, что service_name установлен правильно
        assert metrics.service_name == "analytics"
        
        # Проверяем, что все специфичные метрики созданы
        assert hasattr(metrics, 'events_processed')
        assert hasattr(metrics, 'stats_queries')
        assert hasattr(metrics, 'event_processing_time')
        assert hasattr(metrics, 'stored_events')
        
        # Инкрементируем счетчики и проверяем значения
        metrics.events_processed.labels(event_type="move").inc(20)
        metrics.stats_queries.labels(query_type="player").inc(5)
        
        assert metrics.events_processed.labels(event_type="move")._value.get() == 20
        assert metrics.stats_queries.labels(query_type="player")._value.get() == 5
        
    def test_api_gateway_metrics(self):
        """Тест метрик API Gateway"""
        # Создаем экземпляр метрик API Gateway
        metrics = ApiGatewayMetrics()
        
        # Проверяем, что service_name установлен правильно
        assert metrics.service_name == "api_gateway"
        
        # Проверяем, что все специфичные метрики созданы
        assert hasattr(metrics, 'upstream_latency')
        assert hasattr(metrics, 'upstream_errors')
        assert hasattr(metrics, 'active_games')
        assert hasattr(metrics, 'api_key_validations')
        
        # Инкрементируем счетчики и проверяем значения
        metrics.upstream_errors.labels(upstream_service="battle_mechanics", error_type="timeout").inc(2)
        metrics.api_key_validations.labels(result="success").inc(15)
        metrics.active_games.set(7)
        
        assert metrics.upstream_errors.labels(upstream_service="battle_mechanics", error_type="timeout")._value.get() == 2
        assert metrics.api_key_validations.labels(result="success")._value.get() == 15
        assert metrics.active_games._value.get() == 7 
import pytest
from prometheus_client import REGISTRY, Counter, Gauge, Histogram
from common.metrics import (
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
        assert match_duration_seconds._count.get() == 3
    
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
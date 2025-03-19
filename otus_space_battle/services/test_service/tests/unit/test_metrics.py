import pytest
from prometheus_client import REGISTRY, Counter, Gauge, Histogram
from common.metrics import (
    game_events_total,
    active_players_gauge,
    match_duration_seconds,
    resource_usage_bytes,
    api_requests_total,
    api_request_duration_seconds,
    error_total,
    player_rating_gauge
)

@pytest.mark.unit
class TestMetrics:
    @pytest.fixture(autouse=True)
    def clear_registry(self):
        """Очищаем регистр метрик перед каждым тестом"""
        collectors = list(REGISTRY._collector_to_names.keys())
        for collector in collectors:
            REGISTRY.unregister(collector)

    def test_game_events_counter(self):
        """Тест счетчика игровых событий"""
        # Проверяем, что метрика существует
        assert game_events_total._name == 'game_events_total'
        assert game_events_total._type == 'counter'

        # Увеличиваем счетчик
        game_events_total.labels(event_type='battle_start').inc()
        game_events_total.labels(event_type='battle_end').inc()

        # Проверяем значения
        assert game_events_total.labels(event_type='battle_start')._value.get() == 1
        assert game_events_total.labels(event_type='battle_end')._value.get() == 1

    def test_active_players_gauge(self):
        """Тест датчика активных игроков"""
        # Проверяем, что метрика существует
        assert active_players_gauge._name == 'active_players_gauge'
        assert active_players_gauge._type == 'gauge'

        # Устанавливаем значение
        active_players_gauge.set(10)
        assert active_players_gauge._value.get() == 10

        # Увеличиваем значение
        active_players_gauge.inc(5)
        assert active_players_gauge._value.get() == 15

        # Уменьшаем значение
        active_players_gauge.dec(3)
        assert active_players_gauge._value.get() == 12

    def test_match_duration_histogram(self):
        """Тест гистограммы длительности матчей"""
        # Проверяем, что метрика существует
        assert match_duration_seconds._name == 'match_duration_seconds'
        assert match_duration_seconds._type == 'histogram'

        # Записываем несколько значений
        match_duration_seconds.observe(60.0)  # 1 минута
        match_duration_seconds.observe(300.0)  # 5 минут
        match_duration_seconds.observe(600.0)  # 10 минут

        # Проверяем, что значения записаны
        assert match_duration_seconds._sum.get() == 960.0
        assert match_duration_seconds._count.get() == 3

    def test_resource_usage_bytes(self):
        """Тест датчика использования ресурсов"""
        # Проверяем, что метрика существует
        assert resource_usage_bytes._name == 'resource_usage_bytes'
        assert resource_usage_bytes._type == 'gauge'

        # Устанавливаем значения для разных типов ресурсов
        resource_usage_bytes.labels(resource_type='memory').set(1024 * 1024)  # 1MB
        resource_usage_bytes.labels(resource_type='disk').set(1024 * 1024 * 100)  # 100MB

        # Проверяем значения
        assert resource_usage_bytes.labels(resource_type='memory')._value.get() == 1024 * 1024
        assert resource_usage_bytes.labels(resource_type='disk')._value.get() == 1024 * 1024 * 100

    def test_api_requests_counter(self):
        """Тест счетчика API запросов"""
        # Проверяем, что метрика существует
        assert api_requests_total._name == 'api_requests_total'
        assert api_requests_total._type == 'counter'

        # Увеличиваем счетчик для разных эндпоинтов
        api_requests_total.labels(endpoint='/api/v1/battles').inc()
        api_requests_total.labels(endpoint='/api/v1/players').inc(2)

        # Проверяем значения
        assert api_requests_total.labels(endpoint='/api/v1/battles')._value.get() == 1
        assert api_requests_total.labels(endpoint='/api/v1/players')._value.get() == 2

    def test_api_request_duration(self):
        """Тест гистограммы длительности API запросов"""
        # Проверяем, что метрика существует
        assert api_request_duration_seconds._name == 'api_request_duration_seconds'
        assert api_request_duration_seconds._type == 'histogram'

        # Записываем несколько значений
        api_request_duration_seconds.labels(endpoint='/api/v1/battles').observe(0.1)
        api_request_duration_seconds.labels(endpoint='/api/v1/players').observe(0.2)

        # Проверяем, что значения записаны
        assert api_request_duration_seconds._sum.get() == 0.3
        assert api_request_duration_seconds._count.get() == 2

    def test_error_counter(self):
        """Тест счетчика ошибок"""
        # Проверяем, что метрика существует
        assert error_total._name == 'error_total'
        assert error_total._type == 'counter'

        # Увеличиваем счетчик для разных типов ошибок
        error_total.labels(error_type='validation_error').inc()
        error_total.labels(error_type='database_error').inc(2)

        # Проверяем значения
        assert error_total.labels(error_type='validation_error')._value.get() == 1
        assert error_total.labels(error_type='database_error')._value.get() == 2

    def test_player_rating_gauge(self):
        """Тест датчика рейтинга игрока"""
        # Проверяем, что метрика существует
        assert player_rating_gauge._name == 'player_rating_gauge'
        assert player_rating_gauge._type == 'gauge'

        # Устанавливаем значения для разных игроков
        player_rating_gauge.labels(player_id='player1').set(1500)
        player_rating_gauge.labels(player_id='player2').set(2000)

        # Проверяем значения
        assert player_rating_gauge.labels(player_id='player1')._value.get() == 1500
        assert player_rating_gauge.labels(player_id='player2')._value.get() == 2000 
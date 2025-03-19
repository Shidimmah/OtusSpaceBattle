import pytest
from prometheus_client import REGISTRY
from common.metrics import (
    ServiceMetrics,
    BattleMechanicsMetrics,
    ResourceManagementMetrics,
    RankingMetrics,
    AnalyticsMetrics,
    ApiGatewayMetrics
)

@pytest.fixture(autouse=True)
def clear_prometheus_registry():
    """Очищаем реестр Prometheus перед каждым тестом"""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)

def test_service_metrics_initialization():
    """Тест инициализации базовых метрик сервиса"""
    metrics = ServiceMetrics("test_service")
    
    assert metrics.service_name == "test_service"
    assert metrics.request_count._name == "request_count_total"
    assert metrics.request_latency._name == "request_latency_seconds"
    assert metrics.error_count._name == "error_count_total"
    assert metrics.active_connections._name == "active_connections"

def test_battle_mechanics_metrics():
    """Тест метрик сервиса боевой механики"""
    metrics = BattleMechanicsMetrics()
    
    assert metrics.service_name == "battle_mechanics"
    # Проверяем специфичные метрики
    assert metrics.movement_count._name == "movement_commands_total"
    assert metrics.rotation_count._name == "rotation_commands_total"
    assert metrics.fire_count._name == "fire_commands_total"
    assert metrics.collision_count._name == "collision_checks_total"
    
    # Тестируем увеличение счетчиков
    metrics.movement_count.labels(result="success").inc()
    metrics.rotation_count.labels(result="success").inc()
    metrics.fire_count.labels(result="success").inc()
    metrics.collision_count.labels(result="no_collision").inc()

def test_resource_management_metrics():
    """Тест метрик сервиса управления ресурсами"""
    metrics = ResourceManagementMetrics()
    
    assert metrics.service_name == "resource_management"
    assert metrics.fuel_usage._name == "fuel_usage_total"
    assert metrics.torpedo_usage._name == "torpedo_usage_total"
    assert metrics.resource_check_count._name == "resource_checks_total"
    assert metrics.active_ships._name == "active_ships"
    
    # Тестируем метрики
    metrics.fuel_usage.labels(ship_id="test_ship").inc(10.5)
    metrics.torpedo_usage.labels(ship_id="test_ship").inc()
    metrics.resource_check_count.labels(resource_type="fuel", result="success").inc()
    metrics.active_ships.labels(game_id="test_game").set(5)

def test_ranking_metrics():
    """Тест метрик сервиса рейтинга"""
    metrics = RankingMetrics()
    
    assert metrics.service_name == "ranking"
    assert metrics.rank_updates._name == "rank_updates_total"
    assert metrics.points_awarded._name == "points_awarded_total"
    assert metrics.leaderboard_queries._name == "leaderboard_queries_total"
    assert metrics.active_players._name == "active_players"
    
    # Тестируем метрики
    metrics.rank_updates.labels(result_type="win").inc()
    metrics.points_awarded.labels(points_type="gained").inc(100)
    metrics.leaderboard_queries.inc()
    metrics.active_players.set(10)

def test_analytics_metrics():
    """Тест метрик сервиса аналитики"""
    metrics = AnalyticsMetrics()
    
    assert metrics.service_name == "analytics"
    assert metrics.events_processed._name == "events_processed_total"
    assert metrics.stats_queries._name == "stats_queries_total"
    assert metrics.event_processing_time._name == "event_processing_seconds"
    assert metrics.stored_events._name == "stored_events"
    
    # Тестируем метрики
    metrics.events_processed.labels(event_type="battle_end").inc()
    metrics.stats_queries.labels(query_type="player").inc()
    metrics.event_processing_time.labels(event_type="battle_start").observe(0.1)
    metrics.stored_events.labels(game_id="test_game").set(100)

def test_api_gateway_metrics():
    """Тест метрик API Gateway"""
    metrics = ApiGatewayMetrics()
    
    assert metrics.service_name == "api_gateway"
    assert metrics.upstream_latency._name == "upstream_latency_seconds"
    assert metrics.upstream_errors._name == "upstream_errors_total"
    assert metrics.active_games._name == "active_games"
    assert metrics.api_key_validations._name == "api_key_validations_total"
    
    # Тестируем метрики
    metrics.upstream_latency.labels(upstream_service="battle_mechanics").observe(0.05)
    metrics.upstream_errors.labels(upstream_service="ranking", error_type="timeout").inc()
    metrics.active_games.set(3)
    metrics.api_key_validations.labels(result="success").inc()

def test_metrics_labels():
    """Тест правильности работы с метками метрик"""
    metrics = ServiceMetrics("test_service")
    
    # Тестируем базовые метрики с метками
    metrics.request_count.labels(
        service="test_service",
        endpoint="/test",
        method="GET"
    ).inc()
    
    metrics.request_latency.labels(
        service="test_service",
        endpoint="/test"
    ).observe(0.1)
    
    metrics.error_count.labels(
        service="test_service",
        error_type="ValueError"
    ).inc()
    
    metrics.active_connections.labels(
        service="test_service"
    ).set(1)

def test_metrics_edge_cases():
    """Тест граничных случаев для метрик"""
    metrics = ServiceMetrics("test_service")
    
    # Тест отрицательных значений (Gauge позволяет отрицательные значения)
    metrics.active_connections.labels(service="test_service").set(-1)
    assert float(metrics.active_connections.labels(service="test_service")._value.get()) == -1
    
    # Тест очень больших значений
    large_value = 1e9
    metrics.request_count.labels(
        service="test_service",
        endpoint="/test",
        method="GET"
    ).inc(large_value)
    
    # Тест очень маленьких значений для гистограммы
    small_value = 1e-9
    metrics.request_latency.labels(
        service="test_service",
        endpoint="/test"
    ).observe(small_value) 
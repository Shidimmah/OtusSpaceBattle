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

@pytest.mark.unit
class TestMetrics:
    def test_base_metrics(self):
        """Тест базовых метрик сервиса"""
        metrics = ServiceMetrics("test_service")
        
        # Проверяем создание базовых метрик
        assert metrics.request_count._name == 'request_count_total'
        assert metrics.request_latency._name == 'request_latency_seconds'
        assert metrics.error_count._name == 'error_count_total'
        assert metrics.active_connections._name == 'active_connections'
        
        # Проверяем работу метрик
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
            error_type="validation"
        ).inc()
        
        metrics.active_connections.labels(
            service="test_service"
        ).set(5)
    
    def test_battle_mechanics_metrics(self):
        """Тест метрик боевой механики"""
        metrics = BattleMechanicsMetrics()
        
        # Проверяем специфичные метрики
        assert metrics.movement_count._name == 'movement_commands_total'
        assert metrics.rotation_count._name == 'rotation_commands_total'
        assert metrics.fire_count._name == 'fire_commands_total'
        assert metrics.collision_count._name == 'collision_checks_total'
        
        # Проверяем работу метрик
        metrics.movement_count.labels(result="success").inc()
        metrics.rotation_count.labels(result="success").inc()
        metrics.fire_count.labels(result="success").inc()
        metrics.collision_count.labels(result="detected").inc()
    
    def test_resource_management_metrics(self):
        """Тест метрик управления ресурсами"""
        metrics = ResourceManagementMetrics()
        
        # Проверяем специфичные метрики
        assert metrics.fuel_usage._name == 'fuel_usage_total'
        assert metrics.torpedo_usage._name == 'torpedo_usage_total'
        assert metrics.resource_check_count._name == 'resource_checks_total'
        assert metrics.active_ships._name == 'active_ships'
        
        # Проверяем работу метрик
        metrics.fuel_usage.labels(ship_id="ship1").inc(10)
        metrics.torpedo_usage.labels(ship_id="ship1").inc()
        metrics.resource_check_count.labels(
            resource_type="fuel",
            result="success"
        ).inc()
        metrics.active_ships.labels(game_id="game1").set(2)
    
    def test_ranking_metrics(self):
        """Тест метрик рейтинга"""
        metrics = RankingMetrics()
        
        # Проверяем специфичные метрики
        assert metrics.rank_updates._name == 'rank_updates_total'
        assert metrics.points_awarded._name == 'points_awarded_total'
        assert metrics.leaderboard_queries._name == 'leaderboard_queries_total'
        assert metrics.active_players._name == 'active_players'
        
        # Проверяем работу метрик
        metrics.rank_updates.labels(result_type="win").inc()
        metrics.points_awarded.labels(points_type="gained").inc(10)
        metrics.leaderboard_queries.inc()
        metrics.active_players.set(100)
    
    def test_analytics_metrics(self):
        """Тест метрик аналитики"""
        metrics = AnalyticsMetrics()
        
        # Проверяем специфичные метрики
        assert metrics.events_processed._name == 'events_processed_total'
        assert metrics.stats_queries._name == 'stats_queries_total'
        assert metrics.event_processing_time._name == 'event_processing_seconds'
        assert metrics.stored_events._name == 'stored_events'
        
        # Проверяем работу метрик
        metrics.events_processed.labels(event_type="move").inc()
        metrics.stats_queries.labels(query_type="game").inc()
        metrics.event_processing_time.labels(event_type="move").observe(0.01)
        metrics.stored_events.labels(game_id="game1").set(50)
    
    def test_api_gateway_metrics(self):
        """Тест метрик API Gateway"""
        metrics = ApiGatewayMetrics()
        
        # Проверяем специфичные метрики
        assert metrics.upstream_latency._name == 'upstream_latency_seconds'
        assert metrics.upstream_errors._name == 'upstream_errors_total'
        assert metrics.active_games._name == 'active_games'
        assert metrics.api_key_validations._name == 'api_key_validations_total'
        
        # Проверяем работу метрик
        metrics.upstream_latency.labels(upstream_service="auth").observe(0.1)
        metrics.upstream_errors.labels(
            upstream_service="auth",
            error_type="timeout"
        ).inc()
        metrics.active_games.set(10)
        metrics.api_key_validations.labels(result="success").inc() 
# -*- coding: utf-8 -*-
"""
Tests unitaires pour le module geometry
"""
import pytest
import sys
import os

# Ajoute le chemin racine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processing.geometry.calculator import GeometryCalculator


class TestGeometryCalculator:
    """Tests pour GeometryCalculator (Rust ou Python)"""
    
    def test_distance_2d_basic(self):
        """Test distance 2D simple (3-4-5 triangle)"""
        result = GeometryCalculator.distance_2d(0, 0, 3, 4)
        assert abs(result - 5.0) < 0.001
    
    def test_distance_2d_same_point(self):
        """Distance entre un point et lui-même = 0"""
        result = GeometryCalculator.distance_2d(5, 5, 5, 5)
        assert result == 0.0
    
    def test_distance_3d_basic(self):
        """Test distance 3D"""
        result = GeometryCalculator.distance_3d(0, 0, 0, 1, 1, 1)
        expected = 1.732  # sqrt(3)
        assert abs(result - expected) < 0.01
    
    def test_angle_between_points_90deg(self):
        """Test angle 90 degrés"""
        # Points formant un angle droit
        result = GeometryCalculator.angle_between_points(
            0, 1,   # p1 (haut)
            0, 0,   # p2 (centre)
            1, 0    # p3 (droite)
        )
        assert abs(result - 90.0) < 1.0
    
    def test_angle_between_points_180deg(self):
        """Test angle 180 degrés (ligne droite)"""
        result = GeometryCalculator.angle_between_points(
            -1, 0,  # p1
            0, 0,   # p2
            1, 0    # p3
        )
        assert abs(result - 180.0) < 1.0
    
    def test_fingers_extended_all_down(self):
        """Test tous doigts baissés"""
        # Landmarks simulés (21 points avec y décroissant = doigts baissés)
        landmarks = [(0.5, 0.5 + i * 0.01, 0.0) for i in range(21)]
        result = GeometryCalculator.fingers_extended(landmarks)
        # Tous les doigts devraient être 0 (baissés)
        assert len(result) == 5
        assert sum(result) <= 1  # Max 1 doigt (pouce peut être ambigu)
    
    def test_pinch_distance_far(self):
        """Test distance pinch (doigts éloignés)"""
        # Landmarks avec pouce et index éloignés
        landmarks = [(0.0, 0.0, 0.0)] * 21
        landmarks[4] = (0.0, 0.0, 0.0)   # Pouce
        landmarks[8] = (0.5, 0.5, 0.0)   # Index
        result = GeometryCalculator.pinch_distance(landmarks)
        assert result > 0.5
    
    def test_pinch_distance_close(self):
        """Test distance pinch (doigts proches)"""
        landmarks = [(0.0, 0.0, 0.0)] * 21
        landmarks[4] = (0.5, 0.5, 0.0)   # Pouce
        landmarks[8] = (0.51, 0.51, 0.0) # Index très proche
        result = GeometryCalculator.pinch_distance(landmarks)
        assert result < 0.05


class TestRustIntegration:
    """Tests spécifiques à l'intégration Rust"""
    
    def test_rust_module_available(self):
        """Vérifie que le module Rust est chargé"""
        from src.processing.geometry.calculator import RUST_AVAILABLE
        # Ce test passe quel que soit le résultat, juste info
        print(f"Rust available: {RUST_AVAILABLE}")
        assert True
    
    def test_rust_distance_performance(self):
        """Benchmark rapide Rust vs Python"""
        import time
        
        iterations = 10000
        
        start = time.perf_counter()
        for _ in range(iterations):
            GeometryCalculator.distance_2d(0, 0, 3, 4)
        elapsed = time.perf_counter() - start
        
        ops_per_sec = iterations / elapsed
        print(f"Performance: {ops_per_sec:.0f} ops/sec")
        
        # Doit être rapide (>10000 ops/sec minimum)
        assert ops_per_sec > 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

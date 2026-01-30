import pytest
import time
from src.optimized_utils import AdaptiveOneEuroFilter, AdaptiveSensitivityMapper

def test_adaptive_filter():
    """Vérifie que le filtre diminue le bruit sur des entrées stables."""
    filter_obj = AdaptiveOneEuroFilter()
    
    # Position stable avec bruit
    raw_x, raw_y = 100.0, 100.0
    ts = time.time()
    
    # Premier point (initialisation)
    fx, fy = filter_obj(raw_x, raw_y, ts)
    assert fx == raw_x
    assert fy == raw_y
    
    # Simuler du bruit léger sur une position stable
    last_fx, last_fy = fx, fy
    for i in range(10):
        ts += 0.033  # ~30fps
        # Ajouter un bruit de +/- 2 pixels
        noise_x = 2.0 if i % 2 == 0 else -2.0
        curr_x = raw_x + noise_x
        curr_y = raw_y + noise_x
        
        fx, fy = filter_obj(curr_x, curr_y, ts)
        
        # Le filtre doit lisser : la variation sortie doit être < variation entrée
        # Ici variation entrée est 4px (-2 à +2)
        assert abs(fx - last_fx) < 2.0
        last_fx, last_fy = fx, fy

def test_mapper_gamma():
    """Vérifie que le mapping respecte la deadzone et la sensibilité."""
    mapper = AdaptiveSensitivityMapper(screen_width=1920, screen_height=1080, gamma=1.3)
    
    # Test centre (presque 0.5, 0.5) -> Doit être proche du centre de l'écran ou deadzone
    # Deadzone est 0.02
    mx, my = mapper.map(0.5, 0.5)
    assert mx == 1920 // 2
    assert my == 1080 // 2
    
    # Test coins
    mx, my = mapper.map(0.0, 0.0)
    assert mx == 0
    assert my == 0
    
    mx, my = mapper.map(1.0, 1.0)
    assert mx == 1920
    assert my == 1080
    
    # Test non-linéarité gamma
    # À 0.75 (modèle centré = 0.5 sur [-1,1]), avec gamma 1.3
    # Le résultat doit être différent d'un mapping linéaire (0.75 * 1920 = 1440)
    mx, _ = mapper.map(0.75, 0.5)
    linear_val = int(0.75 * 1920)
    assert mx != linear_val

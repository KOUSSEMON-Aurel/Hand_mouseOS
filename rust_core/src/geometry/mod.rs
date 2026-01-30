//! Calculs géométriques optimisés pour la détection de gestes
//! 
//! Ces fonctions sont appelées ~30 fois par seconde et bénéficient
//! d'une implémentation Rust pour des gains de 5-30x vs Python.

use pyo3::prelude::*;

/// Distance euclidienne 2D
#[pyfunction]
pub fn distance_2d(x1: f32, y1: f32, x2: f32, y2: f32) -> f32 {
    let dx = x2 - x1;
    let dy = y2 - y1;
    (dx * dx + dy * dy).sqrt()
}

/// Distance euclidienne 3D
#[pyfunction]
pub fn distance_3d(x1: f32, y1: f32, z1: f32, x2: f32, y2: f32, z2: f32) -> f32 {
    let dx = x2 - x1;
    let dy = y2 - y1;
    let dz = z2 - z1;
    (dx * dx + dy * dy + dz * dz).sqrt()
}

/// Calcul d'angle entre trois points (en degrés)
/// Retourne l'angle au point central p2
#[pyfunction]
pub fn angle_between_points(
    x1: f32, y1: f32,
    x2: f32, y2: f32,
    x3: f32, y3: f32
) -> f32 {
    let v1x = x1 - x2;
    let v1y = y1 - y2;
    let v2x = x3 - x2;
    let v2y = y3 - y2;
    
    let dot = v1x * v2x + v1y * v2y;
    let mag1 = (v1x * v1x + v1y * v1y).sqrt();
    let mag2 = (v2x * v2x + v2y * v2y).sqrt();
    
    if mag1 < 1e-6 || mag2 < 1e-6 {
        return 0.0;
    }
    
    let cos_angle = (dot / (mag1 * mag2)).clamp(-1.0, 1.0);
    cos_angle.acos().to_degrees()
}

/// Détecte quels doigts sont étendus
/// Retourne un vecteur [thumb, index, middle, ring, pinky] avec 1=étendu, 0=plié
#[pyfunction]
pub fn fingers_extended(landmarks: Vec<(f32, f32, f32)>) -> Vec<u8> {
    if landmarks.len() < 21 {
        return vec![0, 0, 0, 0, 0];
    }
    
    // Indices MediaPipe
    const TIPS: [usize; 5] = [4, 8, 12, 16, 20];
    const PIPS: [usize; 5] = [3, 6, 10, 14, 18];
    const MCPS: [usize; 5] = [2, 5, 9, 13, 17];
    
    let mut result = Vec::with_capacity(5);
    
    // Pouce: comparaison X (gauche/droite selon main)
    // Simplifié: tip.x < pip.x (main droite)
    let thumb_extended = landmarks[TIPS[0]].0 < landmarks[PIPS[0]].0;
    result.push(if thumb_extended { 1 } else { 0 });
    
    // Autres doigts: tip.y < pip.y (plus haut = étendu)
    for i in 1..5 {
        let tip_y = landmarks[TIPS[i]].1;
        let pip_y = landmarks[PIPS[i]].1;
        result.push(if tip_y < pip_y { 1 } else { 0 });
    }
    
    result
}

/// Calcule le centre de la paume
#[pyfunction]
pub fn palm_center(landmarks: Vec<(f32, f32, f32)>) -> (f32, f32, f32) {
    if landmarks.len() < 21 {
        return (0.0, 0.0, 0.0);
    }
    
    // Moyenne des points 0, 5, 9, 13, 17 (base de la paume)
    const PALM_INDICES: [usize; 5] = [0, 5, 9, 13, 17];
    
    let mut sum_x = 0.0;
    let mut sum_y = 0.0;
    let mut sum_z = 0.0;
    
    for &idx in &PALM_INDICES {
        sum_x += landmarks[idx].0;
        sum_y += landmarks[idx].1;
        sum_z += landmarks[idx].2;
    }
    
    (sum_x / 5.0, sum_y / 5.0, sum_z / 5.0)
}

/// Calcul batch de distances (optimisé SIMD-like)
#[pyfunction]
pub fn batch_distances(points: Vec<(f32, f32)>) -> Vec<f32> {
    points.windows(2)
        .map(|w| distance_2d(w[0].0, w[0].1, w[1].0, w[1].1))
        .collect()
}

/// Distance pinch (pouce-index)
#[pyfunction]
pub fn pinch_distance(landmarks: Vec<(f32, f32, f32)>) -> f32 {
    if landmarks.len() < 21 {
        return 1.0;
    }
    
    let thumb_tip = landmarks[4];
    let index_tip = landmarks[8];
    
    distance_3d(
        thumb_tip.0, thumb_tip.1, thumb_tip.2,
        index_tip.0, index_tip.1, index_tip.2
    )
}
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_distance_2d() {
        assert_eq!(distance_2d(0.0, 0.0, 3.0, 4.0), 5.0);
    }

    #[test]
    fn test_angle_between_points() {
        // Angle droit (90 degrés)
        let angle = angle_between_points(1.0, 0.0, 0.0, 0.0, 0.0, 1.0);
        assert!((angle - 90.0).abs() < 1e-6);
        
        // Angle plat (180 degrés)
        let angle = angle_between_points(1.0, 0.0, 0.0, 0.0, -1.0, 0.0);
        assert!((angle - 180.0).abs() < 1e-6);
    }

    #[test]
    fn test_fingers_extended() {
        let mut landmarks = vec![(0.0, 0.0, 0.0); 21];
        
        // Simuler index étendu (8.y < 6.y)
        landmarks[8].1 = 0.5;
        landmarks[6].1 = 0.7;
        
        // Simuler majeur plié (12.y > 10.y)
        landmarks[12].1 = 0.8;
        landmarks[10].1 = 0.6;
        
        let result = fingers_extended(landmarks);
        assert_eq!(result[1], 1, "Index should be extended");
        assert_eq!(result[2], 0, "Middle should be folded");
    }
}

//! rust_core - Extensions Rust haute performance pour Hand Mouse OS
//!
//! Ce crate fournit des fonctions optimisées pour:
//! - Calculs géométriques (distances, angles)
//! - Filtres de lissage (One-Euro)
//! - Détection de doigts étendus
//!
//! Gains de performance: 5-30x vs Python pur

use pyo3::prelude::*;

mod geometry;
mod filters;

use geometry::{
    distance_2d, distance_3d, angle_between_points,
    fingers_extended, palm_center, batch_distances, pinch_distance
};
use filters::{OneEuroFilter, OneEuroFilter2D};

/// Module Python rust_core
#[pymodule]
fn rust_core(_py: Python, m: &PyModule) -> PyResult<()> {
    // Géométrie
    m.add_function(wrap_pyfunction!(distance_2d, m)?)?;
    m.add_function(wrap_pyfunction!(distance_3d, m)?)?;
    m.add_function(wrap_pyfunction!(angle_between_points, m)?)?;
    m.add_function(wrap_pyfunction!(fingers_extended, m)?)?;
    m.add_function(wrap_pyfunction!(palm_center, m)?)?;
    m.add_function(wrap_pyfunction!(batch_distances, m)?)?;
    m.add_function(wrap_pyfunction!(pinch_distance, m)?)?;
    
    // Filtres
    m.add_class::<OneEuroFilter>()?;
    m.add_class::<OneEuroFilter2D>()?;
    
    Ok(())
}

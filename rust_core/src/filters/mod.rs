//! Filtres de lissage optimisés
//!
//! Implémentation Rust du filtre One-Euro pour un lissage
//! ultra-performant du curseur souris.

pub mod simd_filter;

use pyo3::prelude::*;
use std::f32::consts::PI;

/// Filtre One-Euro pour le lissage du curseur
/// 
/// Adaptatif: faible bruit au repos, réactif en mouvement
#[pyclass]
pub struct OneEuroFilter {
    min_cutoff: f32,
    beta: f32,
    d_cutoff: f32,
    x_prev: Option<f32>,
    dx_prev: f32,
    t_prev: Option<f32>,
}

#[pymethods]
impl OneEuroFilter {
    #[new]
    pub fn new(min_cutoff: f32, beta: f32, d_cutoff: f32) -> Self {
        Self {
            min_cutoff,
            beta,
            d_cutoff,
            x_prev: None,
            dx_prev: 0.0,
            t_prev: None,
        }
    }
    
    /// Filtre une valeur
    pub fn filter(&mut self, x: f32, t: f32) -> f32 {
        if self.x_prev.is_none() {
            self.x_prev = Some(x);
            self.t_prev = Some(t);
            return x;
        }
        
        let dt = (t - self.t_prev.unwrap()).max(1e-6);
        let dx = (x - self.x_prev.unwrap()) / dt;
        
        // Filtre la dérivée
        let dx_hat = self.exponential_smoothing(
            dx,
            self.dx_prev,
            self.alpha(dt, self.d_cutoff)
        );
        
        // Cutoff adaptatif
        let cutoff = self.min_cutoff + self.beta * dx_hat.abs();
        
        // Filtre la position
        let x_hat = self.exponential_smoothing(
            x,
            self.x_prev.unwrap(),
            self.alpha(dt, cutoff)
        );
        
        self.x_prev = Some(x_hat);
        self.dx_prev = dx_hat;
        self.t_prev = Some(t);
        
        x_hat
    }
    
    /// Reset le filtre
    pub fn reset(&mut self) {
        self.x_prev = None;
        self.dx_prev = 0.0;
        self.t_prev = None;
    }
}

impl OneEuroFilter {
    fn alpha(&self, dt: f32, cutoff: f32) -> f32 {
        let tau = 1.0 / (2.0 * PI * cutoff);
        1.0 / (1.0 + tau / dt)
    }
    
    fn exponential_smoothing(&self, x: f32, x_prev: f32, alpha: f32) -> f32 {
        alpha * x + (1.0 - alpha) * x_prev
    }
}

/// Filtre 2D combinant deux filtres One-Euro
#[pyclass]
pub struct OneEuroFilter2D {
    filter_x: OneEuroFilter,
    filter_y: OneEuroFilter,
}

#[pymethods]
impl OneEuroFilter2D {
    #[new]
    pub fn new(min_cutoff: f32, beta: f32, d_cutoff: f32) -> Self {
        Self {
            filter_x: OneEuroFilter::new(min_cutoff, beta, d_cutoff),
            filter_y: OneEuroFilter::new(min_cutoff, beta, d_cutoff),
        }
    }
    
    /// Filtre une position 2D
    pub fn filter(&mut self, x: f32, y: f32, t: f32) -> (f32, f32) {
        (
            self.filter_x.filter(x, t),
            self.filter_y.filter(y, t)
        )
    }
    
    /// Reset les filtres
    pub fn reset(&mut self) {
        self.filter_x.reset();
        self.filter_y.reset();
    }
}

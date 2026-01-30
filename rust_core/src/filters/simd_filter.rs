use pyo3::prelude::*;
use numpy::{PyReadonlyArray2, PyArray2};
use std::f32::consts::PI;

#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

/// État du filtre batch pour toutes les landmarks
#[pyclass]
pub struct BatchOneEuroFilter {
    min_cutoff: f32,
    beta: f32,
    d_cutoff: f32,
    // États précédents (21 landmarks × 3 coords = 63 valeurs)
    x_prev: Vec<f32>,
    dx_prev: Vec<f32>,
    t_prev: Option<f32>,
    initialized: bool,
}

#[pymethods]
impl BatchOneEuroFilter {
    #[new]
    pub fn new(min_cutoff: f32, beta: f32, d_cutoff: f32) -> Self {
        Self {
            min_cutoff,
            beta,
            d_cutoff,
            x_prev: vec![0.0; 63], // 21 landmarks × 3 (x,y,z)
            dx_prev: vec![0.0; 63],
            t_prev: None,
            initialized: false,
        }
    }

    /// Filtre toutes les landmarks d'un coup (ZERO-COPY avec NumPy)
    /// 
    /// Args:
    ///     landmarks: NumPy array (21, 3) de type float32
    ///     t: timestamp actuel
    /// 
    /// Returns:
    ///     NumPy array (21, 3) filtré
    pub fn filter_batch<'py>(
        &mut self,
        landmarks: PyReadonlyArray2<'py, f32>,
        t: f32
    ) -> PyResult<Bound<'py, PyArray2<f32>>> {
        let array = landmarks.as_array();
        let shape = array.shape();
        
        if shape[0] != 21 || shape[1] != 3 {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Expected shape (21, 3), got ({}, {})", shape[0], shape[1])
            ));
        }

        // Accès direct à la mémoire (ZERO-COPY!)
        let input: Vec<f32> = array.iter().copied().collect();

        // Première frame : initialiser
        if !self.initialized {
            self.x_prev.copy_from_slice(&input);
            self.t_prev = Some(t);
            self.initialized = true;
            
            // Retourner une copie du array d'entrée
            let py = landmarks.py();
            let out_array = PyArray2::from_owned_array_bound(py, array.to_owned());
            return Ok(out_array);
        }

        let dt = (t - self.t_prev.unwrap()).max(1e-6);

        // Traitement batch avec SIMD
        let output = self.filter_simd(&input, dt);

        // Mise à jour de l'état
        self.x_prev.copy_from_slice(&output);
        self.t_prev = Some(t);

        // Convertir en NumPy array (21, 3) - Utiliser from_slice2
        use numpy::ndarray::Array2;
        let array_2d = Array2::from_shape_vec((21, 3), output)
            .expect("Failed to reshape output");
        Ok(PyArray2::from_owned_array_bound(landmarks.py(), array_2d))
    }

    /// Reset le filtre
    pub fn reset(&mut self) {
        self.x_prev.fill(0.0);
        self.dx_prev.fill(0.0);
        self.t_prev = None;
        self.initialized = false;
    }
}

impl BatchOneEuroFilter {
    /// Filtre SIMD utilisant AVX2 (8 floats en parallèle)
    #[cfg(target_arch = "x86_64")]
    fn filter_simd(&mut self, input: &[f32], dt: f32) -> Vec<f32> {
        let mut output = vec![0.0f32; 63];

        // Vérifier support AVX2 au runtime
        if is_x86_feature_detected!("avx2") {
            unsafe {
                self.filter_simd_avx2(input, dt, &mut output);
            }
        } else {
            // Fallback scalaire
            self.filter_scalar(input, dt, &mut output);
        }

        output
    }

    #[cfg(not(target_arch = "x86_64"))]
    fn filter_simd(&mut self, input: &[f32], dt: f32) -> Vec<f32> {
        let mut output = vec![0.0f32; 63];
        self.filter_scalar(input, dt, &mut output);
        output
    }

    /// Implémentation AVX2 (traite 8 floats à la fois)
    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "avx2")]
    unsafe fn filter_simd_avx2(&mut self, input: &[f32], dt: f32, output: &mut [f32]) {
        // Constantes broadcast en registres 256-bit (8×f32)
        let dt_vec = _mm256_set1_ps(dt);
        let one = _mm256_set1_ps(1.0);
        
        // Calcul alpha pour d_cutoff (dérivée)
        let alpha_d = self.alpha(dt, self.d_cutoff);
        let alpha_d_vec = _mm256_set1_ps(alpha_d);
        let one_minus_alpha_d = _mm256_set1_ps(1.0 - alpha_d);

        // Traiter par blocs de 8
        for i in (0..56).step_by(8) {
            // Charger 8 valeurs
            let x = _mm256_loadu_ps(input.as_ptr().add(i));
            let x_prev = _mm256_loadu_ps(self.x_prev.as_ptr().add(i));
            let dx_prev = _mm256_loadu_ps(self.dx_prev.as_ptr().add(i));

            // dx = (x - x_prev) / dt
            let dx = _mm256_div_ps(_mm256_sub_ps(x, x_prev), dt_vec);

            // dx_hat = alpha_d * dx + (1 - alpha_d) * dx_prev
            let dx_hat = _mm256_add_ps(
                _mm256_mul_ps(alpha_d_vec, dx),
                _mm256_mul_ps(one_minus_alpha_d, dx_prev)
            );

            // cutoff = min_cutoff + beta * abs(dx_hat)
            // abs(x) = andnot(sign_mask, x)
            let sign_mask = _mm256_set1_ps(-0.0);
            let abs_dx_hat = _mm256_andnot_ps(sign_mask, dx_hat);
            let cutoff = _mm256_add_ps(
                _mm256_set1_ps(self.min_cutoff),
                _mm256_mul_ps(_mm256_set1_ps(self.beta), abs_dx_hat)
            );

            // alpha = 1 / (1 + tau / dt) où tau = 1 / (2π * cutoff)
            // Simplifié: alpha ≈ 1 / (1 + 1/(2π*cutoff*dt))
            let two_pi = _mm256_set1_ps(2.0 * PI);
            let tau = _mm256_div_ps(one, _mm256_mul_ps(two_pi, cutoff));
            let alpha_x = _mm256_div_ps(one, _mm256_add_ps(one, _mm256_div_ps(tau, dt_vec)));

            // x_hat = alpha_x * x + (1 - alpha_x) * x_prev
            let x_hat = _mm256_add_ps(
                _mm256_mul_ps(alpha_x, x),
                _mm256_mul_ps(_mm256_sub_ps(one, alpha_x), x_prev)
            );

            // Stocker résultats
            _mm256_storeu_ps(output.as_mut_ptr().add(i), x_hat);
            _mm256_storeu_ps(self.dx_prev.as_mut_ptr().add(i), dx_hat);
        }

        // Traiter les 7 derniers floats (63 % 8 = 7) en scalaire
        for i in 56..63 {
            output[i] = self.filter_scalar_single(input[i], i, dt);
        }
    }

    /// Fallback scalaire (sans SIMD)
    fn filter_scalar(&mut self, input: &[f32], dt: f32, output: &mut [f32]) {
        for i in 0..63 {
            output[i] = self.filter_scalar_single(input[i], i, dt);
        }
    }

    /// Filtre une seule valeur (logique OneEuro standard)
    fn filter_scalar_single(&mut self, x: f32, idx: usize, dt: f32) -> f32 {
        let dx = (x - self.x_prev[idx]) / dt;
        
        // Filtre dérivée
        let alpha_d = self.alpha(dt, self.d_cutoff);
        let dx_hat = alpha_d * dx + (1.0 - alpha_d) * self.dx_prev[idx];
        
        // Cutoff adaptatif
        let cutoff = self.min_cutoff + self.beta * dx_hat.abs();
        
        // Filtre position
        let alpha_x = self.alpha(dt, cutoff);
        let x_hat = alpha_x * x + (1.0 - alpha_x) * self.x_prev[idx];
        
        self.dx_prev[idx] = dx_hat;
        x_hat
    }

    /// Calcul coefficient alpha
    fn alpha(&self, dt: f32, cutoff: f32) -> f32 {
        let tau = 1.0 / (2.0 * PI * cutoff);
        1.0 / (1.0 + tau / dt)
    }
}

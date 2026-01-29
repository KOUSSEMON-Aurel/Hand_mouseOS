use pyo3::prelude::*;
use std::f32::consts::PI;

#[pyclass]
#[derive(Clone)]
struct OneEuroFilter {
    min_cutoff: f32,
    beta: f32,
    d_cutoff: f32,
    x_prev: f32,
    dx_prev: f32,
    t_prev: f32,
}

#[pymethods]
impl OneEuroFilter {
    #[new]
    fn new(t0: f32, x0: f32, dx0: Option<f32>, min_cutoff: Option<f32>, beta: Option<f32>, d_cutoff: Option<f32>) -> Self {
        Self {
            min_cutoff: min_cutoff.unwrap_or(1.0),
            beta: beta.unwrap_or(0.0),
            d_cutoff: d_cutoff.unwrap_or(1.0),
            x_prev: x0,
            dx_prev: dx0.unwrap_or(0.0),
            t_prev: t0,
        }
    }

    fn smoothing_factor(&self, t_e: f32, cutoff: f32) -> f32 {
        let r = 2.0 * PI * cutoff * t_e;
        r / (r + 1.0)
    }

    fn exponential_smoothing(&self, a: f32, x: f32, x_prev: f32) -> f32 {
        a * x + (1.0 - a) * x_prev
    }

    fn __call__(&mut self, t: f32, x: f32) -> f32 {
        let t_e = t - self.t_prev;
        if t_e <= 0.0 {
            return self.x_prev;
        }

        // The filtered derivative of the signal.
        let a_d = self.smoothing_factor(t_e, self.d_cutoff);
        let dx = (x - self.x_prev) / t_e;
        let dx_hat = self.exponential_smoothing(a_d, dx, self.dx_prev);

        // The filtered signal.
        let cutoff = self.min_cutoff + self.beta * dx_hat.abs();
        let a = self.smoothing_factor(t_e, cutoff);
        let x_hat = self.exponential_smoothing(a, x, self.x_prev);

        // Update history
        self.x_prev = x_hat;
        self.dx_prev = dx_hat;
        self.t_prev = t;

        x_hat
    }
}

#[pyclass]
struct RustHybridFilter {
    one_euro_x: OneEuroFilter,
    one_euro_y: OneEuroFilter,
    state: [f32; 4], // x, y, vx, vy
    last_timestamp: f32,
    last_pos: Option<(f32, f32)>,
    dead_zone: f32,
}

#[pymethods]
impl RustHybridFilter {
    #[new]
    fn new() -> Self {
        Self {
            one_euro_x: OneEuroFilter::new(0.0, 0.0, None, Some(1.0), Some(0.007), None),
            one_euro_y: OneEuroFilter::new(0.0, 0.0, None, Some(1.0), Some(0.007), None),
            state: [0.0; 4],
            last_timestamp: 0.0,
            last_pos: None,
            dead_zone: 2.0,
        }
    }

    fn process(&mut self, raw_x: f32, raw_y: f32, timestamp_sec: f32) -> (f32, f32) {
        if self.last_pos.is_none() {
            self.last_pos = Some((raw_x, raw_y));
            self.state = [raw_x, raw_y, 0.0, 0.0];
            self.one_euro_x.t_prev = timestamp_sec;
            self.one_euro_x.x_prev = raw_x;
            self.one_euro_y.t_prev = timestamp_sec;
            self.one_euro_y.x_prev = raw_y;
            self.last_timestamp = timestamp_sec;
            return (raw_x, raw_y);
        }

        let dt = (timestamp_sec - self.last_timestamp).max(0.001);
        self.last_timestamp = timestamp_sec;

        // Kalman Prediction
        self.state[0] += self.state[2] * dt;
        self.state[1] += self.state[3] * dt;
        
        // Simple Alpha-Beta filter logic (matches simplified Kalman)
        let alpha = 0.5;
        let beta = 0.1;
        
        let res_x = raw_x - self.state[0];
        let res_y = raw_y - self.state[1];
        
        self.state[0] += alpha * res_x;
        self.state[1] += alpha * res_y;
        self.state[2] += (beta / dt) * res_x;
        self.state[3] += (beta / dt) * res_y;

        let pred_x = self.state[0];
        let pred_y = self.state[1];
        let velocity = (self.state[2].powi(2) + self.state[3].powi(2)).sqrt();

        let (smooth_x, smooth_y) = if velocity > 500.0 {
            (pred_x, pred_y)
        } else {
            (self.one_euro_x.__call__(timestamp_sec, raw_x), self.one_euro_y.__call__(timestamp_sec, raw_y))
        };

        let last = self.last_pos.unwrap();
        let dist = ((smooth_x - last.0).powi(2) + (smooth_y - last.1).powi(2)).sqrt();
        
        let current_dead_zone = if velocity < 10.0 { 5.0 } else { self.dead_zone };
        
        if dist < current_dead_zone {
            return last;
        }

        self.last_pos = Some((smooth_x, smooth_y));
        (smooth_x, smooth_y)
    }
}

#[pymodule]
fn hand_mouse_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OneEuroFilter>()?;
    m.add_class::<RustHybridFilter>()?;
    Ok(())
}

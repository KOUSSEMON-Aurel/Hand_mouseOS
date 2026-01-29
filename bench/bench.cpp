#include "bench.h"

// C wrapper for shared library
extern "C" {
float c_distance_3d(float x1, float y1, float z1, float x2, float y2,
                    float z2) {
  Point3D p1 = {x1, y1, z1};
  Point3D p2 = {x2, y2, z2};
  return distance_3d(p1, p2);
}

void c_batch_distances(const Point3D *p1s, const Point3D *p2s, float *results,
                       int n) {
  batch_distances(p1s, p2s, results, n);
}
}

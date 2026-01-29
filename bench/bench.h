#ifndef BENCH_H
#define BENCH_H

#include <math.h>

typedef struct {
    float x, y, z;
} Point3D;

float distance_3d(Point3D p1, Point3D p2) {
    float dx = p1.x - p2.x;
    float dy = p1.y - p2.y;
    float dz = p1.z - p2.z;
    return sqrtf(dx*dx + dy*dy + dz*dz);
}

void batch_distances(const Point3D* p1s, const Point3D* p2s, float* results, int n) {
    for (int i = 0; i < n; i++) {
        results[i] = distance_3d(p1s[i], p2s[i]);
    }
}

#endif

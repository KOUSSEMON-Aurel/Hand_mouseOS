#include "hand_utils.h"
#include <math.h>

float calculate_distance(Point3D a, Point3D b) {
  float dx = b.x - a.x;
  float dy = b.y - a.y;
  float dz = b.z - a.z;
  return sqrtf(dx * dx + dy * dy + dz * dz);
}

float calculate_angle(Point3D a, Point3D b, Point3D c) {
  Point3D ba = {a.x - b.x, a.y - b.y, a.z - b.z};
  Point3D bc = {c.x - b.x, c.y - b.y, c.z - b.z};

  float dot = dot_product(ba, bc);
  float magBA = sqrtf(ba.x * ba.x + ba.y * ba.y + ba.z * ba.z);
  float magBC = sqrtf(bc.x * bc.x + bc.y * bc.y + bc.z * bc.z);

  return acosf(dot / (magBA * magBC)) * 180.0f / M_PI;
}

Point3D normalize_vector(Point3D v) {
  float mag = sqrtf(v.x * v.x + v.y * v.y + v.z * v.z);
  if (mag == 0)
    return v;
  return (Point3D){v.x / mag, v.y / mag, v.z / mag};
}

float dot_product(Point3D a, Point3D b) {
  return a.x * b.x + a.y * b.y + a.z * b.z;
}

Point3D cross_product(Point3D a, Point3D b) {
  return (Point3D){a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z,
                   a.x * b.y - a.y * b.x};
}

int is_pinch_gesture(Point3D thumb, Point3D index) {
  return calculate_distance(thumb, index) < 0.05f;
}

int is_fist_gesture(Point3D *fingers, int count) {
  for (int i = 0; i < count; i++) {
    if (fingers[i].y < 0.5f)
      return 0;
  }
  return 1;
}

int is_palm_open(Point3D *fingers, int count) {
  for (int i = 0; i < count; i++) {
    if (fingers[i].y > 0.5f)
      return 0;
  }
  return 1;
}

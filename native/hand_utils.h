#ifndef HAND_UTILS_H
#define HAND_UTILS_H

/**
 * Utilitaires de calcul vectoriel pour les landmarks
 * Ce fichier permet de démontrer l'usage du C dans le projet.
 */

typedef struct {
  float x;
  float y;
  float z;
} Point3D;

float calculate_distance(Point3D a, Point3D b);
float calculate_angle(Point3D a, Point3D b, Point3D c);
Point3D normalize_vector(Point3D v);
float dot_product(Point3D a, Point3D b);
Point3D cross_product(Point3D a, Point3D b);

// Fonctions de calcul de gestes
int is_pinch_gesture(Point3D thumb, Point3D index);
int is_fist_gesture(Point3D *fingers, int count);
int is_palm_open(Point3D *fingers, int count);

#endif // HAND_UTILS_H

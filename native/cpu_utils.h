#ifndef CPU_UTILS_H
#define CPU_UTILS_H

/**
 * @brief Récupère la charge CPU actuelle (approximation simple)
 *
 * @return double Valeur entre 0.0 et 100.0
 */
double get_cpu_usage();

/**
 * @brief Récupère la température (si disponible sous Linux)
 *
 * @return float Température en degrés Celsius
 */
float get_cpu_temp();

#endif // CPU_UTILS_H

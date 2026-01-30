#include "cpu_utils.h"
#include <stdio.h>
#include <unistd.h>

/**
 * Implémentation simple lisant /proc/stat pour obtenir l'usage CPU.
 * Utile pour surveiller l'impact du traitement Mediapipe/Rust en temps réel.
 */
double get_cpu_usage() {
  FILE *file = fopen("/proc/stat", "r");
  if (!file)
    return -1.0;

  unsigned long long user, nice, system, idle;
  if (fscanf(file, "cpu %llu %llu %llu %llu", &user, &nice, &system, &idle) !=
      4) {
    fclose(file);
    return -1.0;
  }
  fclose(file);

  static unsigned long long prev_user, prev_nice, prev_system, prev_idle;

  unsigned long long total = (user - prev_user) + (nice - prev_nice) +
                             (system - prev_system) + (idle - prev_idle);
  unsigned long long work =
      (user - prev_user) + (nice - prev_nice) + (system - prev_system);

  double usage = (total > 0) ? ((double)work / total) * 100.0 : 0.0;

  prev_user = user;
  prev_nice = nice;
  prev_system = system;
  prev_idle = idle;

  return usage;
}

float get_cpu_temp() {
  FILE *file = fopen("/sys/class/thermal/thermal_zone0/temp", "r");
  if (!file)
    return -1.0f;

  int temp;
  if (fscanf(file, "%d", &temp) != 1) {
    fclose(file);
    return -1.0f;
  }
  fclose(file);

  return (float)temp / 1000.0f;
}

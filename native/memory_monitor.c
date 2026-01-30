#include "cpu_utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * Module de surveillance mémoire en C
 * Complète cpu_utils.c pour un monitoring système complet
 */

typedef struct {
  unsigned long total;
  unsigned long free;
  unsigned long available;
  unsigned long buffers;
  unsigned long cached;
} MemoryInfo;

MemoryInfo get_memory_info() {
  MemoryInfo info = {0, 0, 0, 0, 0};
  FILE *file = fopen("/proc/meminfo", "r");
  if (!file)
    return info;

  char line[256];
  while (fgets(line, sizeof(line), file)) {
    if (strncmp(line, "MemTotal:", 9) == 0)
      sscanf(line, "MemTotal: %lu", &info.total);
    else if (strncmp(line, "MemFree:", 8) == 0)
      sscanf(line, "MemFree: %lu", &info.free);
    else if (strncmp(line, "MemAvailable:", 13) == 0)
      sscanf(line, "MemAvailable: %lu", &info.available);
    else if (strncmp(line, "Buffers:", 8) == 0)
      sscanf(line, "Buffers: %lu", &info.buffers);
    else if (strncmp(line, "Cached:", 7) == 0)
      sscanf(line, "Cached: %lu", &info.cached);
  }

  fclose(file);
  return info;
}

float get_memory_usage_percent() {
  MemoryInfo info = get_memory_info();
  if (info.total == 0)
    return -1.0f;

  unsigned long used = info.total - info.available;
  return (float)used / info.total * 100.0f;
}

unsigned long get_total_memory_mb() {
  MemoryInfo info = get_memory_info();
  return info.total / 1024;
}

unsigned long get_available_memory_mb() {
  MemoryInfo info = get_memory_info();
  return info.available / 1024;
}

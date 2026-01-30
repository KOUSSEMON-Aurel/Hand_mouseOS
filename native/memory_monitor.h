#ifndef MEMORY_MONITOR_H
#define MEMORY_MONITOR_H

typedef struct {
  unsigned long total;
  unsigned long free;
  unsigned long available;
  unsigned long buffers;
  unsigned long cached;
} MemoryInfo;

MemoryInfo get_memory_info();
float get_memory_usage_percent();
unsigned long get_total_memory_mb();
unsigned long get_available_memory_mb();

#endif

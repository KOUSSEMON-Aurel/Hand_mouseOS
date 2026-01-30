#include "cpu_utils.h"
#include <stdio.h>
#include <unistd.h>

/**
 * ============================================================================
 * MODULE DE SURVEILLANCE CPU NATIF - HandMouseOS
 * ============================================================================
 *
 * Ce module est implémenté en langage C pour une efficacité maximale.
 * Contrairement aux implémentations Python, le C nous permet de minimiser
 * l'empreinte mémoire et d'éviter le surcoût de l'interpréteur lors de la
 * lecture des statistiques système.
 *
 * ARCHITECTURE :
 * - Lecture directe de /proc/stat (Kernel Stats)
 * - Calcul différentiel de la charge processeur
 * - Accès aux zones thermiques via /sys/class/thermal
 *
 * OPTIMISATIONS :
 * - Utilisation de types long long pour éviter les overflows sur les systèmes
 *   fonctionnant depuis longtemps (uptime élevé).
 * - Static variables pour le stockage de l'état précédent.
 *
 * ----------------------------------------------------------------------------
 * LICENCE : MIT
 * AUTEUR : Aurel
 * ----------------------------------------------------------------------------
 *
 * DOCUMENTATION DÉTAILLÉE DES CHAMPS /proc/stat :
 * - user: temps passé en mode utilisateur normal
 * - nice: temps passé en mode utilisateur avec basse priorité
 * - system: temps passé en mode noyau
 * - idle: temps passé en attente (rien à faire)
 * - iowait: temps passé à attendre des entrées/sorties
 * - irq: temps passé à traiter les interruptions matérielles
 * - softirq: temps passé à traiter les interruptions logicielles
 *
 * ============================================================================
 */

double get_cpu_usage() {
  FILE *file = fopen("/proc/stat", "r");
  if (!file)
    return -1.0;

  unsigned long long user, nice, system, idle, iowait, irq, softirq, steal,
      guest, guest_nice;
  // On lit tous les champs pour être le plus précis possible
  if (fscanf(file, "cpu %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu",
             &user, &nice, &system, &idle, &iowait, &irq, &softirq, &steal,
             &guest, &guest_nice) < 7) {
    fclose(file);
    return -1.0;
  }
  fclose(file);

  static unsigned long long p_user, p_nice, p_system, p_idle, p_iowait, p_irq,
      p_softirq, p_steal, p_guest, p_guest_nice;

  unsigned long long PrevIdle = p_idle + p_iowait;
  unsigned long long Idle = idle + iowait;

  unsigned long long PrevNonIdle =
      p_user + p_nice + p_system + p_irq + p_softirq + p_steal;
  unsigned long long NonIdle = user + nice + system + irq + softirq + steal;

  unsigned long long PrevTotal = PrevIdle + PrevNonIdle;
  unsigned long long Total = Idle + NonIdle;

  unsigned long long totald = Total - PrevTotal;
  unsigned long long idled = Idle - PrevIdle;

  double usage =
      (totald > 0) ? ((double)(totald - idled) / totald) * 100.0 : 0.0;

  p_user = user;
  p_nice = nice;
  p_system = system;
  p_idle = idle;
  p_iowait = iowait;
  p_irq = irq;
  p_softirq = softirq;
  p_steal = steal;
  p_guest = guest;
  p_guest_nice = guest_nice;

  return usage;
}

/**
 * @brief Récupère la température du CPU
 * Lit le premier capteur thermique disponible sur le système.
 */
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

/* This software is distributed under the following license:
 * http://host-sflow.sourceforge.net/license.html
 */

#if defined(__cplusplus)
extern "C" {
#endif

#include "hsflowd.h"
#include <kstat.h>
#include <dirent.h>
#include <procfs.h>
#include <sys/sysinfo.h> 

  extern int debug;

  /*_________________------------------------------__________________
    _________________     runningProcesses_prstat  __________________
    -----------------______________________________------------------
  */
  int read_prstat_line(void *magic, char *line) {
    if(line) {
      int total=0;
      // This might break in non-english locales
      if(sscanf(line, "Total: %d", &total) == 1) {
	*(uint32_t *)magic = (uint32_t)total;
      }
    }
    return YES; // keep going
  }

  int runningProcesses_prstat(void) {
#define MAX_PS_LINELEN 256
    char line[MAX_PS_LINELEN];
    char *ps_cmd[] = { "/usr/bin/prstat", "-n1", "0", "1", NULL};
    uint32_t proc_run = 0;
    if(myExec(&proc_run, ps_cmd, read_prstat_line, line, MAX_PS_LINELEN)) {
      return (int)proc_run;
    }
    return -1;
  }

  /*_________________---------------------------__________________
    _________________   runningProcesses_proc   __________________
    -----------------___________________________------------------
  */

  int runningProcesses_proc(void) {
#define FILENAME_BUFFER_SIZE 64	
    DIR *procdir;
    char filename_buf[FILENAME_BUFFER_SIZE];
    int fd=0, proc_no;
    struct dirent *direntp;
    psinfo_t psinfo;
    int proc_run = 0;

    if (!(procdir = opendir("/proc"))) {
      return -1;
    }

    strncpy(filename_buf, "/proc/", 6);
    for (proc_no = 0; (direntp = readdir(procdir)); ) {

      if (direntp->d_name[0] == '.') continue;
      
      snprintf(&filename_buf[6], FILENAME_BUFFER_SIZE - 6, "%s/psinfo", direntp->d_name);
      if ((fd = open(filename_buf, O_RDONLY)) < 0) {
	if(debug) myLog(LOG_INFO, "cannot open %s : %s", filename_buf, strerror(errno));
	proc_run = -1;
	break;
      }
      
      if (read(fd, &psinfo, sizeof(psinfo_t)) == sizeof(psinfo_t)) {

	// consult the process state name character
	if(debug > 2) myLog(LOG_INFO, "pr_sname=%c", psinfo.pr_lwp.pr_sname);

	// http://docs.oracle.com/cd/E19253-01/817-6223/gelse/index.html
	// 'S' = Sleeping
	// 'R' = Runnable (but not running right now)
	// 'Z' = Zombie
	// 'T' = sTopped
	// 'I' = Intermediate state
	// 'O' = On processor (actually running right now)

	// To be consistent with the number in /proc/loadavg on Linux,
	// we have to count both 'O's and 'R's here:
	if ('O' == psinfo.pr_lwp.pr_sname
	    || 'R' == psinfo.pr_lwp.pr_sname) {
	  proc_run++;
	}
      }
      close(fd);
    }
    closedir(procdir);
    
    return (int)proc_run;
  }


  /*_________________---------------------------__________________
    _________________     runningProcesses      __________________
    -----------------___________________________------------------
    Try to use the number from /proc if we can because it is more
    correct - giving the number of processes that are really running
    rather than just the number of processes in the process table.
    However be willing to fall back on prstat if it turns
    out that we no longer have permission to read the /proc file.
  */

  int runningProcesses(HSP *sp) {
    int running = 0;

    if(sp->use_prstat == NO) {
      // This may only work properly if root privileges were retained,  otherwise
      // we may be allowed to read just one psinfo file: our own, and sometimes
      // maybe one or two others.
      running = runningProcesses_proc();
      if(running == -1) {
	if(debug) myLog(LOG_INFO, "falling back prstat(1) for count of running processes");
	sp->use_prstat = YES;
      }
    }

    if(sp->use_prstat) {
      // use a less efficient approach that seems to work without root privileges
      running = runningProcesses_prstat();
    }

    return running;
  }

  /*_________________---------------------------__________________
    _________________     readCpuCounters       __________________
    -----------------___________________________------------------
  */
  
  int readCpuCounters(HSP *sp, SFLHost_cpu_counters *cpu) {
    int gotData = NO;

    kstat_ctl_t *kc;
    kstat_t *ksp = NULL;
    kstat_named_t *knp;

    kc = kstat_open();
    if (NULL == kc) {
      myLog(LOG_ERR, "readCpuCounters kstat_open() failed");
    } else {
      ksp = kstat_lookup(kc, "unix", 0, "system_misc");
      if (NULL == ksp) {
	myLog(LOG_ERR, "kstat_loockup error (unix:*:system_misc:*)");
      }
    }

    if (NULL != ksp) {
      if (-1 == kstat_read(kc, ksp, NULL)) {
	myLog(LOG_ERR, "kstat_read error (module: %s, name: %s, class: %s)",
	      ksp->ks_module, ksp->ks_name, ksp->ks_class);
      } else {
	// kstat load-averages are expressed in fixed-point, so we must
	// divide by 256.0 to get to the correct float value.  Thanks
	// to David Johnson for pointing this out.
	// load_one
	knp = kstat_data_lookup(ksp, "avenrun_1min");
	cpu->load_one = ((float)knp->value.ui32) / 256.0;

	// load_five
	knp = kstat_data_lookup(ksp, "avenrun_5min");
	cpu->load_five = ((float)knp->value.ui32) / 256.0;

	// load_fifteen
	knp = kstat_data_lookup(ksp, "avenrun_15min");
	cpu->load_fifteen = ((float)knp->value.ui32) / 256.0;

	// proc_total
	knp = kstat_data_lookup(ksp, "nproc");
	cpu->proc_total = knp->value.ui32;

	// cpu_num
	knp = kstat_data_lookup(ksp, "ncpus");
	cpu->cpu_num = knp->value.ui32;

	// uptime
	knp = kstat_data_lookup(ksp, "boot_time");
	time_t boot = knp->value.ui32;
	time_t uptime = time(NULL) - boot;
	cpu->uptime = uptime;

	gotData = YES;
      }
    }

    ksp = kstat_lookup(kc, "cpu_info", -1, NULL);
    if (NULL == ksp) {
      myLog(LOG_ERR, "kstat_loockup error (cpu_info:*:cpu_info0:*)");
    }

    if (NULL != ksp) {
      if (-1 == kstat_read(kc, ksp, NULL)) {
	myLog(LOG_ERR, "kstat_read error (module: %s, name: %s, class: %s)",
	      ksp->ks_module, ksp->ks_name, ksp->ks_class);
      } else {

	// cpu_speed
	knp = kstat_data_lookup(ksp, "clock_MHz");
	cpu->cpu_speed = (uint32_t)knp->value.i32;

	gotData = YES;
      }
    }

    // running processes
    int running = runningProcesses(sp);
    if(debug) myLog(LOG_INFO, "runningProcesses() returned %d\n", running);
    if(running > 0) {
      cpu->proc_run = running;
      gotData = YES;
    }

    // From Ganglia's libmetrics
#define CPUSTATES	5
#define CPUSTATE_IDLE	0
#define CPUSTATE_USER	1
#define CPUSTATE_KERNEL	2
#define CPUSTATE_IOWAIT	3
#define CPUSTATE_SWAP	4

    cpu_stat_t cpu_stat;
    int cpu_id = sysconf(_SC_NPROCESSORS_ONLN);
    uint64_t cpu_info[CPUSTATES] = { 0 };
    long stathz = sysconf(_SC_CLK_TCK);
    uint64_t interrupts = 0;
    uint64_t contexts = 0;
#ifndef KSNAME_BUFFER_SIZE
#define KSNAME_BUFFER_SIZE 32
#endif

#define STATHZ_TO_MS(t) (((t) * 1000) / stathz)

    char ks_name[KSNAME_BUFFER_SIZE];
    int i, n;
    for (i = 0; cpu_id > 0; i++) {
      n = p_online(i, P_STATUS);
      if (1 == n || (-1 == n && EINVAL == errno)) {
	continue;
      }

      snprintf(ks_name, KSNAME_BUFFER_SIZE, "cpu_stat%d", i);
      cpu_id--;

      ksp = kstat_lookup(kc, "cpu_stat", i, ks_name);
      if (NULL == ksp) {
	myLog(LOG_ERR, "kstat_lookup error (module: cpu_stat, inst: %d, name %s)", i, ks_name);
	continue;
      }

      if (-1 == kstat_read(kc, ksp, &cpu_stat)) {
	myLog(LOG_ERR, "kstat_read error (module: %s, name: %s, class: %s)",
	      ksp->ks_module, ksp->ks_name, ksp->ks_class);
	continue;
      }

      if(debug>1) {
	myLog(LOG_INFO, "adding cpu stats for cpu=%d (idle=%u user=%u wait=%u swap=%u kernel=%u)",
	      cpu_id,
	      cpu_stat.cpu_sysinfo.cpu[CPU_IDLE],
	      cpu_stat.cpu_sysinfo.cpu[CPU_USER],
	      cpu_stat.cpu_sysinfo.wait[W_IO] + cpu_stat.cpu_sysinfo.wait[W_PIO],
	      cpu_stat.cpu_sysinfo.wait[W_SWAP],
	      cpu_stat.cpu_sysinfo.cpu[CPU_KERNEL]);
      }
	      

      cpu_info[CPUSTATE_IDLE] += cpu_stat.cpu_sysinfo.cpu[CPU_IDLE];
      cpu_info[CPUSTATE_USER] += cpu_stat.cpu_sysinfo.cpu[CPU_USER];
      cpu_info[CPUSTATE_IOWAIT] += cpu_stat.cpu_sysinfo.wait[W_IO] + cpu_stat.cpu_sysinfo.wait[W_PIO];
      cpu_info[CPUSTATE_SWAP] += cpu_stat.cpu_sysinfo.wait[W_SWAP];
      cpu_info[CPUSTATE_KERNEL] += cpu_stat.cpu_sysinfo.cpu[CPU_KERNEL];
      interrupts += cpu_stat.cpu_sysinfo.intr + cpu_stat.cpu_sysinfo.trap;
      contexts += cpu_stat.cpu_sysinfo.pswitch;
      gotData = YES;
    }

    // cpu_user
    cpu->cpu_user = (uint32_t)STATHZ_TO_MS(cpu_info[CPUSTATE_USER]);

    // cpu_nice
    SFL_UNDEF_COUNTER(cpu->cpu_nice);

    // cpu_system
    cpu->cpu_system = (uint32_t)STATHZ_TO_MS(cpu_info[CPUSTATE_KERNEL]);

    // cpu_idle
    cpu->cpu_idle = (uint32_t)STATHZ_TO_MS(cpu_info[CPUSTATE_IDLE]);

    // cpu_wio
    cpu->cpu_wio = (uint32_t)STATHZ_TO_MS(cpu_info[CPUSTATE_IOWAIT]);

    // cpu_intr
    SFL_UNDEF_COUNTER(cpu->cpu_intr);

    // cpu_sintr
    SFL_UNDEF_COUNTER(cpu->cpu_sintr);
	
    // interrupts
    cpu->interrupts = interrupts;

    // contexts
    cpu->contexts = contexts;

    if(kc) kstat_close(kc);
    return gotData;
  }

#if defined(__cplusplus)
} /* extern "C" */
#endif


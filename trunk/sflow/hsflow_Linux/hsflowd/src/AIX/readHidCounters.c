/* This software is distributed under the following license:
 * http://host-sflow.sourceforge.net/license.html
 */

#if defined(__cplusplus)
extern "C" {
#endif

#include "sys/utsname.h"
#include "hsflowd.h"
extern int debug;
  /*_________________---------------------------__________________
    _________________     readHidCounters       __________________
    -----------------___________________________------------------
  */
  
  int readHidCounters(HSP *sp, SFLHost_hid_counters *hid, char *hbuf, int hbufLen, char *rbuf, int rbufLen)
  {
    struct utsname uu;
    if(uname(&uu) == -1) {
      myLog(LOG_ERR, "uname() failed: %s", strerror(errno));
      return NO;
    }

    if(debug>1) {
      myLog(LOG_INFO, "utsname.sysname=%s nodename=%s release=%s version=%s machine=%s",
	    uu.sysname,
	    uu.nodename,
	    uu.release,
	    uu.version,
	    uu.machine);
    }

    if(uu.nodename) {
      int len = my_strlen(uu.nodename);
      if(len > hbufLen) len = hbufLen;
      memcpy(hbuf, uu.nodename, len);
      hid->hostname.str = hbuf;
      hid->hostname.len = len;
    }

    // UUID
    memcpy(hid->uuid, sp->uuid, 16);

    // machine_type
    hid->machine_type = SFLMT_unknown;
#ifdef __i386__
    hid->machine_type = SFLMT_x86;
#endif
#ifdef __x86_64__
    hid->machine_type = SFLMT_x86_64;
#endif
#ifdef __ia64__
    hid->machine_type = SFLMT_ia64;
#endif
#ifdef __sparc__
    hid->machine_type = SFLMT_sparc;
#endif
#ifdef __alpha__
    hid->machine_type = SFLMT_alpha;
#endif
#ifdef __powerpc__
    hid->machine_type = SFLMT_powerpc;
#endif
#ifdef __m68k__
    hid->machine_type = SFLMT_68k;
#endif
#ifdef __mips__
    hid->machine_type = SFLMT_mips;
#endif
#ifdef __arm__
    hid->machine_type = SFLMT_arm;
#endif
#ifdef __hppa__
    hid->machine_type = SFLMT_hppa;
#endif
#ifdef __s390__
    hid->machine_type = SFLMT_s390;
#endif

    // os name
    hid->os_name = SFLOS_aix;

    // os release
    if(uu.version && uu.release) {
      snprintf(rbuf, rbufLen, "%s.%s", uu.version, uu.release);
      hid->os_release.str = rbuf;
      hid->os_release.len = my_strlen(rbuf);
    }
    
    return YES;
  }

#if defined(__cplusplus)
} /* extern "C" */
#endif


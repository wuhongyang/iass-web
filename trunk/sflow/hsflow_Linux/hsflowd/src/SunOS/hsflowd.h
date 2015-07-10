/* This software is distributed under the following license:
 * http://host-sflow.sourceforge.net/license.html
 */

#ifndef HSFLOWD_H
#define HSFLOWD_H 1

#if defined(__cplusplus)
extern "C" {
#endif

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <time.h>
#include <errno.h>
#include <netdb.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <syslog.h>
#include <signal.h>
#include <fcntl.h>
#include <assert.h>
#include <ctype.h>
#include <pthread.h>

#include <sys/types.h>
#include <sys/mman.h> // for mlockall()
#include <pwd.h> // for getpwnam()
#include <grp.h>
#include <sys/resource.h> // for setrlimit()
#include <limits.h> // for UINT_MAX

#include <signal.h>
#include <ucontext.h>

#include <stdarg.h> // for va_start()
#include "util.h"
#include "sflow_api.h"

#ifdef HSF_JSON
#include "cJSON.h"
#define HSP_MAX_JSON_MSG_BYTES 10000
#define HSP_READJSON_BATCH 100
#define HSP_JSON_RCV_BUF 2000000

  typedef struct _HSPApplication {
    struct _HSPApplication *ht_nxt;
    char *application;
    uint32_t hash;
    uint32_t dsIndex;
    uint16_t servicePort;
    uint32_t service_port_clash;
    uint32_t settings_revisionNo;
    int json_counters;
    int json_ops_counters;
    time_t last_json_counters;
    time_t last_json;
#define HSP_COUNTER_SYNTH_TIMEOUT 120
#define HSP_JSON_APP_TIMEOUT 7200
    SFLSampler *sampler;
    SFLPoller *poller;
    SFLCounters_sample_element counters;
  } HSPApplication;

#endif /* HSF_JSON */

#define ADD_TO_LIST(linkedlist, obj)		\
  do {						\
    obj->nxt = linkedlist;			\
    linkedlist = obj;				\
  } while(0)

#define HSP_DAEMON_NAME "hsflowd"
#define HSP_DEFAULT_PIDFILE "/var/run/hsflowd.pid"
#define HSP_DEFAULT_CONFIGFILE "/etc/hsflowd.conf"
#define HSP_DEFAULT_OUTPUTFILE "/etc/hsflowd.auto"
#define HSP_DEFAULT_VMSTORE_FILE "/etc/hsflowd.data"
#define HSP_DEFAULT_CRASH_FILE "/etc/hsflowd.crash"
#define HSP_DEFAULT_UUID_FILE "/etc/hsflowd.uuid"

  /* Numbering to avoid clash. See http://www.sflow.org/developers/dsindexnumbers.php */
#define HSP_DEFAULT_PHYSICAL_DSINDEX 1
#define HSP_DEFAULT_SUBAGENTID 100000
#define HSP_MAX_SUBAGENTID 199999
#define HSP_DEFAULT_LOGICAL_DSINDEX_START 100000
#define HSP_DEFAULT_APP_DSINDEX_START 150000
#define HSP_MAX_TICKS 60
#define HSP_DEFAULT_DNSSD_STARTDELAY 30
#define HSP_DEFAULT_DNSSD_RETRYDELAY 300
#define HSP_DEFAULT_DNSSD_MINDELAY 10
#define HSP_DNSSD_STACKSIZE 2000000
#define HSP_REFRESH_VMS 60
#define HSP_REFRESH_ADAPTORS 180

  // the limit we will request before calling mlockall()
  // calling res_search() seems to allocate about 11MB
  // (not sure why), so set the limit accordingly.
#define HSP_RLIMIT_MEMLOCK (1024 * 1024 * 15)
  // set to 0 to disable the memlock feature
  // #define HSP_RLIMIT_MEMLOCK 0

  // only one receiver, so the receiverIndex is a constant
#define HSP_SFLOW_RECEIVER_INDEX 1

  // just assume the sector size is 512 bytes
#define HSP_SECTOR_BYTES 512

  // upper limit on number of VIFs per VM
#define HSP_MAX_VIFS 64

  // forward declarations
  struct _HSPSFlow;
  struct _HSP;

  typedef struct _HSPCollector {
    struct _HSPCollector *nxt;
    SFLAddress ipAddr;
    uint32_t udpPort;
    struct sockaddr_in6 sendSocketAddr;
  } HSPCollector;

  typedef struct _HSPCIDR {
    struct _HSPCIDR *nxt;
    SFLAddress ipAddr;
    SFLAddress mask;
    uint32_t maskBits;
  } HSPCIDR;

#define SFL_UNDEF_COUNTER(c) c=(typeof(c))-1
#define SFL_UNDEF_GAUGE(c) c=0

  typedef struct _HSPApplicationSettings {
    struct _HSPApplicationSettings *nxt;
    char *application;
    int got_sampling_n;
    uint32_t sampling_n;
    int got_polling_secs;
    uint32_t polling_secs;
  } HSPApplicationSettings;

  typedef struct _HSPSFlowSettings {
    HSPCollector *collectors;
    uint32_t numCollectors;
    uint32_t samplingRate;
    uint32_t pollingInterval;
    uint32_t headerBytes;
#define HSP_MAX_HEADER_BYTES 256
    HSPApplicationSettings *applicationSettings;
    uint32_t ulogGroup;
#define HSP_DEFAULT_ULOG_GROUP 0
    double ulogProbability;
    uint32_t ulogSamplingRate;
    uint32_t ulogSubSamplingRate;
    uint32_t ulogActualSamplingRate;
    uint32_t jsonPort;
#define HSP_DEFAULT_JSON_PORT 0
    HSPCIDR *agentCIDRs;
  } HSPSFlowSettings;

  typedef struct _HSPSFlow {
    struct _HSP *myHSP;
    SFLAgent *agent;
    SFLPoller *poller;

    HSPSFlowSettings *sFlowSettings_file;
    HSPSFlowSettings *sFlowSettings_dnsSD;
    HSPSFlowSettings *sFlowSettings;
    char *sFlowSettings_str;
    uint32_t revisionNo;

    uint32_t subAgentId;
    char *agentDevice;
    SFLAddress agentIP;
    int explicitAgentDevice;
    int explicitAgentIP;
  } HSPSFlow; 

  typedef enum { HSPSTATE_READCONFIG=0,
		 HSPSTATE_WAITCONFIG,
		 HSPSTATE_RUN,
		 HSPSTATE_END
  } EnumHSPState;

#ifdef HSFLOWD_MAIN
  static const char *HSPStateNames[] = {
    "READCONFIG",
    "WAITCONFIG",
    "RUN",
    "END"
  };
#endif

  // persistent state for mapping VM domIds to
  // sFlow datasource indices
#define HSP_MAX_VMSTORE_LINELEN 100
#define HSP_VMSTORE_SEPARATORS " \t\r\n="
  typedef struct _HSPVMStore {
    struct _HSPVMStore *nxt;
    u_char uuid[16];
    uint32_t dsIndex;
  } HSPVMStore;
  

  // userData structure to store state for VM data-sources
  typedef struct _HSPVMState {
    uint32_t network_count;
    int32_t marked;
    uint32_t vm_index;
    uint32_t domId;
    SFLAdaptorList *interfaces;
    UTStringArray *volumes;
    UTStringArray *disks;
  } HSPVMState;
    
  typedef enum { IPSP_NONE=0,
		 IPSP_LOOPBACK6,
		 IPSP_LOOPBACK4,
		 IPSP_SELFASSIGNED4,
		 IPSP_IP6_SCOPE_LINK,
		 IPSP_VLAN6,
		 IPSP_VLAN4,
		 IPSP_IP6_SCOPE_UNIQUE,
		 IPSP_IP6_SCOPE_GLOBAL,
		 IPSP_IP4,
		 IPSP_NUM_PRIORITIES,
  } EnumIPSelectionPriority;

  // cache nio counters per adaptor
  typedef struct _HSPAdaptorNIO {
    SFLAddress ipAddr;
    uint32_t /*EnumIPSelectionPriority*/ ipPriority;
    int32_t loopback;
    int32_t bond_master;
    int32_t vlan;
    int32_t forCounters;
#define HSP_VLAN_ALL -1
    SFLHost_nio_counters nio;
    SFLHost_nio_counters last_nio;
    uint32_t last_bytes_in32;
    uint32_t last_bytes_out32;
#define HSP_MAX_NIO_DELTA32 0x7FFFFFFF
#define HSP_MAX_NIO_DELTA64 (uint64_t)(1.0e13)
    time_t last_update;
  } HSPAdaptorNIO;

  typedef struct _HSPDiskIO {
    uint64_t last_sectors_read;
    uint64_t last_sectors_written;
    uint64_t bytes_read;
    uint64_t bytes_written;
  } HSPDiskIO;

  typedef struct _HSP {
    EnumHSPState state;
    time_t clk;
    HSPSFlow *sFlow;
    char *configFile;
    char *outputFile;
    char *pidFile;
    int dropPriv;
    uint32_t outputRevisionNo;
    FILE *f_out;
    // crashdump
    char *crashFile;
    // Identity
    char hostname[SFL_MAX_HOSTNAME_CHARS+1];
    char os_release[SFL_MAX_OSRELEASE_CHARS+1];
    u_char uuid[16];
    char *uuidFile;
    // interfaces and MACs
    SFLAdaptorList *adaptorList;
    // HSPAdaptorNIOList adaptorNIOList;

    // have to poll the NIO counters fast enough to avoid 32-bit rollover
    // of the bytes counters.  On a 10Gbps interface they can wrap in
    // less than 5 seconds.  On a virtual interface the data rate could be
    // higher still. The program may decide to turn this off. For example,
    // if it finds evidence that the counters are already 64-bit in the OS,
    // or if it decides that all interface speeds are limited to 1Gbps or less.
    time_t nio_last_update;
    time_t nio_polling_secs;
#define HSP_NIO_POLLING_SECS_32BIT 3

    int refreshAdaptorList;
    int refreshVMList;
    // 64-bit diskIO accumulators
    HSPDiskIO diskIO;
    // UDP send sockets
    int socket4;
    int socket6;
#ifdef HSF_XEN
#ifdef XENCTRL_HAS_XC_INTERFACE
    xc_interface *xc_handle;
#else
    int xc_handle; // libxc
#endif
    struct xs_handle *xs_handle; // xenstore
    uint32_t page_size;
#endif
#ifdef HSF_VRT
    virConnectPtr virConn;
#endif
    uint32_t num_domains;
    // persistent state
    uint32_t maxDsIndex;
    char *vmStoreFile;
    FILE *f_vmStore;
    int vmStoreInvalid;
    HSPVMStore *vmStore;
    // inter-thread communication
    pthread_mutex_t *config_mut;
    int DNSSD;
    char *DNSSD_domain;
    uint32_t previousPollingInterval;
    // the DNSSD thread and his private state
    pthread_t *DNSSD_thread;
    int DNSSD_countdown;
    uint32_t DNSSD_startDelay;
    uint32_t DNSSD_retryDelay;
    uint32_t DNSSD_ttl;
#ifdef HSF_JSON
    int json_soc;
    int json_soc6;
    HSPApplication **applicationHT;
    uint32_t applicationHT_size;
#define HSP_INITIAL_JSON_APP_HT_SIZE 16
    uint32_t applicationHT_entries;
#endif
    int use_prstat;
  } HSP;

  // expose some config parser fns
  int HSPReadConfigFile(HSP *sp);
  HSPSFlowSettings *newSFlowSettings(void);
  HSPCollector *newCollector(HSPSFlowSettings *sFlowSettings);
  void freeSFlowSettings(HSPSFlowSettings *sFlowSettings);
  void setApplicationSampling(HSPSFlowSettings *settings, char *app, uint32_t n);
  void setApplicationPolling(HSPSFlowSettings *settings, char *app, uint32_t secs);
  void clearApplicationSettings(HSPSFlowSettings *settings);
  void lookupApplicationSettings(HSPSFlowSettings *settings, char *app, uint32_t *p_sampling, uint32_t *p_polling);
  EnumIPSelectionPriority agentAddressPriority(HSP *sp, SFLAddress *addr, int vlan, int loopback);
  int selectAgentAddress(HSP *sp);
  void addAgentCIDR(HSPSFlowSettings *settings, HSPCIDR *cidr);
  void clearAgentCIDRs(HSPSFlowSettings *settings);

  // using DNS SRV+TXT records
#define SFLOW_DNS_SD "_sflow._udp"
#define HSP_MAX_DNS_LEN 255
  typedef void (*HSPDnsCB)(HSP *sp, uint16_t rtype, uint32_t ttl, u_char *key, int keyLen, u_char *val, int valLen);
  int dnsSD(HSP *sp, HSPDnsCB callback);

  // read functions
  int readInterfaces(HSP *sp);
  int readCpuCounters(HSP *sp, SFLHost_cpu_counters *cpu);
  int readMemoryCounters(SFLHost_mem_counters *mem);
  int readDiskCounters(HSP *sp, SFLHost_dsk_counters *dsk);
  int readNioCounters(HSP *sp, SFLHost_nio_counters *nio, char *devFilter, SFLAdaptorList *adList);
  HSPAdaptorNIO *getAdaptorNIO(SFLAdaptorList *adaptorList, char *deviceName);
  void updateNioCounters(HSP *sp);
  int readHidCounters(HSP *sp, SFLHost_hid_counters *hid, char *hbuf, int hbufLen, char *rbuf, int rbufLen);
  int readJSON(HSP *sp, int soc);
  void json_app_timeout_check(HSP *sp);

#if defined(__cplusplus)
} /* extern "C" */
#endif

#endif /* HSFLOWD_H */

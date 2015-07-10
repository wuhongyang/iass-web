Which Download?
==============
XenServer
---------
*   **XenServer 6.2**: hsflowd-xenserver62-<version>.iso
*   **XenServer 6.1**: hsflowd-xenserver61-<version>.iso
*   **XenServer 6.02**: hsflowd-xenserver602-<version>.iso
*   **XenServer 6.0**: hsflowd-xenserver60-<version>.iso
*   **XenServer 5.6 FP2**: hsflowd-xenserver56FP2-<version>.iso
*   **XenServer 5.6 FP1**: hsflowd-xenserver56FP1-<version>.iso
*   **Xen Cloud 1.0**: hsflowd_XCP_10-<version>.i386.rpm

Windows
-------
*   **Windows 64-bit (Vista or later, includes Hyper-V switch support, installed if possible)**: hsflowd-win-<version>-x64.msi
*   **Windows 32-bit (Vista or later)**: hsflowd-win-<version>-x86.msi
*   **Windows XP or Windows Server 2003 or 2008 R1**: hsflowd-winxp-<version>-x86.msi

For release 1.22.1, all of the Windows builds have been migrated to use an MSI
installer rather than an exe. If you have an old version installed with the exe
installer, it will prompt you to first uninstall it. You will need to re-enter
the sFlow settings for this time only.

Red Hat KVM
-----------
please build from sources using: **make LIBVIRT=yes**

Linux
-----
*   **Red Hat/CentOS/Fedora 64-bit**: hsflowd-<version>.x86_64.rpm
*   **Red Hat/CentOS/Fedora 32-bit**: hsflowd-<version>.i386.rpm
*   **Debian/Ubuntu 64-bit**: hsflowd_<version>_x86_86.deb

Solaris
-------
please build from sources.  Note that a package built on Solaris 10 will
not work on Solaris 11, and vice-versa.

FreeBSD
-------
please build from sources

Darwin
------
please build from sources

AIX
---
*  **AIX 7.1 ppc**: hsflowd-<version>.aix7.1.ppc.rpm 

Sources
-------
* hsflowd-<version>.tar.gz
* hsflowd-<version>.zip

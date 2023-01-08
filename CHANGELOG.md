# Changelog
Version 2023.01:
* Fixed `vm_set_resolution` function

Version 2021.09:
* Updated reports layout
* Updated tests

Version 0.11:
* Added '--file_args' option to pass an argument to the main file/executable.
* '--uac_parent' option renamed to '--open_with' as it may be used with any type of files, not only the executables.
* Updated vm_record() - added new options and updated defaults.
* Small improvements in html report.

Version 0.10.3:
* Added function vm_functions.vm_disable_time_sync() and option to disable host-guest time sync ('--no_time_sync').

Version 0.10.2:
* Added option to check VirtualBox version online (--check_version). Will warn if outdated version is used.
Windows binary does not have this option.
* Fixed '--log' option.

Version 0.10.1:
* Added function vm_functions.vm_memdump() and option to dump VM memory (--memdump).
This may take some time and disk space.
* Added script to build Windows binary using [Nuitka](https://nuitka.net/). See 'scripts' folder.

Version 0.10:
* Added option to dump all VM's network traffic to the file ('--pcap'). File will be saved as {vm_name}_{snapshot}.pcap.
* Added option '--get_file' to download file (memory dumps, logs, reports, etc) before stopping VM.
* Removed option 'keep' for all of the arguments. Omitting argument will do the same.
* Added function vm_set_mac(vm, mac) and option to change MAC address for VM before start.
Can be set to specific MAC ('--mac 80AABBCCDDEE'), 'new' for random mac in VirtualBox range or 'random' for random one.
* Logs levels tweaked to make default output more clean.
* Added argument '--debug' (alias for '--verbosity debug').
* Added standalone Windows binary. See releases section for download.

Version 0.9.2:
* Added option '--delay' to control delay before/after starting VMs. Depends on hardware performance.
* Added md5 checksum calculation.
* Updated html report generation logic.
* Additional check to make sure that number of thread <= number of VMs.

Version 0.9.1:
* Added check for original file at the end of analysis.
* Added more data to html report.
* Small cleanups.

Version 0.9:
* Added option to generate html report ('--report'). Result (including screenshots) will be saved under ./reports/<file_hash> directory.
* Added option to record video from guest VM ('--record output.webm').
* uac_parent is now applied to both pre_exec and post_exec commands too.
* Removed '--info' and '--uac_fix' arguments. Both options are enabled from now on.
* Added alias '--user' for '--login' option.

Version 0.8.2:
* Added vm_backup(vm) function. Takes live snapshot with name in 'backup_YYYY_MM_DD_HH_MM_SS' format.

Version 0.8.1:
* Fixed bug with some command line args were ignored (--ui).

Version 0.8:
* Added options 'uac_fix' and 'uac_parent' for vm_exec() function.
Used to circumvent VirtualBox error VERR_PROC_ELEVATION_REQUIRED, when trying to execute application with mandatory UAC elevation.
* Added short aliases for '--vms' and '--snapshots' options: '-v' and '-s'.
* Added option 'dictionary' for list_vms() function. List of VMs will be returned as {'vm': '/group'} dictionary.
* Added function to clone VM - vm_clone().
* Added function to record guest screen - vm_record().
* Added option to restore current snapshot: vm_snapshot_restore('vm', 'restorecurrent').
* Updated vm_screenshot() function - code to generate image index moved to main script.
* All files converted to Unix EOL (LF).

Version 0.7.3:
* Docstring added for all the functions (Sphinx format). Usage: help(function_name).
* Added functions to export and import VMs - vm_export() and vm_import(). Have separate timeout settings as operations are time consuming.

Version 0.7.2:
* Added function to enumerate guest properties - vm_enumerate().
* Updated list_ips() function.
* Added functions to control snapshots - vm_snapshot_take() and vm_snapshot_remove(). Currently not used.

Version 0.7.1:
* Added option to redirect log to file ('--log vm_automation.log'). Default: log to console ('--log console').

Version 0.7:
* Added option to control number of concurrently running tasks ('--threads 2'). Set to '0' to set to number of VMs.
* Added option to control log verbosity ('--verbosity debug|info|error').
* Added parameter ignore_status_error to vm_stop() function. May be used when trying to stop already stopped VM.
* Added aliases for vm_copyto() and vm_copyfrom() functions - vm_upload() and vm_download().
* Fixed command line arguments processing.
* Added unittests for some of the functions ('tests/test.py').
* Other minor updates for few functions.

Version 0.6.2:
* Bug fixes in list_snapshots() function.

Version 0.6.1:
* All vm_functions are now returning exactly 3 values: [exit_code, stdout, stderr].
* New function to get IP addresses of guest - vm_functions.list_ips(vm).
* Fixes in arguments parser.

Version 0.6:
* Script now can use all available VMs ('--vms all') and snapshots ('--snapshots all'). Use with caution and make sure you have only testing VMs.
* New function to get list of snapshots for specific VM - vm_functions.list_snapshots().
* Script updated to handle keyboard interrupts (Ctrl+C).
* Option to set random screen resolution from most common ones ('--resolution random').
* Some tweaks and fixes.

Version 0.5:
* All functions moved to external files: vm_functions (all VM control functions) and support_functions (randomize filename, calculate a hash and show links to Google/VT).
* The main routine moved to file demo.py.
* New function to get list of VMs - vm_functions.list_vms().
* Fixed logic when the file was removed before execution - script will move on to the next task without waiting for a timeout.

Version 0.4:
* Updated to use 'argparse' to parse command-line arguments.
* All of the settings now can be configured via the command line (see '--help' or examples above).

Version 0.3.1-0.3.2:
* Optionally calculate sha256 hash of a file and show links to VirusTotal and Google searches.
* Small fixes.

Version 0.3:
* Added option to enable/disable network for guest OS.
* Added option to start scripts before/after running the main file.
* Added option to change the display resolution.

Version 0.2:
* Added parallel execution of multiple VMs.

Version 0.1:
* First public release.

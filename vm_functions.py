import datetime
import logging
import random
import re
import secrets
import subprocess

if __name__ == "__main__":
    print('This script only contains functions and cannot be called directly. See demo scripts for usage examples.')
    exit(1)

# Set essential options
if 'vboxmanage_path' not in locals():
    vboxmanage_path = 'vboxmanage'
if 'timeout' not in locals():
    timeout = 60


def vboxmanage(cmd, timeout=timeout):
    """Wrapper for "VBoxManage" command

    :param cmd: Command to run.
    :param timeout: Timeout for operation, seconds.
    :return: returncode, stdout, stderr.
    """
    cmd = f'{vboxmanage_path} {cmd}'.split()
    logging.debug(f'''Running command: {' '.join(cmd)}''')
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, text=True)
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        logging.critical('vboxmanage path is incorrect. Stopping.')
        exit(1)


def virtualbox_version(strip_newline=1, strip_build=0):
    """Return VirtualBox version

    :param strip_newline: Strip new line.
    :param strip_build: Strip build number.
    :return: returncode, stdout, stderr.
    """
    result = vboxmanage('--version')
    version = result[1]
    if strip_newline:
        version = version.rstrip()
    if strip_build:
        version = re.findall(r'^(\d+(?:\.\d+)*)', version)[0]
    return result[0], version, result[2]


def list_vms(list=1, dictionary=0):
    """Return list of virtual machines

    :param list: Return stdout as a list.
    :param dictionary: Return stdout as a {'vm': 'group'} dictionary. Overrides 'list' option.
    :return: returncode, stdout, stderr.
    """
    if dictionary:
        options = '--long'
    else:
        options = ''
    result = vboxmanage(f'list vms --sorted {options}')
    if result[0] == 0:
        if dictionary:
            # Convert output to {'vm': 'group'} dictionary.
            vms = re.findall(r'^Name:\s+(\S+)', result[1], flags=re.MULTILINE)
            groups = re.findall(r'^Groups:\s+(\S+)', result[1], flags=re.MULTILINE)
            vms_list_ = dict(zip(vms, groups))
        elif list:
            vms_list_ = re.findall(r'^"(\w+)"', result[1], flags=re.MULTILINE)
        else:
            vms_list_ = result[1]
        return result[0], vms_list_, result[2]
    else:
        logging.error(f'Unable to get list of VMs: {result[2]}')
        return result[0], result[1], result[2]


def list_snapshots(vm, list=1):
    """Return list of snapshots for specific virtual machine

    :param vm: Virtual machine name.
    :param list: Return stdout as a list.
    :return: returncode, stdout, stderr.
    """
    result = vboxmanage(f'snapshot {vm} list --machinereadable')
    if result[0] == 0:
        if list == 1:
            snapshots_list = re.findall(r'^SnapshotName(?:-\d+)?="(\S+)"', result[1], flags=re.MULTILINE)
        else:
            snapshots_list = result[1]
        return result[0], snapshots_list, result[2]
    else:
        logging.error(f'Unable to get list of snapshots: {result[2]}')
        return result[0], result[1], result[2]


def vm_start(vm, ui='gui'):
    """Start virtual machine

    :param vm: Virtual machine name.
    :param ui: Start virtual machine with or without GUI.
    :return: returncode, stdout, stderr.
    """
    if ui == '0':
        ui = 'headless'
    elif ui == '1':
        ui = 'gui'
    ui = ui.lower()
    logging.info(f'Starting VM "{vm}".')
    if ui not in ['gui', 'sdl', 'headless', 'separate']:
        logging.error('Unknown ui type set. Assuming gui.')
        ui = 'gui'
    result = vboxmanage(f'startvm {vm} --type {ui}')
    if result[0] == 0:
        logging.info(f'VM {vm} started')
    else:
        logging.error(f'Error while starting VM "{vm}": {result[2]}')
    return result[0], result[1], result[2]


def vm_stop(vm, ignore_status_error=0):
    """Stop virtual machine

    :param vm: Virtual machine name.
    :param ignore_status_error: Option to ignore errors when they are expected to happen.
    :return: returncode, stdout, stderr.
    """
    logging.info(f'Stopping VM "{vm}".')
    result = vboxmanage(f'controlvm {vm} poweroff')
    if result[0] == 0:
        logging.debug('VM stopped.')
    else:
        if 'is not currently running' in result[2] or 'Invalid machine state: PoweredOff' in result[2] and \
                ignore_status_error:
            logging.debug(f'VM already stopped: {result[2]}')
        else:
            logging.error(f'Error while stopping VM: {result[2]}')
    return result[0], result[1], result[2]


def vm_enumerate(vm, pattern=None):
    """Enumerate virtual machine properties

    :param vm: Virtual machine name.
    :param pattern: Pattern for virtual machine properties.
    :return: returncode, stdout, stderr.
    """
    logging.debug(f'Enumerating VM "{vm}" guest properties.')
    if pattern:
        result = vboxmanage(f'guestproperty enumerate {vm} --pattern {pattern}')
    else:
        result = vboxmanage(f'guestproperty enumerate {vm}')
    if result[0] == 0:
        logging.debug('VM properties enumerated.')
    else:
        logging.error(f'Error while enumerating guest properties: {result[2]}')
    return result[0], result[1], result[2]


def list_ips(vm):
    """Get list of IP addresses of guest

    :param vm: Virtual machine name.
    :return: returncode, stdout, stderr.
    """
    result = vm_enumerate(vm, pattern='/VirtualBox/GuestInfo/Net/*/V4/IP')
    if result[0] == 0:
        ips_list = re.findall(r'value:\s(\d+\.\d+\.\d+\.\d+)', result[1], flags=re.MULTILINE)
        return result[0], ips_list, result[2]
    else:
        logging.error(f'Unable to get list of IP addresses: {result[2]}')
        return result[0], result[1], result[2]


def vm_snapshot_take(vm, snapshot, live=0):
    """Take snapshot for virtual machine

    :param vm: Virtual machine name.
    :param snapshot: Snapshot name.
    :param live: Take a live snapshot.
    :return: returncode, stdout, stderr.
    """
    if live:
        logging.info(f'Taking live snapshot "{snapshot}" for VM "{vm}".')
        options = '--live'
    else:
        logging.info(f'Taking snapshot "{snapshot}" for VM "{vm}".')
        options = ''
    result = vboxmanage(f'snapshot {vm} take {snapshot} {options}')
    if result[0] == 0:
        logging.debug('Snapshot created.')
    else:
        logging.error(f'Error while creating snapshot: {result[2]}')
    return result[0], result[1], result[2]


def vm_backup(vm):
    """Take live snapshot for virtual machine with timestamp

    :param vm: Virtual machine name.
    :return: returncode, stdout, stderr.
    """
    now = datetime.datetime.now()
    snapshot = f'backup_{now.strftime("%Y_%m_%d_%H_%M_%S")}'
    result = vm_snapshot_take(vm, snapshot, live=1)
    return result[0], result[1], result[2]


def vm_snapshot_restore(vm, snapshot, ignore_status_error=0):
    """Restore snapshot for virtual machine

    :param vm: Virtual machine name.
    :param snapshot: Snapshot name.
    :param ignore_status_error: Option to ignore errors when they are expected to happen.
    :return: returncode, stdout, stderr.
    """
    if snapshot == 'restorecurrent':
        logging.info(f'Restoring VM "{vm}" to current snapshot.')
        result = vboxmanage(f'snapshot {vm} restorecurrent')
        if result[0] == 0:
            logging.debug(f'VM "{vm}" restored to current snapshot.')
        else:
            logging.error(f'Error while restoring VM "{vm}" to current snapshot: {result[2]}.')
    else:
        logging.info(f'Restoring VM "{vm}" to snapshot "{snapshot}".')
        result = vboxmanage(f'snapshot {vm} restore {snapshot}')
        if result[0] == 0:
            logging.debug(f'VM "{vm}" restored to snapshot "{snapshot}".')
        else:
            if 'Could not find a snapshot' in result[2] and ignore_status_error:
                logging.debug(f'VM "{vm}" does not have snapshot "{snapshot}": {result[2]}.')
            else:
                logging.error(f'Error while restoring VM "{vm}" to snapshot "{snapshot}": {result[2]}.')
    return result[0], result[1], result[2]


def vm_snapshot_remove(vm, snapshot):
    """Remove snapshot for virtual machine

    :param vm: Virtual machine name.
    :param snapshot: Snapshot name.
    :return: returncode, stdout, stderr.
    """
    logging.info(f'Removing snapshot "{snapshot}" for VM "{vm}"')
    result = vboxmanage(f'snapshot {vm} delete {snapshot}')
    if result[0] == 0:
        logging.debug('Snapshot removed.')
    else:
        logging.error(f'Error while removing snapshot: {result[2]}')
    return result[0], result[1], result[2]


def vm_network(vm, link_state):
    """Change guest OS network link state

    :param vm: Virtual machine name.
    :param link_state: Guest OS network link state.
    :return: returncode, stdout, stderr.
    """
    if link_state in ['on', 'off']:
        logging.info(f'Setting network parameters to {link_state} for VM {vm}')
        result = vboxmanage(f'controlvm {vm} setlinkstate1 {link_state}')
        if result[0] == 0:
            logging.debug(f'Network state set.')
        else:
            logging.error(f'Unable to change network state for VM: {result[2]}.')
        return result[0], result[1], result[2]
    else:
        return 0, 0, 0


def vm_set_resolution(vm, screen_resolution):
    """Control guest OS screen resolution

    :param vm: Virtual machine name.
    :param screen_resolution: Guest OS screen resolution (W H D).
    :return: returncode, stdout, stderr.
    """
    if not screen_resolution:
        return 0, 0, 0
    if screen_resolution == 'random':
        screen_resolution = random.choice(['1024 768 32', '1280 1024 32', '1440 1080 32', '1600 1200 32', '1920 1080 32'])
    logging.debug(f'Changing screen resolution for VM "{vm}".')
    result = vboxmanage(f'controlvm {vm} setvideomodehint {screen_resolution}')
    if result[0] == 0:
        logging.debug('Screen resolution changed.')
    else:
        logging.error(f'Unable to change screen resolution: {result[2]}')
    return result[0], result[1], result[2]


def vm_set_mac(vm, mac):
    """Change MAC address for VM

    :param vm: Virtual machine name.
    :param mac: New MAC address.
    :return: returncode, stdout, stderr.
    """
    logging.debug(f'Changing MAC address for VM "{vm}".')
    if mac == 'new':
        # Generate new MAC in VirtualBox range (080027xxxxxx)
        mac = f'080027{secrets.token_hex(3)}'
    if mac == 'random':
        # Fully random MAC
        mac = secrets.token_hex(6)
    result = vboxmanage(f'modifyvm {vm} --macaddress1 {mac}')
    if result[0] == 0:
        logging.debug('MAC changed.')
    else:
        logging.error(f'Unable to change MAC address: {result[2]}')
    return result[0], result[1], result[2]


def vm_pcap(vm, file):
    """Dump all VM's network traffic to a file

    :param vm: Virtual machine name.
    :param file: Output file (pcap format).
    :return: returncode, stdout, stderr.
    """
    result = vboxmanage(f'modifyvm {vm} --nictrace1 on --nictracefile1 {file}')
    if result[0] == 0:
        logging.debug(f'Saving network traffic from VM "{vm}" as {file}.')
    else:
        logging.error(f'Unable to update VM settings to capture traffic: {result[2]}')
    return result[0], result[1], result[2]


def vm_memdump(vm, file):
    """Dump VM memory to a file

    :param vm: Virtual machine name.
    :param file: Output file.
    :return: returncode, stdout, stderr.
    """
    result = vboxmanage(f'debugvm {vm} dumpvmcore --filename={file}')
    if result[0] == 0:
        logging.debug(f'Dumping memory of VM "{vm}" as {file}.')
    else:
        logging.error(f'Unable to dump VM memory: {result[2]}')
    return result[0], result[1], result[2]


def vm_disable_time_sync(vm):
    """Disable host-guest time sync for VM

    :param vm: Virtual machine name.
    :return: returncode, stdout, stderr.
    """
    result = vboxmanage(f'setextradata {vm} "VBoxInternal/Devices/VMMDev/0/Config/GetHostTimeDisabled" "1"')
    if result[0] == 0:
        logging.debug(f'Time sync disabled for VM "{vm}".')
    else:
        logging.error(f'Unable to disable time sync for VM: {result[2]}')
    return result[0], result[1], result[2]


def vm_exec(vm, username, password, remote_file, open_with='%windir%\\explorer.exe', file_args=None):
    """Execute file/command on guest OS

    :param vm: Virtual machine name.
    :param username: Guest OS username (login).
    :param password: Guest OS password.
    :param remote_file: Path to file on guest OS.
    :param open_with: Parent application that will start/open main file.
    :param file_args: Optional arguments
    :return: returncode, stdout, stderr.
    """
    logging.info(f'{vm}: Executing file "{remote_file}" with parent "{open_with}" on VM "{vm}".')
    if file_args:
        cmd = f'guestcontrol {vm} --username {username} --password {password} start {open_with} {remote_file} {file_args}'
    else:
        cmd = f'guestcontrol {vm} --username {username} --password {password} start {open_with} {remote_file}'

    result = vboxmanage(cmd)
    if result[0] == 0:
        logging.debug('File executed successfully.')
    else:
        logging.error(f'Error while executing file: {result[2]}')
    return result[0], result[1], result[2]


def vm_file_stat(vm, username, password, remote_file):
    """Get information about file on guest OS

    :param vm: Virtual machine name.
    :param username: Guest OS username (login).
    :param password: Guest OS password.
    :param remote_file: Path to file on guest OS.
    :return: returncode, stdout, stderr.
    """
    logging.debug(f'Checking if file "{remote_file}" exist on VM "{vm}".')
    result = vboxmanage(f'guestcontrol {vm} --username {username} --password {password} stat {remote_file}')
    if result[0] == 0:
        logging.debug('File exist.')
    else:
        logging.error(f'Error while checking for file: {result[2]}')
    return result[0], result[1], result[2]


def vm_copyto(vm, username, password, local_file, remote_file):
    """Upload file to virtual machine

    :param vm: Virtual machine name.
    :param username: Guest OS username (login).
    :param password: Guest OS password.
    :param local_file: Path to local file on host OS.
    :param remote_file: Path to file on guest OS.
    :return: returncode, stdout, stderr.
    """
    logging.info(f'Uploading "{local_file}" as "{remote_file}" to VM "{vm}".')
    result = vboxmanage(
        f'guestcontrol {vm} --username {username} --password {password} copyto {local_file} {remote_file}')
    if result[0] == 0:
        logging.debug(f'File uploaded.')
    else:
        logging.error(f'Error while uploading file: {result[2]}')
    return result[0], result[1], result[2]


# Alias to vm_copyto()
def vm_upload(vm, username, password, local_file, remote_file):
    """Upload file to virtual machine

    :param vm: Virtual machine name.
    :param username: Guest OS username (login).
    :param password: Guest OS password.
    :param local_file: Path to local file on host OS.
    :param remote_file: Path to file on guest OS.
    :return: returncode, stdout, stderr.
    """
    result = vm_copyto(vm, username, password, local_file, remote_file)
    return result[0], result[1], result[2]


def vm_copyfrom(vm, username, password, remote_file, local_file):
    """Download file from virtual machine

    :param vm: Virtual machine name.
    :param username: Guest OS username (login).
    :param password: Guest OS password.
    :param local_file: Path to local file on host OS.
    :param remote_file: Path to file on guest OS.
    :return: returncode, stdout, stderr.
    """
    logging.info(f'Downloading file "{remote_file}" from VM "{vm}" as "{local_file}".')
    result = vboxmanage(
        f'guestcontrol {vm} --username {username} --password {password} copyfrom {remote_file} {local_file}')
    if result[0] == 0:
        logging.debug(f'File downloaded.')
    else:
        logging.error(f'Error while downloading file: {result[2]}')
    return result[0], result[1], result[2]


# Alias to vm_copyfrom()
def vm_download(vm, username, password, remote_file, local_file):
    """Download file from virtual machine

    :param vm: Virtual machine name.
    :param username: Guest OS username (login).
    :param password: Guest OS password.
    :param local_file: Path to local file on host OS.
    :param remote_file: Path to file on guest OS.
    :return: returncode, stdout, stderr.
    """
    result = vm_copyfrom(vm, username, password, local_file, remote_file)
    return result[0], result[1], result[2]


def vm_screenshot(vm, screenshot_name):
    """Take screenshot from guest OS

    :param vm: Virtual machine name.
    :param screenshot_name: Name of file to save screenshot as.
    :return: returncode, stdout, stderr.
    """
    logging.debug(f'Taking screenshot "{screenshot_name}" on VM "{vm}".')
    result = vboxmanage(f'controlvm {vm} screenshotpng {screenshot_name}')
    if result[0] == 0:
        logging.debug('Screenshot created.')
    else:
        logging.error(f'Error while taking screenshot: {result[2]}')
    return result[0], result[1], result[2]


def vm_record(vm, filename, screens='all', fps=10, videorate=512, duration=0):
    """Start screen recording on VM

    :param vm: Virtual machine name.
    :param filename: Name of file to save video as (.webm).
    :param screens: Screens to record.
    :param fps: Frames per second (1-30).
    :param videorate: Bitrate, kbps (122-1228).
    :param duration: Record duration, seconds.
    :return:
    """
    logging.info(f'Recording video as "{filename}" on VM "{vm}".')
    result = vboxmanage(f'controlvm {vm} recording screens {screens}')
    if result[0] != 0:
        return result[0], result[1], result[2]

    result = vboxmanage(f'controlvm {vm} recording filename {filename}')
    if result[0] != 0:
        return result[0], result[1], result[2]

    if 1 <= fps <= 30:
        result = vboxmanage(f'controlvm {vm} recording videofps {fps}')
        if result[0] != 0:
            return result[0], result[1], result[2]

    # result = vboxmanage(f'controlvm {vm} recording videores {videores}')
    # if result[0] != 0:
    #     return result[0], result[1], result[2]

    if 122 <= videorate <= 1228:
        result = vboxmanage(f'controlvm {vm} recording videorate {videorate}')
        if result[0] != 0:
            return result[0], result[1], result[2]

    if duration > 0:
        result = vboxmanage(f'controlvm {vm} recording maxtime {duration}')
        if result[0] != 0:
            return result[0], result[1], result[2]

    result = vboxmanage(f'controlvm {vm} recording on')
    if result[0] == 0:
        logging.debug('Recording started.')
    else:
        logging.error(f'Error while recording video: {result[2]}')

    return result[0], result[1], result[2]


def vm_record_stop(vm):
    """Stop screen recording on VM

    :param vm: Virtual machine name.
    :return:
    """
    logging.info(f'Stopping recording on VM "{vm}".')
    result = vboxmanage(f'controlvm {vm} recording off')
    if result[0] == 0:
        logging.debug('Recording stopped.')
    else:
        logging.error(f'Error while stopping recording: {result[2]}')
    return result[0], result[1], result[2]


def vm_import(vm, vm_file, preview=0, timeout=600):
    """Import virtual machine from file

    :param vm: Virtual machine name.
    :param vm_file: Path to input file.
    :param preview: Only preview (no actual import).
    :param timeout: Timeout for operation, seconds.
    :return: returncode, stdout, stderr.
    """
    if preview:
        logging.info(f'Importing file {vm_file} in preview mode.')
        options = '--dry-run'
    else:
        logging.info(f'Importing file {vm_file}.')
        options = ''
    if vm:
        result = vboxmanage(f'import {vm_file} {options} --vmname {vm}', timeout=timeout)
    else:
        result = vboxmanage(f'import {vm} {options}', timeout=timeout)
    if result[0] == 0:
        logging.debug('VM imported.')
    else:
        logging.error(f'Error while importing VM: {result[2]}')
    return result[0], result[1], result[2]


def vm_export(vm, vm_file, file_format='ovf20', timeout=600):
    """Export virtual machine to file

    :param vm: Virtual machine name.
    :param vm_file: Path to output file.
    :param file_format: Format for output file.
    :param timeout: Timeout for operation, seconds.
    :return: returncode, stdout, stderr.
    """
    if file_format not in ['legacy09', 'ovf09', 'ovf10', 'ovf20', 'opc10']:
        logging.error('Unknown file format. Exiting.')
        exit()
    logging.info(f'Exporting VM "{vm}" as {vm_file}.')
    result = vboxmanage(f'export {vm} --output {vm_file}', timeout=timeout)
    if result[0] == 0:
        logging.debug('VM exported.')
    else:
        logging.error(f'Error while exporting VM: {result[2]}')
    return result[0], result[1], result[2]


def vm_clone(vm, name, mode='all', register=1, timeout=600):
    """Clone virtual machine

    :param vm: Virtual machine to clone.
    :param name: Clone name.
    :param mode: Clone mode (machine/machinechildren/all).
    :param register: Register cloned virtual machine.
    :param timeout: Timeout for operation, seconds.
    :return:
    """
    if register:
        options = '--register'
    else:
        options = ''
    result = vboxmanage(f'clonevm {vm} --mode={mode} --name={name} {options}', timeout=timeout)
    return result[0], result[1], result[2]

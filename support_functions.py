import datetime
import hashlib
import logging
import os
import random
import re
import string
import platform

if __name__ == "__main__":
    print('This script only contains functions and cannot be called directly. See demo scripts for usage examples.')
    exit(1)


# Check Python version
def check_python_version():
    return int(platform.python_version_tuple()[0]) == 3 and int(platform.python_version_tuple()[1]) >= 6


# Normalize path (replace '\' and '/' with '\\').
def normalize_path(path):
    path.replace('\\', '\\\\')
    normalized_path = path.replace('/', '\\\\')
    return normalized_path


# Calculate file hashed (sha256 and md5)
def file_hash(file):
    file_hash_sha256 = hashlib.sha256()
    file_hash_md5 = hashlib.md5()
    block_size = 65536
    with open(file, 'rb') as f:
        fb = f.read(block_size)
        while len(fb) > 0:
            file_hash_sha256.update(fb)
            file_hash_md5.update(fb)
            fb = f.read(block_size)
    sha256 = file_hash_sha256.hexdigest()
    md5 = file_hash_md5.hexdigest()
    return sha256, md5


# Calculate file size (KB)
def file_size(file):
    size = os.path.getsize(file)
    size_kb = round(size / 1024)
    return size_kb


# Show info about file
def file_info(file):
    file = ''.join(file)
    logging.info(f'File: "{file}"')

    # Check if file exists
    if not os.path.isfile(file):
        logging.error(f'File "{file}" does not exists.')
        return 1

    # Print hash and links
    sha256 = file_hash(file)[0]
    md5 = file_hash(file)[1]
    size = file_size(file)
    logging.info(f'SHA256 hash: {sha256}')
    logging.info(f'MD5 hash: {md5}')
    logging.info(f'Size: {size} Kb')
    logging.info(f'VirusTotal search: https://www.virustotal.com/gui/file/{sha256}/detection')
    logging.info(f'Google search: https://www.google.com/search?q={sha256}\n')
    return 0, sha256, md5, size


# Generate random file name
def randomize_filename(login, file, destination_folder):
    # File name
    random_name = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(4, 20)))

    # File extension
    file_extension = re.search(r'\.\w+$', file).group()
    if not file_extension:
        logging.debug('Unable to obtain file extension. Assuming .exe')
        file_extension = '.exe'

    # Destination folder
    if destination_folder.lower() in ['desktop', 'downloads', 'documents']:
        destination_folder = f'C:\\Users\\{login}\\{destination_folder}\\'
    elif destination_folder.lower() == 'temp':
        destination_folder = f'C:\\Users\\{login}\\AppData\\Local\\Temp\\'
    else:
        logging.debug('Using custom remote_folder')

    random_filename = destination_folder + random_name + file_extension
    logging.debug(f'Remote file: "{random_filename}"')
    return random_filename


# Generate html report
def html_report(vm, snapshot, filename, file_args, file_size, sha256, md5, timeout, vm_network_state,
                reports_directory='reports'):
    logging.debug(f"Creating report for task {vm}_{snapshot}")

    # Set options and paths
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    destination_dir = f'{reports_directory}/{sha256}'
    destination_file = f'{destination_dir}/index.html'

    # Create directory, if it does not exist
    os.makedirs(destination_dir, mode=0o444, exist_ok=True)

    # Content of html file
    html_template_header = f"""
    <!DOCTYPE html>
    <html>
    <title>Report: {filename}</title>
    <body>
    <table>
      <caption><h4>File info:</h4></caption>
      <tr><td><b>Name:</b></td><td>{filename}</td></tr>
      <tr><td><b>Arguments:</b></td><td>{file_args}</td></tr>
      <tr><td><b>Size:</b></td><td>{file_size} Kb</td></tr>
      <tr><td><b>SHA-256:</b></td>
        <td>{sha256} (<a href="https://www.virustotal.com/gui/search/{sha256}" target=_blank>VT Search</a>)</td></tr>
      <tr><td><b>MD5:</b></td><td>{md5}</td></tr>
      <tr><td><b>Scanned on:</b></td><td>{time}</td></tr>
      <tr><td><b>Duration:</b></td><td>{timeout} seconds</td></tr>
      <tr><td><b>Network:</b></td><td>{vm_network_state}</td></tr>
    </table>
    """

    html_template_tasks = f"""<br><br><b>Task:</b> {vm}_{snapshot}<br>
        <b>Downloads:</b> """
    if os.path.isfile(f"{destination_dir}/{vm}_{snapshot}.webm"):
        html_template_tasks += (
            f"""<a href={vm}_{snapshot}.webm target=_blank>Screen recording</a> """
        )
    if os.path.isfile(f"{destination_dir}/{vm}_{snapshot}.pcap"):
        html_template_tasks += (
            f"""<a href={vm}_{snapshot}.pcap target=_blank>Traffic dump</a> """
        )
    if os.path.isfile(f"{destination_dir}/{vm}_{snapshot}.dmp"):
        html_template_tasks += (
            f"""<a href={vm}_{snapshot}.dmp target=_blank>Memory dump</a> """
        )

    # Search for screenshots in reports directory
    html_template_tasks += """
    <b><br>Screenshots:</b><br>
    """
    screenshots = os.listdir(destination_dir)
    for screenshot in screenshots:
        # Check if filename matches task name and have .png extension
        if re.search(rf"{vm}_{snapshot}_\d+\.png", screenshot):
            html_template_tasks += f"""
                <a href="{screenshot}" target=_blank><img src="{screenshot}" width="120" high="100"></img></a>
                """

    # Write data to report file
    file_object = open(destination_file, mode='a', encoding='utf-8')
    # If file is empty, write html header first
    if os.path.getsize(destination_file) == 0:
        file_object.write(html_template_header)
    # Write screenshots block
    file_object.write(html_template_tasks)

import argparse
import logging

import subprocess
import PyInstaller.__main__
import shutil
from _common import get_os, setup_log, OS, get_python_version, cd, check_node, check_yarn, check_pyinstaller

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-d', '--debug', action='store_true',
                    help='Set log level to Debug')

args = parser.parse_args()
log = setup_log(logging.DEBUG if args.debug else logging.INFO)

## System & Dependencies Check
detected_os = get_os()
detected_py = get_python_version()
log.debug("OS : {}".format(detected_os))
log.debug("Python version : {}".format(detected_py))

if detected_os == OS.UNKNOWN:
    log.fatal("Unknown OS !")
    exit(1)

if detected_py < (3, 5):
    log.fatal("Unsupported python version !")
    exit(1)

if not check_node():
    log.fatal("NodeJs is not install. It's a required dependency !")
    exit(1)

if not check_yarn():
    log.fatal("Yarn is not install. It's a required dependency !")
    exit(1)


if not check_pyinstaller():
    log.fatal("Pyinstaller is not install. It's a required dependency !")
    exit(1)

## Build Cli
def pyinstaller_args():
    common = [
            '--workpath=./build/',
            '--specpath=.',
            '-y',
            '--onedir',
            '--name=cli',
            '--distpath=../../dist',
            'main.py',
        ]
    if detected_os == OS.LINUX:
        return common
    if detected_os == OS.MAC:
        return common
    if detected_os == OS.WIN:
        common.extend(['--add-binary=../third/msvcp/msvcp140.dll;.'])
        return common

log.info('Building Cli')
with cd("../../cli"):
    try:
        PyInstaller.__main__.run(pyinstaller_args())
    except Exception as e:
        log.error(e)
        log.fatal("Cli building failed")
        exit(1)
log.info('Cli successfully built')

## Build Gui
log.info('Building Cli')
with cd("../../gui"):
    r = subprocess.run(['yarn', 'build'], shell=True) if detected_os == OS.WIN else subprocess.run(['yarn', 'build'])
    if r.returncode != 0:
        log.fatal("Cli building failed")
        exit(1)
log.info('Cli successfully built')


## Move Generated Files
def gui_build_files_location():
    if detected_os == OS.LINUX:
        return './gui-unpacked/linux-unpacked'
    if detected_os == OS.MAC:
        log.warning('Gui files path location not tested on mac')
        return './gui-unpacked/linux-unpacked'
    if detected_os == OS.WIN:
        return './gui-unpacked/win-unpacked'


log.info('Moving the build files to final location')
with cd("../../../dist"):
    shutil.rmtree('./gui', ignore_errors=True)
    shutil.move(gui_build_files_location(), "./gui")
    shutil.rmtree('./gui-unpacked', ignore_errors=True)

log.info('Build to Final Directory')

log.info('Build completed!')
log.info('It should have generated a folder called dist/, inside you will find the final project files that you can share with everyone!')
log.info('Enjoy and remember to respect the License!')
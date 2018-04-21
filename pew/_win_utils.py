# -*- coding=utf-8 -*-
# psutil is painfully slow in win32. So to avoid adding big
# dependencies like pywin32 a ctypes based solution is preferred

# Code based on the winappdbg project http://winappdbg.sourceforge.net/
# (BSD License) - adapted from Celery
# https://github.com/celery/celery/blob/2.5-archived/celery/concurrency/processes/_win.py
import os
from ctypes import (
    byref, sizeof, windll, Structure, WinError, POINTER,
    c_size_t, c_char, c_void_p
)
from ctypes.wintypes import DWORD, LONG
from ._utils import to_unicode

ERROR_NO_MORE_FILES = 18
INVALID_HANDLE_VALUE = c_void_p(-1).value
SHELL_NAMES = ['cmd', 'powershell', 'pwsh', 'cmder']
global SHELL_NAMES

if os.environ.get('RUNNING_CI'):
    SHELL_NAMES.append('python')


class PROCESSENTRY32(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('cntUsage', DWORD),
        ('th32ProcessID', DWORD),
        ('th32DefaultHeapID', c_size_t),
        ('th32ModuleID', DWORD),
        ('cntThreads', DWORD),
        ('th32ParentProcessID', DWORD),
        ('pcPriClassBase', LONG),
        ('dwFlags', DWORD),
        ('szExeFile', c_char * 260),
    ]


LPPROCESSENTRY32 = POINTER(PROCESSENTRY32)


def CreateToolhelp32Snapshot(dwFlags=2, th32ProcessID=0):
    hSnapshot = windll.kernel32.CreateToolhelp32Snapshot(
        dwFlags,
        th32ProcessID
    )
    if hSnapshot == INVALID_HANDLE_VALUE:
        raise WinError()
    return hSnapshot


def Process32First(hSnapshot):
    pe = PROCESSENTRY32()
    pe.dwSize = sizeof(PROCESSENTRY32)
    success = windll.kernel32.Process32First(hSnapshot, byref(pe))
    if not success:
        if windll.kernel32.GetLastError() == ERROR_NO_MORE_FILES:
            return
        raise WinError()
    return pe


def Process32Next(hSnapshot, pe=None):
    if pe is None:
        pe = PROCESSENTRY32()
    pe.dwSize = sizeof(PROCESSENTRY32)
    success = windll.kernel32.Process32Next(hSnapshot, byref(pe))
    if not success:
        if windll.kernel32.GetLastError() == ERROR_NO_MORE_FILES:
            return
        raise WinError()
    return pe


def get_all_processes():
    """Return a dictionary of properties about all processes.

    >>> get_all_processes()
    {
        1509: {
            'parent_pid': 1201,
            'executable': 'C:\\Program\\\\ Files\\Python36\\python.exe'
        }
    }
    """
    h_process = CreateToolhelp32Snapshot()
    pids = {}
    pe = Process32First(h_process)
    while pe:
        pids[pe.th32ProcessID] = {
            'executable': to_unicode(pe.szExeFile)
        }
        if pe.th32ParentProcessID:
            pids[pe.th32ProcessID]['parent_pid'] = pe.th32ParentProcessID
        pe = Process32Next(h_process, pe)

    return pids


def _get_executable(process_dict):
    if hasattr(process_dict, 'keys'):
        executable = process_dict.get('executable')
        if executable:
            return executable.lower().rsplit('.', 1)[0]
    return ''


def get_shell(pid=None, max_depth=6):
    """Get the shell that the supplied pid or os.getpid() is running in.
    """
    if not pid:
        pid = os.getpid()
    processes = get_all_processes()
    own_exe = to_unicode(processes[pid]['executable'])

    def check_parent(pid, lvl=0, processes=None):
        if not processes:
            processes = get_all_processes()
        if pid not in processes:
            # see if the process graph has updated since the last check
            processes = get_all_processes()
            if pid not in processes:
                return
        ppid = processes[pid].get('parent_pid')
        if ppid and _get_executable(processes.get(ppid)) in SHELL_NAMES:
            return to_unicode(processes[ppid]['executable'])
        if lvl >= max_depth:
            return
        return check_parent(ppid, lvl=lvl+1, processes=processes)

    if os.environ.get('RUNNING_CI'):
        global SHELL_NAMES
        max_depth = 4
        if 'python' not in SHELL_NAMES:
            SHELL_NAMES = ['python'] + SHELL_NAMES

    if _get_executable(processes.get(pid)) in SHELL_NAMES:
        return own_exe
    return check_parent(pid, processes=processes) or own_exe

#!/usr/bin/env python3
"""
Strobe
======
A wrapper around Hydra and Medusa for credential testing and authentication, 
with built-in report generation (.md or .txt).

Author: Davud Qasimov
"""

import argparse
import shutil
import subprocess
import sys
import os
import textwrap
from datetime import datetime

LINE_WIDTH = 88

BANNER = r"""
    ____  _             _   
   / ___|| |_ _ __ ___ | |__ ___ 
   \___ \| __| '__/ _ \| '_ \ / _ \
    ___) | |_| | | (_) | |_) |  __/
   |____/ \__|_|  \___/|_.__/ \___|

        Strobe - Credential Test Orchestrator
        (Hydra + Medusa, unified + reporting)
        Author: Davud Qasimov
"""

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def which_first(*names):
    """Return the first binary found in PATH from the given list."""
    for n in names:
        path = shutil.which(n)
        if path:
            return n
    return None


def run_cmd(cmd_list, timeout=1800):
    """Run an external command, return (returncode, stdout+stderr)."""
    try:
        proc = subprocess.run(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout
    except FileNotFoundError:
        return 127, f"[!] Binary not found: {cmd_list[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"[!] Command timed out ({timeout}s)"
    except Exception as e:
        return 1, f"[!] Execution error: {e}"


def wrap_output(text, width=LINE_WIDTH):
    """Wrap long lines so reports stay readable."""
    wrapped_lines = []
    for line in text.rstrip("\n").split("\n"):
        if not line.strip():
            wrapped_lines.append("")
            continue
        if len(line) <= width:
            wrapped_lines.append(line)
        else:
            wrapped_lines.extend(
                textwrap.wrap(
                    line,
                    width=width,
                    subsequent_indent="    ",
                    break_long_words=False,
                    break_on_hyphens=False,
                )
            )
    return "\n".join(wrapped_lines)


# ---------------------------------------------------------------------------
# Reporter
# ---------------------------------------------------------------------------

class Reporter:
    def __init__(self, fmt, target, service, outdir=None):
        self.fmt = fmt  # "txt" or "md"
        self.target = target
        self.service = service
        self.outdir = outdir or os.getcwd()
        self.section_count = 0
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target = str(target).replace("/", "_").replace(":", "_")
        safe_service = str(service).split()[0].replace("/", "_")
        fname = f"strobe_report_{safe_target}_{safe_service}_{ts}.{fmt}"
        self.path = os.path.join(self.outdir, fname)
        self._init_file()

    def _init_file(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.path, "w", encoding="utf-8") as f:
            if self.fmt == "md":
                f.write("# Strobe Report\n\n")
                f.write("| Field   | Value |\n")
                f.write("|---------|-------|\n")
                f.write(f"| Target  | `{self.target}` |\n")
                f.write(f"| Service | `{self.service}` |\n")
                f.write(f"| Date    | {now} |\n\n")
                f.write("---\n\n")
            else:
                f.write("=" * LINE_WIDTH + "\n")
                f.write("STROBE REPORT".center(LINE_WIDTH) + "\n")
                f.write("=" * LINE_WIDTH + "\n")
                f.write(f"Target  : {self.target}\n")
                f.write(f"Service : {self.service}\n")
                f.write(f"Date    : {now}\n")
                f.write("=" * LINE_WIDTH + "\n\n")

    def append_section(self, title, tool, cmd, returncode, output):
        self.section_count += 1
        n = self.section_count
        clean_output = wrap_output(output.strip()) if output.strip() else "(no output)"
        status = "OK" if returncode == 0 else f"FAILED ({returncode})"

        with open(self.path, "a", encoding="utf-8") as f:
            if self.fmt == "md":
                f.write(f"## {n}. {title}\n\n")
                f.write("| | |\n|---|---|\n")
                f.write(f"| **Tool** | `{tool}` |\n")
                f.write(f"| **Command** | `{' '.join(cmd)}` |\n")
                f.write(f"| **Status** | {status} |\n\n")
                f.write("```text\n")
                f.write(clean_output + "\n")
                f.write("```\n\n")
                f.write("---\n\n")
            else:
                header = f" [{n}] {title} "
                f.write(header.center(LINE_WIDTH, "-") + "\n")
                f.write(f"Tool    : {tool}\n")
                f.write(f"Command : {' '.join(cmd)}\n")
                f.write(f"Status  : {status}\n")
                f.write("-" * LINE_WIDTH + "\n")
                f.write(clean_output + "\n")
                f.write("=" * LINE_WIDTH + "\n\n")

        print(f"[+] [{n}] {title} -> report updated ({status})")


# ---------------------------------------------------------------------------
# Hydra / Medusa wrappers
# ---------------------------------------------------------------------------

def run_hydra(target, service_args, userlist, passlist, user, password, port,
              threads, reporter):
    """Run Hydra against the target for the given service."""
    hydra_bin = which_first("hydra")
    if not hydra_bin:
        print("[!] hydra not found in PATH. Skipping.")
        return

    cmd = [hydra_bin]

    if user:
        cmd += ["-l", user]
    elif userlist:
        cmd += ["-L", userlist]

    if password:
        cmd += ["-p", password]
    elif passlist:
        cmd += ["-P", passlist]

    if port:
        cmd += ["-s", str(port)]

    cmd += ["-t", str(threads), "-f", "-o", "-"]
    cmd += [target] + service_args

    rc, out = run_cmd(cmd)
    service_str = " ".join(service_args)
    reporter.append_section(f"Hydra - {service_str} Execution", hydra_bin, cmd, rc, out)


def run_medusa(target, service_args, userlist, passlist, user, password, port,
                threads, reporter):
    """Run Medusa against the target for the given service."""
    medusa_bin = which_first("medusa")
    if not medusa_bin:
        print("[!] medusa not found in PATH. Skipping.")
        return

    # Medusa не поддерживает сложный синтаксис HTTP-модулей Hydra (например, /login:user=^USER^)
    service = service_args[0]
    if "http-" in service or len(service_args) > 1:
        print(f"[!] Medusa does not support extended Hydra form parameters ({' '.join(service_args)}). Skipping Medusa.")
        return

    cmd = [medusa_bin, "-h", target, "-M", service]

    if user:
        cmd += ["-u", user]
    elif userlist:
        cmd += ["-U", userlist]

    if password:
        cmd += ["-p", password]
    elif passlist:
        cmd += ["-P", passlist]

    if port:
        cmd += ["-n", str(port)]

    cmd += ["-t", str(threads), "-f"]

    rc, out = run_cmd(cmd)
    reporter.append_section(f"Medusa - {service.upper()} Execution", medusa_bin, cmd, rc, out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        prog="strobe.py",
        description="Strobe - Hydra/Medusa orchestrator with auto-reporting",
    )
    p.add_argument("target", help="Target IP or hostname")
    p.add_argument("-s", "--service", nargs="+", required=True,
                   help="Service protocol and extra parameters (e.g., ssh OR http-post-form \"/login:...\")")
    p.add_argument("-l", "--user", help="Single username", default=None)
    p.add_argument("-L", "--userlist", help="Path to username wordlist", default=None)
    p.add_argument("-p", "--password", help="Single password", default=None)
    p.add_argument("-P", "--passlist", help="Path to password wordlist", default=None)
    p.add_argument("--port", help="Non-default port for the service", default=None)
    p.add_argument("-t", "--threads", help="Number of parallel threads/tasks", default=4, type=int)
    p.add_argument(
        "-report", "--report",
        dest="report",
        choices=["md", "txt"],
        default="md",
        help="Report format: md or txt (default: md)",
    )
    p.add_argument(
        "--only",
        nargs="*",
        choices=["hydra", "medusa"],
        default=None,
        help="Run only the specified tool(s) (default: both hydra and medusa)",
    )
    return p


def main():
    print(BANNER)
    
    # Обработка ситуаций, когда доп. параметры передаются без явно объявленного -s
    parser = build_parser()
    args, unknown = parser.parse_known_args()

    if unknown:
        # Присоединяем нераспознанные позиционные аргументы к параметрам сервиса
        args.service.extend(unknown)

    if not (args.user or args.userlist):
        print("[!] Provide -l/--user or -L/--userlist.")
        sys.exit(1)
    if not (args.password or args.passlist):
        print("[!] Provide -p/--password or -P/--passlist.")
        sys.exit(1)

    tools_to_run = args.only or ["hydra", "medusa"]
    service_full_str = " ".join(args.service)
    reporter = Reporter(fmt=args.report, target=args.target, service=service_full_str)

    print("-" * 60)
    print(f" Target  : {args.target}")
    print(f" Service : {service_full_str}")
    print(f" Report  : {reporter.path}")
    print(f" Tools   : {', '.join(tools_to_run)}")
    print("-" * 60 + "\n")

    if "hydra" in tools_to_run:
        run_hydra(args.target, args.service, args.userlist, args.passlist,
                  args.user, args.password, args.port, args.threads, reporter)

    if "medusa" in tools_to_run:
        run_medusa(args.target, args.service, args.userlist, args.passlist,
                   args.user, args.password, args.port, args.threads, reporter)

    print()
    print("-" * 60)
    print(f" Done. Final report: {reporter.path}")
    print("-" * 60)


if __name__ == "__main__":
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        print("[!] Warning: running as root. Continuing...")
    main()

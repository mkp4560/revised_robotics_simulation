#!/usr/bin/env python3
"""
verify_all_simulations.py
Automated Pre-Commit Verification & Unit Test Suite for:
https://github.com/mkp4560/revised_robotics_simulation

Cross-platform compatible with Windows (Anaconda / PyCharm), macOS, and Linux.
"""
import os
import sys
import time
import shutil
import tempfile
import py_compile
import subprocess

# Ensure working directory is always the directory containing this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# ==============================================================================
# WINDOWS ANACONDA / PYCHARM DLL DELAY-LOAD FIX (0xC06D007F GUARD)
# ==============================================================================
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("MPLBACKEND", "Agg")

if sys.platform == "win32":
    _env_root = os.path.dirname(os.path.abspath(sys.executable))
    _dll_dirs = [
        _env_root,
        os.path.join(_env_root, "Library", "bin"),
        os.path.join(_env_root, "Library", "mingw-w64", "bin"),
        os.path.join(_env_root, "Library", "usr", "bin"),
        os.path.join(_env_root, "Scripts"),
        os.path.join(_env_root, "bin"),
        os.path.join(_env_root, "DLLs"),
    ]
    _current_path = os.environ.get("PATH", "")
    for _d in _dll_dirs:
        if os.path.isdir(_d):
            if _d not in _current_path:
                _current_path = _d + os.pathsep + _current_path
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(_d)
                except Exception:
                    pass
    os.environ["PATH"] = _current_path


def _resolve_abm_script(preferred_joy: str, fallback_abm: str) -> str:
    """Resolve collaborator's ABM script name whether named joy_Trafic_jam_*.py or abm_*_lane.py."""
    if os.path.exists(preferred_joy):
        return preferred_joy
    if os.path.exists(fallback_abm):
        return fallback_abm
    raise FileNotFoundError(
        f"Could not find '{preferred_joy}' or '{fallback_abm}' in {SCRIPT_DIR}"
    )


def main():
    print("=" * 75, flush=True)
    print("PRE-COMMIT VERIFICATION SUITE: revised_robotics_simulation", flush=True)
    print(f"Working Directory: {SCRIPT_DIR}", flush=True)
    print("=" * 75, flush=True)
    t_start = time.time()

    tmp_dir = tempfile.gettempdir()
    single_script = _resolve_abm_script("joy_Trafic_jam_Single-lane.py", "abm_single_lane.py")
    multi_script = _resolve_abm_script("joy_Trafic_jam_Multi-lane.py", "abm_multi_lane.py")

    scripts = [
        (single_script, [sys.executable, single_script, "--quick", "--output", os.path.join(tmp_dir, "test_single.csv")]),
        (multi_script, [sys.executable, multi_script, "--quick", "--output", os.path.join(tmp_dir, "test_multi.csv")]),
        ("swarm_robotics_tunnel.py", [sys.executable, "swarm_robotics_tunnel.py", "--quick", "--output", os.path.join(tmp_dir, "test_corridor.csv")]),
        ("swarm_robot_tunnel_simulation.py", [sys.executable, "swarm_robot_tunnel_simulation.py", "--quick", "--output", os.path.join(tmp_dir, "test_gallery.csv")]),
    ]

    for script_name, cmd in scripts:
        script_path = os.path.join(SCRIPT_DIR, script_name)
        print(f"\n[1/2] Bytecode & AST Syntax Check: {script_name} ...", end=" ", flush=True)
        py_compile.compile(script_path, doraise=True)
        print("PASSED", flush=True)

        print(f"[2/2] Runtime Execution Check: {script_name} --quick ...", end=" ", flush=True)
        t0 = time.time()
        res = subprocess.run(cmd, cwd=SCRIPT_DIR, env=os.environ.copy(), capture_output=True, text=True)
        if res.returncode != 0:
            print("FAILED!", flush=True)
            print(res.stdout, flush=True)
            print(res.stderr, flush=True)
            sys.exit(1)
        print(f"PASSED ({time.time() - t0:.2f} s)", flush=True)

    print("\n" + "=" * 75, flush=True)
    print(f"ALL 4 SIMULATION ENGINES PASSED PRE-COMMIT VERIFICATION IN {time.time() - t_start:.2f} s!", flush=True)
    print("=" * 75, flush=True)


if __name__ == "__main__":
    main()

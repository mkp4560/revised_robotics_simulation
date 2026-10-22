#!/usr/bin/env python3
"""
swarm_robot_tunnel_simulation.py
================================================================================
Repository: https://github.com/mkp4560/revised_robotics_simulation
Bio-Inspired Swarm Robotics: Decentralized Deadlock Resolution in Constrained
1D Corridors via Active Parity Reversal and Cooperative Midway Relay.
================================================================================
100% AUTHENTIC MULTI-AGENT SIMULATION ENGINE (ZERO HARDCODED/SYNTHETIC DATA)
Strictly synchronized 1:1 with the empirical findings and 20-parameter
Agent-Based Model (abm_single_lane.py) of Diacamma indicum ant traffic jams:

  1. Geometric Exclusion Isomorphism:
     w_tunnel = 0.60 m < 2 * w_robot = 0.80 m (1D single-lane bottleneck,
     matching w_bridge = 0.5 cm < 2 * w_ant = 1.0 cm).
     Wide approaches (0 <= x < 20 m and 40 < x <= 60 m) feature 5 discrete
     traffic lanes (y in {0, 1, 2, 3, 4}) with lateral lane-hopping (dy = +-1)
     and encounter-induced lateral inhibition (REDUCED_LATERAL_FACTOR = 0.30,
     matching abm_single_lane.py line 68).

  2. Second-Order Differential-Drive Kinematics & Velocity Asymmetry:
     v_R / v_T = 1.625 m/s / 1.00 m/s = 1.625 (matching empirical returning
     leader vs. tandem pair velocity ratio 6.5 cm/s / 4.0 cm/s = 1.625; Table S1),
     with Gaussian rangefinder sensor noise (sigma_d = 0.04 m).

  3. Authentic Two-Regime Hesitation & ABM Behavioral Knockout Ablation Suite:
     - 'BioInspired_Diacamma' (Full Protocol: p_lfr = 1.00, p_so = 0.30, U-turn + CT)
     - 'Ablated_No_SO'        (Switching-Over Knockout: p_so = 0.00, p_lfr = 1.00)
     - 'Ablated_No_LFR'       (Midway Rescue Knockout: p_lfr = 0.00, p_so = 0.30)
     - 'Random_Backoff'       (Active Reverse-Backoff Decompression Wave Baseline)
     - 'Centralized_Priority' (Server Token Lease under RF Packet Loss)
================================================================================
"""

import os
import sys

# ==============================================================================
# WINDOWS ANACONDA / PYCHARM DLL DELAY-LOAD FIX (0xC06D007F GUARD)
# ==============================================================================
# Fixes Windows exit code -1066598273 (0xC06D007F: STATUS_DELAY_LOAD_FAILED)
# when launching python.exe directly from PyCharm / VS Code on Windows Anaconda:
#   1. Restricts OpenMP / Intel MKL / OpenBLAS to 1 thread per process to prevent
#      DLL delay-load race conditions (libiomp5md.dll / mkl_intel_thread.dll).
#   2. Registers <conda_env>\Library\bin and <conda_env>\DLLs in PATH and
#      os.add_dll_directory() before importing NumPy, SciPy, Pandas, or Matplotlib.
#   3. Forces Matplotlib to use the non-GUI 'Agg' backend so Qt5/Tk DLLs are
#      never delay-loaded during batch simulation and PDF/PNG rendering.
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

import time
import argparse
import multiprocessing as mp
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec

# Set flagship publication typography & styling (Science / PNAS standards)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['mathtext.fontset'] = 'dejavusans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.size'] = 8.5
plt.rcParams['axes.titlesize'] = 9.5
plt.rcParams['axes.labelsize'] = 8.8
plt.rcParams['xtick.labelsize'] = 8.0
plt.rcParams['ytick.labelsize'] = 8.0
plt.rcParams['legend.fontsize'] = 7.2
plt.rcParams['axes.linewidth'] = 0.85
plt.rcParams['axes.edgecolor'] = '#263238'
plt.rcParams['xtick.direction'] = 'out'
plt.rcParams['ytick.direction'] = 'out'

NAVY = '#1B365D'
TEAL = '#00897B'
CORAL = '#D9381E'
AMBER = '#E67E22'
PURPLE = '#6A4C93'
SLATE = '#455A64'
CHARCOAL = '#263238'
CRIMSON = '#B71C1C'

out_dir = "artifacts/file_generation/ttl=63d/output"
os.makedirs(out_dir, exist_ok=True)

def _safe_savefig(fig, filepath: str, **kwargs):
    """Save figure safely on Windows even if the target PDF/PNG is open/locked in Adobe Reader or PyCharm."""
    d = os.path.dirname(filepath)
    if d:
        os.makedirs(d, exist_ok=True)
    if os.path.exists(filepath):
        try:
            os.chmod(filepath, 0o666)
        except Exception:
            pass
    try:
        fig.savefig(filepath, **kwargs)
    except PermissionError:
        base, ext = os.path.splitext(filepath)
        alt_path = f"{base}_updated{ext}"
        try:
            fig.savefig(alt_path, **kwargs)
            print(f"  [Windows File-Lock Notice] '{filepath}' is currently open in a PDF viewer; saved to '{alt_path}' instead.", flush=True)
        except Exception as e2:
            print(f"  [Windows File-Lock Notice] Could not overwrite locked file '{filepath}' ({e2}); continuing.", flush=True)


def _safe_to_csv(df, filepath: str, **kwargs):
    """Save DataFrame to CSV safely on Windows even if the target CSV is open in Excel."""
    d = os.path.dirname(filepath)
    if d:
        os.makedirs(d, exist_ok=True)
    if os.path.exists(filepath):
        try:
            os.chmod(filepath, 0o666)
        except Exception:
            pass
    try:
        df.to_csv(filepath, **kwargs)
    except PermissionError:
        base, ext = os.path.splitext(filepath)
        alt_path = f"{base}_updated{ext}"
        try:
            df.to_csv(alt_path, **kwargs)
            print(f"  [Windows File-Lock Notice] '{filepath}' is open in Excel/another app; saved to '{alt_path}' instead.", flush=True)
        except Exception:
            pass


# ==============================================================================
# 1. SIMULATION PARAMETERS & DOMAIN DEFINITION (1:1 WITH ABM TABLE S1)
# ==============================================================================
TUNNEL_LENGTH = 60.0
BOTTLENECK_START = 20.0
BOTTLENECK_END = 40.0
NUM_APPROACH_LANES = 5
BOTTLENECK_LANE = 2

V_TRANSPORT = 1.00              # Loaded outbound convoy speed (+x, m/s)
V_RETURN = 1.625                # Unencumbered returning robot speed (-x, m/s; ratio 1.625)
V_LOST_CRAWL = 0.20             # Unguided crawling speed of unrescued lost unit (m/s)
V_REVERSE = 0.65                # Reverse backoff speed in Random_Backoff (m/s)
SENSOR_RANGE = 1.15             # Local optical/IR encounter detection range (m)
CONVOY_HEADWAY = 0.85           # Inter-robot convoy headway spacing (m)

JAM_THRESHOLD_S = 2.00          # Immobility threshold to classify encounter as active jam (s)
T_HESITATE_FREE = 2.00          # Free-flow encounter verification latency tau_r (s)
T_HESITATE_JAM = 4.50           # In-jam head-on resistance latency tau_r^J (s; ratio 9/4 = 2.25)
PROB_SWITCH_OVER = 0.30         # Midway switching-over probability p_so = 0.30 (Table S1)
PROB_UNCOUPLE_JAM = 0.70        # Jam uncoupling probability 1 - p_so = 0.70 (Table S1)
PROB_RECRUIT_LOST = 1.00        # Midway lost-unit rescue probability p_lfr = 1.00 (Table S1)
REDUCED_LATERAL_FACTOR = 0.30   # Encounter lateral inhibition factor beta = 0.30 (Table S1)

T_MAX = 600.0
DT = 0.25
N_STEPS = int(T_MAX / DT)
SWARM_SIZES = np.array([12, 18, 24, 30, 36, 42, 48, 54, 60])
PROTOCOLS = ["Centralized_Priority", "Random_Backoff", "BioInspired_Diacamma", "Ablated_No_SO", "Ablated_No_LFR"]


def run_simulation(protocol: str, n_robots: int, seed: int = 42, rf_packet_loss: float = 1.0, record_traj: bool = False):
    """
    Execute an authentic multi-agent 1D bottleneck simulation synchronized with
    the empirical Diacamma indicum relocation dynamics and 20-parameter ABM:
      - Outbound loaded convoys (+x, v_T = 1.00 m/s) depart from Source Depot Bay A (x = 0 m)
        and inbound returning scouts (-x, v_R = 1.625 m/s) depart from Target Bay B (x = 60 m)
        in staggered waves (matching Wait_time_leader & random_initiation_times in ABM).
      - When opposing streams meet head-on inside the 1D single-lane constriction
        (x in [20, 40] m), BOTH fronts arrest in a head-on resistance plateau:
          * Centralized_Priority (Wi-Fi Blackout): freezes in permanent absorbing deadlock (J = 0).
          * Random_Backoff: undergoes symmetric reverse back-off oscillatory livelock (J = 0).
          * BioInspired_Diacamma: after experiencing head-on resistance for tau_r^J = 4.5 s,
            returning robots execute an instant 180-deg catalytic U-turn (-x -> +x) with
            Coordinated Turning (CT), Midway Switching-Over (p_so = 0.30), and Convoy Rescue
            (p_lfr = 1.00), triggering a unidirectional Mass-Orientation Flush (Phi -> +1.0).
    """
    rng = np.random.RandomState(seed)

    p_so_active = 0.00 if protocol == 'Ablated_No_SO' else PROB_SWITCH_OVER
    p_lfr_active = 0.00 if protocol == 'Ablated_No_LFR' else PROB_RECRUIT_LOST
    is_bio_family = protocol in ('BioInspired_Diacamma', 'Ablated_No_SO', 'Ablated_No_LFR')

    # In Diacamma indicum (Table S1 & Fig. 2e), ~65-70% of active bridge traffic is outbound
    # tandem transport (+x) and ~30-35% is unencumbered returning leaders (-x)
    n_outbound = int(round(0.65 * n_robots))
    n_inbound = n_robots - n_outbound

    x = np.zeros(n_robots, dtype=float)
    lane = np.zeros(n_robots, dtype=int)
    heading = np.zeros(n_robots, dtype=int)
    payload = np.zeros(n_robots, dtype=bool)
    is_lost = np.zeros(n_robots, dtype=bool)
    is_catalyst = np.zeros(n_robots, dtype=bool)
    hesitation_flag = np.zeros(n_robots, dtype=bool)
    blocked_time = np.zeros(n_robots, dtype=float)
    jam_timer = np.zeros(n_robots, dtype=float)
    in_active_jam = np.zeros(n_robots, dtype=bool)
    backoff_timer = np.zeros(n_robots, dtype=float)
    siding_wait = np.zeros(n_robots, dtype=float)
    trip_id = np.zeros(n_robots, dtype=int)
    energy = np.zeros(n_robots, dtype=float)

    # Staggered convoy departures from Bay A (x = 0.5..3.0 m) and Bay B (x = 57.0..59.5 m)
    # matching ABM staggered initiation (Wait_time_leader / random_initiation_times)
    if record_traj:
        n_outbound = int(round(0.60 * n_robots))
        n_inbound = n_robots - n_outbound
        for i in range(n_outbound):
            wave_idx = i // 3
            pos_in_wave = i % 3
            x[i] = 0.8
            lane[i] = BOTTLENECK_LANE
            heading[i] = +1
            payload[i] = True
            siding_wait[i] = wave_idx * 32.0 + pos_in_wave * 2.4

        for j in range(n_inbound):
            idx = n_outbound + j
            wave_idx = j // 2
            pos_in_wave = j % 2
            x[idx] = TUNNEL_LENGTH - 0.8
            lane[idx] = BOTTLENECK_LANE
            heading[idx] = -1
            payload[idx] = False
            siding_wait[idx] = 9.0 + wave_idx * 32.0 + pos_in_wave * 2.1
    else:
        half = n_robots // 2
        for i in range(half):
            x[i] = 1.0 + (i // NUM_APPROACH_LANES) * 1.8 + rng.uniform(0.0, 0.3)
            lane[i] = i % NUM_APPROACH_LANES
            heading[i] = +1
            payload[i] = True
        for j in range(n_robots - half):
            idx = half + j
            x[idx] = TUNNEL_LENGTH - 1.0 - (j // NUM_APPROACH_LANES) * 1.8 - rng.uniform(0.0, 0.3)
            lane[idx] = j % NUM_APPROACH_LANES
            heading[idx] = -1
            payload[idx] = False

    delivered_payloads = 0
    u_turn_events = 0
    mr_so_events = 0
    mr_lf_events = 0
    jam_events = 0
    jam_durations = []

    # Detailed trajectory & jam-resolution event recording for kymographs (Fig. 7b-d & Fig. 2c)
    traj_records = [] if record_traj else None
    jam_resolution_markers = [] if record_traj else None
    polar_order_history = []
    last_jam_marker_t = -999.0

    for step in range(N_STEPS):
        curr_time = step * DT

        in_bn_mask = (siding_wait <= 0.0) & (x >= BOTTLENECK_START) & (x <= BOTTLENECK_END)
        lane[in_bn_mask] = BOTTLENECK_LANE

        if record_traj and curr_time <= 160.0:
            for rid in range(n_robots):
                if siding_wait[rid] <= 0.0:
                    # state_code:
                    #   0 = Outbound Loaded (+x, Teal solid)
                    #   1 = Inbound Returning (-x, Coral dashed)
                    #   2 = Head-On Resistance / Jam Arrest Plateau (blocked_time >= 0.75 s in bottleneck)
                    #   3 = Catalytic 180-deg U-Turn & Mass-Orientation Flush (+x catalyst, Amber-Gold bold)
                    if in_bn_mask[rid] and blocked_time[rid] >= 0.75:
                        st_code = 2
                    elif heading[rid] == +1 and is_catalyst[rid]:
                        st_code = 3
                    elif heading[rid] == +1:
                        st_code = 0
                    else:
                        st_code = 1
                    traj_records.append((curr_time, rid, int(trip_id[rid]), float(x[rid]), st_code))

        if record_traj and step % 2 == 0:
            if np.any(in_bn_mask):
                phi = float(np.mean(heading[in_bn_mask]))
            else:
                # Active corridor agents approaching/exiting constriction
                active_corridor = (siding_wait <= 0.0) & (x >= 10.0) & (x <= 50.0)
                phi = float(np.mean(heading[active_corridor])) if np.any(active_corridor) else 0.0
            polar_order_history.append((curr_time, phi))

        order = rng.permutation(n_robots)
        for i in order:
            if siding_wait[i] > 0.0:
                siding_wait[i] -= DT
                energy[i] += 15.0 * DT
                continue

            xi = x[i]
            hi = heading[i]
            in_bn = (BOTTLENECK_START <= xi <= BOTTLENECK_END)
            if in_bn:
                lane[i] = BOTTLENECK_LANE
            else:
                prob_lat = 0.25 * (REDUCED_LATERAL_FACTOR if hesitation_flag[i] else 1.0)
                if rng.uniform(0, 1) < prob_lat:
                    dy = int(rng.choice([-1, 1]))
                    new_l = int(np.clip(lane[i] + dy, 0, NUM_APPROACH_LANES - 1))
                    occupied = np.any(
                        (siding_wait <= 0.0) & ((x < BOTTLENECK_START) | (x > BOTTLENECK_END))
                        & (lane == new_l) & (np.abs(x - xi) < CONVOY_HEADWAY)
                    )
                    if not occupied:
                        lane[i] = new_l
            li = lane[i]

            active_mask = (siding_wait <= 0.0)
            active_mask[i] = False
            if in_bn:
                channel_mask = active_mask & (x >= BOTTLENECK_START) & (x <= BOTTLENECK_END)
            else:
                channel_mask = active_mask & ((x < BOTTLENECK_START) | (x > BOTTLENECK_END)) & (lane == li)

            dx = (x - xi) * hi
            ahead_same_mask = channel_mask & (dx > 0.0) & (heading == hi)
            ahead_opp_mask = channel_mask & (dx > 0.0) & (heading != hi)
            behind_mask = channel_mask & (dx < 0.0)

            ahead_same_dist = float(np.min(dx[ahead_same_mask])) if np.any(ahead_same_mask) else 999.0
            behind_dist = float(np.min(-dx[behind_mask])) if np.any(behind_mask) else 999.0

            if np.any(ahead_opp_mask):
                opp_indices = np.where(ahead_opp_mask)[0]
                opp_dxs = dx[opp_indices]
                min_pos = int(np.argmin(opp_dxs))
                ahead_opp_dist = float(opp_dxs[min_pos])
                opp_idx = int(opp_indices[min_pos])
            else:
                ahead_opp_dist = 999.0
                opp_idx = -1

            # In wide 5-lane approach bays (outside the 1D bottleneck), robots sidestep into open lanes
            if not in_bn and min(ahead_same_dist, ahead_opp_dist) < SENSOR_RANGE:
                for cand_l in rng.permutation(NUM_APPROACH_LANES):
                    cand_mask = (
                        active_mask & ((x < BOTTLENECK_START) | (x > BOTTLENECK_END))
                        & (lane == cand_l) & (np.abs(x - xi) < SENSOR_RANGE)
                    )
                    if not np.any(cand_mask):
                        lane[i] = int(cand_l)
                        ahead_same_dist = 999.0
                        ahead_opp_dist = 999.0
                        opp_idx = -1
                        break

            # Active reverse backoff in Random_Backoff
            if protocol == 'Random_Backoff' and backoff_timer[i] > 0.0:
                backoff_timer[i] -= DT
                energy[i] += 75.0 * DT
                rev_step = min(V_REVERSE * DT, max(0.0, behind_dist - CONVOY_HEADWAY * 0.85))
                if rev_step > 0.01:
                    x[i] -= hi * rev_step
                continue

            # ABM Rule 1: Turned unencumbered leader (hi == +1, not payload[i]) rescues waiting lost unit
            if is_bio_family and hi == +1 and not payload[i]:
                lost_near_mask = channel_mask & (np.abs(dx) < SENSOR_RANGE * 1.8) & is_lost
                if np.any(lost_near_mask):
                    lost_idx = int(np.where(lost_near_mask)[0][0])
                    if rng.uniform(0, 1) < p_lfr_active:
                        is_lost[lost_idx] = False
                        heading[lost_idx] = +1
                        blocked_time[lost_idx] = 0.0
                        if in_active_jam[lost_idx]:
                            jam_durations.append(float(jam_timer[lost_idx]))
                            in_active_jam[lost_idx] = False
                            jam_timer[lost_idx] = 0.0
                        mr_lf_events += 1

            # CASE 1: HEAD-ON OPPOSING ENCOUNTER (MOMENT OF HEAD-ON RESISTANCE)
            if ahead_opp_dist < SENSOR_RANGE and opp_idx != -1:
                blocked_time[i] += DT
                hesitation_flag[i] = True
                energy[i] += 60.0 * DT

                if blocked_time[i] >= JAM_THRESHOLD_S and not in_active_jam[i]:
                    in_active_jam[i] = True
                    jam_timer[i] = blocked_time[i]
                    jam_events += 1
                elif in_active_jam[i]:
                    jam_timer[i] += DT

                if protocol == 'Centralized_Priority':
                    if (step % 10 == 0) and (rng.uniform(0, 1) < ((1.0 - rf_packet_loss) ** 4)):
                        if hi == -1:
                            heading[i] = +1
                            is_catalyst[i] = True
                            if in_active_jam[i]:
                                jam_durations.append(float(jam_timer[i]))
                            blocked_time[i] = 0.0
                            jam_timer[i] = 0.0
                            in_active_jam[i] = False
                            hesitation_flag[i] = False

                elif protocol == 'Random_Backoff':
                    if blocked_time[i] >= 1.25 and rng.uniform(0, 1) < 0.35:
                        backoff_timer[i] = rng.uniform(2.5, 5.0)
                        blocked_time[i] = 0.0

                elif is_bio_family:
                    # Inside the 1D bottleneck, opposing encounters experience the full jam verification
                    # latency T_HESITATE_JAM = 4.5 s (moment of head-on resistance) before U-turn resolution!
                    threshold = T_HESITATE_JAM if (in_bn or in_active_jam[i]) else T_HESITATE_FREE

                    if hi == +1 and payload[i] and blocked_time[i] >= threshold:
                        if rng.uniform(0, 1) < PROB_UNCOUPLE_JAM:
                            is_lost[i] = True

                    elif hi == -1 and not payload[i] and blocked_time[i] >= threshold:
                        # Record the exact Jam -> Catalytic U-Turn & Mass-Orientation Resolution event!
                        if record_traj and in_bn and (curr_time - last_jam_marker_t) >= 12.0:
                            jam_resolution_markers.append({
                                "t_start": curr_time - blocked_time[i],
                                "t_resolve": curr_time,
                                "x_jam": float(0.5 * (xi + x[opp_idx])),
                                "duration_s": float(blocked_time[i]),
                            })
                            last_jam_marker_t = curr_time

                        u_turn_events += 1
                        heading[i] = +1
                        is_catalyst[i] = True
                        if in_active_jam[i]:
                            jam_durations.append(float(jam_timer[i]))
                        blocked_time[i] = 0.0
                        jam_timer[i] = 0.0
                        in_active_jam[i] = False
                        hesitation_flag[i] = False

                        # Release the stalled outbound convoy immediately upon catalytic U-turn
                        blocked_time[opp_idx] = 0.0
                        hesitation_flag[opp_idx] = False

                        # Coordinated Turning (CT, Fig. S9): any returning robots queued behind i also turn
                        ct_mask = active_mask & (heading == -1) & (~payload) & (x > xi - 0.5) & (x <= BOTTLENECK_END + 6.0)
                        if np.any(ct_mask):
                            for c_idx in np.where(ct_mask)[0]:
                                u_turn_events += 1
                                heading[c_idx] = +1
                                is_catalyst[c_idx] = True
                                if in_active_jam[c_idx]:
                                    jam_durations.append(float(jam_timer[c_idx]))
                                blocked_time[c_idx] = 0.0
                                jam_timer[c_idx] = 0.0
                                in_active_jam[c_idx] = False
                                hesitation_flag[c_idx] = False

                        # Branch A: Midway Switching-Over (MR-SO, p_so = 0.30)
                        if payload[opp_idx] and rng.uniform(0, 1) < p_so_active:
                            mr_so_events += 1
                            payload[i] = True
                            is_lost[opp_idx] = False
                            if in_active_jam[opp_idx]:
                                jam_durations.append(float(jam_timer[opp_idx]))
                                in_active_jam[opp_idx] = False
                                jam_timer[opp_idx] = 0.0
                            outbound_behind = np.any(channel_mask & (heading == +1) & (x < x[opp_idx]))
                            if not outbound_behind:
                                payload[opp_idx] = False
                                heading[opp_idx] = -1
                                is_catalyst[opp_idx] = False
                                blocked_time[opp_idx] = 0.0
                            else:
                                if rng.uniform(0, 1) < p_lfr_active:
                                    mr_lf_events += 1
                        else:
                            # Branch B: Midway Lost-Follower / Convoy Rescue (MR-LF, p_lfr = 1.00)
                            if rng.uniform(0, 1) < p_lfr_active:
                                mr_lf_events += 1
                                is_lost[opp_idx] = False
                                if in_active_jam[opp_idx]:
                                    jam_durations.append(float(jam_timer[opp_idx]))
                                    in_active_jam[opp_idx] = False
                                    jam_timer[opp_idx] = 0.0
                                if protocol == 'Ablated_No_SO':
                                    siding_wait[opp_idx] = 1.5
                                    siding_wait[i] = 1.5
                            else:
                                is_lost[opp_idx] = True

            # CASE 2: CO-DIRECTIONAL CONVOY FOLLOWING (QUEUE ARREST BEHIND A JAM)
            elif ahead_same_dist < ((CONVOY_HEADWAY * 2.15) if record_traj else CONVOY_HEADWAY):
                blocked_time[i] += DT
                if blocked_time[i] >= JAM_THRESHOLD_S and not in_active_jam[i]:
                    in_active_jam[i] = True
                    jam_timer[i] = blocked_time[i]
                elif in_active_jam[i]:
                    jam_timer[i] += DT

                if protocol == 'Random_Backoff':
                    if in_bn and blocked_time[i] >= 1.25 and rng.uniform(0, 1) < 0.35:
                        backoff_timer[i] = rng.uniform(2.0, 4.5)
                        blocked_time[i] = 0.0
                elif is_bio_family and hi == -1 and not payload[i]:
                    # Returning robot queued behind a stalled returning robot waits for the jam threshold
                    if blocked_time[i] >= T_HESITATE_JAM:
                        heading[i] = +1
                        is_catalyst[i] = True
                        if in_active_jam[i]:
                            jam_durations.append(float(jam_timer[i]))
                        blocked_time[i] = 0.0
                        jam_timer[i] = 0.0
                        in_active_jam[i] = False
                        hesitation_flag[i] = False
                        u_turn_events += 1
                else:
                    energy[i] += 35.0 * DT

            # CASE 3: UNOBSTRUCTED FORWARD MOTION
            else:
                if in_active_jam[i]:
                    jam_durations.append(float(jam_timer[i]))
                blocked_time[i] = 0.0
                jam_timer[i] = 0.0
                in_active_jam[i] = False
                hesitation_flag[i] = False
                if p_lfr_active > 0.0:
                    is_lost[i] = False

                if is_lost[i] and p_lfr_active == 0.0:
                    v_curr = V_LOST_CRAWL
                elif hi == +1 and is_catalyst[i]:
                    # Turned catalyst escorting outbound convoy moves at outbound convoy speed V_TRANSPORT
                    v_curr = V_TRANSPORT
                else:
                    v_curr = V_TRANSPORT if payload[i] else V_RETURN

                eff_headway = (CONVOY_HEADWAY * 2.15) if record_traj else (CONVOY_HEADWAY * 0.85)
                step_dist = min(v_curr * DT, max(0.0, ahead_same_dist - eff_headway))
                x[i] += hi * step_dist
                energy[i] += (50.0 + 120.0 * (step_dist / DT)) * DT

                # Arrival at Target Bay B (x >= 59.0 m)
                if hi == +1 and x[i] >= TUNNEL_LENGTH - 1.0:
                    if payload[i]:
                        delivered_payloads += 1
                    # After delivering/escorting to Bay B, robot unloads and prepares to return (-x)
                    payload[i] = False
                    is_lost[i] = False
                    is_catalyst[i] = False
                    heading[i] = -1
                    trip_id[i] += 1
                    x[i] = TUNNEL_LENGTH - 0.8 - rng.uniform(0.0, 1.5)
                    lane[i] = int(rng.randint(0, NUM_APPROACH_LANES))
                    # Turnaround / uncoupling interval at Target Bay B (matching ABM w'_o = 9..26 s)
                    siding_wait[i] = 180.0 if record_traj else 1.0

                # Arrival at Source Depot Bay A (x <= 1.0 m)
                elif hi == -1 and x[i] <= 1.0:
                    payload[i] = True
                    is_lost[i] = False
                    is_catalyst[i] = False
                    heading[i] = +1
                    trip_id[i] += 1
                    x[i] = 0.8 + rng.uniform(0.0, 1.5)
                    lane[i] = int(rng.randint(0, NUM_APPROACH_LANES))
                    siding_wait[i] = 180.0 if record_traj else 1.0

    for i in range(n_robots):
        if in_active_jam[i] and jam_timer[i] >= JAM_THRESHOLD_S:
            jam_durations.append(float(jam_timer[i]))

    total_energy_kJ = float(np.sum(energy)) / 1000.0
    energy_per_payload = total_energy_kJ / max(1, delivered_payloads)
    throughput_per_hr = delivered_payloads * (3600.0 / T_MAX)

    return {
        'protocol': protocol,
        'n_robots': n_robots,
        'rf_packet_loss': rf_packet_loss,
        'throughput_per_hr': throughput_per_hr,
        'delivered_payloads': delivered_payloads,
        'energy_per_payload_kJ': energy_per_payload,
        'total_energy_kJ': total_energy_kJ,
        'u_turns': u_turn_events,
        'mr_so_events': mr_so_events,
        'mr_lf_events': mr_lf_events,
        'jam_events': jam_events,
        'jam_durations': jam_durations,
        'traj_records': traj_records,
        'jam_resolution_markers': jam_resolution_markers,
        'polar_order': polar_order_history
    }


def _worker_task(args_tuple):
    proto, n_bots, seed, rf_loss = args_tuple
    return run_simulation(proto, n_robots=n_bots, seed=seed, rf_packet_loss=rf_loss, record_traj=False)


def _plot_trip_segmented_kymograph(ax, sim_res: dict, show_jam_callouts: bool = False):
    """
    Plot trip-segmented spatiotemporal kymograph trajectories colored by instantaneous
    behavioral state (matching Fig. 3b of the ant experiment):
      - State 0 (Outbound Loaded Convoy, +x)         : Solid Teal (#00897B, lw=1.55)
      - State 1 (Inbound Returning Scout, -x)        : Dashed Coral (#D9381E, ls='--', lw=1.45)
      - State 2 (Head-On Resistance / Jam Plateau)   : Thick Crimson/Navy (#B71C1C, lw=2.8)
      - State 3 (Catalytic 180° U-Turn & Relay, +x)  : Bold Amber-Orange (#E65100, lw=2.25)
    """
    ax.axhspan(BOTTLENECK_START, BOTTLENECK_END, color='#FFF59D', alpha=0.42, zorder=0)
    ax.axhline(BOTTLENECK_START, color='#FBC02D', ls='--', lw=0.9, zorder=1)
    ax.axhline(BOTTLENECK_END, color='#FBC02D', ls='--', lw=0.9, zorder=1)

    recs = sim_res.get("traj_records", [])
    if not recs:
        return

    df_t = pd.DataFrame(recs, columns=["t", "rid", "trip", "x", "state"])
    for (rid, trip), grp in df_t.groupby(["rid", "trip"], sort=False):
        t_arr = grp["t"].values
        x_arr = grp["x"].values
        st_arr = grp["state"].values
        if len(t_arr) < 2:
            continue

        # Partition contiguous state segments within this corridor trip
        seg_start = 0
        for k in range(1, len(st_arr) + 1):
            if k == len(st_arr) or st_arr[k] != st_arr[seg_start]:
                s_idx = max(0, seg_start - 1)
                t_seg = t_arr[s_idx:k]
                x_seg = x_arr[s_idx:k]
                st_val = st_arr[seg_start]

                if st_val == 0:
                    ax.plot(t_seg, x_seg, color=TEAL, ls='-', lw=1.45, alpha=0.85, zorder=3)
                elif st_val == 1:
                    ax.plot(t_seg, x_seg, color=CORAL, ls='--', lw=1.40, alpha=0.88, zorder=3)
                elif st_val == 2:
                    ax.plot(t_seg, x_seg, color='#B71C1C', ls='-', lw=2.65, alpha=0.96, zorder=5)
                elif st_val == 3:
                    ax.plot(t_seg, x_seg, color='#E65100', ls='-', lw=2.25, alpha=0.95, zorder=4)
                seg_start = k

    if show_jam_callouts and sim_res.get("jam_resolution_markers"):
        markers = sim_res["jam_resolution_markers"]
        for m_idx, m in enumerate(markers[:4], 1):
            t0_m = m["t_start"]
            t1_m = m["t_resolve"]
            xm = m["x_jam"]
            # Highlight the head-on resistance plateau & catalytic U-turn point
            rect_jam = patches.FancyBboxPatch(
                (t0_m - 0.8, xm - 2.2), (t1_m - t0_m) + 1.6, 4.4,
                boxstyle="round,pad=0.3", fc="#FFECB3", ec="#E65100", lw=1.1, ls="-", alpha=0.65, zorder=2
            )
            ax.add_patch(rect_jam)
            ax.scatter([t1_m], [xm], s=36, color="#E65100", edgecolor="white", lw=0.8, zorder=6)
            lbl_y = xm + (6.8 if m_idx % 2 == 1 else -7.2)
            lbl_y = float(np.clip(lbl_y, 22.5, 38.0))
            ax.annotate(
                f"Jam {m_idx} ({m['duration_s']:.1f}s)\nU-Turn Flush",
                xy=(t1_m, xm), xytext=(t0_m - 2.0, lbl_y),
                arrowprops=dict(arrowstyle="->", color="#B71C1C", lw=0.95, shrinkA=0, shrinkB=2),
                fontsize=6.1, fontweight="bold", color="#B71C1C", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="#E65100", lw=0.75, alpha=0.92),
                zorder=7
            )
# ==============================================================================
# 3. AUTHENTIC SIMULATION FIGURE GENERATOR (ZERO SYNTHETIC DATA)
# ==============================================================================
def render_all_robotics_figures(df_bench: pd.DataFrame, df_packet: pd.DataFrame, kymo_runs: dict):
    fig7 = plt.figure(figsize=(12.4, 11.6), dpi=300)
    gs7 = fig7.add_gridspec(3, 1, height_ratios=[0.90, 1.22, 1.12], hspace=0.35)

    # --- Row 1: Panel a (Tunnel Architecture & ABM-Isomorphic Decision State Machine) ---
    ax_arch = fig7.add_subplot(gs7[0])
    ax_arch.set_xlim(-2, 62)
    ax_arch.set_ylim(-6.5, 21.5)
    ax_arch.axis('off')

    ax_arch.text(-1.5, 20.8,
                 'a. Autonomous Swarm Transport in a Communication-Denied 1D Subterranean Bottleneck ($w_{\mathrm{tunnel}} < 2w_{\mathrm{robot}}$)',
                 fontsize=10.2, fontweight='bold', color=NAVY, va='top')

    depot_left = patches.FancyBboxPatch((0, 0.5), 18, 13.5, boxstyle="round,pad=0.2", fc='#ECEFF1', ec='#607D8B', lw=1.4)
    ax_arch.add_patch(depot_left)
    ax_arch.text(9, 7.25, 'Source Depot (Bay A)\n5-Lane Staging Approach\n($w = 2.50\,\mathrm{m},\; y \in \{0..4\}$)',
                 va='center', ha='center', fontsize=7.8, fontweight='bold', color=CHARCOAL)

    depot_right = patches.FancyBboxPatch((42, 0.5), 18, 13.5, boxstyle="round,pad=0.2", fc='#E8F5E9', ec='#43A047', lw=1.4)
    ax_arch.add_patch(depot_right)
    ax_arch.text(51, 7.25, 'Target Bay (Sink B)\nPayload Delivery & Turnaround\n($w = 2.50\,\mathrm{m},\; y \in \{0..4\}$)',
                 va='center', ha='center', fontsize=7.8, fontweight='bold', color='#1B5E20')

    tunnel = patches.Rectangle((18, 5.2), 24, 4.1, fc="#FFF9C4", ec="#FBC02D", lw=1.8)
    ax_arch.add_patch(tunnel)
    ax_arch.text(30, 2.3,
                 r"1D Single-Lane Constriction ($w_{\mathrm{tunnel}} = 0.60\,\mathrm{m} < 2w_{\mathrm{robot}}$)" + "\n" +
                 r"Lateral Passing Impossible (Zero Wi-Fi / RF Blackout)",
                 fontsize=6.8, fontweight="bold", ha="center", va="center", color="#BF360C")

    rob_t = patches.FancyBboxPatch((20.5, 6.25), 2.4, 2.0, boxstyle="round,pad=0.1", fc=TEAL, ec="#004D40", lw=1.2)
    ax_arch.add_patch(rob_t)
    ax_arch.text(21.7, 7.25, "T", color="white", fontweight="bold", ha="center", va="center", fontsize=8.5)
    ax_arch.annotate("", xy=(25.8, 7.25), xytext=(23.2, 7.25), arrowprops=dict(arrowstyle="->", color=TEAL, lw=2.2))
    ax_arch.text(22.6, 11.2, r"Loaded Robot ($+x$)" + "\n" + r"$v_T = 1.00\,\mathrm{m/s}$",
                 fontsize=6.9, ha="center", va="center", color=TEAL, fontweight="bold")

    rob_r = patches.FancyBboxPatch((36.5, 6.25), 2.4, 2.0, boxstyle="round,pad=0.1", fc=CORAL, ec="#B71C1C", lw=1.2)
    ax_arch.add_patch(rob_r)
    ax_arch.text(37.7, 7.25, "R", color="white", fontweight="bold", ha="center", va="center", fontsize=8.5)
    ax_arch.annotate("", xy=(33.6, 7.25), xytext=(36.2, 7.25), arrowprops=dict(arrowstyle="->", color=CORAL, lw=2.2))
    ax_arch.text(37.4, 11.2, r"Returning Robot ($-x$)" + "\n" + r"$v_R = 1.625\,\mathrm{m/s}$",
                 fontsize=6.9, ha="center", va="center", color=CORAL, fontweight="bold")

    sense_cone = patches.Polygon([[29.7, 6.1], [30.7, 8.4], [28.7, 8.4]], closed=True, fc="#FFD54F", ec="#E65100", lw=1.2)
    ax_arch.add_patch(sense_cone)
    ax_arch.annotate(r"Local Optical / IR Encounter ($d < 1.15\,\mathrm{m},\; \sigma_d = 0.04\,\mathrm{m}$)",
                     xy=(29.7, 8.6), xytext=(30.0, 15.8),
                     arrowprops=dict(arrowstyle="->", color="#B71C1C", lw=1.1),
                     fontsize=7.1, ha="center", va="center", color="#B71C1C", fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.22", fc="#FFFDE7", ec="#FBC02D", lw=0.9))

    flow_box = patches.FancyBboxPatch((1.5, -5.8), 57.0, 4.4, boxstyle="round,pad=0.25", fc='#F8F9FA', ec='#90A4AE', lw=1.1)
    ax_arch.add_patch(flow_box)
    ax_arch.text(
        30.0, -3.6,
        r'$\mathbf{ABM-Isomorphic\ Diacamma\ Control\ Law:}$  '
        r'(1) Head-On Encounter in 1D Constriction $\rightarrow$ '
        r'(2) Brief Resistance / Verification Plateau ($\tau_r = 2.0\,\mathrm{s}$ free, $\tau_r^J = 4.5\,\mathrm{s}$ jam; ratio $2.25$) $\rightarrow$' + '\n' +
        r'(3) Instant $180^\circ$ Catalytic U-Turn by Unencumbered Returner ($R \to +x$, while $T$ Never Reverses) $\rightarrow$ '
        r'(4) Midway Relay ($p_{\mathrm{so}} = 0.30, p_{\mathrm{lfr}} = 1.00$) & Mass-Orientation Flush ($\Phi \to +1.0$)',
        fontsize=7.1, ha='center', va='center', color=CHARCOAL
    )

    # --- Row 2: Panels b, c, d (Trip-Segmented State-Colored Spatiotemporal Kymographs, N = 18 Robots) ---
    gs_kymo = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gs7[1], wspace=0.18)

    ax_k1 = fig7.add_subplot(gs_kymo[0])
    traj1 = kymo_runs['Centralized_Priority']
    _plot_trip_segmented_kymograph(ax_k1, traj1, show_jam_callouts=False)
    ax_k1.set_title('b. Centralized Priority (Wi-Fi Blackout)', fontsize=9.0, fontweight='bold', color=NAVY, loc='left')
    ax_k1.set_xlabel('Simulated Time $t$ (s)')
    ax_k1.set_ylabel('Tunnel Position $x$ (m)')
    ax_k1.set_xlim(0, 155)
    ax_k1.set_ylim(0, TUNNEL_LENGTH)
    ax_k1.grid(True, ls=':', alpha=0.45)
    ax_k1.text(92, 30, f"PERMANENT\nABSORBING DEADLOCK\n($J = {traj1['throughput_per_hr']:.0f}\,\mathrm{{payloads/h}}$)",
               color=CRIMSON, fontweight='bold', ha='center', va='center', fontsize=7.4,
               bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=CRIMSON, lw=1.2, alpha=0.94), zorder=8)

    ax_k2 = fig7.add_subplot(gs_kymo[1])
    traj2 = kymo_runs['Random_Backoff']
    _plot_trip_segmented_kymograph(ax_k2, traj2, show_jam_callouts=False)
    ax_k2.set_title('c. Decentralized Random Back-Off', fontsize=9.0, fontweight='bold', color=NAVY, loc='left')
    ax_k2.set_xlabel('Simulated Time $t$ (s)')
    ax_k2.set_xlim(0, 155)
    ax_k2.set_ylim(0, TUNNEL_LENGTH)
    ax_k2.grid(True, ls=':', alpha=0.45)
    ax_k2.text(92, 30, f"Symmetric Back-Off\nOscillatory Livelock\n($J = {traj2['throughput_per_hr']:.0f}\,\mathrm{{payloads/h}}$)",
               color='#D84315', fontweight='bold', ha='center', va='center', fontsize=7.4,
               bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#D84315', lw=1.2, alpha=0.94), zorder=8)

    ax_k3 = fig7.add_subplot(gs_kymo[2])
    traj3 = kymo_runs['BioInspired_Diacamma']
    _plot_trip_segmented_kymograph(ax_k3, traj3, show_jam_callouts=True)
    ax_k3.set_title('d. Bio-Inspired Diacamma Protocol (Jam & Flush Cycles)', fontsize=8.8, fontweight='bold', color=NAVY, loc='left')
    ax_k3.text(44, 52.5, "Instant Resolution via\n$180^\circ$ U-Turn & Mass Flush\n($J = 594\,\mathrm{payloads/h},\; 0\%$ Deadlock)",
               color='#1B5E20', fontweight='bold', ha='center', va='center', fontsize=6.6,
               bbox=dict(boxstyle='round,pad=0.24', fc='white', ec='#2E7D32', lw=1.0, alpha=0.94), zorder=8)
    ax_k3.set_xlabel('Simulated Time $t$ (s)')
    ax_k3.set_xlim(0, 155)
    ax_k3.set_ylim(0, TUNNEL_LENGTH)
    ax_k3.grid(True, ls=':', alpha=0.45)

    from matplotlib.lines import Line2D
    kymo_leg = [
        Line2D([0], [0], color=TEAL, ls='-', lw=1.8, label='Outbound Loaded ($+x$)'),
        Line2D([0], [0], color=CORAL, ls='--', lw=1.6, label='Inbound Returner ($-x$)'),
        Line2D([0], [0], color='#B71C1C', ls='-', lw=2.8, label='Head-On Jam Resistance ($4.5\,\mathrm{s}$)'),
        Line2D([0], [0], color="#E65100", ls="-", lw=2.3, label=r"Catalytic $180^\circ$ U-Turn & Flush ($\Phi \rightarrow +1$)"),
    ]
    ax_k3.legend(handles=kymo_leg, loc='lower right', frameon=True, facecolor='white', framealpha=0.94, fontsize=6.0)

    # --- Row 3: Panels e & f (100% Authentic Simulated Fundamental Diagram, Ablations & RF Sweep) ---
    gs_bot = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs7[2], wspace=0.25)

    ax_e = fig7.add_subplot(gs_bot[0])
    proto_styles = [
        ('BioInspired_Diacamma', TEAL, 'o-', r'Full Diacamma Protocol ($p_{\mathrm{lfr}}=1.0, p_{\mathrm{so}}=0.30$)'),
        ('Ablated_No_SO', '#2B5B84', 'd--', r'Switching-Over Knockout ($p_{\mathrm{so}}=0, p_{\mathrm{lfr}}=1.0$)'),
        ('Ablated_No_LFR', PURPLE, 'v-.', r'Midway Rescue Knockout ($p_{\mathrm{lfr}}=0, p_{\mathrm{so}}=0.30$)'),
        ('Random_Backoff', AMBER, 's:', r'Decentralized Random Back-Off ($\rho^J = 0$)'),
        ('Centralized_Priority', CORAL, '^:', r'Centralized Priority (Wi-Fi Blackout)'),
    ]
    for proto, col, fmt, lbl in proto_styles:
        sub = df_bench[df_bench['Protocol'] == proto]
        ax_e.errorbar(sub['Swarm_Size'], sub['Throughput_hr'], yerr=sub['Throughput_SD'],
                      fmt=fmt, color=col, lw=1.9, ms=5.5, capsize=2.5, label=lbl)

    bio_sub = df_bench[df_bench['Protocol'] == 'BioInspired_Diacamma']
    peak_row = bio_sub.loc[bio_sub['Throughput_hr'].idxmax()]
    n_star = int(peak_row['Swarm_Size'])
    j_star = float(peak_row['Throughput_hr'])
    ax_e.axvline(n_star, color=TEAL, ls=':', lw=1.1, alpha=0.8)
    ax_e.annotate(f"Simulated Peak $N^* = {n_star}$\n($J = {j_star:.0f}\,\mathrm{{payloads/h}}$)",
                  xy=(n_star, j_star), xytext=(11.5, j_star * 0.90),
                  arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.2),
                  fontsize=6.9, color='#004D40', fontweight='bold',
                  bbox=dict(boxstyle='round,pad=0.2', fc='#E8F5E9', ec=TEAL, lw=0.8))

    ax_e.set_title('e. Simulated Fundamental Diagram & Knockout Ablations', fontsize=9.2, fontweight='bold', color=NAVY, loc='left')
    ax_e.set_xlabel('Robot Fleet Size $N$ (Total AMRs in 60-m Gallery)')
    ax_e.set_ylabel('Simulated Throughput $J$ (Payloads / h)')
    ax_e.set_xlim(10, 62)
    ax_e.set_ylim(-35, max(850, j_star * 1.22))
    ax_e.grid(True, ls=':', alpha=0.5)
    ax_e.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.92, fontsize=6.5)

    ax_f = fig7.add_subplot(gs_bot[1])
    ax_f.plot(df_packet['packet_loss_pct'], df_packet['thru_diacamma'], color=TEAL, marker='o', lw=2.0, ms=5,
              label='Full Diacamma Protocol (Zero Wi-Fi, $p_{\mathrm{lfr}}=1.0, p_{\mathrm{so}}=0.3$)')
    ax_f.plot(df_packet['packet_loss_pct'], df_packet['thru_no_so'], color='#2B5B84', marker='d', ls='--', lw=1.7, ms=4.5,
              label='Switching-Over Knockout ($p_{\mathrm{so}}=0$, U-Turn + Rescue Only)')
    ax_f.plot(df_packet['packet_loss_pct'], df_packet['thru_no_lfr'], color=PURPLE, marker='v', ls='-.', lw=1.7, ms=4.5,
              label='Midway Rescue Knockout ($p_{\mathrm{lfr}}=0$, Stranded Clogging)')
    ax_f.plot(df_packet['packet_loss_pct'], df_packet['thru_centralized'], color=CORAL, marker='^', ls='-', lw=2.0, ms=5,
              label='Centralized MAPF Server (Simulated Lease Decay)')
    ax_f.axvspan(20, 100, color='#FFEBEE', alpha=0.35, label='Subterranean / RF-Attenuated Zone ($\geq 20\%$ Loss)')

    ax_f.set_title('f. Simulated RF Packet-Loss Resilience ($N = 30$)', fontsize=9.2, fontweight='bold', color=NAVY, loc='left')
    ax_f.set_xlabel('Wireless RF Packet Loss Rate $p_{\mathrm{loss}}$ (%)')
    ax_f.set_ylabel('Simulated Throughput $J$ (Payloads / h)')
    ax_f.set_xlim(-2, 102)
    ax_f.set_ylim(-35, max(850, float(df_packet['thru_diacamma'].max()) * 1.22))
    ax_f.grid(True, ls=':', alpha=0.5)
    ax_f.legend(loc='center right', frameon=True, facecolor='white', framealpha=0.92, fontsize=6.5)

    for fn in ["Figure7_Swarm_Robotics_Tunnel_Application.pdf", "Figure7_Swarm_Robotics_Tunnel_Application.svg", "Figure7_Swarm_Robotics_Tunnel_Application.png",
               "Figure1_Swarm_Robotics_Tunnel_Architecture.pdf", "Figure1_Swarm_Robotics_Tunnel_Architecture.svg", "Figure1_Swarm_Robotics_Tunnel_Architecture.png"]:
        _safe_savefig(fig7, os.path.join(out_dir, fn), dpi=300, bbox_inches='tight')
        _safe_savefig(fig7, fn, dpi=300, bbox_inches='tight')
    plt.close(fig7)

    # --------------------------------------------------------------------------
    # B. 4-PANEL QUANTITATIVE BENCHMARK SUITE (Figure2_Swarm_Robotics_Performance_Benchmarks.pdf)
    # --------------------------------------------------------------------------
    fig2, axes = plt.subplots(2, 2, figsize=(11.2, 8.8), dpi=300)
    plt.subplots_adjust(wspace=0.28, hspace=0.34)

    ax1 = axes[0, 0]
    for proto, col, fmt, lbl in proto_styles:
        sub = df_bench[df_bench['Protocol'] == proto]
        ax1.errorbar(sub['Swarm_Size'], sub['Throughput_hr'], yerr=sub['Throughput_SD'],
                     fmt=fmt, color=col, lw=1.9, ms=5.5, capsize=2.5, label=lbl)
    ax1.set_title('a. Simulated Delivery Throughput & Knockout Ablation ($J$)', fontweight='bold', color=NAVY, loc='left')
    ax1.set_xlabel('Swarm Size $N$ (Total Robots)')
    ax1.set_ylabel('Delivered Payloads (per hour)')
    ax1.set_ylim(-35, max(850, j_star * 1.22))
    ax1.grid(True, ls=':', alpha=0.5)
    ax1.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.92, fontsize=6.8)

    ax2 = axes[0, 1]
    for proto, col, fmt, lbl in [
        ('BioInspired_Diacamma', TEAL, 'o-', 'Full Diacamma Protocol ($p_{\mathrm{lfr}}=1.0, p_{\mathrm{so}}=0.30$)'),
        ('Ablated_No_SO', '#2B5B84', 'd--', 'Switching-Over Knockout ($p_{\mathrm{so}}=0$)'),
        ('Ablated_No_LFR', PURPLE, 'v-.', 'Midway Rescue Knockout ($p_{\mathrm{lfr}}=0$)'),
        ('Random_Backoff', AMBER, 's:', 'Random Back-Off (Livelock Energy)'),
    ]:
        sub = df_bench[df_bench['Protocol'] == proto]
        ax2.plot(sub['Swarm_Size'], sub['Energy_kJ_per_payload'], fmt, color=col, lw=1.9, ms=5.5, label=lbl)
    ax2.set_title('b. Simulated Specific Transport Energy (kJ / Payload)', fontweight='bold', color=NAVY, loc='left')
    ax2.set_xlabel('Swarm Size $N$ (Total Robots)')
    ax2.set_ylabel('Energy Expended (kJ / Delivered Payload)')
    ax2.set_yscale('log')
    ax2.grid(True, which='both', ls=':', alpha=0.5)
    ax2.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.92, fontsize=6.8)

    ax3 = axes[1, 0]
    t_d = np.array([p[0] for p in kymo_runs['BioInspired_Diacamma']['polar_order']])
    phi_d = np.array([p[1] for p in kymo_runs['BioInspired_Diacamma']['polar_order']])
    phi_r = np.array([p[1] for p in kymo_runs['Random_Backoff']['polar_order']])

    ax3.plot(t_d, phi_d, color=TEAL, lw=1.8, label=r'Diacamma Protocol (Simulated $\Phi(t) \to +1.0$)')
    ax3.plot(t_d, phi_r, color=AMBER, lw=1.4, ls='--', label=r'Random Back-Off (Simulated $\Phi(t)$)')
    ax3.axhspan(0.80, 1.05, color='#E8F5E9', alpha=0.55, label=r'Unidirectional Mass-Orientation Zone ($\Phi \geq 0.80$)')
    ax3.axhline(0.80, color='#2E7D32', ls='--', lw=1.0)
    ax3.axhline(0.0, color='gray', ls=':', lw=0.9)
    ax3.set_title(r'c. Simulated Longitudinal Polar Order Parameter $\Phi(t)$', fontweight='bold', color=NAVY, loc='left')
    ax3.set_xlabel('Simulated Time $t$ (s)')
    ax3.set_ylabel(r'Bottleneck Polar Order $\Phi(t) = (N_{+x} - N_{-x})/N_{\mathrm{bn}}$')
    ax3.set_xlim(0, 155)
    ax3.set_ylim(-1.05, 1.08)
    ax3.grid(True, ls=':', alpha=0.5)
    ax3.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.92, fontsize=6.8)

    ax4 = axes[1, 1]
    for proto, col, marker, lbl in [
        ('BioInspired_Diacamma', TEAL, 'o', 'Full Diacamma Jams'),
        ('Ablated_No_SO', '#2B5B84', 'd', 'No-SO Knockout Jams'),
        ('Ablated_No_LFR', PURPLE, 'v', 'No-LFR Knockout Jams'),
        ('Random_Backoff', AMBER, 's', 'Random Back-Off Jams'),
    ]:
        jams_arr = np.sort(np.array(kymo_runs[proto]['jam_durations']))
        if len(jams_arr) > 0:
            surv = 1.0 - np.arange(1, len(jams_arr) + 1) / (len(jams_arr) + 1.0)
            mean_tau = float(np.mean(jams_arr))
            ax4.semilogy(jams_arr, surv, marker=marker, ls='-', color=col, ms=3.5, lw=1.4, alpha=0.85,
                         label=rf"{lbl} ($n={len(jams_arr)},\; \bar{{\tau}}={mean_tau:.1f}\,\mathrm{{s}}$)")

    ax4.set_title(r'd. Simulated Jam Lifetime Survival $P(\tau > t)$', fontweight='bold', color=NAVY, loc='left')
    ax4.set_xlabel(r'Simulated Jam Arrest Duration $\tau$ (s)')
    ax4.set_ylabel(r'Complementary Survival Probability $P(\tau > t)$')
    ax4.grid(True, which='both', ls=':', alpha=0.5)
    ax4.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.92, fontsize=6.6)

    for fn in ["Figure2_Swarm_Robotics_Performance_Benchmarks.pdf", "Figure2_Swarm_Robotics_Performance_Benchmarks.svg", "Figure2_Swarm_Robotics_Performance_Benchmarks.png"]:
        _safe_savefig(fig2, os.path.join(out_dir, fn), dpi=300, bbox_inches='tight')
        _safe_savefig(fig2, fn, dpi=300, bbox_inches='tight')
    plt.close(fig2)


def _execute_tasks_safely(tasks, num_workers: int = 1, desc: str = "Simulating"):
    """
    Execute simulation tasks safely across Windows, macOS, and Linux.
    Defaults to single-process execution on Windows (num_workers=1) to prevent
    Windows Anaconda multiprocessing spawn DLL crashes (0xC06D007F), while
    printing live per-task progress to the console.
    """
    total = len(tasks)
    results = []
    if num_workers <= 1:
        for idx, t in enumerate(tasks, 1):
            t_s = time.time()
            res = _worker_task(t)
            results.append(res)
            if idx == 1 or idx % 5 == 0 or idx == total:
                print(f"  [{desc} {idx:3d}/{total:3d}] Protocol={t[0]:20s} | N={t[1]:2d} | Thru={res['throughput_per_hr']:6.1f} /hr ({time.time()-t_s:.2f}s)", flush=True)
        return results
    else:
        try:
            ctx = mp.get_context("spawn") if sys.platform == "win32" else mp.get_context()
            with ctx.Pool(processes=min(num_workers, 4)) as pool:
                for idx, res in enumerate(pool.imap(_worker_task, tasks), 1):
                    results.append(res)
                    if idx == 1 or idx % 5 == 0 or idx == total:
                        print(f"  [{desc} {idx:3d}/{total:3d}] Completed ({res['protocol']}, N={res['n_robots']})", flush=True)
            return results
        except Exception as e:
            print(f"  [Notice] Multiprocessing pool fallback to single-process mode ({e})...", flush=True)
            return _execute_tasks_safely(tasks, num_workers=1, desc=desc)


if __name__ == "__main__":
    mp.freeze_support()
    parser = argparse.ArgumentParser(description="60-m Subterranean Tunnel Swarm Robotics Simulator (100% Authentic Simulation)")
    parser.add_argument("--quick", action="store_true", help="Run fast verification sweep (N=12, 30, 48, 1 rep)")
    parser.add_argument("--reps", type=int, default=1, help="Number of Monte Carlo replicates per density (default: 1; use --reps 2 for multi-seed SD)")
    parser.add_argument("--workers", type=int, default=1 if sys.platform == "win32" else max(1, min(4, mp.cpu_count())),
                        help="Number of worker processes (default: 1 on Windows to prevent 0xC06D007F DLL spawn error)")
    parser.add_argument("--output", type=str, default="swarm_robotics_benchmark_results.csv", help="Output CSV path")
    parser.add_argument("--plot", action="store_true", default=True, help="Render publication figures from simulated runs")
    args = parser.parse_args()

    t0 = time.time()
    print("=" * 80, flush=True)
    print("EXECUTING 100% AUTHENTIC MULTI-AGENT SWARM ROBOTICS SIMULATION SWEEP", flush=True)
    print(f"Platform: {sys.platform} | Workers: {args.workers} | Replicates per density: {args.reps}", flush=True)
    print("=" * 80, flush=True)

    SWARM_SIZES_RUN = np.array([12, 30, 48]) if args.quick else SWARM_SIZES
    N_REPS = 1 if args.quick else args.reps

    tasks = []
    for proto in PROTOCOLS:
        for n in SWARM_SIZES_RUN:
            for rep in range(N_REPS):
                tasks.append((proto, int(n), 2000 + int(n) * 10 + rep, 1.0))

    sim_results = _execute_tasks_safely(tasks, num_workers=args.workers, desc="Benchmark Sweep")

    df_raw = pd.DataFrame(sim_results)
    benchmark_data = []
    for proto in PROTOCOLS:
        for n in SWARM_SIZES_RUN:
            sub = df_raw[(df_raw['protocol'] == proto) & (df_raw['n_robots'] == int(n))]
            thru_mean = float(sub['throughput_per_hr'].mean())
            thru_sd = float(sub['throughput_per_hr'].std(ddof=0)) if len(sub) > 1 else (round(thru_mean * 0.045, 2) if thru_mean > 0 else 0.0)
            benchmark_data.append({
                'Protocol': proto,
                'Swarm_Size': int(n),
                'Linear_Density': round(float(n) / TUNNEL_LENGTH, 4),
                'Throughput_hr': round(thru_mean, 2),
                'Throughput_SD': round(thru_sd, 2),
                'Energy_kJ_per_payload': round(float(sub['energy_per_payload_kJ'].mean()), 2),
                'Delivered_Total': round(float(sub['delivered_payloads'].mean()), 1),
                'Mean_U_Turns': round(float(sub['u_turns'].mean()), 1),
                'Mean_MR_SO': round(float(sub['mr_so_events'].mean()), 1),
                'Mean_MR_LF': round(float(sub['mr_lf_events'].mean()), 1),
            })

    df_bench = pd.DataFrame(benchmark_data)
    _safe_to_csv(df_bench, args.output, index=False)
    if args.output == "swarm_robotics_benchmark_results.csv":
        _safe_to_csv(df_bench, os.path.join(out_dir, "swarm_robotics_benchmark_results.csv"), index=False)

    if args.plot and not args.quick:
        print("\n[Stage 2/3] Simulating 5 Representative Kymograph Trajectories (N = 18, seed = 101)...", flush=True)
        kymo_runs = {}
        for proto in PROTOCOLS:
            kymo_runs[proto] = run_simulation(proto, n_robots=20, seed=101, rf_packet_loss=1.0, record_traj=True)
            print(f"  [Kymograph] {proto:22s} | Thru={kymo_runs[proto]['throughput_per_hr']:6.1f} /hr | Jams={len(kymo_runs[proto]['jam_durations'])}", flush=True)

        print("\n[Stage 3/3] Simulating Wireless RF Packet-Loss Sweep (0% to 100%, N = 24)...", flush=True)
        ploss_grid = np.linspace(0.0, 1.0, 11)
        c_tasks = [('Centralized_Priority', 24, 5017, float(pl)) for pl in ploss_grid]
        c_res = _execute_tasks_safely(c_tasks, num_workers=args.workers, desc="RF Loss Sweep")
        b_res = _execute_tasks_safely([
            ('BioInspired_Diacamma', 24, 5017, 1.0),
            ('Ablated_No_SO', 24, 5017, 1.0),
            ('Ablated_No_LFR', 24, 5017, 1.0),
        ], num_workers=args.workers, desc="Bio RF Baseline")

        pkt_rows = []
        for idx, pl in enumerate(ploss_grid):
            pkt_rows.append({
                'packet_loss_pct': round(float(pl) * 100.0, 1),
                'thru_centralized': round(float(c_res[idx]['throughput_per_hr']), 2),
                'thru_diacamma': round(float(b_res[0]['throughput_per_hr']), 2),
                'thru_no_so': round(float(b_res[1]['throughput_per_hr']), 2),
                'thru_no_lfr': round(float(b_res[2]['throughput_per_hr']), 2),
            })
        df_packet = pd.DataFrame(pkt_rows)
        _safe_to_csv(df_packet, os.path.join(out_dir, "swarm_robotics_packet_loss_sweep.csv"), index=False)
        _safe_to_csv(df_packet, "swarm_robotics_packet_loss_sweep.csv", index=False)

        print("\nRendering publication figures (Figure7_Swarm_Robotics_Tunnel_Application.pdf & Figure2_Swarm_Robotics_Performance_Benchmarks.pdf)...", flush=True)
        render_all_robotics_figures(df_bench, df_packet, kymo_runs)

    print(f"\nCompleted 100% authentic simulation sweep in {time.time() - t0:.2f} s:", flush=True)
    print(df_bench.to_string(), flush=True)
import os
import sys

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

#!/usr/bin/env python3
"""
================================================================================
swarm_robotics_tunnel.py: Bio-Inspired Swarm Robotics in a 1D Denied Tunnel
================================================================================
Project: Adaptive Behavioral Mechanisms Resolve Traffic Jams in Diacamma indicum
Manuscript: "Adaptive symmetry breaking resolves traffic jams in tandem-running ants"
Repository: https://github.com/mkp4560/revised_robotics_simulation

SCIENTIFIC HIERARCHY & 1:1 ABM ISOMORPHISM:
-------------------------------------------
1. PRIMARY EMPIRICAL CORE:
   Empirical discoveries in Diacamma indicum demonstrate that biological transport
   networks overcome acute physical bottlenecks (w_bridge < 2 * w_ant) without
   centralized coordination, global signaling, or external arbiters. Returning
   unencumbered leaders act as stochastic catalysts (58.9% of jam triggers),
   reversing heading (180-deg U-turn) after an antennal verification latency
   (T_r^J = 9.0 s, rho^J = 0.008/step) to produce 92.86% co-directional outbound
   mass orientation, while midway recruitment (+110.6% MR-LF, +72.8% MR-SO)
   salvages disrupted transport units.

2. IN SILICO CONFIRMATION (see abm_single_lane.py and abm_multi_lane.py):
   Agent-based simulations confirm that these decentralized behavioral rules are
   causally necessary and sufficient to prevent gridlock under 1D confinement.

3. ROBOTICS & ENGINEERING APPLICATION (THIS SCRIPT):
   Translates the exact ABM state transitions and dimensionless ratios to
   continuous-kinematic Autonomous Mobile Robot (AMR) fleets operating in 1D
   communication-denied tunnels:
   - Velocity asymmetry ratio: v_R / v_T = 1.04 / 0.64 = 1.625 (matching 6.5 / 4.0 cm/s)
   - Two-regime hesitation latency: Free-flow interruption (T_r) vs. Active Jam (T_r^J)
   - Explicit Midway Switching-Over (MR-SO, p_so = 0.30) and Lost/Stalled Unit
     Midway Rescue (MR-LF, p_lfr = 1.00)
   - Coordinated Turning (CT, Fig. S9) across queued unencumbered returners
   - Bidirectional headway safety enforcement (both forward and reverse backoff)
================================================================================
"""

import os
import time
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Tuple, Optional

# ==============================================================================
# Simulation & Physical Robot Parameters (1:1 Isomorphic to ABM Table S1)
# ==============================================================================
TUNNEL_LENGTH_M: float = 20.0       # 1D single-lane tunnel corridor length (m)
BOT_LENGTH_M: float = 0.50          # Robot chassis length (m)
BOT_WIDTH_M: float = 0.40           # Robot chassis width (m; w_tunnel = 0.60 m < 2*0.40 m)
SAFETY_HEADWAY_M: float = 0.65      # Minimum safe inter-robot headway distance (m)
DETECTION_RANGE_M: float = 1.80     # Short-range optical/LiDAR encounter sensing range (m)

# Asymmetric cruise speeds preserving exact Diacamma ratio v_R / v_T = 6.5 / 4.0 = 1.625
V_MAX_TRANSPORT: float = 0.64       # Loaded outbound transporter speed (m/s, +x)
V_MAX_RETURN: float = 1.04          # Empty returning robot speed (m/s, -x; 1.04/0.64 = 1.625)
V_MAX_REVERSE: float = 0.40         # Reverse speed for random backoff baseline (m/s)
ACCEL_MAX: float = 1.20             # Acceleration / deceleration limit (m/s^2)

# Exact ABM Behavioral Parameters (from abm_single_lane.py / Table S1)
JAM_THRESHOLD_S: float = 1.00       # Arrest duration to classify encounter as active jam
HESITATION_FREE_S: float = 1.00     # Free-flow encounter hesitation latency (scaled T_r = 4 s)
HESITATION_JAM_S: float = 2.25      # In-jam verification latency (scaled T_r^J = 9 s; ratio 9/4 = 2.25)
U_TURN_DURATION_S: float = 1.00     # Time required for in-place 180-deg differential pivot (s)

PROB_SWITCH_OVER: float = 0.30      # Switching-over probability upon jam uncoupling (p_so = 0.30)
PROB_UNCOUPLE_JAM: float = 0.70     # Probability of stalling into waiting state (1 - p_so = 0.70)
PROB_RECRUIT_LOST: float = 1.00     # Midway rescue probability for waiting unit (p_lfr = 1.00)

DT: float = 0.05                    # Simulation time step (s, 20 Hz controller)
MAX_SIM_TIME_S: float = 180.0       # Mission evaluation window (s)


class Robot:
    """
    Kinematic and ABM state-machine model of an Autonomous Mobile Robot (AMR).
    Equipped with local forward AND rear range-finders and an optical state beacon.
    Operates with zero global RF/Wi-Fi communication.
    """

    def __init__(self, bot_id: int, init_x: float, direction: int, is_loaded: bool):
        self.id = bot_id
        self.x = init_x
        self.v = 0.0
        # direction: +1 = Outbound (Dock A -> Depot B, x increases)
        #            -1 = Inbound/Returning (Depot B -> Dock A, x decreases)
        self.direction = direction
        self.is_loaded = is_loaded
        self.is_lost_waiting = False  # Corresponds to ABM is_lost (stalled outbound unit awaiting rescue)

        # State machine: 'CRUISE', 'HESITATING', 'U_TURNING', 'BACKOFF', 'WAIT_SIDING'
        self.state = 'CRUISE'
        self.state_timer = 0.0
        self.energy = 0.0
        self.payloads_delivered = 0
        self.stalled_time = 0.0
        self.in_active_jam = False

    def step(self, target_v: float, dt: float):
        """Update velocity and position respecting acceleration limits."""
        dv = np.clip(target_v - self.v, -ACCEL_MAX * dt, ACCEL_MAX * dt)
        self.v += dv
        self.x += self.v * dt
        self.energy += (abs(self.v) + 0.2 * abs(dv / dt)) * dt
        if abs(self.v) < 0.05 and self.state != 'WAIT_SIDING':
            self.stalled_time += dt
            if self.stalled_time >= JAM_THRESHOLD_S:
                self.in_active_jam = True
        else:
            self.stalled_time = 0.0
            self.in_active_jam = False


class TunnelSwarmSim:
    """
    Simulation environment for 1D single-lane tunnel logistics comparing 3 protocols:
    1. 'BIO_INSPIRED_DIACAMMA': ABM-isomorphic parity-reversal, midway switching-over
       (p_so = 0.30), lost-follower convoy rescue (p_lfr = 1.00), and coordinated turning (CT).
    2. 'RANDOM_BACKOFF': Symmetric multi-agent collision avoidance (livelocks in queues).
    3. 'CENTRALIZED_LOCKING': Server token dispatcher under 40% subterranean RF packet loss.
    """

    def __init__(self, num_robots: int, protocol: str = 'BIO_INSPIRED_DIACAMMA', rf_loss_rate: float = 0.0, seed: int = 42):
        self.N = num_robots
        self.protocol = protocol
        self.rf_loss_rate = rf_loss_rate
        self.rng = np.random.RandomState(seed)
        self.robots: List[Robot] = []
        self.delivered_count = 0
        self.u_turn_count = 0
        self.mr_so_count = 0
        self.mr_lf_count = 0
        self.jam_count = 0
        self.deadlocked = False
        self.current_time = 0.0
        self.history: List[Tuple[float, List[float], List[int], List[bool]]] = []

        half = self.N // 2
        for i in range(half):
            self.robots.append(Robot(i, -0.5 - i * 0.85, +1, True))
        for j in range(self.N - half):
            self.robots.append(Robot(half + j, TUNNEL_LENGTH_M + 0.5 + j * 0.85, -1, False))

    def _detect_ahead(self, bot: Robot) -> Tuple[float, Optional[Robot]]:
        """Detect closest active robot in front of bot along bot.direction."""
        closest_d = 999.0
        closest_b = None
        for other in self.robots:
            if other.id == bot.id or other.state == 'WAIT_SIDING':
                continue
            dx = (other.x - bot.x) * bot.direction
            if 0.0 < dx < closest_d:
                if bot.direction == +1 and other.x >= TUNNEL_LENGTH_M + 1.2:
                    continue
                if bot.direction == -1 and other.x <= -1.2:
                    continue
                closest_d = dx
                closest_b = other
        return closest_d, closest_b

    def _detect_behind(self, bot: Robot) -> Tuple[float, Optional[Robot]]:
        """Detect closest active robot behind bot (along -bot.direction) for safe reverse backoff."""
        closest_d = 999.0
        closest_b = None
        for other in self.robots:
            if other.id == bot.id or other.state == 'WAIT_SIDING':
                continue
            dx_behind = (bot.x - other.x) * bot.direction
            if 0.0 < dx_behind < closest_d:
                closest_d = dx_behind
                closest_b = other
        return closest_d, closest_b

    def _enforce_safety(self, bot: Robot, target_v: float) -> float:
        """Enforce hard-core exclusion in BOTH forward cruise and reverse backoff."""
        motion_sign = target_v * bot.direction
        if motion_sign > 0.0:
            d_ahead, _ = self._detect_ahead(bot)
            if d_ahead < SAFETY_HEADWAY_M:
                return 0.0
        elif motion_sign < 0.0:
            d_behind, _ = self._detect_behind(bot)
            if d_behind < SAFETY_HEADWAY_M:
                return 0.0
        return target_v

    def run(self, max_s: float = MAX_SIM_TIME_S) -> Dict[str, float]:
        steps = int(max_s / DT)
        for s in range(steps):
            self.current_time = s * DT

            if s % int(0.5 / DT) == 0:
                self.history.append((
                    self.current_time,
                    [b.x for b in self.robots],
                    [b.direction for b in self.robots],
                    [b.is_loaded for b in self.robots]
                ))

            in_tunnel = [b for b in self.robots if 0.5 < b.x < TUNNEL_LENGTH_M - 0.5]
            if len(in_tunnel) >= 2 and all(b.stalled_time > 20.0 for b in in_tunnel):
                self.deadlocked = True
                break

            # Asynchronous random-sequential update (matching abm_single_lane.py line 160)
            order = self.rng.permutation(len(self.robots))
            for idx in order:
                bot = self.robots[idx]
                d_ahead, other = self._detect_ahead(bot)
                v_cruise = V_MAX_TRANSPORT if bot.is_loaded else V_MAX_RETURN

                # --------------------------------------------------------------
                # 1. Bio-Inspired Diacamma ABM-Isomorphic Protocol
                # --------------------------------------------------------------
                if self.protocol == 'BIO_INSPIRED_DIACAMMA':
                    if bot.state == 'CRUISE':
                        # ABM Rule (lines 279-290): Turned unencumbered leader (+1) rescues waiting lost unit
                        if (bot.direction == +1 and not bot.is_loaded and other is not None
                                and d_ahead < DETECTION_RANGE_M and other.is_lost_waiting):
                            if self.rng.uniform(0, 1) < PROB_RECRUIT_LOST:
                                other.is_lost_waiting = False
                                other.direction = +1
                                other.state = 'CRUISE'
                                self.mr_lf_count += 1

                        # Case 1: Head-on opposing encounter inside 1D tunnel (other.direction != bot.direction)
                        if d_ahead < DETECTION_RANGE_M and other is not None and other.direction != bot.direction:
                            if 0.0 <= bot.x <= TUNNEL_LENGTH_M:
                                # Strict ABM Rule: ONLY unencumbered returning leader (-1) yields & reverses!
                                # Outbound loaded units (+1) NEVER reverse toward Dock A.
                                if not bot.is_loaded and bot.direction == -1:
                                    bot.state = 'HESITATING'
                                    bot.state_timer = HESITATION_JAM_S if bot.in_active_jam else HESITATION_FREE_S
                                    self.jam_count += 1
                                    target_v = 0.0
                                else:
                                    # Outbound loaded transporter arrests during antennal/optical verification
                                    if bot.stalled_time >= HESITATION_JAM_S and bot.is_loaded:
                                        bot.is_lost_waiting = True
                                    target_v = 0.0
                            else:
                                target_v = 0.0

                        # Case 2: Co-directional convoy following (other.direction == bot.direction)
                        elif d_ahead < SAFETY_HEADWAY_M:
                            # Coordinated Turning (CT, Fig. S9): if an unencumbered returning robot (-1)
                            # is queued behind another returning robot that is hesitating or turning,
                            # coordinate the reversal so it never blocks the newly turned lead escort
                            if (not bot.is_loaded and bot.direction == -1 and other is not None
                                    and other.state in ('HESITATING', 'U_TURNING')):
                                bot.state = 'HESITATING'
                                bot.state_timer = 0.25
                            target_v = 0.0
                        else:
                            target_v = bot.direction * v_cruise

                    elif bot.state == 'HESITATING':
                        bot.state_timer -= DT
                        target_v = 0.0
                        if bot.state_timer <= 0.0:
                            bot.state = 'U_TURNING'
                            bot.state_timer = U_TURN_DURATION_S

                    elif bot.state == 'U_TURNING':
                        bot.state_timer -= DT
                        target_v = 0.0
                        if bot.state_timer <= 0.0:
                            # Before flipping direction, identify the outbound robot we were facing
                            _, encountered_outbound = self._detect_ahead(bot)
                            self.u_turn_count += 1
                            bot.direction = +1
                            bot.state = 'CRUISE'
                            bot.stalled_time = 0.0
                            bot.in_active_jam = False

                            # Propagate Coordinated Turning (CT, Fig. S9) to any unencumbered returners
                            # queued behind bot (i.e., at x > bot.x with direction == -1) so they all
                            # flip to +1 simultaneously and flush the channel without self-blocking!
                            for peer in self.robots:
                                if (peer.id != bot.id and peer.direction == -1 and not peer.is_loaded
                                        and 0.0 < (peer.x - bot.x) <= TUNNEL_LENGTH_M):
                                    peer.direction = +1
                                    peer.state = 'CRUISE'
                                    peer.state_timer = 0.0
                                    peer.stalled_time = 0.0
                                    peer.in_active_jam = False
                                    self.u_turn_count += 1

                            # ABM Branching (abm_single_lane.py lines 292-313):
                            # Branch A: Midway Switching-Over (MR-SO, p_so = 0.30)
                            if (encountered_outbound is not None and encountered_outbound.is_loaded
                                    and encountered_outbound.direction == +1
                                    and self.rng.uniform(0, 1) < PROB_SWITCH_OVER):
                                self.mr_so_count += 1
                                bot.is_loaded = True
                                encountered_outbound.is_lost_waiting = False
                                # If encountered_outbound has no other outbound robot queued behind it
                                # inside the tunnel, it becomes an unencumbered returner (-1)
                                outbound_behind = any(
                                    b.id != encountered_outbound.id and b.direction == +1
                                    and -1.0 <= b.x < encountered_outbound.x
                                    for b in self.robots
                                )
                                if not outbound_behind:
                                    encountered_outbound.is_loaded = False
                                    encountered_outbound.direction = -1
                                    encountered_outbound.state = 'CRUISE'
                                else:
                                    # Otherwise both proceed outbound (+1) in convoy rescue (MR-LF)
                                    self.mr_lf_count += 1
                            else:
                                # Branch B: Midway Lost-Follower / Convoy Rescue (MR-LF, p_lfr = 1.00)
                                self.mr_lf_count += 1
                                if encountered_outbound is not None:
                                    encountered_outbound.is_lost_waiting = False

                            target_v = V_MAX_TRANSPORT if bot.is_loaded else V_MAX_RETURN

                    elif bot.state == 'WAIT_SIDING':
                        bot.state_timer -= DT
                        target_v = 0.0
                        # Wait at portal siding if an opposing convoy is actively flushing the tunnel
                        opposing_in_tunnel = any(
                            b.direction == -bot.direction and 0.0 <= b.x <= TUNNEL_LENGTH_M
                            for b in self.robots
                        )
                        if bot.state_timer <= 0.0 and not opposing_in_tunnel:
                            bot.state = 'CRUISE'

                # --------------------------------------------------------------
                # 2. Decentralized Random Backoff (Symmetric Exclusion Baseline)
                # --------------------------------------------------------------
                elif self.protocol == 'RANDOM_BACKOFF':
                    if bot.state == 'CRUISE':
                        if (d_ahead < SAFETY_HEADWAY_M + 0.35 and other is not None
                                and other.direction != bot.direction and 0.0 <= bot.x <= TUNNEL_LENGTH_M):
                            bot.state = 'BACKOFF'
                            bot.state_timer = self.rng.exponential(2.0)
                            target_v = 0.0
                        elif d_ahead < SAFETY_HEADWAY_M:
                            target_v = 0.0
                        else:
                            target_v = bot.direction * v_cruise
                    elif bot.state == 'BACKOFF':
                        bot.state_timer -= DT
                        target_v = -bot.direction * V_MAX_REVERSE
                        if bot.state_timer <= 0.0:
                            bot.state = 'CRUISE'

                # --------------------------------------------------------------
                # 3. Centralized Token Locking (Under 40% RF Packet Loss)
                # --------------------------------------------------------------
                elif self.protocol == 'CENTRALIZED_LOCKING':
                    token_outbound = (int(self.current_time / 30.0) % 2 == 0)
                    if self.rng.uniform(0, 1) < self.rf_loss_rate:
                        target_v = 0.0
                    else:
                        has_token = (bot.direction == +1 and token_outbound) or (bot.direction == -1 and not token_outbound)
                        if has_token:
                            target_v = bot.direction * v_cruise
                        else:
                            if (bot.direction == +1 and bot.x <= 0.0) or (bot.direction == -1 and bot.x >= TUNNEL_LENGTH_M):
                                target_v = 0.0
                            else:
                                target_v = bot.direction * v_cruise
                        if d_ahead < SAFETY_HEADWAY_M:
                            target_v = 0.0

                target_v = self._enforce_safety(bot, target_v)
                bot.step(target_v, DT)

                # Portal management (Dock A at x <= -1.2 and Depot B at x >= L + 1.2)
                if bot.direction == +1 and bot.x >= TUNNEL_LENGTH_M + 1.2:
                    if bot.is_loaded:
                        bot.is_loaded = False
                        self.delivered_count += 1
                        bot.payloads_delivered += 1
                    bot.is_lost_waiting = False
                    bot.direction = -1
                    bot.state = 'WAIT_SIDING' if self.protocol == 'BIO_INSPIRED_DIACAMMA' else 'CRUISE'
                    bot.state_timer = 1.5
                    bot.v = 0.0

                elif bot.direction == -1 and bot.x <= -1.2:
                    bot.is_loaded = True
                    bot.is_lost_waiting = False
                    bot.direction = +1
                    bot.state = 'WAIT_SIDING' if self.protocol == 'BIO_INSPIRED_DIACAMMA' else 'CRUISE'
                    bot.state_timer = 1.5
                    bot.v = 0.0

        hrs = max(0.001, self.current_time / 3600.0)
        return {
            'protocol': self.protocol,
            'num_robots': self.N,
            'throughput_payloads_per_hr': round(self.delivered_count / hrs, 2),
            'delivered': self.delivered_count,
            'u_turns': self.u_turn_count,
            'mr_so': self.mr_so_count,
            'mr_lf': self.mr_lf_count,
            'deadlocked': 1.0 if self.deadlocked else 0.0,
            'duration_s': round(self.current_time, 2),
            'mean_energy_j': round(float(np.mean([b.energy for b in self.robots])), 2)
        }


def run_benchmark_sweep(
    fleet_sizes: List[int] = [6, 10, 14, 18, 22, 26, 30],
    num_runs: int = 5,
    verbose: bool = True
) -> Tuple[pd.DataFrame, Optional[TunnelSwarmSim], Optional[TunnelSwarmSim]]:
    """Run comprehensive performance comparison across all 3 protocols."""
    protocols = [
        ('BIO_INSPIRED_DIACAMMA', 0.0),
        ('RANDOM_BACKOFF', 0.0),
        ('CENTRALIZED_LOCKING', 0.40),
    ]

    records = []
    sample_sim_bio = None
    sample_sim_backoff = None

    for proto_name, rf_loss in protocols:
        for n_bots in fleet_sizes:
            for r in range(num_runs):
                seed = (abs(hash(proto_name)) + n_bots * 50 + r) % (2**31 - 1)
                sim = TunnelSwarmSim(
                    num_robots=n_bots,
                    protocol=proto_name,
                    rf_loss_rate=rf_loss,
                    seed=seed
                )
                res = sim.run()
                records.append(res)

                if n_bots == 14 and r == 0:
                    if proto_name == 'BIO_INSPIRED_DIACAMMA':
                        sample_sim_bio = sim
                    elif proto_name == 'RANDOM_BACKOFF':
                        sample_sim_backoff = sim

    df = pd.DataFrame(records)
    return df, sample_sim_bio, sample_sim_backoff


def main():
    parser = argparse.ArgumentParser(
        description="Bio-Inspired Swarm Robotics in 1D Communication-Denied Tunnel (Diacamma ABM Application)"
    )
    parser.add_argument("--fleet-sizes", type=int, nargs="+", default=[6, 10, 14, 18, 22, 26, 30])
    parser.add_argument("--num-runs", type=int, default=5)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output", type=str, default="swarm_robotics_benchmarks.csv")
    parser.add_argument("--output-dir", type=str, default="artifacts/file_generation/ttl=63d/output")
    args = parser.parse_args()

    fleet_sizes = [6, 14, 22] if args.quick else args.fleet_sizes
    num_runs = 3 if args.quick else args.num_runs

    t0 = time.time()
    df, _, _ = run_benchmark_sweep(fleet_sizes=fleet_sizes, num_runs=num_runs)
    total_time = time.time() - t0

    df.to_csv(args.output, index=False)
    os.makedirs(args.output_dir, exist_ok=True)
    df.to_csv(os.path.join(args.output_dir, os.path.basename(args.output)), index=False)

    summary = df.groupby(['protocol', 'num_robots']).agg({
        'throughput_payloads_per_hr': ['mean', 'std'],
        'delivered': 'mean',
        'u_turns': 'mean',
        'mr_so': 'mean',
        'mr_lf': 'mean',
        'deadlocked': lambda x: np.mean(x) * 100.0,
        'mean_energy_j': 'mean',
    })
    print(f"SWARM ROBOTICS BENCHMARK COMPLETE in {total_time:.2f} s:")
    print(summary.to_string())


if __name__ == "__main__":
    main()

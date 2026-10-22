# Adaptive Symmetry Breaking Resolves Traffic Jams in Tandem-Running Ants: Agent-Based Models & Bio-Inspired Swarm Robotics Simulators

[License: MIT](https://www.google.com/search?q=LICENSE)
[](https://www.python.org/)
[Reproducibility Suite](https://www.google.com/search?q=reproduce_all_simulations_and_figures.py)

Official empirical dataset, 2D active-matter cellular-automaton Agent-Based Models (ABMs), and 1D communication-denied Swarm Robotics simulation repository accompanying the manuscript:

> **Adaptive symmetry breaking resolves traffic jams in tandem-running ants**  
> **Manish K. Pathak**$^{1}$, **Joy D. Bairagya**$^{2}$, **Sagar Chakraborty**$^{2,\ast}$, and **Sumana Annagiri**$^{1,\ast}$  
> $^{1}$Behaviour and Ecology Lab, Department of Biological Sciences, Indian Institute of Science Education and Research (IISER) Kolkata, Mohanpur 741246, West Bengal, India  
> $^{2}$Department of Physics, Indian Institute of Technology (IIT) Kanpur, Kanpur 208016, Uttar Pradesh, India  
> $^{\ast}$Corresponding authors: `sumana@iiserkol.ac.in`, `sagarc@iitk.ac.in`

---

## 1. Scientific Overview

Bidirectional transport through narrow physical bottlenecks ($w_{\text{channel}} < 2w_{\text{agent}}$, where lateral passing is physically impossible) is vulnerable to catastrophic gridlock across biological trails, pedestrian corridors, and subterranean multi-robot fleets. This repository provides the complete empirical datasets, 2D cellular-automaton Agent-Based Models (ABMs), and 1D communication-denied Swarm Robotics simulators demonstrating how the ponerine ant *Diacamma indicum* resolves single-lane traffic jams without centralized control or global communication:

1. **Empirical Discovery (`data/Dataset_S1.xlsx`)**: Across $N = 12$ paired colonies ($n = 24$ whole-colony nest relocations, $56$ traffic jams, $348$ longitudinal orientation snapshots), constricting bridge width from $2.5\text{ cm}$ ($5$ lanes) to $0.5\text{ cm}$ ($1$ lane) induces an **$18.67$-fold surge in traffic jams** ($0.25 \pm 0.62 \to 4.67 \pm 2.99$, Wilcoxon $W = 0.0, P = 4.88 \times 10^{-4}$), yet transport duration increases by only **$1.32$-fold** ($14.58 \pm 4.54 \to 19.25 \pm 6.37\text{ min}$, $P = 0.0186$). Unencumbered returning leaders act as stochastic catalysts ($58.9\%$ of jam triggers), executing adaptive $180^\circ$ U-turns after an antennal verification latency ($T_r^J = 9.0\text{ s}, \rho^J = 0.008\text{ step}^{-1}$) to drive $92.86\%$ outbound mass orientation ($P = 5.50 \times 10^{-12}$) and midway recruitment ($+110.6\%$ lost-follower rescue $\text{MR-LF}$, $+72.8\%$ switching-over $\text{MR-SO}$).
2. **Active-Matter Agent-Based Models (`joy_Trafic_jam_Single-lane.py`, `joy_Trafic_jam_Multi-lane.py`, `abm_single_lane.py`, `abm_multi_lane.py`)**: Discrete 2D lattice cellular automata ($152 \times 5$ cells, $\Delta x = 0.5\text{ cm}$, $\Delta t = 1/13\text{ s}$) parameterized directly from empirical video tracking (**Table S1**), including behavioral knockout ablations ($p_{\text{so}} = 0$ and $p_{\text{lfr}} = 0$).
3. **Bio-Inspired Swarm Robotics Simulators (`swarm_robot_tunnel_simulation.py`, `swarm_robotics_tunnel.py`)**: Translates the exact *Diacamma* parity-reversal, two-regime verification latency ($\tau_r = 2.0\text{ s}$ free, $\tau_r^J = 4.5\text{ s}$ jam; ratio $2.25$), midway switching-over ($p_{\text{so}} = 0.30$), lost-unit convoy rescue ($p_{\text{lfr}} = 1.00$), and coordinated turning (`CT`) rules to Autonomous Mobile Robot (AMR) fleets operating in communication-denied 1D tunnels ($w_{\text{tunnel}} = 0.60\text{ m} < 2w_{\text{robot}} = 0.80\text{ m}$, velocity ratio $v_R / v_T = 1.625$).

---

## 2. Repository File Inventory & Manuscript Mapping

| File / Directory | Description & Manuscript Figure Mapping |
| :--- | :--- |
| `reproduce_all_simulations_and_figures.py` | **Master Deterministic Reproducibility Pipeline**: Executes ABM simulations, knockout ablations, and Swarm Robotics benchmarks; renders **Figs. 5, 6, 7** and **SI Robotics Fig. 2**; and verifies cryptographic SHA-256 checksums (`reproducibility_sha256_manifest.csv`). |
| `verify_all_simulations.py` | **Automated Pre-Commit Verification Suite**: Cross-platform (Windows / macOS / Linux) syntax and runtime test suite validating all 4 simulation engines in $\sim 60\text{ s}$. |
| `joy_Trafic_jam_Single-lane.py` | Original 1D Single-Lane Bottleneck ABM by Joy D. Bairagya ($152 \times 5$ lattice with central $15\text{-cm}$ single-lane constriction; reproduces **Figs. 1c–g, 5a–d** and **Figs. S1, S3–S11**). |
| `joy_Trafic_jam_Multi-lane.py` | Original 5-Lane Multi-Lane Control ABM by Joy D. Bairagya (unobstructed lateral passing across all $152 \times 5$ cells; reproduces **Fig. 5c** and **Fig. S2**). |
| `abm_single_lane.py` & `abm_multi_lane.py` | Object-oriented, CLI-parameterized 1D Single-Lane and 5-Lane Control ABM modules. |
| `swarm_robot_tunnel_simulation.py` | **60-m Subterranean Logistics Gallery Simulator**: Compares `Centralized_Priority` (Wi-Fi blackout), `Random_Backoff`, `BioInspired_Diacamma`, `Ablated_No_SO` ($p_{\text{so}} = 0$), and `Ablated_No_LFR` ($p_{\text{lfr}} = 0$) across $N \in [12, 60]$ robots and $0\%\text{--}100\%$ RF packet loss (reproduces **Fig. 7a–f** and **SI Section S4**). |
| `swarm_robotics_tunnel.py` | **20-m Continuous-Kinematic AMR Corridor Simulator**: $20\text{ Hz}$ differential-drive controller with bounded acceleration ($1.2\text{ m/s}^2$) and bidirectional headway safety enforcement. |
| `ml_marl_and_surrogate_analysis.py` | **Decentralized MARL & Surrogate SHAP/Sobol/SBI Analysis**: Demonstrates policy-gradient convergence onto *Diacamma* rules and computes exact 16-coalition Shapley attributions (**Fig. S12**). |
| `Robotic_Simulation_Line_by_Line_Guide_for_Biologists.pdf` | Comprehensive line-by-line biological and algorithmic guide mapping every block of the robotics code to *Diacamma indicum* relocation rules. |
| `data/Dataset_S1.xlsx` | Master 10-sheet empirical tracking, jam log ($n = 56$ jams), polar orientation ($n = 348$ snapshots), and statistical audit workbook (**Dataset S1**). |
| `data/*.csv` | Pre-computed empirical and simulation benchmark datasets (`structured_summary_datasheet.csv`, `tidy_long_master_datasheet.csv`, `swarm_robotics_benchmark_results.csv`, `swarm_robotics_packet_loss_sweep.csv`, `reproducible_abm_knockout_results.csv`). |
| `figures/` | Publication-grade vector `.pdf`, `.svg`, and high-resolution `.png` simulation figures. |

---

## 3. System Requirements & Installation (< 30 Seconds)

* **Operating Systems**: Windows 10/11 (Anaconda / Miniconda / PyCharm), macOS (12+), and Linux (Ubuntu 20.04/22.04/24.04).
* **Python Version**: Python $\ge 3.9$ (tested on Python 3.9, 3.10, 3.11, and 3.12).
* **Dependencies**: Standard scientific Python stack (`numpy>=1.24.0`, `scipy>=1.10.0`, `pandas>=2.0.0`, `matplotlib>=3.7.0`, `openpyxl>=3.1.0`).
* **Hardware**: Runs on any standard desktop or laptop CPU (no GPU required).

```bash
git clone https://github.com/mkp4560/revised_robotics_simulation.git
cd revised_robotics_simulation
pip install -r requirements.txt
```

---

## 4. Quick Verification & Reproducing All Manuscript Results

### A. Fast Verification Suite 

```bash
python verify_all_simulations.py
```

* Validates AST/bytecode compilation (`PASSED`) and executes a fast runtime verification (`--quick`) across all 4 simulation engines (`joy_Trafic_jam_Single-lane.py`, `joy_Trafic_jam_Multi-lane.py`, `swarm_robotics_tunnel.py`, and `swarm_robot_tunnel_simulation.py`).

### B. Master End-to-End Reproducibility Pipeline (ABM + Swarm Robotics + Figures 5, 6, 7)

```bash
# Fast mode (~4 minutes): Runs deterministic ABM knockouts, 5-protocol robotics kymographs,
# generates Figures 5, 6, 7, and verifies bit-for-bit determinism & SHA-256 checksums:
python reproduce_all_simulations_and_figures.py --mode fast

# Full multi-replicate sweep mode:
python reproduce_all_simulations_and_figures.py --mode full
```

### C. Running Individual Simulation Engines

```bash
# 1. 60-m Subterranean Tunnel Swarm Robotics Simulator (Fig. 7 & SI Section S4):
python swarm_robot_tunnel_simulation.py --reps 2 --output swarm_robotics_benchmark_results.csv

# 2. 20-m Continuous-Kinematic AMR Corridor Simulator (SI Section S4):
python swarm_robotics_tunnel.py --num-runs 5 --output swarm_robotics_benchmarks.csv

# 3. 1D Single-Lane Bottleneck Ant ABM (12 empirical colony sizes, N = 54..160):
python joy_Trafic_jam_Single-lane.py --num-sims 25 --output single_lane_simulation_results.csv

# 4. 5-Lane Multi-Lane Control Ant ABM (12 empirical colony sizes, N = 54..160):
python joy_Trafic_jam_Multi-lane.py --num-sims 25 --output multi_lane_simulation_results.csv

# 5. Decentralized MARL Convergence & Surrogate SHAP/Sobol/SBI Analysis (Fig. S12):
python ml_marl_and_surrogate_analysis.py
```

---

## 5. License & Citation

This project is licensed under the **MIT License** — see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details. If you use this code or dataset in your research, please cite our manuscript (see [CITATION.cff](https://www.google.com/search?q=CITATION.cff)):

```bibtex
@article{Pathak2026DiacammaTraffic,
  author  = {Pathak, Manish K. and Bairagya, Joy D. and Chakraborty, Sagar and Annagiri, Sumana},
  title   = {Adaptive symmetry breaking resolves traffic jams in tandem-running ants},
  year    = {2026},
  url     = {https://github.com/mkp4560/revised_robotics_simulation}
}
```

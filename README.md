# 🔴 Connect4 AI: Comparative Strategy Engine

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-GUI-green.svg)](https://www.pygame.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-orange.svg)](https://pandas.pydata.org/)

## 🎯 Project Overview
This project serves as a testbed for comparing various Artificial Intelligence approaches to the classic solved game of Connect 4. I developed a modular Python environment that pits traditional heuristic search algorithms against probabilistic methods and supervised learning models. 

The application allows users to challenge these agents at varying difficulty levels or observe **AI vs. AI** simulations to analyze algorithmic efficiency and decision-making styles.

---

## 📈 Executive Performance Summary
The suite implements four distinct algorithmic strategies, offering a comparative look at how different AI paradigms approach zero-sum game theory.

| Algorithm | Type | Strategy | Pros/Cons |
| :--- | :--- | :--- | :--- |
| **Minimax** | Deterministic | Alpha-Beta Pruning | **🏆 Optimal:** Perfect play at high depths, but computationally expensive. |
| **Monte Carlo (MCTS)** | Probabilistic | Random Simulations (UCB1) | **🚀 Flexible:** Requires no heuristic knowledge, but performance scales strictly with simulation time. |
| **A Search** | Heuristic | Best-First Greedy | **⚡ Fast:** Evaluates immediate board value, but lacks long-term strategic foresight. |
| **ID3 Tree** | Supervised | Entropy/Information Gain | **🧠 Learned:** Mimics human patterns from dataset, but limited by training data quality. |

**Key Takeaway:** While Minimax with Alpha-Beta pruning provides the most consistent defensive play, the MCTS agent demonstrates surprising creativity in "trap" setups when given sufficient simulation time.

---

## 🔬 Technical Deep Dive

### 1. Algorithmic Implementation
* **Minimax with Alpha-Beta Pruning:**
    * Implemented a depth-limited search (up to depth 6) to balance response time and accuracy.
    * Utilizes a custom evaluation function that prioritizes center-column control and "window" scoring (checking sets of 4 slots for potential wins).
    * Includes a dynamic difficulty setting that adjusts the recursion depth.

* **Monte Carlo Tree Search (MCTS):**
    * Constructs a search tree where nodes represent board states.
    * Uses **UCB1 (Upper Confidence Bound 1)** to balance *exploration* (trying new moves) vs. *exploitation* (sticking to known winning paths).
    * Performance is tunable via simulation count (e.g., 500 simulations for "Hard" mode).

* **ID3 Decision Tree (Pattern Recognition):**
    * Uses `pandas` to process `dataset_connect4.csv`, converting board states into a decision tree based on Information Gain.
    * Demonstrates how game logic can be learned from data rather than hard-coded rules.

### 2. Software Architecture
* **Modular Design:** Separation of concerns between `game_logic.py` (rules), `ai_algorithms.py` (intelligence), and `main.py` (GUI).
* **Data-Driven:** The ID3 implementation dynamically trains the model at runtime using the `dataset_connect4.csv` loaded via Pandas.

---


## 🛠️ Installation & Usage

### 1. Clone & Setup
```bash
git clone [https://github.com/pedrooamaroo/Connect4-AI-Suite.git](https://github.com/pedrooamaroo/Connect4-AI-Suite.git)
cd Connect4-AI-Suite
pip install -r requirements.txt

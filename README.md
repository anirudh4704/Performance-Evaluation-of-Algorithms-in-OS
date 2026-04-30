# ⚙️ OS Algorithm Solver

A clean, beginner-friendly web app that **automatically selects and explains the best Operating System algorithm** for your problem — no AI, just smart rule-based logic.

Built with **Python (Flask)** + plain HTML/CSS/JS. No database, no login, no heavy frameworks.

---

## 🚀 Live Demo

> Run locally — see setup instructions below.

---

## ✨ Features

- **3 problem categories:** CPU Scheduling, Memory Management, Disk Scheduling
- **Auto-selects the optimal algorithm** based on your input using rule-based logic
- **Step-by-step solution** with tables, Gantt charts, and seek traces
- **Plain-English explanation** of why the algorithm was chosen, what it does, and why others weren't picked
- Zero setup complexity — no database, no login, no external APIs

---

## 🧠 Algorithms Covered

| Category | Algorithms |
|---|---|
| CPU Scheduling | FCFS · SJF (non-preemptive) · Round Robin |
| Memory Management | FIFO · LRU · Optimal |
| Disk Scheduling | FCFS · SSTF · SCAN (Elevator) |

### Selection Logic (rule-based, not AI)

**CPU:**
- 1 process or all equal burst times → **FCFS**
- 4+ processes with a time quantum → **Round Robin**
- Varying burst times, no quantum → **SJF**

**Memory:**
- Frames ≥ unique pages → **FIFO**
- Small reference string (≤ 8 refs) → **Optimal**
- Large reference string → **LRU**

**Disk:**
- ≤ 3 requests → **FCFS**
- Requests clustered near head (avg distance < 30) → **SSTF**
- Many spread-out requests → **SCAN**

---

## 🖥️ Screenshots

> CPU Scheduling with Gantt chart, Memory page fault table, Disk seek distance breakdown.

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Fonts:** Space Mono + DM Sans (Google Fonts)
- **No frameworks, no database, no JS bundler**

---

## ⚡ Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/os-algorithm-solver.git
cd os-algorithm-solver
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python3 app.py
```

### 5. Open in browser

```
http://127.0.0.1:5000
```

> **macOS users:** If port 5000 is blocked (AirPlay Receiver conflict), either:
> - Go to **System Settings → General → AirDrop & Handoff** and turn off AirPlay Receiver, or
> - Change the last line of `app.py` to `app.run(debug=True, port=8080)` and visit `http://127.0.0.1:8080`

---

## 📁 Project Structure

```
os_solver/
├── app.py                  # Flask backend + all algorithm logic
├── requirements.txt        # Dependencies (just Flask)
├── templates/
│   └── index.html          # Main UI template
└── static/
    ├── css/
    │   └── style.css       # Styling
    └── js/
        └── main.js         # Frontend interactivity + result rendering
```

---

## 📖 How It Works

1. **User selects** a problem type (CPU / Memory / Disk)
2. **User enters** their data (processes, page string, disk queue, etc.)
3. **Backend analyzes** the input and picks the best algorithm using simple rules
4. **Results are displayed** with:
   - The chosen algorithm name
   - A step-by-step solution table
   - A Gantt chart (CPU) or seek trace (Disk)
   - Summary statistics (avg wait time, page faults, total seek distance)
   - A plain-English explanation of the decision

---

## 🤝 Contributing

Pull requests are welcome! Some ideas for contributions:

- Add preemptive SJF (SRTF)
- Add priority scheduling
- Add animated Gantt chart
- Add dark/light theme toggle
- Export results as PDF

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Author

Made with ☕ for OS students everywhere.

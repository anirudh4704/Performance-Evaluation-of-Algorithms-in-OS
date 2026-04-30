"""
OS Algorithm Solver - Flask Backend
Automatically selects and solves OS scheduling/management problems.
"""

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# ─────────────────────────────────────────────
#  CPU SCHEDULING ALGORITHMS
# ─────────────────────────────────────────────

def fcfs_cpu(processes):
    """First-Come First-Served: sort by arrival time, process in order."""
    procs = sorted(processes, key=lambda p: p['arrival'])
    time, steps, total_wait, total_turn = 0, [], 0, 0

    for p in procs:
        if time < p['arrival']:
            time = p['arrival']          # CPU idle gap
        start = time
        finish = time + p['burst']
        wait = start - p['arrival']
        turnaround = finish - p['arrival']
        total_wait += wait
        total_turn += turnaround
        steps.append({
            'pid': p['pid'], 'arrival': p['arrival'], 'burst': p['burst'],
            'start': start, 'finish': finish,
            'waiting': wait, 'turnaround': turnaround
        })
        time = finish

    n = len(procs)
    return steps, round(total_wait / n, 2), round(total_turn / n, 2)


def sjf_cpu(processes):
    """Shortest Job First (non-preemptive): pick shortest burst among ready jobs."""
    procs = [dict(p) for p in processes]   # copy so we can mark done
    time, done, steps = 0, [], []
    total_wait, total_turn = 0, 0

    while len(done) < len(procs):
        # jobs that have arrived and aren't done
        ready = [p for p in procs if p['arrival'] <= time and p not in done]
        if not ready:
            time += 1
            continue
        p = min(ready, key=lambda x: x['burst'])   # shortest burst
        start = time
        finish = time + p['burst']
        wait = start - p['arrival']
        turnaround = finish - p['arrival']
        total_wait += wait
        total_turn += turnaround
        steps.append({
            'pid': p['pid'], 'arrival': p['arrival'], 'burst': p['burst'],
            'start': start, 'finish': finish,
            'waiting': wait, 'turnaround': turnaround
        })
        time = finish
        done.append(p)

    n = len(procs)
    return steps, round(total_wait / n, 2), round(total_turn / n, 2)


def round_robin_cpu(processes, quantum):
    """Round Robin: each process gets a fixed time slice (quantum)."""
    from collections import deque
    procs = sorted([dict(p) for p in processes], key=lambda x: x['arrival'])
    remaining = {p['pid']: p['burst'] for p in procs}
    arrival   = {p['pid']: p['arrival'] for p in procs}
    burst_map  = {p['pid']: p['burst'] for p in procs}

    queue = deque()
    time = 0
    in_queue = set()
    steps = []
    finish_time = {}

    # seed queue with processes that arrive at time 0
    for p in procs:
        if p['arrival'] <= time:
            queue.append(p['pid'])
            in_queue.add(p['pid'])

    while queue or any(r > 0 for r in remaining.values()):
        if not queue:
            # advance time to next arrival
            next_arrive = min(arrival[pid] for pid, r in remaining.items() if r > 0)
            time = next_arrive
            for p in procs:
                if p['arrival'] <= time and p['pid'] not in in_queue and remaining[p['pid']] > 0:
                    queue.append(p['pid'])
                    in_queue.add(p['pid'])

        pid = queue.popleft()
        run = min(quantum, remaining[pid])
        start = time
        time += run
        remaining[pid] -= run

        # enqueue newly arrived processes
        for p in procs:
            if p['arrival'] <= time and p['pid'] not in in_queue and remaining[p['pid']] > 0:
                queue.append(p['pid'])
                in_queue.add(p['pid'])

        if remaining[pid] > 0:
            queue.append(pid)   # re-queue if not done
        else:
            finish_time[pid] = time

        steps.append({'pid': pid, 'start': start, 'end': time, 'ran': run})

    total_wait, total_turn = 0, 0
    summary = []
    for p in procs:
        ft = finish_time[p['pid']]
        turnaround = ft - arrival[p['pid']]
        wait = turnaround - burst_map[p['pid']]
        total_wait += wait
        total_turn += turnaround
        summary.append({'pid': p['pid'], 'arrival': arrival[p['pid']],
                        'burst': burst_map[p['pid']], 'finish': ft,
                        'waiting': wait, 'turnaround': turnaround})

    n = len(procs)
    return steps, summary, round(total_wait / n, 2), round(total_turn / n, 2)


def select_cpu_algorithm(processes, quantum):
    """
    Simple rule-based algorithm selection:
    - 1 process → FCFS (trivially optimal)
    - All same burst → FCFS (no benefit to SJF/RR)
    - Many processes (>=4) + quantum provided → Round Robin (fairness)
    - Otherwise → SJF (minimises average waiting time)
    """
    n = len(processes)
    bursts = [p['burst'] for p in processes]
    all_same = len(set(bursts)) == 1

    if n == 1 or all_same:
        return 'FCFS', 'Single process or all bursts are equal — FCFS is trivially optimal here.'
    if n >= 4 and quantum:
        return 'RR', 'Multiple processes with a time quantum provided — Round Robin ensures fair CPU sharing.'
    return 'SJF', 'Varying burst times without a quantum — SJF minimises average waiting time.'


# ─────────────────────────────────────────────
#  MEMORY MANAGEMENT ALGORITHMS
# ─────────────────────────────────────────────

def fifo_memory(pages, frames):
    """FIFO: replace the page that arrived earliest (queue order)."""
    from collections import deque
    memory, queue = [], deque()
    faults, steps = 0, []

    for page in pages:
        hit = page in memory
        evicted = None
        if not hit:
            faults += 1
            if len(memory) < frames:
                memory.append(page)
                queue.append(page)
            else:
                evicted = queue.popleft()
                memory.remove(evicted)
                memory.append(page)
                queue.append(page)
        steps.append({'page': page, 'memory': list(memory), 'fault': not hit, 'evicted': evicted})

    return steps, faults


def lru_memory(pages, frames):
    """LRU: replace the least-recently-used page."""
    memory, recent = [], []
    faults, steps = 0, []

    for page in pages:
        hit = page in memory
        evicted = None
        if hit:
            recent.remove(page)
            recent.append(page)
        else:
            faults += 1
            if len(memory) < frames:
                memory.append(page)
                recent.append(page)
            else:
                evicted = recent.pop(0)
                memory.remove(evicted)
                memory.append(page)
                recent.append(page)
        steps.append({'page': page, 'memory': list(memory), 'fault': not hit, 'evicted': evicted})

    return steps, faults


def optimal_memory(pages, frames):
    """Optimal: replace the page that will not be used for the longest time."""
    memory = []
    faults, steps = 0, []

    for i, page in enumerate(pages):
        hit = page in memory
        evicted = None
        if not hit:
            faults += 1
            if len(memory) < frames:
                memory.append(page)
            else:
                # find future uses
                future = {}
                for m in memory:
                    try:
                        future[m] = pages[i+1:].index(m)
                    except ValueError:
                        future[m] = float('inf')   # never used again
                evicted = max(future, key=future.get)
                memory.remove(evicted)
                memory.append(page)
        steps.append({'page': page, 'memory': list(memory), 'fault': not hit, 'evicted': evicted})

    return steps, faults


def select_memory_algorithm(pages, frames):
    """
    Rule-based selection:
    - frames >= unique pages → FIFO (no faults possible, FIFO is simplest)
    - small reference string (<=8) → Optimal (feasible to predict)
    - else → LRU (practical best-approximation of Optimal)
    """
    unique = len(set(pages))
    if frames >= unique:
        return 'FIFO', 'Frame count covers all unique pages — any algorithm works; FIFO is simplest.'
    if len(pages) <= 8:
        return 'Optimal', 'Small reference string — Optimal is feasible and gives the fewest faults.'
    return 'LRU', 'Large reference string — LRU is the best practical approximation of Optimal.'


# ─────────────────────────────────────────────
#  DISK SCHEDULING ALGORITHMS
# ─────────────────────────────────────────────

def fcfs_disk(requests, head):
    """FCFS: serve requests in the order they arrive."""
    steps, total = [], 0
    pos = head
    for r in requests:
        seek = abs(r - pos)
        total += seek
        steps.append({'from': pos, 'to': r, 'seek': seek})
        pos = r
    return steps, total


def sstf_disk(requests, head):
    """SSTF: always serve the closest request next."""
    remaining = list(requests)
    pos, total, steps = head, 0, []
    while remaining:
        closest = min(remaining, key=lambda r: abs(r - pos))
        seek = abs(closest - pos)
        total += seek
        steps.append({'from': pos, 'to': closest, 'seek': seek})
        pos = closest
        remaining.remove(closest)
    return steps, total


def scan_disk(requests, head, max_track=199):
    """SCAN (elevator): move in one direction, reverse at end."""
    left  = sorted([r for r in requests if r < head], reverse=True)
    right = sorted([r for r in requests if r >= head])
    order = right + [max_track] + left   # go right first then sweep left

    steps, total, pos = [], 0, head
    for r in order:
        if r == max_track and r not in requests:
            continue   # skip boundary unless it's an actual request
        seek = abs(r - pos)
        total += seek
        steps.append({'from': pos, 'to': r, 'seek': seek})
        pos = r
    return steps, total


def select_disk_algorithm(requests, head):
    """
    Rule-based selection:
    - <=3 requests → FCFS (overhead of smarter algorithms not worth it)
    - requests clustered near head (avg distance < 30) → SSTF (quick wins)
    - many spread-out requests → SCAN (minimises head movement overall)
    """
    n = len(requests)
    avg_dist = sum(abs(r - head) for r in requests) / n if n else 0

    if n <= 3:
        return 'FCFS', 'Very few requests — FCFS is simple and efficient enough.'
    if avg_dist < 30:
        return 'SSTF', 'Requests clustered near the head — SSTF minimises seek time efficiently.'
    return 'SCAN', 'Many spread-out requests — SCAN (elevator) avoids starvation and minimises total movement.'


# ─────────────────────────────────────────────
#  EXPLANATION TEXTS
# ─────────────────────────────────────────────

ALGO_INFO = {
    # CPU
    'FCFS': {
        'what': 'First-Come First-Served processes jobs in arrival order. Simple, no starvation, but long jobs can block short ones (convoy effect).',
        'others': 'SJF would reduce average wait, but all bursts are equal so it makes no difference. Round Robin adds unnecessary context switches here.'
    },
    'SJF': {
        'what': 'Shortest Job First picks the process with the smallest burst time. Minimises average waiting time but can starve long processes.',
        'others': 'FCFS would give higher average wait because longer jobs may run first. Round Robin needs a quantum and adds overhead without benefit here.'
    },
    'RR': {
        'what': 'Round Robin gives every process a fixed time slice (quantum). Fair and responsive, ideal when many processes share the CPU.',
        'others': 'FCFS would let long jobs monopolise the CPU. SJF without preemption could starve new short jobs that arrive later.'
    },
    # Memory
    'FIFO': {
        'what': 'First-In First-Out replaces the oldest page in memory. Simple queue, easy to implement, but can suffer Bélády\'s anomaly.',
        'others': 'LRU/Optimal are unnecessary when frames cover all unique pages — any algorithm produces zero faults.'
    },
    'LRU': {
        'what': 'Least Recently Used replaces the page unused for the longest time. Good practical approximation of Optimal.',
        'others': 'FIFO ignores recency, leading to more faults. Optimal is theoretically best but requires future knowledge — impractical in real OS.'
    },
    'Optimal': {
        'what': 'Optimal replaces the page that won\'t be needed for the longest time in the future. Theoretically fewest page faults possible.',
        'others': 'FIFO and LRU produce more faults. Optimal is only feasible when the full reference string is known in advance (e.g. simulations).'
    },
    # Disk
    'FCFS_disk': {
        'what': 'FCFS serves disk requests in arrival order. Simple and fair but can cause excessive head movement.',
        'others': 'SSTF/SCAN overhead isn\'t justified for just a handful of requests. FCFS is plenty efficient here.'
    },
    'SSTF': {
        'what': 'Shortest Seek Time First always moves to the nearest request. Reduces average seek time but can starve far-away requests.',
        'others': 'FCFS ignores proximity, wasting movement. SCAN is better when requests are spread across the disk, but here they\'re clustered.'
    },
    'SCAN': {
        'what': 'SCAN (elevator algorithm) moves the disk arm in one direction, serving all requests along the way, then reverses.',
        'others': 'FCFS wastes movement jumping back and forth. SSTF risks starvation on a busy disk. SCAN balances fairness and efficiency.'
    },
}


# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json()
    problem_type = data.get('type')

    try:
        if problem_type == 'cpu':
            result = solve_cpu(data)
        elif problem_type == 'memory':
            result = solve_memory(data)
        elif problem_type == 'disk':
            result = solve_disk(data)
        else:
            return jsonify({'error': 'Unknown problem type'}), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


def solve_cpu(data):
    raw = data.get('processes', [])
    quantum = int(data.get('quantum', 0)) or None

    processes = []
    for i, p in enumerate(raw):
        processes.append({
            'pid': f"P{i+1}",
            'arrival': int(p['arrival']),
            'burst': int(p['burst'])
        })

    algo, why = select_cpu_algorithm(processes, quantum)

    if algo == 'FCFS':
        steps, avg_wait, avg_turn = fcfs_cpu(processes)
        info = ALGO_INFO['FCFS']
        return {
            'algorithm': 'FCFS (First-Come First-Served)',
            'why': why,
            'what': info['what'],
            'others': info['others'],
            'type': 'cpu_table',
            'steps': steps,
            'avg_wait': avg_wait,
            'avg_turnaround': avg_turn
        }
    elif algo == 'SJF':
        steps, avg_wait, avg_turn = sjf_cpu(processes)
        info = ALGO_INFO['SJF']
        return {
            'algorithm': 'SJF (Shortest Job First)',
            'why': why,
            'what': info['what'],
            'others': info['others'],
            'type': 'cpu_table',
            'steps': steps,
            'avg_wait': avg_wait,
            'avg_turnaround': avg_turn
        }
    else:  # RR
        q = quantum or 2
        timeline, summary, avg_wait, avg_turn = round_robin_cpu(processes, q)
        info = ALGO_INFO['RR']
        return {
            'algorithm': f'Round Robin (Quantum = {q})',
            'why': why,
            'what': info['what'],
            'others': info['others'],
            'type': 'cpu_rr',
            'timeline': timeline,
            'steps': summary,
            'avg_wait': avg_wait,
            'avg_turnaround': avg_turn,
            'quantum': q
        }


def solve_memory(data):
    pages  = list(map(int, str(data.get('pages', '')).split()))
    frames = int(data.get('frames', 3))

    algo, why = select_memory_algorithm(pages, frames)

    if algo == 'FIFO':
        steps, faults = fifo_memory(pages, frames)
        info = ALGO_INFO['FIFO']
    elif algo == 'Optimal':
        steps, faults = optimal_memory(pages, frames)
        info = ALGO_INFO['Optimal']
    else:  # LRU
        steps, faults = lru_memory(pages, frames)
        info = ALGO_INFO['LRU']

    return {
        'algorithm': f'{algo} Page Replacement',
        'why': why,
        'what': info['what'],
        'others': info['others'],
        'type': 'memory',
        'steps': steps,
        'faults': faults,
        'hits': len(pages) - faults,
        'total': len(pages),
        'frames': frames
    }


def solve_disk(data):
    requests = list(map(int, str(data.get('requests', '')).split()))
    head = int(data.get('head', 0))

    algo, why = select_disk_algorithm(requests, head)

    if algo == 'FCFS':
        steps, total = fcfs_disk(requests, head)
        info = ALGO_INFO['FCFS_disk']
        algo_label = 'FCFS (First-Come First-Served)'
    elif algo == 'SSTF':
        steps, total = sstf_disk(requests, head)
        info = ALGO_INFO['SSTF']
        algo_label = 'SSTF (Shortest Seek Time First)'
    else:  # SCAN
        steps, total = scan_disk(requests, head)
        info = ALGO_INFO['SCAN']
        algo_label = 'SCAN (Elevator Algorithm)'

    return {
        'algorithm': algo_label,
        'why': why,
        'what': info['what'],
        'others': info['others'],
        'type': 'disk',
        'steps': steps,
        'total_seek': total,
        'head': head,
        'requests': requests
    }


if __name__ == '__main__':
    app.run(debug=True)

// test_runner.js
const fs = require('fs');
const { spawnSync } = require('child_process');

function naturalCompare(a, b) {
    return a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });
}

function simulateFCFS(processes) {
    const procs = JSON.parse(JSON.stringify(processes));
    procs.sort((a, b) => {
        if (a.at !== b.at) return a.at - b.at;
        return naturalCompare(a.id, b.id);
    });

    let time = 0;
    const results = [];
    const ganttBlocks = [];

    for (const p of procs) {
        if (time < p.at) {
            ganttBlocks.push({ process: "Idle", start: time, end: p.at });
            time = p.at;
        }

        const start = time;
        const ct = start + p.bt;
        time = ct;

        ganttBlocks.push({ process: p.id, start: start, end: ct });

        const tat = ct - p.at;
        const wt = tat - p.bt;

        results.push({
            id: p.id,
            at: p.at,
            bt: p.bt,
            ct: ct,
            tat: tat,
            wt: wt
        });
    }

    const n = results.length;
    const avgTat = n > 0 ? results.reduce((acc, r) => acc + r.tat, 0) / n : 0;
    const avgWt = n > 0 ? results.reduce((acc, r) => acc + r.wt, 0) / n : 0;

    return { results, avgTat, avgWt, ganttBlocks };
}

function simulateSJF(processes) {
    const procs = processes.map(p => ({
        id: p.id,
        at: p.at,
        bt: p.bt,
        remaining: p.bt,
        completed: false
    }));

    let time = 0;
    let completed = 0;
    const n = procs.length;
    const results = {};
    const ganttBlocks = [];

    while (completed < n) {
        const available = procs.filter(p => !p.completed && p.at <= time);

        if (available.length === 0) {
            const uncompleted = procs.filter(p => !p.completed);
            const nextAt = Math.min(...uncompleted.map(p => p.at));
            ganttBlocks.push({ process: "Idle", start: time, end: nextAt });
            time = nextAt;
            continue;
        }

        available.sort((a, b) => {
            if (a.bt !== b.bt) return a.bt - b.bt;
            if (a.at !== b.at) return a.at - b.at;
            return naturalCompare(a.id, b.id);
        });

        const p = available[0];
        const start = time;
        const ct = start + p.bt;
        time = ct;

        p.completed = true;
        completed += 1;

        ganttBlocks.push({ process: p.id, start: start, end: ct });

        const tat = ct - p.at;
        const wt = tat - p.bt;

        results[p.id] = {
            id: p.id,
            at: p.at,
            bt: p.bt,
            ct: ct,
            tat: tat,
            wt: wt
        };
    }

    const sortedProcs = JSON.parse(JSON.stringify(processes)).sort((a, b) => naturalCompare(a.id, b.id));
    const resList = sortedProcs.map(p => results[p.id]);

    const avgTat = n > 0 ? resList.reduce((acc, r) => acc + r.tat, 0) / n : 0;
    const avgWt = n > 0 ? resList.reduce((acc, r) => acc + r.wt, 0) / n : 0;

    return { results: resList, avgTat, avgWt, ganttBlocks };
}

function simulateRR(processes, quantum) {
    const procs = processes.map(p => ({
        id: p.id,
        at: p.at,
        bt: p.bt,
        rem: p.bt,
        ct: 0
    }));

    let time = 0;
    const queue = [];
    const n = procs.length;
    let completed = 0;
    const ganttBlocks = [];

    const inarrival = [...procs].sort((a, b) => {
        if (a.at !== b.at) return a.at - b.at;
        return naturalCompare(a.id, b.id);
    });

    if (inarrival.length > 0 && inarrival[0].at > time) {
        ganttBlocks.push({
            process: "Idle",
            start: time,
            end: inarrival[0].at
        });
        time = inarrival[0].at;
    }

    while (completed < n) {
        while (inarrival.length > 0 && inarrival[0].at <= time) {
            queue.push(inarrival.shift());
        }

        if (queue.length === 0) {
            if (inarrival.length > 0) {
                const nextAt = inarrival[0].at;
                ganttBlocks.push({ process: "Idle", start: time, end: nextAt });
                time = nextAt;
                continue;
            } else {
                break;
            }
        }

        const curr = queue.shift();
        const runT = Math.min(quantum, curr.rem);
        const start = time;

        for (let step = 0; step < runT; step++) {
            time += 1;
            curr.rem -= 1;

            while (inarrival.length > 0 && inarrival[0].at <= time) {
                queue.push(inarrival.shift());
            }
        }

        ganttBlocks.push({ process: curr.id, start: start, end: time });

        if (curr.rem === 0) {
            curr.ct = time;
            completed += 1;
        } else {
            queue.push(curr);
        }
    }

    const results = [];
    for (const p of procs) {
        const tat = p.ct - p.at;
        const wt = tat - p.bt;
        results.push({
            id: p.id,
            at: p.at,
            bt: p.bt,
            ct: p.ct,
            tat: tat,
            wt: wt
        });
    }

    const avgTat = n > 0 ? results.reduce((acc, r) => acc + r.tat, 0) / n : 0;
    const avgWt = n > 0 ? results.reduce((acc, r) => acc + r.wt, 0) / n : 0;

    return { results, avgTat, avgWt, ganttBlocks };
}

// 5 Required Test Cases from instructions:
// 1. process มาถึงพร้อมกัน
// 2. มี Idle ช่วงต้น
// 3. มี Idle ช่วงกลาง
// 4. quantum ใหญ่กว่า BT ทุกตัว
// 5. 1 process เดียว
// Plus: default values, and natural sorting (e.g. P2, P10)

const testCases = [
    {
        name: "Case 1: Arrive at same time",
        processes: [{ id: "P1", at: 0, bt: 4 }, { id: "P2", at: 0, bt: 2 }, { id: "P3", at: 0, bt: 6 }],
        quantum: 2
    },
    {
        name: "Case 2: Idle at start",
        processes: [{ id: "P1", at: 2, bt: 4 }, { id: "P2", at: 3, bt: 5 }],
        quantum: 2
    },
    {
        name: "Case 3: Idle in middle",
        processes: [{ id: "P1", at: 0, bt: 2 }, { id: "P2", at: 5, bt: 3 }],
        quantum: 2
    },
    {
        name: "Case 4: Quantum larger than all BT",
        processes: [{ id: "P1", at: 0, bt: 3 }, { id: "P2", at: 1, bt: 2 }],
        quantum: 10
    },
    {
        name: "Case 5: Single process",
        processes: [{ id: "P1", at: 0, bt: 5 }],
        quantum: 2
    },
    {
        name: "Case 6: Default inputs",
        processes: [{ id: "P1", at: 0, bt: 5 }, { id: "P2", at: 1, bt: 3 }, { id: "P3", at: 2, bt: 8 }, { id: "P4", at: 3, bt: 6 }],
        quantum: 2
    },
    {
        name: "Case 7: Natural sort order (P2 before P10)",
        processes: [{ id: "P1", at: 0, bt: 2 }, { id: "P2", at: 1, bt: 4 }, { id: "P10", at: 1, bt: 4 }],
        quantum: 2
    }
];

let allPassed = true;

for (const tc of testCases) {
    console.log(`\n========================================\nTesting: ${tc.name}\n========================================`);
    
    // Run Python reference
    const pyScript = `
import json, sys
import cpu_scheduling as cs

procs = ${JSON.stringify(tc.processes)}
q = ${tc.quantum}

f_res, f_atat, f_awt, f_gantt = cs.simulate_fcfs(procs)
s_res, s_atat, s_awt, s_gantt = cs.simulate_sjf(procs)
r_res, r_atat, r_awt, r_gantt = cs.simulate_rr_exact(procs, q)

out = {
    "fcfs": {"results": f_res, "avgTat": f_atat, "avgWt": f_awt, "gantt": f_gantt},
    "sjf": {"results": s_res, "avgTat": s_atat, "avgWt": s_awt, "gantt": s_gantt},
    "rr": {"results": r_res, "avgTat": r_atat, "avgWt": r_awt, "gantt": r_gantt}
}
print(json.dumps(out))
`;
    const pyRes = spawnSync('python', ['-c', pyScript], { encoding: 'utf-8' });
    if (pyRes.error || pyRes.status !== 0) {
        console.error('Python execution error:', pyRes.stderr);
        allPassed = false;
        continue;
    }

    const pyOutput = JSON.parse(pyRes.stdout.trim());

    // Run JS implementation
    const jsFcfs = simulateFCFS(tc.processes);
    const jsSjf = simulateSJF(tc.processes);
    const jsRr = simulateRR(tc.processes, tc.quantum);

    const checkAlgo = (algoName, jsData, pyData) => {
        let match = true;
        // check avgTat, avgWt (precision up to 4 decimal places)
        if (Math.abs(jsData.avgTat - pyData.avgTat) > 1e-4) {
            console.error(`[${algoName}] avgTat mismatch: JS=${jsData.avgTat}, PY=${pyData.avgTat}`);
            match = false;
        }
        if (Math.abs(jsData.avgWt - pyData.avgWt) > 1e-4) {
            console.error(`[${algoName}] avgWt mismatch: JS=${jsData.avgWt}, PY=${pyData.avgWt}`);
            match = false;
        }
        // check results length and content
        if (JSON.stringify(jsData.results) !== JSON.stringify(pyData.results)) {
            console.error(`[${algoName}] results mismatch:`);
            console.error('JS:', JSON.stringify(jsData.results));
            console.error('PY:', JSON.stringify(pyData.results));
            match = false;
        }
        // check gantt blocks
        const jsG = jsData.ganttBlocks.map(b => ({ process: b.process, start: b.start, end: b.end }));
        const pyG = pyData.gantt.map(b => ({ process: b.process, start: b.start, end: b.end }));
        if (JSON.stringify(jsG) !== JSON.stringify(pyG)) {
            console.error(`[${algoName}] gantt mismatch:`);
            console.error('JS:', JSON.stringify(jsG));
            console.error('PY:', JSON.stringify(pyG));
            match = false;
        }

        if (match) {
            console.log(`[${algoName}] PASSED ✓`);
        } else {
            allPassed = false;
        }
    };

    checkAlgo("FCFS", jsFcfs, pyOutput.fcfs);
    checkAlgo("SJF", jsSjf, pyOutput.sjf);
    checkAlgo("RR", jsRr, pyOutput.rr);
}

if (allPassed) {
    console.log("\n>>> ALL TEST CASES PASSED IDENTICALLY WITH PYTHON! <<<");
} else {
    console.error("\n>>> SOME TEST CASES FAILED! <<<");
    process.exit(1);
}

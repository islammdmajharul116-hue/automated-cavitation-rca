# Automated Root Cause Diagnostics and Cavitation Prevention in Flow Systems

This project is a runnable prototype for pump cavitation detection and automated control response. It estimates available NPSH, compares it against required NPSH, detects acoustic cavitation signatures, selects a likely root cause, and produces PLC-style corrective actions.

## Why It Matters

Cavitation in centrifugal and overhung pumps can destroy impellers, seals, and bearings quickly. In chemical or high-energy process loops, that failure can stop production and create major safety and compliance risk.

## What Is Included

- `src/cavitation_rca.py` - diagnostic and corrective-action prototype
- `data/pump_signal_log.csv` - synthetic pressure, flow, and acoustic logs
- `requirements.txt` - no external packages required
- `GITHUB_NOTES.md` - how to publish this project to GitHub

## Run

```bash
python src/cavitation_rca.py
```

## Engineering Concepts Demonstrated

- NPSH margin calculation
- Acoustic cavitation thresholding
- Root cause classification
- PLC-style VFD and valve response logic
- Compliance log generation
- Asset record update pattern

## Real-World Extension

Replace the sample CSV with data from pressure transducers, flow meters, acoustic emission sensors, or a historian. The control recommendations can be mapped to PLC tags after engineering validation.

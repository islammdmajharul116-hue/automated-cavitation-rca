from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "pump_signal_log.csv"


@dataclass
class PumpFrame:
    second: int
    suction_pressure_kpa: float
    discharge_pressure_kpa: float
    vapor_pressure_kpa: float
    flow_m3_h: float
    acoustic_rms_db: float
    vfd_hz: float
    suction_valve_pct: float


def load_log(path: Path = DATA_PATH) -> list[PumpFrame]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            PumpFrame(
                second=int(row["second"]),
                suction_pressure_kpa=float(row["suction_pressure_kpa"]),
                discharge_pressure_kpa=float(row["discharge_pressure_kpa"]),
                vapor_pressure_kpa=float(row["vapor_pressure_kpa"]),
                flow_m3_h=float(row["flow_m3_h"]),
                acoustic_rms_db=float(row["acoustic_rms_db"]),
                vfd_hz=float(row["vfd_hz"]),
                suction_valve_pct=float(row["suction_valve_pct"]),
            )
            for row in csv.DictReader(handle)
        ]


def npsh_available(frame: PumpFrame, fluid_density_kg_m3: float = 998.0) -> float:
    gravity = 9.80665
    pressure_head = ((frame.suction_pressure_kpa - frame.vapor_pressure_kpa) * 1000.0) / (
        fluid_density_kg_m3 * gravity
    )
    suction_losses = 0.00042 * frame.flow_m3_h**2
    return pressure_head - suction_losses


def npsh_required(frame: PumpFrame) -> float:
    base_required = 5.8
    flow_penalty = 0.0019 * max(0.0, frame.flow_m3_h - 80.0) ** 2
    speed_penalty = 0.08 * max(0.0, frame.vfd_hz - 55.0)
    return base_required + flow_penalty + speed_penalty


def detect_cavitation(frame: PumpFrame, margin_m: float) -> bool:
    acoustic_trip = frame.acoustic_rms_db >= 76.0
    hydraulic_trip = margin_m < 1.0
    return acoustic_trip and hydraulic_trip


def classify_root_cause(frame: PumpFrame, margin_m: float) -> str:
    if frame.suction_valve_pct < 75.0:
        return "restricted suction valve"
    if frame.flow_m3_h > 115.0 and frame.vfd_hz >= 60.0:
        return "pump operating too far right on curve"
    if margin_m < 0.0:
        return "insufficient suction head"
    return "incipient cavitation signature"


def corrective_action(frame: PumpFrame, cause: str) -> dict[str, float | str]:
    new_vfd_hz = max(45.0, frame.vfd_hz - 4.0)
    new_valve_pct = min(100.0, frame.suction_valve_pct + 12.0)
    return {
        "action": f"Override: reduce VFD and open suction path because of {cause}",
        "vfd_hz_setpoint": round(new_vfd_hz, 1),
        "suction_valve_pct_setpoint": round(new_valve_pct, 1),
    }


def run_diagnostics() -> None:
    for frame in load_log():
        available = npsh_available(frame)
        required = npsh_required(frame)
        margin = available - required
        cavitating = detect_cavitation(frame, margin)

        status = "CAVITATION RISK" if cavitating else "normal"
        print(
            f"t={frame.second:02d}s | NPSHa={available:5.2f} m | "
            f"NPSHr={required:5.2f} m | margin={margin:5.2f} m | "
            f"acoustic={frame.acoustic_rms_db:4.1f} dB | {status}"
        )

        if cavitating:
            cause = classify_root_cause(frame, margin)
            action = corrective_action(frame, cause)
            print(f"  RCA: {cause}")
            print(f"  PLC action: {action}")
            print(f"  Compliance log: event=PUMP_CAVITATION_PREVENTED, asset=P-204, second={frame.second}")


if __name__ == "__main__":
    run_diagnostics()

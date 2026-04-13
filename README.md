# ⬡ GRsimulator
### *General Relativity Solar System Gravity Simulator*

> "Gravity is not a force that pulls; it is the very shape of space and time itself."

**GRsimulator** is a high-precision, Python-based engine that moves beyond Newtonian physics to model the universe as Einstein saw it. Instead of treating gravity as an invisible string pulling planets together, this simulator treats the Sun as a heavy weight on a trampoline, curving the "fabric" of spacetime. Planets simply follow the straightest possible path (a *geodesic*) through that curved surface.

---

## 🌟 Why GRsimulator?

Most space simulators use "Newtonian" gravity because it's simpler. While that works for basic orbits, it fails to explain the precision of our universe. **GRsimulator** is built from the ground up to be "relativistically correct."

- **Physics-First:** We don't use "patches" for relativity; we solve the actual Einsteinian equations of motion.
- **Multi-Scale Precision:** From the massive Sun ($10^{30}$ kg) down to a $70$ kg human, the engine maintains accuracy across an extreme range of scales.
- **Active Exploration:** Pilot rockets and plan missions where **Time Dilation** isn't just a theory—it's a functional constraint on your journey.

---

## 🚀 Key Features

- **Schwarzschild Spacetime:** Accurate modeling of the static, curved geometry around the Sun.
- **Mercury's Precession:** Witness the "flowering" orbit of Mercury—a phenomenon Newtonian physics cannot explain.
- **Gravitational Time Dilation:** See how time moves slower for objects closer to a massive body (Proper Time vs. Coordinate Time).
- **Interactive 3D Visualization:** Real-time rendering of spacetime paths with persistent orbit trails and camera controls.
- **Rocket Propulsion (Phase 2):** Launch and steer rockets with active thrust vectors within a General Relativity field.

---

## 🛠️ Technology Stack

- **Language:** Python 3.10+
- **Numerics:** NumPy & SciPy (High-order adaptive ODE solvers like RK45)
- **Visualization:** Matplotlib / PyOpenGL (Real-time 3D rendering)
- **Data:** Telemetry export via NumPy `.npz` and CSV

---

## 📐 How It Works (The Simple Version)

Imagine the Sun is a bowling ball on a rubber sheet. 
1. **The Metric:** We define the "shape" of the rubber sheet (Schwarzschild Metric).
2. **The Connection:** we calculate the "slopes" and "curves" at every point (Christoffel Symbols).
3. **The Path:** We find the path of least resistance for a planet or rocket (The Geodesic Equation).
4. **The Solve:** We use a high-powered math "engine" to step through time and update positions (RK45 Integrator).

*For a deep dive into the math and architecture, see our [Technical Details](docs/TECHNICAL_DETAILS.md).*

---

## 🚥 Getting Started

### Prerequisites
- Python 3.10 or higher
- `pip install numpy scipy matplotlib`

### Running a Scenario
You can run pre-configured scientific scenarios straight from the CLI:
```bash
python main.py --scenario mercury_precession
```

---

## 🗺️ Roadmap
- **Phase 1 (MVP):** Planetary orbits in a Schwarzschild field. (Complete)
- **Phase 2 (Growth):** Rockets, thrust, and human-scale objects. (In Progress)
- **Phase 3 (Vision):** Rotating Black Holes (Kerr Metric) and Gravitational Lensing.

---

## 📜 License & Usage
This project is an **Open-Source Educational & Scientific Research Tool**. It is designed for students and researchers to explore the beauty of General Relativity without the "red tape" of proprietary software.

*Created as a Technical Challenge Project by Prince Joshi.*

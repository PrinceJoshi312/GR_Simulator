# Technical Details: GRsimulator Architecture

This document provides a detailed breakdown of the physics, numerics, and software architecture used in **GRsimulator**.

## 1. The Physics Model: Curvature as Geometry

### Schwarzschild Metric
We model the Sun as a static, spherically symmetric mass $M$. The spacetime geometry is described by the Schwarzschild solution:
$$ds^2 = -\left(1 - \frac{r_s}{r}\right) c^2 dt^2 + \left(1 - \frac{r_s}{r}\right)^{-1} dr^2 + r^2 (d\theta^2 + \sin^2\theta d\phi^2)$$
where $r_s = \frac{2GM}{c^2}$ is the Schwarzschild radius. This metric tells us how "distances" and "times" are measured near a massive body.

### The Geodesic Equation: "Straight" Lines in Curved Space
In General Relativity, objects don't feel a "force" of gravity. Instead, they move along paths that extremize proper time (geodesics). This is governed by the geodesic equation:
$$\frac{d^2 x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta} \frac{dx^\alpha}{d\tau} \frac{dx^\beta}{d\tau} = 0$$
The simulator solves this 4D non-linear system for $(t, r, \theta, \phi)$ in the equatorial plane ($\theta = \pi/2$), which simplifies the math while preserving all the key relativistic effects like precession and time dilation.

---

## 2. How the Engine Works: A Step-by-Step Breakdown

When you click "Run" in GRsimulator, the engine performs the following cycle for every object in every frame:

1.  **Metric Sampling:** The `Physics Layer` looks at the object's current position $(r, \phi)$ and calculates the **Metric Tensor** $g_{\mu\nu}$ at that exact point in space.
2.  **Curvature Calculation:** Using the metric, the engine solves for the **Christoffel Symbols** $\Gamma^\mu_{\alpha\beta}$. These are essentially the "slopes" or "forces of geometry" that tell the object how to curve.
3.  **Equation of Motion (EOM) Assembly:** The `Geodesic Layer` plugs these symbols into the geodesic equation to find the object's **Acceleration** (the second derivative of its position).
4.  **The Numerical Step:** The `Numerics Layer` takes this acceleration and uses the **RK45 Integrator** to "step" the object forward in time. This isn't a fixed step; if the object is near the Sun where gravity is "steep," the engine automatically takes smaller, more precise steps.
5.  **Relativistic Update:** The engine updates the object's **Proper Time** ($\tau$) and **Coordinate Time** ($t$). This is where you see the clock on a rocket move slower than the clock on Earth.
6.  **Rendering:** Finally, the `Visualization Layer` translates these 4D coordinates into a 3D position on your screen and draws an orbit trail.

---

## 3. Technology Stack Deep Dive: Why These Tools?

### **Python 3.10+**
Python is the "glue" of the scientific world. We chose it because it allows researchers and students to read the code as easily as they read a textbook. The logic is transparent and un-obfuscated.

### **NumPy: The Tensor Engine**
While Python is slow for heavy math, **NumPy** is lightning fast. We use NumPy's vectorized arrays to perform the tensor math for the metric and Christoffel symbols. This allows us to simulate multiple planets simultaneously without the CPU breaking a sweat.

### **SciPy: The High-Order Solver**
General Relativity equations are "stiff"—meaning small errors can spiral out of control. We use **SciPy's `solve_ivp`** (specifically the RK45 method) because it's a "smart" integrator. It monitors its own error levels and adjusts the simulation speed to ensure the orbits don't drift.

### **Matplotlib / PyOpenGL: Visualizing the Fabric**
The visualization layer handles the complex task of projecting 4D relativistic paths onto a 3D screen. We use **Matplotlib** for clean, scientific plotting of orbit trails and **PyOpenGL** for high-performance 3D rendering.

---

## 4. Multi-Scale Challenges: Handling Humans & Stars

The biggest technical hurdle in GRsimulator is the **Scale Ratio**. A 70kg human is "invisible" to a $10^{30}$kg Sun. 
- **Double Precision:** We use 64-bit floats (`float64`) to ensure that even at a distance of $150$ million kilometers (1 AU), a human's position is tracked down to the millimeter.
- **Thrust Integration:** For rockets, we modify the geodesic equation by adding a "Force Term" $F^\mu / m$. This allows the simulator to handle **non-geodesic motion**, which is how a pilot "fights" the curvature of space to land on a planet or escape a black hole.

---

## 5. Real-Time Telemetry & Validation: The Trust Layer

To bridge the gap between heavy physics computation and an interactive UI, GRsimulator employs a "Trust-First" communication architecture.

### Background Simulation Loop (The Heartbeat)
The backend doesn't wait for UI requests to advance the physics. Instead, a **60Hz asynchronous background loop** runs within the FastAPI lifespan. 
- **Deterministic Stepping:** Every 16.6ms, the loop triggers `step_run()` for all active simulations.
- **Concurrency:** This loop is isolated from the REST API, ensuring that a slow UI or network hiccup never "stalls" the physics engine.

### Telemetry Streaming via SSE
We use **Server-Sent Events (SSE)** to push high-frequency data to the frontend.
- **One-Way Efficiency:** Unlike WebSockets, SSE is optimized for one-way streams (Server -> UI), reducing overhead for telemetry.
- **Broadcast Mechanism:** The `SimulationEngine` uses `asyncio.Queue` per connected client. When the physics loop finishes a step, it broadcasts a "snapshot" of all objects to these queues simultaneously.

### The Validation Layer: Real-Time Verification
Scientific credibility requires constant monitoring of numerical health. Every telemetry packet is enhanced with **Validation Metadata** before it leaves the server:
- **Stability Checks:** The engine monitors for `NaN` or `Inf` values that signal numerical "evaporation" or integration failure.
- **Event Horizon Proximity:** For every object, the engine calculates the ratio $R / R_s$. If an object approaches the Schwarzschild radius ($R \rightarrow R_s$), the system flags a "Critical" state, as the metric becomes singular and standard integration becomes unreliable.
- **Error Estimation:** The system tracks the "Energy Constant" of the orbit. In a perfect Schwarzschild vacuum, this should be invariant; any drift in this value is reported as an "Error Estimate" in the UI.

### Coordinate Scaling & Visualization
The 3D viewport operates on a "Visual Unit" system where **$1$ unit = $10^9$ meters** ($1$ million km). 
- **Precision Preservation:** All physics calculations are performed in SI units (meters) with `float64` precision. Scaling only happens at the "Last Mile" in the frontend telemetry service to prevent precision loss during integration.
- **Axis Mapping:** The 2D physics plane $(x, y)$ is mapped to the 3D visual plane $(x, 0, z)$ to align with the standard "orbital plane" representation in astronomical visualizations.

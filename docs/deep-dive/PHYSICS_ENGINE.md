# Physics Engine: General Relativity Deep Dive

This document provides a rigorous mathematical and conceptual breakdown of the physics kernel powering **GRsimulator**.

## 1. Foundations: Geometry as Gravity

In General Relativity (GR), gravity is not a force but a consequence of the curvature of four-dimensional spacetime. Objects in freefall do not "accelerate" due to a force; they follow **geodesics**—the "straightest possible paths" in curved space.

### The Metric Tensor ($g_{\mu\nu}$)
The metric tensor defines the "ruler" of spacetime. It allows us to calculate the interval $ds^2$ between two events:
$$ds^2 = g_{\mu\nu} dx^\mu dx^\nu$$

## 2. The Schwarzschild Metric (Static Central Mass)

Used for non-rotating bodies (like a simplified Sun), the Schwarzschild metric describes the geometry outside a spherically symmetric mass $M$:

$$ds^2 = -\left(1 - \frac{r_s}{r}\right) c^2 dt^2 + \left(1 - \frac{r_s}{r}\right)^{-1} dr^2 + r^2 (d\theta^2 + \sin^2\theta d\phi^2)$$

Where:
*   $r_s = \frac{2GM}{c^2}$ is the **Schwarzschild Radius** (Event Horizon).
*   $t$ is **Coordinate Time** (measured by an observer at infinity).
*   $\tau$ is **Proper Time** (measured by a clock on the orbiting object).

### Key Relativistic Effects Simulated:
1.  **Perihelion Precession:** Unlike Newtonian orbits which are closed ellipses, GR orbits "shift" slightly every revolution. This was the first major proof of Einstein's theory (Mercury's orbit).
2.  **Gravitational Time Dilation:** Clocks closer to the mass run slower than clocks further away.

---

## 3. The Kerr Metric (Rotating Central Mass)

The Kerr metric is far more complex, describing spacetime around a spinning mass. This introduces the concept of **Frame Dragging**.

### The Metric Components (Equatorial Plane $\theta = \pi/2$):
In our simulator, we use the Boyer-Lindquist representation simplified for the equatorial plane to ensure performance:

*   $g_{tt} = -(1 - \frac{r_s r}{\rho^2})$
*   $g_{rr} = \frac{\rho^2}{\Delta}$
*   $g_{\phi\phi} = \frac{A}{\rho^2}$
*   $g_{t\phi} = -\frac{r_s r a}{\rho^2}$

Where:
*   $\Delta = r^2 - r_s r + a^2$
*   $\rho^2 = r^2$ (at the equator)
*   $a = \frac{J}{Mc}$ is the **Spin Parameter** (Angular momentum per unit mass).

### Frame Dragging (Lense-Thirring Effect)
The $g_{t\phi}$ term represents the "twisting" of spacetime. A rotating black hole literally "drags" the space around it, forcing objects to move in the direction of the spin even if they have no initial angular velocity.

---

## 4. The Equations of Motion: Geodesics

To find where a planet goes, we solve the **Geodesic Equation**:

$$\frac{d^2 x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta} \frac{dx^\alpha}{d\tau} \frac{dx^\beta}{d\tau} = 0$$

### Christoffel Symbols ($\Gamma^\mu_{\alpha\beta}$)
These represent the "connection" or the "gravitational field" derived from derivatives of the metric:
$$\Gamma^\mu_{\alpha\beta} = \frac{1}{2} g^{\mu\sigma} (\partial_\beta g_{\sigma\alpha} + \partial_\alpha g_{\sigma\beta} - \partial_\sigma g_{\alpha\beta})$$

The simulator's `christoffel.py` calculates these symbols analytically for Schwarzschild and Kerr metrics to provide the precise "curvature force" at every step.

---

## 5. Numerical Implementation: RK4 Integration

Since these differential equations are non-linear and coupled, we cannot solve them exactly for multiple bodies. We use the **4th-Order Runge-Kutta (RK4)** method.

### The Algorithm:
For each state vector $Y = [x, y, v_x, v_y]$, we compute four "slopes" ($k_1, k_2, k_3, k_4$):
1.  $k_1 = f(t_n, Y_n)$
2.  $k_2 = f(t_n + \frac{h}{2}, Y_n + \frac{h}{2} k_1)$
3.  $k_3 = f(t_n + \frac{h}{2}, Y_n + \frac{h}{2} k_2)$
4.  $k_4 = f(t_n + h, Y_n + h k_3)$

The next state is: $Y_{n+1} = Y_n + \frac{h}{6}(k_1 + 2k_2 + 2k_3 + k_4)$

This method provides $O(h^4)$ accuracy, allowing for stable planetary orbits over long simulation times without the "energy drift" found in simpler Euler methods.

---

## 6. Time Dilation Calculation

The simulator tracks two times for every object:
1.  **Coordinate Time ($t$):** The master clock of the simulation.
2.  **Proper Time ($\tau$):** The time experienced by the object itself.

The relationship is derived from the metric:
$$d\tau = \sqrt{-g_{tt} dt^2 - \frac{1}{c^2}(g_{rr} dr^2 + g_{\phi\phi} d\phi^2 + 2g_{t\phi} dt d\phi)}$$

In the simulation, you will notice the **Time Drift ($\Delta t$)** value increasing faster for objects closer to the Sun or moving at extreme velocities (relativistic speeds).

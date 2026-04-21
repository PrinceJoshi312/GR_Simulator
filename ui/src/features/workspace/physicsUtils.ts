import * as THREE from "three";

export function calculateDisplacement(x: number, z: number, objects: Record<string, any>) {
  // Visual masses for visualization only (not physical)
  const SUN_VISUAL_MASS = 120;
  
  const massiveBodies = [
    { x: 0, z: 0, mass: SUN_VISUAL_MASS },
    ...Object.entries(objects).map(([name, obj]) => {
        // Boost large planets for visibility
        let visualMass = 12;
        const n = name.toLowerCase();
        if (n === "jupiter") visualMass = 35;
        if (n === "saturn") visualMass = 28;
        if (n === "uranus" || n === "neptune") visualMass = 18;
        if (n === "earth" || n === "venus") visualMass = 12;
        if (n === "mars" || n === "mercury") visualMass = 8;
        
        return {
            x: obj.position[0],
            z: obj.position[2],
            mass: visualMass
        };
    })
  ];

  let dy = 0;
  massiveBodies.forEach(body => {
    const dx = x - body.x;
    const dz = z - body.z;
    const distSq = dx * dx + dz * dz;
    const dist = Math.sqrt(distSq);
    
    // Potential-like displacement: pull = M / (r + epsilon)
    // We use a sharper drop-off for more defined 'dents'
    // dy -= (body.mass * 200) / (dist + 5);
    
    // Combining a broad potential with a sharper local dent
    const pull = (body.mass * 80) / (dist + 15) + (body.mass * 120) / (distSq / 5.0 + 2.0);
    dy -= pull;
  });
  
  return dy;
}

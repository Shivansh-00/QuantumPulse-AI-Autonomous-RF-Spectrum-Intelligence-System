import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const TARGET_FPS = 30;
const FRAME_INTERVAL = 1 / TARGET_FPS;

function WaveMesh({ signalData }) {
  const meshRef = useRef();
  const geometryRef = useRef();
  const lastFrameTime = useRef(0);

  // Create wave geometry from signal data or default animated wave
  const { positions, colors } = useMemo(() => {
    const width = 200;
    const depth = 30;
    const pos = [];
    const col = [];

    for (let z = 0; z < depth; z++) {
      for (let x = 0; x < width; x++) {
        const xNorm = (x / width) * 2 - 1;
        const zNorm = (z / depth) * 2 - 1;

        let y = 0;
        if (signalData && signalData.length > 0) {
          const dataIdx = Math.floor((x / width) * signalData.length);
          y = (signalData[dataIdx] || 0) * 0.3;
        } else {
          y = Math.sin(xNorm * 8) * 0.2 * Math.cos(zNorm * 3);
        }

        pos.push(xNorm * 5, y, zNorm * 2);

        // Color based on amplitude
        const intensity = Math.abs(y);
        const r = 0.2 + intensity * 2;
        const g = 0.5 - intensity * 0.5;
        const b = 1.0 - intensity * 0.3;
        col.push(r, g, b);
      }
    }

    return {
      positions: new Float32Array(pos),
      colors: new Float32Array(col),
    };
  }, [signalData]);

  // Animate — throttled to TARGET_FPS, idle animation only when no signal data
  useFrame(({ clock }) => {
    const elapsed = clock.elapsedTime;
    if (elapsed - lastFrameTime.current < FRAME_INTERVAL) return;
    lastFrameTime.current = elapsed;

    if (meshRef.current) {
      meshRef.current.rotation.x = -0.5;
      meshRef.current.rotation.z = Math.sin(elapsed * 0.3) * 0.05;
    }

    // Animate vertices only when no signal data (idle state)
    if (geometryRef.current && !signalData) {
      const posAttr = geometryRef.current.attributes.position;
      const colAttr = geometryRef.current.attributes.color;
      const t = elapsed;
      const width = 200;
      const depth = 30;

      for (let z = 0; z < depth; z++) {
        for (let x = 0; x < width; x++) {
          const idx = z * width + x;
          const xNorm = (x / width) * 2 - 1;
          const zNorm = (z / depth) * 2 - 1;

          const y =
            Math.sin(xNorm * 8 + t * 2) * 0.2 *
            Math.cos(zNorm * 3 + t * 0.5) +
            Math.sin(xNorm * 15 + t * 3) * 0.08;

          posAttr.setY(idx, y);

          const intensity = Math.abs(y);
          colAttr.setX(idx, 0.2 + intensity * 3);
          colAttr.setY(idx, 0.4 - intensity * 0.3);
          colAttr.setZ(idx, 1.0 - intensity * 0.2);
        }
      }
      posAttr.needsUpdate = true;
      colAttr.needsUpdate = true;
    }
  });

  return (
    <points ref={meshRef}>
      <bufferGeometry ref={geometryRef}>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={colors.length / 3}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial size={0.03} vertexColors transparent opacity={0.8} sizeAttenuation />
    </points>
  );
}

export default React.memo(function WaveScene({ signalData }) {
  return (
    <Canvas
      camera={{ position: [0, 2, 4], fov: 60 }}
      style={{ background: 'transparent' }}
      gl={{ alpha: true, antialias: false, powerPreference: 'low-power' }}
      dpr={[1, 1.5]}
    >
      <ambientLight intensity={0.5} />
      <WaveMesh signalData={signalData} />
    </Canvas>
  );
});

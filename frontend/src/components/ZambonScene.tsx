import { Canvas } from '@react-three/fiber'
import { ContactShadows, Environment, OrbitControls } from '@react-three/drei'

function PlaceholderZamboni() {
  return (
    <group position={[0, 0, 0]}>
      {/* Body */}
      <mesh position={[0, 0.3, 0]} castShadow receiveShadow>
        <boxGeometry args={[3, 0.6, 1.4]} />
        <meshStandardMaterial color="#1c1c20" metalness={0.5} roughness={0.45} />
      </mesh>

      {/* Cab */}
      <mesh position={[0.5, 1, 0]} castShadow>
        <boxGeometry args={[1.3, 0.8, 1.2]} />
        <meshStandardMaterial color="#26262a" metalness={0.4} roughness={0.4} />
      </mesh>

      {/* Conditioner / rear box */}
      <mesh position={[-1.8, 0.45, 0]} castShadow>
        <boxGeometry args={[0.8, 0.75, 1.35]} />
        <meshStandardMaterial color="#0a0a0b" metalness={0.6} roughness={0.55} />
      </mesh>

      {/* Accent stripe along the body */}
      <mesh position={[0, 0.55, 0.71]}>
        <boxGeometry args={[3.01, 0.04, 0.005]} />
        <meshStandardMaterial
          color="#7dd3fc"
          emissive="#7dd3fc"
          emissiveIntensity={0.6}
        />
      </mesh>
      <mesh position={[0, 0.55, -0.71]}>
        <boxGeometry args={[3.01, 0.04, 0.005]} />
        <meshStandardMaterial
          color="#7dd3fc"
          emissive="#7dd3fc"
          emissiveIntensity={0.6}
        />
      </mesh>

      {/* Wheels (front + rear) */}
      {[
        [1.1, 0, 0.6],
        [1.1, 0, -0.6],
        [-1.1, 0, 0.6],
        [-1.1, 0, -0.6],
      ].map(([x, y, z], i) => (
        <mesh
          key={i}
          position={[x, y, z]}
          rotation={[Math.PI / 2, 0, 0]}
          castShadow
        >
          <cylinderGeometry args={[0.28, 0.28, 0.35, 24]} />
          <meshStandardMaterial color="#08080a" metalness={0.2} roughness={0.85} />
        </mesh>
      ))}
    </group>
  )
}

export function ZambonScene() {
  return (
    <Canvas
      shadows
      camera={{ position: [4.5, 2.5, 5], fov: 42 }}
      gl={{ antialias: true }}
    >
      <ambientLight intensity={0.35} />
      <directionalLight
        position={[6, 9, 5]}
        intensity={1.1}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
        shadow-camera-near={0.1}
        shadow-camera-far={30}
      />
      <PlaceholderZamboni />
      <ContactShadows
        position={[0, 0, 0]}
        opacity={0.55}
        scale={10}
        blur={2.4}
        far={4}
      />
      <Environment preset="warehouse" />
      <OrbitControls
        enablePan={false}
        minDistance={4}
        maxDistance={12}
        minPolarAngle={Math.PI / 6}
        maxPolarAngle={Math.PI / 2.05}
      />
    </Canvas>
  )
}

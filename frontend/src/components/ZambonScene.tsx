import { Suspense, useMemo } from 'react'
import { Color, Mesh, MeshStandardMaterial } from 'three'
import { Canvas } from '@react-three/fiber'
import {
  Bounds,
  Center,
  Environment,
  OrbitControls,
  useGLTF,
} from '@react-three/drei'

const MODEL_URL = '/models/zamboni.gltf'
useGLTF.preload(MODEL_URL)

const POLAR_ANGLE = Math.PI / 2.25 // ~80°, slightly above horizon — locked

function Zamboni() {
  const { scene } = useGLTF(MODEL_URL)
  const cloned = useMemo(() => {
    const copy = scene.clone()
    const material = new MeshStandardMaterial({
      color: new Color('#bdbdc0'),
      metalness: 0.05,
      roughness: 0.85,
    })
    copy.traverse((obj) => {
      if (obj instanceof Mesh) {
        obj.material = material
        obj.castShadow = true
        obj.receiveShadow = true
      }
    })
    return copy
  }, [scene])
  return <primitive object={cloned} />
}

function Floor() {
  return (
    <mesh
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, 0, 0]}
      receiveShadow
    >
      <planeGeometry args={[80, 80]} />
      <meshStandardMaterial color="#1f1f24" roughness={0.9} metalness={0.1} />
    </mesh>
  )
}

export function ZambonScene() {
  return (
    <Canvas
      shadows
      frameloop="demand"
      camera={{ position: [10, 1.8, 0], fov: 35 }}
      gl={{ antialias: true }}
    >
      <color attach="background" args={['#2a2a2e']} />

      <ambientLight intensity={0.45} />
      <directionalLight
        position={[5, 9, 3]}
        intensity={0.9}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-near={0.5}
        shadow-camera-far={30}
        shadow-camera-left={-8}
        shadow-camera-right={8}
        shadow-camera-top={8}
        shadow-camera-bottom={-8}
      />
      <directionalLight position={[-6, 4, -4]} intensity={0.35} />

      <Floor />

      <Suspense fallback={null}>
        <Bounds fit clip observe margin={1.3}>
          <Center bottom>
            <Zamboni />
          </Center>
        </Bounds>
      </Suspense>

      <Environment preset="studio" />
      <OrbitControls
        enablePan={false}
        enableZoom={false}
        minPolarAngle={POLAR_ANGLE}
        maxPolarAngle={POLAR_ANGLE}
      />
    </Canvas>
  )
}

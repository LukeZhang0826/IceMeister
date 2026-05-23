import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import {
  Bounds,
  Center,
  ContactShadows,
  Environment,
  OrbitControls,
  useGLTF,
} from '@react-three/drei'

const MODEL_URL = '/models/zamboni.gltf'
useGLTF.preload(MODEL_URL)

function Zamboni() {
  const { scene } = useGLTF(MODEL_URL)
  return <primitive object={scene} />
}

export function ZambonScene() {
  return (
    <Canvas
      shadows
      frameloop="demand"
      camera={{ position: [6, 4, 8], fov: 38 }}
      gl={{ antialias: true }}
    >
      <ambientLight intensity={0.35} />
      <directionalLight
        position={[6, 9, 5]}
        intensity={1.1}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />

      <Suspense fallback={null}>
        <Bounds fit clip observe margin={1.05}>
          <Center bottom>
            <Zamboni />
          </Center>
        </Bounds>
      </Suspense>

      <ContactShadows
        position={[0, 0, 0]}
        opacity={0.55}
        scale={24}
        blur={2.4}
        far={8}
      />
      <Environment preset="warehouse" />
      <OrbitControls
        enablePan={false}
        enableZoom={false}
        minPolarAngle={Math.PI / 6}
        maxPolarAngle={Math.PI / 2.05}
      />
    </Canvas>
  )
}

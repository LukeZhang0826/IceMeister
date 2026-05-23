import { Suspense, useMemo } from 'react'
import { Box3, Color, Mesh, MeshStandardMaterial, Vector3 } from 'three'
import { Canvas } from '@react-three/fiber'
import { Environment, OrbitControls, useGLTF } from '@react-three/drei'

const MODEL_URL = '/models/zamboni.gltf'
useGLTF.preload(MODEL_URL)

const POLAR_ANGLE = Math.PI / 2.25 // ~80°, locked
const TARGET_SIZE = 3 // model is normalized so its largest dimension is 3 units

function Zamboni() {
  const { scene } = useGLTF(MODEL_URL)

  const normalized = useMemo(() => {
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

    const box = new Box3().setFromObject(copy)
    const size = new Vector3()
    box.getSize(size)
    const maxDim = Math.max(size.x, size.y, size.z)
    if (maxDim > 0) {
      copy.scale.setScalar(TARGET_SIZE / maxDim)
    }

    const scaledBox = new Box3().setFromObject(copy)
    const center = new Vector3()
    scaledBox.getCenter(center)
    copy.position.set(-center.x, -scaledBox.min.y, -center.z)

    return copy
  }, [scene])

  return <primitive object={normalized} />
}

function Floor() {
  return (
    <mesh
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, -0.01, 0]}
      receiveShadow
    >
      <planeGeometry args={[30, 30]} />
      <meshStandardMaterial color="#1f1f24" roughness={0.9} metalness={0.05} />
    </mesh>
  )
}

export function ZambonScene() {
  return (
    <Canvas
      shadows
      frameloop="demand"
      camera={{ position: [5, 1.5, 0], fov: 38, near: 0.1, far: 100 }}
      gl={{ antialias: true, logarithmicDepthBuffer: true }}
    >
      <color attach="background" args={['#2a2a2e']} />

      <ambientLight intensity={0.5} />
      <directionalLight
        position={[4, 6, 3]}
        intensity={0.9}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-near={0.5}
        shadow-camera-far={20}
        shadow-camera-left={-5}
        shadow-camera-right={5}
        shadow-camera-top={5}
        shadow-camera-bottom={-5}
        shadow-bias={-0.0001}
      />
      <directionalLight position={[-4, 3, -3]} intensity={0.3} />

      <Floor />

      <Suspense fallback={null}>
        <Zamboni />
      </Suspense>

      <Environment preset="studio" />
      <OrbitControls
        target={[0, 0.6, 0]}
        enablePan={false}
        enableZoom={false}
        minPolarAngle={POLAR_ANGLE}
        maxPolarAngle={POLAR_ANGLE}
      />
    </Canvas>
  )
}

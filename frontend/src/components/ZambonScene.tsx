import { Suspense, useMemo } from 'react'
import { Box3, Color, Mesh, MeshStandardMaterial, Vector3 } from 'three'
import { Canvas } from '@react-three/fiber'
import { Environment, OrbitControls, useGLTF } from '@react-three/drei'

const MODEL_URL = '/models/zamboni.gltf'
useGLTF.preload(MODEL_URL)

const POLAR_ANGLE = Math.PI / 2.25 // ~80°, locked
const TARGET_SIZE = 3 // largest dimension after normalization
const MODEL_ROTATION: [number, number, number] = [-Math.PI / 7, 0, 0]
const SCENE_BG = '#0a0a0a' // floor + canvas bg + section bg all match — no horizon

function Zamboni() {
  const { scene } = useGLTF(MODEL_URL)

  const normalized = useMemo(() => {
    const copy = scene.clone()
    const material = new MeshStandardMaterial({
      color: new Color('#a6a6a8'),
      metalness: 0.08,
      roughness: 0.78,
    })
    copy.traverse((obj) => {
      if (obj instanceof Mesh) {
        obj.material = material
        obj.castShadow = true
        obj.receiveShadow = true
      }
    })

    // Corrective rotation FIRST — the .gltf has a baked forward-tilt
    copy.rotation.set(...MODEL_ROTATION)

    // Then normalize size based on the rotated bounding box
    const box = new Box3().setFromObject(copy)
    const size = new Vector3()
    box.getSize(size)
    const maxDim = Math.max(size.x, size.y, size.z)
    if (maxDim > 0) {
      copy.scale.setScalar(TARGET_SIZE / maxDim)
    }

    // Re-ground after scale: bottom at y=0, centered on x/z
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
      <planeGeometry args={[40, 40]} />
      <meshStandardMaterial color={SCENE_BG} roughness={0.95} metalness={0.05} />
    </mesh>
  )
}

export function ZambonScene() {
  return (
    <Canvas
      shadows
      frameloop="demand"
      camera={{ position: [-8, 1.5, -1], fov: 32, near: 0.1, far: 100 }}
      gl={{ antialias: true, logarithmicDepthBuffer: true }}
    >
      <color attach="background" args={[SCENE_BG]} />

      <ambientLight intensity={0.55} />
      {/* Key light — upper right-front */}
      <directionalLight
        position={[5, 7, 4]}
        intensity={1.1}
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
      {/* Fill light — opposite side, softer */}
      <directionalLight position={[-5, 4, -3]} intensity={0.45} />
      {/* Rim light — behind, for edge separation */}
      <directionalLight position={[0, 3, -6]} intensity={0.5} />

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

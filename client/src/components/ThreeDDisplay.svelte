<script>
    // Using Threlte v6 from https://next.threlte.xyz/docs/learn/getting-started/your-first-scene 
    import {Canvas} from '@threlte/core';
    import {T, useFrame} from '@threlte/core';
    import * as THREE from 'three';
    import { spring } from 'svelte/motion'


    import { interactivity } from '@threlte/extras'
    interactivity()
    // import * as Utils from 'three/src/math/MathUtils.js'

    /* 
    BUG: [!] Error: Could not load /home/fun-linux/Documents/Rgee-Gallega/DL-Projects/PhD-Projects/exploring-textures-with-stablediffusion/client/node_modules/three/examples/jsm/loaders/DRACOLoader (imported by node_modules/@threlte/extras/dist/hooks/useGltf.js): ENOENT: no such file or directory, open '/home/fun-linux/Documents/Rgee-Gallega/DL-Projects/PhD-Projects/exploring-textures-with-stablediffusion/client/node_modules/three/examples/jsm/loaders/DRACOLoader'
    Error: Could not load /home/fun-linux/Documents/Rgee-Gallega/DL-Projects/PhD-Projects/exploring-textures-with-stablediffusion/client/node_modules/three/examples/jsm/loaders/DRACOLoader (imported by node_modules/@threlte/extras/dist/hooks/useGltf.js): ENOENT: no such file or directory, open '/home/fun-linux/Documents/Rgee-Gallega/DL-Projects/PhD-Projects/exploring-textures-with-stablediffusion/client/node_modules/three/examples/jsm/loaders/DRACOLoader'
    
    */

    import {curr_rendering_path} from '../stores.js';
	import {curr_texture_parts} from '../stores.js';
	import {curr_textureparts_path} from '../stores.js';

    const scale = spring(1)
    let rotation = 0
    useFrame((state, delta) => {
        rotation += delta
    })

    let scene, camera, renderer;
</script>

<Canvas> 

    <T.PerspectiveCamera 
        makeDefault 
        position={[10,10,10]} 
        on:create={({ ref }) => {
            ref.lookAt(0,1,0);
        }}
    />

    <T.DirectionalLight position={[3, 10, 7]} />

    <T.Mesh 
        position={[0,1,0]}
        rotation.y={rotation}
        scale={$scale}
        on:pointerenter={() => scale.set(1.5)}
        on:pointerleave={() => scale.set(1)}
    > 
        <T.BoxGeometry args={[1,2,1]} />
        <T.MeshStandardMaterial color="orange" />
    </T.Mesh>

    <!-- <Threlte.PerspectiveCamera position={{x:20, y:20, z:20}} fov={50}>
        <Threlte.OrbitControls /> 
    </Threlte.PerspectiveCamera>

    <Threlte.AmbientLight color="white" intensity={0.2} />

    <Threlte.DirectionalLight 
        color="white" 
        intensity={2} 
        position={{x:10, y:10, z:10}} 
    />

    <Threlte.Mesh 
        geometry = {new THREE.BoxGeometry(10,10,10)}
        material = {new THREE.MeshStandardMaterial({color:'white'})}
    /> -->

</Canvas>


<style>

</style>
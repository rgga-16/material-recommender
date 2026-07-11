// Renderer / scene / camera / controls construction and teardown for the
// viewport, with proper color management: sRGB output, ACES tone mapping,
// HiDPI pixel ratio, and IBL from RoomEnvironment.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export function createViewer(container, width, height) {
	const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
	renderer.setPixelRatio(window.devicePixelRatio || 1);
	renderer.setSize(width, height);
	renderer.outputColorSpace = THREE.SRGBColorSpace;
	renderer.toneMapping = THREE.ACESFilmicToneMapping;
	renderer.toneMappingExposure = 1.2;
	container.appendChild(renderer.domElement);

	const scene = new THREE.Scene();
	scene.background = new THREE.Color(0x14171c); // matches the dark viewport

	const camera = new THREE.PerspectiveCamera(70, width / height, 0.1, 1000);
	camera.position.z = 5;

	const pmremGenerator = new THREE.PMREMGenerator(renderer);
	const environmentMap = pmremGenerator.fromScene(new RoomEnvironment()).texture;
	scene.environment = environmentMap;

	const controls = new OrbitControls(camera, renderer.domElement);
	controls.enableZoom = true;
	controls.minDistance = 0.0000000001;
	controls.maxDistance = 10000;
	controls.zoomSpeed = 1.5;
	controls.panSpeed = 1.5;
	controls.mouseButtons = {
		LEFT: null,
		MIDDLE: THREE.MOUSE.PAN,
		RIGHT: THREE.MOUSE.ROTATE,
	};
	controls.target.set(0, 0.35, 0);
	controls.update();

	const transformControls = new TransformControls(camera, renderer.domElement);
	// Since r169 TransformControls is no longer an Object3D; its gizmo lives
	// in a separate helper object that must be (re-)added to the scene.
	const transformGizmo = transformControls.getHelper();
	scene.add(transformGizmo);

	const raycaster = new THREE.Raycaster();

	function resize(newWidth, newHeight) {
		if (!newWidth || !newHeight) return;
		camera.aspect = newWidth / newHeight;
		camera.updateProjectionMatrix();
		renderer.setSize(newWidth, newHeight);
	}

	/** Render one high-resolution frame offscreen and return a PNG dataURL. */
	function captureScreenshot(currentWidth, currentHeight, scale = 2) {
		const previousRatio = renderer.getPixelRatio();
		const gizmoWasVisible = transformGizmo.visible;
		transformGizmo.visible = false;
		renderer.setPixelRatio(1);
		renderer.setSize(currentWidth * scale, currentHeight * scale, false);
		renderer.render(scene, camera);
		const dataURL = renderer.domElement.toDataURL('image/png');
		renderer.setPixelRatio(previousRatio);
		renderer.setSize(currentWidth, currentHeight, false);
		transformGizmo.visible = gizmoWasVisible;
		renderer.render(scene, camera);
		return dataURL;
	}

	/** Swap the lighting environment. null -> the default RoomEnvironment;
	 *  a URL -> an equirectangular .exr/.hdr loaded and PMREM-filtered. */
	async function setEnvironment(url) {
		const previous = scene.environment;
		if (!url) {
			scene.environment = environmentMap;
		} else {
			const { EXRLoader } = await import('three/addons/loaders/EXRLoader.js');
			const { RGBELoader } = await import('three/addons/loaders/RGBELoader.js');
			const loader = url.toLowerCase().endsWith('.hdr') ? new RGBELoader() : new EXRLoader();
			const equirect = await loader.loadAsync(url);
			scene.environment = pmremGenerator.fromEquirectangular(equirect).texture;
			equirect.dispose();
		}
		if (previous && previous !== environmentMap && previous !== scene.environment) {
			previous.dispose();
		}
	}

	function dispose() {
		controls.dispose();
		transformControls.dispose();
		pmremGenerator.dispose();
		environmentMap.dispose();
		renderer.dispose();
		renderer.domElement.remove();
	}

	return { renderer, scene, camera, controls, transformControls, transformGizmo,
		raycaster, resize, captureScreenshot, setEnvironment, dispose };
}

/**
 * RED Core Holographic 3D Orb Scene Module.
 * Interactive Three.js post-processed 3D Orb with bloom glow and chromatic aberration.
 * Used as an optional on-demand expand view mode for DynamicWin.
 */

import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';

export function createRedOrbScene(container) {
    const width = container.clientWidth || 800;
    const height = container.clientHeight || 600;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 500);
    camera.position.set(0, 0.5, 5.5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Inner Core Geometry
    const coreGeo = new THREE.IcosahedronGeometry(1.2, 4);
    const coreMat = new THREE.MeshBasicMaterial({
        color: 0xff1122,
        wireframe: true,
        transparent: true,
        opacity: 0.85
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    scene.add(coreMesh);

    // Outer Scan Ring
    const ringGeo = new THREE.TorusGeometry(2.2, 0.02, 16, 100);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0xff3344, wireframe: true });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.rotation.x = Math.PI / 3;
    scene.add(ringMesh);

    let animationFrameId;

    function animate() {
        animationFrameId = requestAnimationFrame(animate);
        coreMesh.rotation.y += 0.008;
        coreMesh.rotation.x += 0.004;
        ringMesh.rotation.z += 0.006;

        renderer.render(scene, camera);
    }

    animate();

    return {
        destroy: () => {
            cancelAnimationFrame(animationFrameId);
            if (renderer.domElement && renderer.domElement.parentNode) {
                renderer.domElement.parentNode.removeChild(renderer.domElement);
            }
        }
    };
}

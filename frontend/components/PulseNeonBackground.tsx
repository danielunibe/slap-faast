import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { gsap } from 'gsap';
import { useBackground } from '../context/BackgroundContext';

const PulseNeonBackground: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { bgMode } = useBackground();
  const isActive = bgMode === 'pulse';

  useEffect(() => {
    if (!containerRef.current || !isActive) return;

    let reqId: number;
    const scene = new THREE.Scene();
    
    const camera = new THREE.PerspectiveCamera(6, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(150, 200, 400);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, logarithmicDepthBuffer: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    containerRef.current.appendChild(renderer.domElement);

    const resizeHandler = () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
    };
    window.addEventListener("resize", resizeHandler);

    // --- SETUP WORLD (Light) ---
    // En las versiones PBR de Three.js modernas, la luz necesita mucha fuerza inicial.
    const ambient = new THREE.AmbientLight(0xffffff, 5.0); // Ambiente elevadísimo para bañar todos los tubos oscuros
    scene.add(ambient);

    const sun = new THREE.SpotLight(0xffffff, 50000); // 50K lux
    sun.position.set(0, 150, 0);
    sun.angle = Math.PI;
    sun.distance = 600;
    sun.decay = 2.0;
    scene.add(sun);

    // Luces Esféricas Blancas (Monocromáticas)
    const lightColor = new THREE.Color(0xffffff);
    const lightGroups: THREE.Group[] = [];
    for (let i = 0; i < 4; i++) { // Aumentado a 4 esferas para más densidad
        const group = new THREE.Group();
        // Decay realista 2.0, pero con intensidad masiva para el "pop"
        const pLight = new THREE.PointLight(lightColor, 0, 200, 1.5); 
        group.add(pLight);
        
        const mesh = new THREE.Mesh(
            new THREE.SphereGeometry(5.0, 32, 32), // Esferas más grandes y suaves
            new THREE.MeshBasicMaterial({ color: lightColor })
        );
        group.add(mesh);
        
        group.position.set(0, -15, 0);
        lightGroups.push(group);
        scene.add(group);
    }

    // --- SETUP WORLD (Composition Tubes) ---
    const createShape = (innerR: number, outerR: number) => {
      const shape = new THREE.Shape();
      shape.absarc(0, 0, outerR, 0, Math.PI * 2, false);
      const hole = new THREE.Path();
      hole.absarc(0, 0, innerR, 0, Math.PI * 2, true);
      shape.holes.push(hole);
      return shape;
    };
    
    // Curvas fieles a la matemática original del creador
    const tubeShape = createShape(4, 6);
    const extrudeProps = {
        depth: 4, bevelEnabled: true, bevelThickness: 0.3, bevelSize: 0.2, bevelSegments: 2, curveSegments: 16
    };
    const tubeGeom = new THREE.ExtrudeGeometry(tubeShape, extrudeProps);
    tubeGeom.center();
    tubeGeom.rotateX(Math.PI * 0.5);
    tubeGeom.rotateZ(Math.PI);
    tubeGeom.computeVertexNormals();

    // Materiales metálicos oscuros pero perceptibles
    const mat1 = new THREE.MeshStandardMaterial({ color: 0x444444, roughness: 0.8, metalness: 0.5, flatShading: true, side: THREE.DoubleSide });
    const mat2 = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.5, metalness: 0.8, flatShading: true, side: THREE.DoubleSide });

    const gridGroup = new THREE.Group();
    const sideLength = 10;
    const radius = 6;
    const offset = 0.3;
    const gap = (radius + offset) * 2;

    for (let x = 0; x < sideLength; x++) {
        for (let z = 0; z < sideLength; z++) {
            const mesh = new THREE.Mesh(tubeGeom, (x+z)%2===0 ? mat1 : mat2);
            mesh.position.set(x * gap, 0, z * gap);
            gridGroup.add(mesh);
        }
    }
    
    // Centrar la grilla entera
    const box = new THREE.Box3().setFromObject(gridGroup);
    const center = box.getCenter(new THREE.Vector3());
    gridGroup.position.sub(center);
    scene.add(gridGroup);
    camera.lookAt(scene.position);

    // --- GSAP ANIMATION ---
    const animRadius = 15;
    const startAnimations = () => {
        lightGroups.forEach(group => {
            const animate = () => {
                // Posicionamiento
                const rx = (Math.random() - 0.5) * 100;
                const rz = (Math.random() - 0.5) * 100;
                group.position.set(rx, -15, rz);
                
                const plight = group.children[0] as THREE.PointLight;
                plight.intensity = 0;

                const subTl = gsap.timeline({ paused: true });
                subTl.to(group.position, { duration: 2, y: 45, ease: "none" });
                subTl.to(plight, { duration: 2, intensity: 150000, distance: 200, ease: "none" }, 0);

                const delay = Math.random() * 2;
                
                // Efecto 'SlowMo' de brincado
                gsap.to(subTl, {
                    progress: 1,
                    duration: 1.5,
                    delay: delay,
                    ease: "power3.inOut",
                    yoyo: true,
                    repeat: 1,
                    onComplete: animate
                });
            };
            animate();
        });
    };
    
    // Kickstart
    startAnimations();

    // RENDER LOOP
    const renderLoop = () => {
        renderer.render(scene, camera);
        reqId = requestAnimationFrame(renderLoop);
    };
    renderLoop();

    return () => {
        window.removeEventListener("resize", resizeHandler);
        cancelAnimationFrame(reqId);
        gsap.killTweensOf(lightGroups.map(g => g.position));
        gsap.killTweensOf(lightGroups.map(g => g.children[0]));
        if (containerRef.current) containerRef.current.innerHTML = '';
        renderer.dispose();
        tubeGeom.dispose();
        mat1.dispose();
        mat2.dispose();
    };
  }, [isActive]);

  return (
    <div 
      ref={containerRef} 
      style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', background: '#020403' }} 
    />
  );
};

export default PulseNeonBackground;

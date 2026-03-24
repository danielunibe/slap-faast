import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { useBackground } from '../context/BackgroundContext';

const VERTEX_SHADER = `
varying vec2 vUv;
void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const FRAGMENT_SHADER = `
varying vec2 vUv;
uniform float uTime;
uniform vec2 uRes;
uniform vec3 uC1, uC2, uC3, uC4;
uniform vec3 uLPos;
uniform float uDepth, uSpeed, uNoise, uWarp, uFreq, uAngle, uFlow, uSWidth;

vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
vec4 tInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

float snoise(vec3 v) {
    const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
    const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);
    vec3 i  = floor(v + dot(v, C.yyy) );
    vec3 x0 = v - i + dot(i, C.xxx) ;
    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min( g.xyz, l.zxy );
    vec3 i2 = max( g.xyz, l.zxy );
    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy; 
    vec3 x3 = x0 - D.yyy;      
    i = mod289(i);
    vec4 p = permute( permute( permute(
                i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
            + i.y + vec4(0.0, i1.y, i2.y, 1.0 ))
            + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
    float n_ = 0.142857142857;
    vec3  ns = n_ * D.wyz - D.xzx;
    vec4 j = p - 49.0 * floor(p * ns.z * ns.z); 
    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_ );    
    vec4 x = x_ *ns.x + ns.yyyy;
    vec4 y = y_ *ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);
    vec4 b0 = vec4( x.xy, y.xy );
    vec4 b1 = vec4( x.zw, y.zw );
    vec4 s0 = floor(b0)*2.0 + 1.0;
    vec4 s1 = floor(b1)*2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));
    vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
    vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;
    vec3 p0 = vec3(a0.xy,h.x);
    vec3 p1 = vec3(a0.zw,h.y);
    vec3 p2 = vec3(a1.xy,h.z);
    vec3 p3 = vec3(a1.zw,h.w);
    vec4 norm = tInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
    p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
    vec4 m = max(0.5 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;
    return 105.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3) ) );
}

float getSurface(vec2 p) {
    float c = cos(uAngle), s = sin(uAngle);
    mat2 rot = mat2(c, -s, s, c);
    vec2 rp = rot * p;
    float n1 = snoise(vec3(rp * uNoise * 0.25, uTime * uSpeed * 0.7));
    float n2 = snoise(vec3(rp * uNoise * 0.25 + vec2(21.4, 15.2), uTime * uSpeed * 0.9));
    vec2 flow = vec2(n1 + sin(rp.x * uNoise * 0.5 + uTime * uSpeed) * 0.3, n2 + cos(rp.y * uNoise * 0.5 - uTime * uSpeed) * 0.3);
    vec2 wp = rp + flow * (uWarp * 0.12);
    float phase = sin(wp.y * (uFreq * 0.5) + flow.y * 2.0) * uFlow;
    float mainWave = sin(wp.x * (uFreq * 0.5) + phase * uWarp * 0.3);
    float n3 = snoise(vec3(wp * 0.5, uTime * uSpeed * 0.5));
    return (mainWave * 0.85 + n3 * 0.15) * 0.5;
}

void main() {
    vec2 uv = gl_FragCoord.xy / uRes.xy;
    vec2 p = uv * 2.0 - 1.0;
    p.x *= uRes.x / uRes.y;
    vec2 e = vec2(0.09, 0.0);
    float dx = (getSurface(p + e.xy) - getSurface(p - e.xy)) / (2.0 * e.x);
    float dy = (getSurface(p + e.yx) - getSurface(p - e.yx)) / (2.0 * e.x);
    vec3 normal = normalize(vec3(-dx, -dy, max(uDepth, 0.02)));
    float t = clamp(dot(normal, normalize(uLPos)) * 0.5 + 0.5 + getSurface(p) * 0.04, 0.0, 1.0);
    t = t * t * (3.0 - 2.0 * t);
    vec3 color = mix(uC1, uC2, smoothstep(0.0, uSWidth + 0.15, t));
    color = mix(color, uC3, smoothstep(uSWidth + 0.05, 0.65, t));
    color = mix(color, uC4, smoothstep(0.55, 1.05, t));
    float grain = fract(sin(dot(uv.xy, vec2(12.9898,78.233))) * 43758.5453);
    gl_FragColor = vec4(color + (grain - 0.5) * 0.03, 1.0);
}
`;

const FluidBackground: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);
  const { fluidConfig, bgMode, currentPalette } = useBackground();
  
  const materialRef = useRef<THREE.ShaderMaterial | null>(null);
  const reqRef = useRef<number>();

  useEffect(() => {
    if (!mountRef.current) return;

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
    camera.position.z = 1;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mountRef.current.appendChild(renderer.domElement);

    const material = new THREE.ShaderMaterial({
      vertexShader: VERTEX_SHADER,
      fragmentShader: FRAGMENT_SHADER,
      uniforms: {
        uTime: { value: 0 },
        uRes: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
        uC1: { value: new THREE.Color(fluidConfig.color1) },
        uC2: { value: new THREE.Color(fluidConfig.color2) },
        uC3: { value: new THREE.Color(fluidConfig.color3) },
        uC4: { value: new THREE.Color(fluidConfig.color4) },
        uDepth: { value: fluidConfig.depth },
        uLPos: { value: new THREE.Vector3(fluidConfig.lightX, fluidConfig.lightY, 1.0) },
        uSpeed: { value: fluidConfig.speed },
        uNoise: { value: fluidConfig.noise },
        uWarp: { value: fluidConfig.warp },
        uFreq: { value: fluidConfig.freq },
        uAngle: { value: fluidConfig.angle },
        uFlow: { value: fluidConfig.flow },
        uSWidth: { value: fluidConfig.shadow }
      }
    });
    materialRef.current = material;

    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material);
    scene.add(mesh);

    const handleResize = () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      if (materialRef.current) materialRef.current.uniforms.uRes.value.set(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    const animate = () => {
      if (materialRef.current) materialRef.current.uniforms.uTime.value = performance.now() / 1000;
      renderer.render(scene, camera);
      reqRef.current = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      window.removeEventListener('resize', handleResize);
      if (reqRef.current) cancelAnimationFrame(reqRef.current);
      if (mountRef.current && renderer.domElement) mountRef.current.removeChild(renderer.domElement);
      renderer.dispose();
      material.dispose();
      scene.clear();
    };
  }, []);

  useEffect(() => {
    if (materialRef.current) {
      const u = materialRef.current.uniforms;
      u.uC1.value.set(fluidConfig.color1);
      u.uC2.value.set(fluidConfig.color2);
      u.uC3.value.set(fluidConfig.color3);
      u.uC4.value.set(fluidConfig.color4);
      u.uDepth.value = fluidConfig.depth;
      u.uSpeed.value = fluidConfig.speed;
      u.uNoise.value = fluidConfig.noise;
      u.uWarp.value = fluidConfig.warp;
      u.uFreq.value = fluidConfig.freq;
      u.uAngle.value = fluidConfig.angle;
      u.uFlow.value = fluidConfig.flow;
      u.uSWidth.value = fluidConfig.shadow;
      u.uLPos.value.set(fluidConfig.lightX, fluidConfig.lightY, 1.0);
    }
  }, [fluidConfig]);

  return (
    <div 
      ref={mountRef} 
      className="fixed inset-0 w-full h-full pointer-events-none z-0 animate-in fade-in duration-1000"
    />
  );
};

export default FluidBackground;

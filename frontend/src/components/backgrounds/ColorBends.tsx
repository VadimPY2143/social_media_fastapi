import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface ColorBendsProps {
  rotation?: number;
  autoRotate?: number;
  speed?: number;
  colors?: string[];
  transparent?: boolean;
  scale?: number;
  frequency?: number;
  warpStrength?: number;
  mouseInfluence?: number;
  parallax?: number;
  noise?: number;
  className?: string;
  style?: React.CSSProperties;
}

const ColorBends: React.FC<ColorBendsProps> = ({
  rotation = 45,
  autoRotate = 1,
  speed = 0.2,
  colors = ['#FF1493', '#FF69B4', '#00CED1', '#7B68EE', '#FFD700'],
  transparent = true,
  scale = 1,
  frequency = 1,
  warpStrength = 1,
  mouseInfluence = 1,
  parallax = 0.5,
  noise = 0.1,
  className = '',
  style = {},
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!containerRef.current || !canvasRef.current) return;

    const container = containerRef.current;
    const canvas = canvasRef.current;

    // Three.js setup
    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: transparent,
    });

    const handleResize = () => {
      const width = container.clientWidth;
      const height = container.clientHeight;
      renderer.setSize(width, height);
      renderer.setPixelRatio(window.devicePixelRatio);
    };

    handleResize();
    window.addEventListener('resize', handleResize);

    // Shader code
    const vertexShader = `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `;

    const fragmentShader = `
      varying vec2 vUv;
      uniform float uTime;
      uniform float uRotation;
      uniform float uSpeed;
      uniform sampler2D uColorTexture;
      uniform float uScale;
      uniform float uFrequency;
      uniform float uWarpStrength;
      uniform vec2 uMouse;
      uniform float uMouseInfluence;
      uniform float uParallax;
      uniform float uNoise;

      // Simple hash function
      float hash(vec2 p) {
        float h = dot(p, vec2(127.1, 311.7));
        return fract(sin(h) * 43758.5453123);
      }

      // Interpolation function
      float interpolate(float a, float b, float t) {
        float ft = t * 3.14159265;
        float f = (1.0 - cos(ft)) * 0.5;
        return a * (1.0 - f) + b * f;
      }

      // Simple 2D noise
      float perlin(vec2 p) {
        vec2 pi = floor(p);
        vec2 pf = fract(p);
        
        float h00 = hash(pi);
        float h10 = hash(pi + vec2(1.0, 0.0));
        float h01 = hash(pi + vec2(0.0, 1.0));
        float h11 = hash(pi + vec2(1.0, 1.0));
        
        float h0 = interpolate(h00, h10, pf.x);
        float h1 = interpolate(h01, h11, pf.x);
        return interpolate(h0, h1, pf.y);
      }

      void main() {
        vec2 uv = vUv;
        
        // Parallax effect
        uv += uMouse * uParallax * uMouseInfluence * 0.1;

        // Rotation
        vec2 center = vec2(0.5);
        vec2 rotated = uv - center;
        float angle = uRotation + uTime * uSpeed * 0.5;
        float c = cos(angle);
        float s = sin(angle);
        rotated = vec2(rotated.x * c - rotated.y * s, rotated.x * s + rotated.y * c);
        rotated += center;

        // Wave distortion
        float waveX = sin(rotated.x * uFrequency * uScale * 6.28 + uTime * uSpeed) * uWarpStrength * 0.2;
        float waveY = cos(rotated.y * uFrequency * uScale * 6.28 + uTime * uSpeed) * uWarpStrength * 0.2;
        
        // Noise
        float n = perlin(rotated * uScale * 5.0 + uTime * uSpeed * 0.3) * uNoise * 0.1;

        // Apply distortion
        vec2 distorted = vec2(
          rotated.x + waveX + n,
          rotated.y + waveY + n
        );

        // Create color bands
        float band = sin(distorted.x * 3.0 + uTime * uSpeed * 0.8) * 0.5 + 0.5;
        band += cos(distorted.y * 3.0 + uTime * uSpeed * 0.6) * 0.3;
        band = fract(band);

        // Sample color from texture
        vec3 color = texture2D(uColorTexture, vec2(band, 0.5)).rgb;

        // Add brightness variation
        float bright = sin(length(distorted - 0.5) * 5.0 + uTime * uSpeed) * 0.3 + 0.8;
        bright += perlin(distorted * 8.0) * 0.2;
        
        color *= bright * 1.4;

        // Glow
        float dist = length(distorted - 0.5);
        float glow = exp(-dist * dist * 3.0) * 0.3;
        color += glow;

        gl_FragColor = vec4(color, 1.0);
      }
    `;

    // Create color texture from color array
    const colorCanvas = document.createElement('canvas');
    colorCanvas.width = 256;
    colorCanvas.height = 1;
    const ctx = colorCanvas.getContext('2d');
    
    if (ctx) {
      for (let i = 0; i < colors.length; i++) {
        const x = (i / colors.length) * 256;
        const width = (256 / colors.length);
        ctx.fillStyle = colors[i];
        ctx.fillRect(x, 0, width, 1);
      }
    }

    const colorTexture = new THREE.CanvasTexture(colorCanvas);
    colorTexture.magFilter = THREE.LinearFilter;
    colorTexture.minFilter = THREE.LinearFilter;

    const uniforms = {
      uTime: { value: 0 },
      uRotation: { value: (rotation * Math.PI) / 180 },
      uSpeed: { value: speed },
      uColorTexture: { value: colorTexture },
      uScale: { value: scale },
      uFrequency: { value: frequency },
      uWarpStrength: { value: warpStrength },
      uMouse: { value: new THREE.Vector2(0, 0) },
      uMouseInfluence: { value: mouseInfluence },
      uParallax: { value: parallax },
      uNoise: { value: noise },
    };

    const material = new THREE.ShaderMaterial({
      uniforms,
      vertexShader,
      fragmentShader,
      side: THREE.DoubleSide,
    });

    const geometry = new THREE.PlaneGeometry(2, 2);
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    // Mouse tracking
    const handleMouseMove = (event: MouseEvent) => {
      const x = (event.clientX / window.innerWidth) * 2 - 1;
      const y = -(event.clientY / window.innerHeight) * 2 + 1;
      uniforms.uMouse.value.set(x, y);
    };

    window.addEventListener('mousemove', handleMouseMove);

    // Animation loop
    let time = 0;
    const animate = () => {
      time += 0.01;
      uniforms.uTime.value = time;
      uniforms.uRotation.value = (rotation * Math.PI) / 180 + (time * autoRotate * Math.PI) / 180;

      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };

    animate();

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      geometry.dispose();
      material.dispose();
      colorTexture.dispose();
      renderer.dispose();
    };
  }, [rotation, autoRotate, speed, colors, scale, frequency, warpStrength, mouseInfluence, parallax, noise]);

  return (
    <div
      ref={containerRef}
      className={`w-full h-full absolute inset-0 ${className}`}
      style={style}
    >
      <canvas ref={canvasRef} className="w-full h-full" />
    </div>
  );
};

export default ColorBends;

/* ═══════════════════════════════════════════════════════════════
   金庸人物志研究院 — Three.js 3D英雄展示
   每个角色页面独立的交互式3D场景
   ═══════════════════════════════════════════════════════════════ */
(function(){
  // 角色配置 — 由页面通过 window.hero3dConfig 设置
  const cfg = window.hero3dConfig || {
    characterName: '侠客',
    characterTitle: '江湖人物',
    themeColor: '#d4a574',
    particleColor: '#e8c9a0',
    elements: ['sword']
  };

  if(typeof THREE === 'undefined') return;

  // 创建容器
  const container = document.getElementById('hero-3d');
  if(!container) return;
  
  const W = container.clientWidth;
  const H = container.clientHeight || 500;

  // 场景
  const scene = new THREE.Scene();
  
  // 相机
  const camera = new THREE.PerspectiveCamera(45, W/H, 0.1, 100);
  camera.position.set(0, 0.5, 8);
  camera.lookAt(0, 0, 0);

  // 渲染器
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(W, H);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  container.appendChild(renderer.domElement);

  // OrbitControls
  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 4;
  controls.maxDistance = 14;
  controls.maxPolarAngle = Math.PI * 0.7;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.4;
  controls.enableZoom = true;
  controls.target.set(0, 0.3, 0);

  // 灯光
  const ambientLight = new THREE.AmbientLight(0x332820, 1.2);
  scene.add(ambientLight);
  
  const mainLight = new THREE.DirectionalLight(0xffeedd, 2.5);
  mainLight.position.set(5, 5, 5);
  scene.add(mainLight);
  
  const rimLight = new THREE.DirectionalLight(
    new THREE.Color(cfg.themeColor), 1.8
  );
  rimLight.position.set(-3, 1, -3);
  scene.add(rimLight);
  
  const bottomLight = new THREE.PointLight(
    new THREE.Color(cfg.particleColor), 1.5, 10
  );
  bottomLight.position.set(0, -2, 2);
  scene.add(bottomLight);

  // 核心光球
  const coreGroup = new THREE.Group();
  const coreGeo = new THREE.IcosahedronGeometry(0.7, 2);
  const coreMat = new THREE.MeshStandardMaterial({
    color: new THREE.Color(cfg.themeColor),
    emissive: new THREE.Color(cfg.themeColor),
    emissiveIntensity: 0.6,
    roughness: 0.2,
    metalness: 0.7,
    wireframe: false,
  });
  const core = new THREE.Mesh(coreGeo, coreMat);
  coreGroup.add(core);

  // 外发光环
  const glowGeo = new THREE.TorusGeometry(0.85, 0.04, 16, 64);
  const glowMat = new THREE.MeshBasicMaterial({
    color: new THREE.Color(cfg.themeColor),
    transparent: true,
    opacity: 0.5,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const glowRing = new THREE.Mesh(glowGeo, glowMat);
  glowRing.rotation.x = Math.PI / 2;
  coreGroup.add(glowRing);

  // 第二光环
  const glowRing2 = new THREE.Mesh(glowGeo.clone(), glowMat.clone());
  glowRing2.material.opacity = 0.25;
  glowRing2.rotation.x = Math.PI / 3;
  glowRing2.rotation.y = Math.PI / 4;
  glowRing2.scale.set(1.2, 1.2, 1.2);
  coreGroup.add(glowRing2);

  scene.add(coreGroup);
  coreGroup.position.y = 0.3;

  // 粒子场
  const particleCount = 200;
  const particleGeo = new THREE.BufferGeometry();
  const particlePositions = new Float32Array(particleCount * 3);
  const particleColors = new Float32Array(particleCount * 3);
  const particleData = [];
  const baseColor = new THREE.Color(cfg.particleColor);
  
  for(let i=0; i<particleCount; i++){
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const r = 1.5 + Math.random() * 4.5;
    particlePositions[i*3] = r * Math.sin(phi) * Math.cos(theta);
    particlePositions[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
    particlePositions[i*3+2] = r * Math.cos(phi);
    
    const brightness = 0.3 + Math.random() * 0.7;
    particleColors[i*3] = baseColor.r * brightness;
    particleColors[i*3+1] = baseColor.g * brightness;
    particleColors[i*3+2] = baseColor.b * brightness;
    
    particleData.push({
      baseX: particlePositions[i*3],
      baseY: particlePositions[i*3+1],
      baseZ: particlePositions[i*3+2],
      speed: 0.2 + Math.random() * 0.6,
      offset: Math.random() * Math.PI * 2,
      amplitude: 0.3 + Math.random() * 0.7,
    });
  }
  
  particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
  particleGeo.setAttribute('color', new THREE.BufferAttribute(particleColors, 3));
  
  const particleMat = new THREE.PointsMaterial({
    size: 0.04,
    vertexColors: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    transparent: true,
    opacity: 0.7,
  });
  const particles = new THREE.Points(particleGeo, particleMat);
  scene.add(particles);

  // 轨道元素 — 根据角色类型创建
  const orbitingElements = [];
  const elementConfigs = {
    sword: { geo: () => {
      const g = new THREE.BufferGeometry();
      const s = 0.6;
      const vertices = new Float32Array([
        // 剑身（菱形）
        -0.03*s, -s, 0,  0.03*s, -s, 0,  0, s, 0,
        -0.03*s, -s, 0,  0.03*s, -s, 0,  0, -s*0.5, 0.04*s,
        0.03*s, -s, 0,  0, s, 0,  0, -s*0.5, 0.04*s,
        -0.03*s, -s, 0,  0, s, 0,  0, -s*0.5, -0.04*s,
      ]);
      g.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
      g.computeVertexNormals();
      return g;
    }, color: '#e8d5c0', size: 0.8 },
    fan: { geo: () => new THREE.CircleGeometry(0.4, 16, 0, Math.PI), color: '#f0e0c8', size: 0.7 },
    staff: { geo: () => new THREE.CylinderGeometry(0.04, 0.04, 1.2, 8), color: '#8b6914', size: 0.5 },
    palm: { geo: () => new THREE.SphereGeometry(0.3, 16, 16), color: '#ffccaa', size: 0.5 },
    needle: { geo: () => new THREE.CylinderGeometry(0.01, 0.01, 0.5, 6), color: '#d0d0d0', size: 0.4 },
    dagger: { geo: () => {
      const g = new THREE.ConeGeometry(0.06, 0.5, 6);
      return g;
    }, color: '#e0d0c0', size: 0.5 },
    flute: { geo: () => new THREE.CylinderGeometry(0.05, 0.05, 0.8, 12), color: '#c8a87c', size: 0.5 },
    whip: { geo: () => new THREE.TorusGeometry(0.3, 0.02, 8, 20), color: '#8b4513', size: 0.5 },
    book: { geo: () => new THREE.BoxGeometry(0.3, 0.4, 0.06), color: '#f5deb3', size: 0.5 },
    lotus: { geo: () => {
      const g = new THREE.TorusGeometry(0.2, 0.04, 8, 6);
      return g;
    }, color: '#ffb6c1', size: 0.5 },
    dragon: { geo: () => new THREE.TorusKnotGeometry(0.2, 0.05, 40, 8), color: '#ffd700', size: 0.6 },
    medicine: { geo: () => new THREE.SphereGeometry(0.2, 12, 12), color: '#90ee90', size: 0.4 },
    arrow: { geo: () => new THREE.ConeGeometry(0.05, 0.5, 6), color: '#c0c0c0', size: 0.5 },
  };

  cfg.elements.forEach((elemType, idx) => {
    const ec = elementConfigs[elemType] || elementConfigs.sword;
    const geo = ec.geo();
    const mat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(ec.color),
      emissive: new THREE.Color(cfg.themeColor),
      emissiveIntensity: 0.3,
      roughness: 0.3,
      metalness: 0.6,
    });
    const mesh = new THREE.Mesh(geo, mat);
    
    // 光环
    const ringGeo = new THREE.TorusGeometry(ec.size, 0.015, 8, 32);
    const ringMat = new THREE.MeshBasicMaterial({
      color: new THREE.Color(cfg.themeColor),
      transparent: true,
      opacity: 0.3,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 2 + (Math.random() - 0.5) * 0.5;
    
    const group = new THREE.Group();
    group.add(mesh);
    group.add(ring);
    
    const orbitRadius = 2.5 + idx * 0.6;
    const orbitSpeed = 0.3 + Math.random() * 0.4;
    const orbitOffset = (Math.PI * 2 / cfg.elements.length) * idx;
    const orbitTilt = (Math.random() - 0.5) * 0.6;
    
    orbitingElements.push({
      group,
      orbitRadius,
      orbitSpeed,
      orbitOffset,
      orbitTilt,
      selfRotation: (Math.random() - 0.5) * 0.02,
    });
    
    scene.add(group);
  });

  // 地面光环
  const floorRingGeo = new THREE.TorusGeometry(2, 0.02, 16, 100);
  const floorRingMat = new THREE.MeshBasicMaterial({
    color: new THREE.Color(cfg.themeColor),
    transparent: true,
    opacity: 0.15,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const floorRing = new THREE.Mesh(floorRingGeo, floorRingMat);
  floorRing.rotation.x = -Math.PI / 2;
  floorRing.position.y = -1.2;
  scene.add(floorRing);

  // 微尘粒子
  const dustCount = 150;
  const dustGeo = new THREE.BufferGeometry();
  const dustPos = new Float32Array(dustCount * 3);
  for(let i=0; i<dustCount; i++){
    dustPos[i*3] = (Math.random() - 0.5) * 8;
    dustPos[i*3+1] = (Math.random() - 0.5) * 6;
    dustPos[i*3+2] = (Math.random() - 0.5) * 8;
  }
  dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
  const dustMat = new THREE.PointsMaterial({
    size: 0.02,
    color: new THREE.Color(cfg.particleColor),
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    transparent: true,
    opacity: 0.4,
  });
  const dust = new THREE.Points(dustGeo, dustMat);
  scene.add(dust);

  // 动画循环
  const clock = new THREE.Clock();
  function animate(){
    requestAnimationFrame(animate);
    
    const t = clock.getElapsedTime();
    controls.update();
    
    // 核心脉动
    const pulse = 1 + Math.sin(t * 1.2) * 0.08;
    coreGroup.scale.setScalar(pulse);
    core.material.emissiveIntensity = 0.5 + Math.sin(t * 1.5) * 0.3;
    glowRing.rotation.z += 0.003;
    glowRing2.rotation.z -= 0.002;
    
    // 粒子动画
    const posArray = particleGeo.attributes.position.array;
    for(let i=0; i<particleCount; i++){
      const d = particleData[i];
      posArray[i*3] = d.baseX + Math.sin(t * d.speed + d.offset) * d.amplitude * 0.5;
      posArray[i*3+1] = d.baseY + Math.cos(t * d.speed * 1.3 + d.offset) * d.amplitude * 0.4;
      posArray[i*3+2] = d.baseZ + Math.cos(t * d.speed * 0.8 + d.offset + 1) * d.amplitude * 0.5;
    }
    particleGeo.attributes.position.needsUpdate = true;
    
    // 轨道元素
    orbitingElements.forEach(el => {
      const angle = t * el.orbitSpeed + el.orbitOffset;
      const x = Math.cos(angle) * el.orbitRadius;
      const z = Math.sin(angle) * el.orbitRadius;
      const y = Math.sin(t * el.orbitSpeed * 0.6 + el.orbitOffset) * 0.8;
      el.group.position.set(x, y + 0.3, z);
      el.group.rotation.y += el.selfRotation;
      el.group.rotation.x += el.selfRotation * 0.5;
    });
    
    // 地面光环
    floorRing.scale.setScalar(1 + Math.sin(t * 0.6) * 0.06);
    floorRing.material.opacity = 0.12 + Math.sin(t * 0.8) * 0.05;
    
    // 微尘旋转
    dust.rotation.y += 0.0008;
    dust.rotation.x += 0.0004;
    
    renderer.render(scene, camera);
  }
  animate();

  // 响应式
  window.addEventListener('resize', () => {
    const w = container.clientWidth;
    const h = container.clientHeight || 500;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });
})();

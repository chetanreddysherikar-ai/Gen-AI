(function () {
  "use strict";

  const root = document.documentElement;
  const themeBtn = document.getElementById("themeBtn");
  const themeIcon = document.getElementById("themeIcon");

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    if (themeIcon) {
      themeIcon.className = theme === "light" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
    }
  }

  const savedTheme = window.localStorage.getItem("theme") || "dark";
  applyTheme(savedTheme);

  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      const current = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      applyTheme(current);
      window.localStorage.setItem("theme", current);
    });
  }

  // Loading state on generate forms
  document.querySelectorAll("form.generate-form").forEach(function (form) {
    form.addEventListener("submit", function () {
      const btn = form.querySelector("button[type='submit'], button.btn-generate");
      if (btn && !btn.disabled) {
        btn.disabled = true;
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Generating…';
      }
    });
  });

  // Password visibility toggle
  document.querySelectorAll("[data-toggle-password]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const targetId = btn.getAttribute("data-toggle-password");
      const input = document.getElementById(targetId);
      if (!input) return;
      const showing = input.type === "text";
      input.type = showing ? "password" : "text";
      btn.querySelector("i").className = showing ? "bi bi-eye" : "bi bi-eye-slash";
    });
  });

  // --- 3D INTERACTIVE MOUSE-TRACKING ROBOT ---
  function init3DRobot() {
    const container = document.getElementById("robot-3d-scene");
    if (!container || typeof THREE === "undefined") return;

    // Clear previous canvas if any
    container.innerHTML = "";

    const width = container.clientWidth || 360;
    const height = container.clientHeight || 380;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 8.5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const mainLight = new THREE.DirectionalLight(0x7c5cff, 2.5);
    mainLight.position.set(5, 8, 5);
    scene.add(mainLight);

    const cyanLight = new THREE.PointLight(0x00f2fe, 3, 10);
    cyanLight.position.set(-4, 2, 4);
    scene.add(cyanLight);

    const pinkLight = new THREE.PointLight(0xff6fa5, 2.5, 10);
    pinkLight.position.set(4, -2, 3);
    scene.add(pinkLight);

    // Main Robot Group
    const robotGroup = new THREE.Group();
    scene.add(robotGroup);

    // 1. Robot Head Group
    const headGroup = new THREE.Group();
    headGroup.position.set(0, 0.8, 0);
    robotGroup.add(headGroup);

    // Head Base (Rounded Metallic Cube)
    const headGeo = new THREE.BoxGeometry(1.6, 1.4, 1.4);
    const headMat = new THREE.MeshStandardMaterial({
      color: 0x1e1e2f,
      metalness: 0.85,
      roughness: 0.25,
    });
    const headMesh = new THREE.Mesh(headGeo, headMat);
    headGroup.add(headMesh);

    // Visor / Faceplate (Dark Curved Mirror)
    const visorGeo = new THREE.BoxGeometry(1.3, 0.8, 0.15);
    const visorMat = new THREE.MeshStandardMaterial({
      color: 0x080812,
      metalness: 0.9,
      roughness: 0.1,
    });
    const visorMesh = new THREE.Mesh(visorGeo, visorMat);
    visorMesh.position.set(0, 0.05, 0.65);
    headGroup.add(visorMesh);

    // Visor Rainbow Neon Frame
    const visorBorderGeo = new THREE.BoxGeometry(1.38, 0.88, 0.05);
    const visorBorderMat = new THREE.MeshBasicMaterial({ color: 0x00f2fe });
    const visorBorder = new THREE.Mesh(visorBorderGeo, visorBorderMat);
    visorBorder.position.set(0, 0.05, 0.62);
    headGroup.add(visorBorder);

    // Glowing Eyes
    const eyeGroup = new THREE.Group();
    eyeGroup.position.set(0, 0.05, 0.74);
    headGroup.add(eyeGroup);

    const eyeGeo = new THREE.SphereGeometry(0.14, 16, 16);
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0x00f2fe });

    const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    leftEye.position.set(-0.35, 0, 0);
    eyeGroup.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye.position.set(0.35, 0, 0);
    eyeGroup.add(rightEye);

    // Headphones / Ear Caps (Left & Right)
    const earGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.25, 32);
    const earMat = new THREE.MeshStandardMaterial({ color: 0x2b2b40, metalness: 0.7, roughness: 0.3 });

    const leftEar = new THREE.Mesh(earGeo, earMat);
    leftEar.rotation.z = Math.PI / 2;
    leftEar.position.set(-0.9, 0.05, 0);
    headGroup.add(leftEar);

    const rightEar = leftEar.clone();
    rightEar.position.set(0.9, 0.05, 0);
    headGroup.add(rightEar);

    // Glowing Ear Rings
    const earRingGeo = new THREE.TorusGeometry(0.36, 0.04, 16, 32);
    const earRingMat = new THREE.MeshBasicMaterial({ color: 0xff6fa5 });

    const leftEarRing = new THREE.Mesh(earRingGeo, earRingMat);
    leftEarRing.rotation.y = Math.PI / 2;
    leftEarRing.position.set(-0.95, 0.05, 0);
    headGroup.add(leftEarRing);

    const rightEarRing = leftEarRing.clone();
    rightEarRing.position.set(0.95, 0.05, 0);
    headGroup.add(rightEarRing);

    // Top Antenna
    const antStemGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.4);
    const antStem = new THREE.Mesh(antStemGeo, earMat);
    antStem.position.set(0, 0.9, 0);
    headGroup.add(antStem);

    const antTipGeo = new THREE.SphereGeometry(0.08, 16, 16);
    const antTipMat = new THREE.MeshBasicMaterial({ color: 0x7c5cff });
    const antTip = new THREE.Mesh(antTipGeo, antTipMat);
    antTip.position.set(0, 1.15, 0);
    headGroup.add(antTip);

    // 2. Neck
    const neckGeo = new THREE.CylinderGeometry(0.25, 0.3, 0.3, 16);
    const neckMat = new THREE.MeshStandardMaterial({ color: 0x151522, metalness: 0.9 });
    const neck = new THREE.Mesh(neckGeo, neckMat);
    neck.position.set(0, -0.05, 0);
    robotGroup.add(neck);

    // 3. Torso / Body
    const bodyGeo = new THREE.CylinderGeometry(0.7, 0.5, 1.4, 32);
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0x222235, metalness: 0.8, roughness: 0.3 });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.set(0, -0.9, 0);
    robotGroup.add(body);

    // Chest LED Emblem
    const chestGeo = new THREE.SphereGeometry(0.18, 16, 16);
    const chestMat = new THREE.MeshBasicMaterial({ color: 0x00f2fe });
    const chestLED = new THREE.Mesh(chestGeo, chestMat);
    chestLED.position.set(0, -0.7, 0.55);
    robotGroup.add(chestLED);

    // Floating Arms
    const armGeo = new THREE.CylinderGeometry(0.12, 0.1, 1.0, 16);
    const armMat = new THREE.MeshStandardMaterial({ color: 0x1a1a2b, metalness: 0.7 });

    const leftArm = new THREE.Mesh(armGeo, armMat);
    leftArm.position.set(-0.95, -0.9, 0);
    leftArm.rotation.z = 0.2;
    robotGroup.add(leftArm);

    const rightArm = new THREE.Mesh(armGeo, armMat);
    rightArm.position.set(0.95, -0.9, 0);
    rightArm.rotation.z = -0.2;
    robotGroup.add(rightArm);

    // Base Platform (Octagonal Ring)
    const platformGeo = new THREE.CylinderGeometry(1.5, 1.7, 0.15, 8);
    const platformMat = new THREE.MeshStandardMaterial({ color: 0x10101d, metalness: 0.9, roughness: 0.1 });
    const platform = new THREE.Mesh(platformGeo, platformMat);
    platform.position.set(0, -1.9, 0);
    robotGroup.add(platform);

    const ringGeo = new THREE.TorusGeometry(1.6, 0.04, 16, 32);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x7c5cff });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 2;
    ring.position.set(0, -1.8, 0);
    robotGroup.add(ring);

    // Floating Particles
    const particleCount = 40;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 8;
      positions[i + 1] = (Math.random() - 0.5) * 8;
      positions[i + 2] = (Math.random() - 0.5) * 8;
    }

    particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0x00f2fe,
      size: 0.08,
      transparent: true,
      opacity: 0.7,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Mouse Tracking Coordinates
    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;

    function onMouseMove(event) {
      // Calculate normalized mouse (-1 to +1)
      targetX = (event.clientX / window.innerWidth) * 2 - 1;
      targetY = -(event.clientY / window.innerHeight) * 2 + 1;
    }

    window.addEventListener("mousemove", onMouseMove);

    // Responsive resize
    window.addEventListener("resize", function () {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });

    // Animation Loop
    let clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const elapsedTime = clock.getElapsedTime();

      // Smooth Lerp for mouse tracking
      currentX += (targetX - currentX) * 0.08;
      currentY += (targetY - currentY) * 0.08;

      // Rotate Head & Visor smoothly towards mouse
      headGroup.rotation.y = currentX * 0.65;
      headGroup.rotation.x = -currentY * 0.45;

      // Rotate Torso slightly
      robotGroup.rotation.y = currentX * 0.25;
      robotGroup.rotation.x = -currentY * 0.15;

      // Move Eyes pupil position inside visor
      eyeGroup.position.x = currentX * 0.12;
      eyeGroup.position.y = 0.05 + currentY * 0.08;

      // Floating Idle Breathing Movement
      robotGroup.position.y = Math.sin(elapsedTime * 2) * 0.12;
      ring.rotation.z = elapsedTime * 0.5;

      // Particle rotation
      particles.rotation.y = elapsedTime * 0.05;

      // Light color pulse
      chestMat.color.setHSL(0.5 + Math.sin(elapsedTime * 3) * 0.1, 1, 0.5);

      renderer.render(scene, camera);
    }

    animate();
  }

  // Run on DOM loaded
  document.addEventListener("DOMContentLoaded", init3DRobot);
})();

function copyText(elementId) {
  const el = document.getElementById(elementId || "result");
  if (!el) return;
  navigator.clipboard.writeText(el.innerText).then(function () {
    const toastEl = document.getElementById("copyToast");
    if (toastEl && window.bootstrap) {
      new bootstrap.Toast(toastEl).show();
    } else {
      alert("Copied to clipboard!");
    }
  });
}

// --- BROWSER NATIVE SPEECH SYNTHESIS VOICE CONTROLLER ---
let currentSpeechUtterance = null;

function playAIVoice(elementId) {
  if (!('speechSynthesis' in window)) {
    alert("Speech Synthesis is not supported in this browser.");
    return;
  }

  const el = document.getElementById(elementId || "result");
  if (!el) return;

  const playBtn = document.getElementById("voicePlayBtn");
  const statusEl = document.getElementById("voiceStatus");

  // If already speaking and paused, resume!
  if (window.speechSynthesis.speaking && window.speechSynthesis.paused) {
    window.speechSynthesis.resume();
    if (playBtn) playBtn.innerHTML = '<i class="bi bi-pause-fill me-1"></i> Pause Voice';
    if (statusEl) statusEl.style.display = "inline-flex";
    return;
  }

  // If already speaking and active, pause!
  if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
    window.speechSynthesis.pause();
    if (playBtn) playBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i> Resume Voice';
    return;
  }

  // Otherwise, start fresh speech synthesis
  window.speechSynthesis.cancel();

  // Clean text from Markdown symbols
  const cleanText = el.innerText.replace(/[*#\-`]/g, "").trim();
  if (!cleanText) return;

  currentSpeechUtterance = new SpeechSynthesisUtterance(cleanText);
  currentSpeechUtterance.rate = 0.95; // Natural human speed
  currentSpeechUtterance.pitch = 1.0;

  // Select preferred English voice
  const voices = window.speechSynthesis.getVoices();
  if (voices.length > 0) {
    const preferredVoice = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("Samantha") || v.name.includes("David") || v.name.includes("Zira")));
    if (preferredVoice) {
      currentSpeechUtterance.voice = preferredVoice;
    }
  }

  currentSpeechUtterance.onstart = function () {
    if (playBtn) playBtn.innerHTML = '<i class="bi bi-pause-fill me-1"></i> Pause Voice';
    if (statusEl) statusEl.style.display = "inline-flex";
  };

  currentSpeechUtterance.onend = function () {
    if (playBtn) playBtn.innerHTML = '<i class="bi bi-volume-up-fill me-1"></i> Listen to AI Voice';
    if (statusEl) statusEl.style.display = "none";
  };

  currentSpeechUtterance.onerror = function () {
    if (playBtn) playBtn.innerHTML = '<i class="bi bi-volume-up-fill me-1"></i> Listen to AI Voice';
    if (statusEl) statusEl.style.display = "none";
  };

  window.speechSynthesis.speak(currentSpeechUtterance);
}

function stopAIVoice() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const playBtn = document.getElementById("voicePlayBtn");
    const statusEl = document.getElementById("voiceStatus");
    if (playBtn) playBtn.innerHTML = '<i class="bi bi-volume-up-fill me-1"></i> Listen to AI Voice';
    if (statusEl) statusEl.style.display = "none";
  }
}


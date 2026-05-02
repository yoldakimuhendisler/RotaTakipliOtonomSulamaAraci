window.onload = initApp;

function initApp() {
    checkWifi();
    setInterval(updateStatuses, 2000);
    init3RpiModel();
}

// Wi-Fi Check
async function checkWifi() {
    const res = await eel.get_wifi_status()();
    const wifiText = document.getElementById('wifi-text');
    const wifiDot = document.getElementById('wifi-dot');
    
    if (res.connected) {
        wifiText.innerText = "Wi-Fi Bağlı: " + res.ssid;
        wifiDot.classList.replace('bg-yellow-500', 'bg-green-500');
        wifiDot.classList.remove('animate-pulse');
        document.getElementById('wifi-modal').style.display = 'none';
        document.getElementById('wifi-modal').style.opacity = '0';
    } else {
        wifiText.innerText = "Bağlantı Bekleniyor...";
        wifiDot.classList.replace('bg-green-500', 'bg-yellow-500');
        wifiDot.classList.add('animate-pulse');
        
        // Modal logic
        const modal = document.getElementById('wifi-modal');
        modal.style.display = 'flex';
        setTimeout(() => { modal.style.opacity = '1'; }, 50);
    }
}

async function closeApp() {
    window.close();
    await eel.close_app()();
}

// Service Controls
async function startAI() {
    const success = await eel.start_ai_server()();
    if(success) updateStatuses();
}

async function stopAI() {
    await eel.stop_ai_server()();
    updateStatuses();
}

async function startGazebo() {
    const success = await eel.start_gazebo()();
    if(success) updateStatuses();
}

async function stopGazebo() {
    await eel.stop_gazebo()();
    updateStatuses();
}

async function openGzClient() {
    await eel.open_gzclient()();
}

async function updateStatuses() {
    checkWifi();

    const aiStatus = await eel.get_ai_status()();
    const gzStatus = await eel.get_gazebo_status()();

    const aiCard = document.getElementById('card-ai');
    if(aiStatus) {
        aiCard.classList.replace('status-off', 'status-on');
    } else {
        aiCard.classList.replace('status-on', 'status-off');
    }

    const gzCard = document.getElementById('card-gazebo');
    if(gzStatus) {
        gzCard.classList.replace('status-off', 'status-on');
    } else {
        gzCard.classList.replace('status-on', 'status-off');
    }
}


// -------------------------------------------------------------
// THREE.JS RASPBERRY PI 5 PROCEDURAL MODEL
// -------------------------------------------------------------
function init3RpiModel() {
    const container = document.getElementById('rpi-canvas-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    // No background, make it transparent
    
    // Camera
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(4, 5, 4);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(5, 10, 7);
    scene.add(dirLight);
    
    const dirLight2 = new THREE.DirectionalLight(0xa855f7, 0.5); // purple tint
    dirLight2.position.set(-5, 5, -5);
    scene.add(dirLight2);

    // -----------------------------------------------------------------
    // Build the Pi Group (GLTF First, fallback to STL)
    // -----------------------------------------------------------------
    const piGroup = new THREE.Group();
    scene.add(piGroup);
    camera.lookAt(piGroup.position);

    const gltfLoader = new THREE.GLTFLoader();
    const stlLoader = new THREE.STLLoader();

    // Check for GLTF first (best for colors)
    gltfLoader.load('assets/rpi5.glb', function (gltf) {
        // Auto scale for GLTF
        const box = new THREE.Box3().setFromObject(gltf.scene);
        const size = box.getSize(new THREE.Vector3()).length();
        const center = box.getCenter(new THREE.Vector3());
        
        gltf.scene.position.x += (gltf.scene.position.x - center.x);
        gltf.scene.position.y += (gltf.scene.position.y - center.y);
        gltf.scene.position.z += (gltf.scene.position.z - center.z);
        
        const scale = 4.0 / size;
        gltf.scene.scale.set(scale, scale, scale);
        
        piGroup.add(gltf.scene);
        
    }, undefined, function (error) {
        // GLTF bulunamazsa STL deneyelim:
        stlLoader.load('assets/rpi5.stl', function (geometry) {
            // Material details
            const material = new THREE.MeshStandardMaterial({ color: 0x166534, metalness: 0.2, roughness: 0.5 });
            const mesh = new THREE.Mesh(geometry, material);
            
            // Otomatik Ortalama ve Boyutlandırma (Görünmezliği önler)
            geometry.computeBoundingBox();
            const bbox = geometry.boundingBox;
            const size = new THREE.Vector3();
            bbox.getSize(size);
            
            const maxDim = Math.max(size.x, size.y, size.z);
            if (maxDim > 0) {
                 const scale = 4.0 / maxDim; // Hedef genişlik (yaklaşık 4 birim)
                 mesh.scale.set(scale, scale, scale);
            }
            
            geometry.center(); // Merkeze al
            piGroup.add(mesh);
            
        }, undefined, function(err) {
            console.error("3D model yüklenirken hata oluştu! Dosyanın assets/rpi5.glb veya rpi5.stl konumunda olduğundan emin olun.");
        });
    });


    // Interaction Variables
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    
    // Auto Rotation
    let autoRotate = true;

    // Mouse Events for rotation
    container.addEventListener('mousedown', (e) => {
        isDragging = true;
        autoRotate = false;
        previousMousePosition = { x: e.offsetX, y: e.offsetY };
    });
    
    container.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const deltaMove = {
                x: e.offsetX - previousMousePosition.x,
                y: e.offsetY - previousMousePosition.y
            };

            piGroup.rotation.y += deltaMove.x * 0.01;
            piGroup.rotation.x += deltaMove.y * 0.01;

            previousMousePosition = { x: e.offsetX, y: e.offsetY };
        }
    });

    document.addEventListener('mouseup', () => { isDragging = false; });
    container.addEventListener('mouseleave', () => { isDragging = false; });
    
    // Zoom with scroll
    container.addEventListener('wheel', (e) => {
        e.preventDefault();
        autoRotate = false;
        camera.position.z += e.deltaY * 0.01;
        camera.position.z = Math.max(2, Math.min(10, camera.position.z));
    }, {passive: false});

    // Animation Loop
    function animate() {
        requestAnimationFrame(animate);
        
        if(autoRotate) {
            piGroup.rotation.y += 0.005;
        }

        renderer.render(scene, camera);
    }
    animate();

    // Handle Resize
    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
}

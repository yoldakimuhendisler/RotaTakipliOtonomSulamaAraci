import { useState, useEffect, useRef } from 'react';

function App() {
  const [telemetry, setTelemetry] = useState({
    battery: 100,
    waterLevel: 100,
    currentTask: 'Beklemede',
    status: 'Bağlı Değil',
    robotX: 0.0,
    robotY: 0.0,
    isSimMode: true
  });
  const [plants, setPlants] = useState([]);
  const [logs, setLogs] = useState([]);
  const [trail, setTrail] = useState([]);
  const logContainerRef = useRef(null);

  useEffect(() => {
    // WebSocket telemetry ve log alıcısı
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socketUrl = `${protocol}//${window.location.host}/ws/telemetry`;
    let socket;
    
    try {
      socket = new WebSocket(socketUrl);
      
      socket.onopen = () => {
        setTelemetry(prev => ({ ...prev, status: 'Aktif' }));
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'telemetry') {
            const rx = data.robot_x !== undefined ? data.robot_x : 0.0;
            const ry = data.robot_y !== undefined ? data.robot_y : 0.0;
            
            setTelemetry(prev => ({
              ...prev,
              battery: data.battery !== undefined ? data.battery : (data.battery_level !== undefined ? data.battery_level : prev.battery),
              waterLevel: data.water_level !== undefined ? data.water_level : prev.waterLevel,
              currentTask: data.current_task || data.current_state || prev.currentTask,
              robotX: rx,
              robotY: ry,
              isSimMode: data.is_sim_mode !== undefined ? data.is_sim_mode : prev.isSimMode
            }));
            
            // Rota izini kaydet (maks 30 nokta)
            setTrail(prev => {
              const last = prev[prev.length - 1];
              if (last && Math.abs(last.x - rx) < 0.05 && Math.abs(last.y - ry) < 0.05) {
                return prev;
              }
              const newTrail = [...prev, { x: rx, y: ry }];
              if (newTrail.length > 30) newTrail.shift();
              return newTrail;
            });

          } else if (data.type === 'log') {
            setLogs(prev => {
              const updated = [...prev, data];
              // Maksimum 100 log sakla
              if (updated.length > 100) updated.shift();
              return updated;
            });
          } else if (data.type === 'new_plant') {
            setPlants(prev => {
              // Zaten ekliyse tekrar ekleme
              if (prev.some(p => p.id === data.plant.id)) return prev;
              return [...prev, data.plant];
            });
          }
        } catch (e) {
          console.error("WebSocket veri çözümleme hatası:", e);
        }
      };

      socket.onclose = () => {
        setTelemetry(prev => ({ ...prev, status: 'Bağlantı Koptu' }));
      };
      
    } catch(e) {
      console.log("WebSocket bağlantı hatası.");
    }

    // Bitkileri Çek
    fetch('/api/plants')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setPlants(data);
      })
      .catch(err => console.log("Bitkiler çekilemedi:", err));

    // Logları Çek
    fetch('/api/logs')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setLogs(data);
      })
      .catch(err => console.log("Loglar çekilemedi:", err));

    return () => {
      if (socket) socket.close();
    };
  }, []);

  // Loglar güncellendiğinde otomatik olarak aşağı kaydır
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  // Log seviyelerine göre renk sınıfı belirleme
  const getLogLevelClass = (level) => {
    switch (level?.toUpperCase()) {
      case 'ERROR':
      case 'HATA':
        return 'text-rose-400 font-bold';
      case 'WARNING':
      case 'UYARI':
        return 'text-amber-400 font-semibold';
      case 'INFO':
      case 'BİLGİ':
      default:
        return 'text-emerald-400';
    }
  };

  // Koordinatları harita yüzdesine dönüştürme (-5 ile +5 aralığını %10 ile %90 arasına haritalar)
  const mapCoords = (x, y) => {
    const minCoord = -5.0;
    const maxCoord = 5.0;
    const range = maxCoord - minCoord;
    
    // Güvenlik sınırlandırmaları
    const posX = Math.max(minCoord, Math.min(maxCoord, x));
    const posY = Math.max(minCoord, Math.min(maxCoord, y));
    
    const pctX = 10 + ((posX - minCoord) / range) * 80;
    const pctY = 90 - ((posY - minCoord) / range) * 80; // Y ekseni web koordinatlarında ters
    
    return { x: pctX, y: pctY };
  };

  const robotPos = mapCoords(telemetry.robotX, telemetry.robotY);

  // SVG Trail çizgisini oluşturma
  const buildSvgPath = () => {
    if (trail.length === 0) return '';
    let d = '';
    trail.forEach((pt, index) => {
      const pos = mapCoords(pt.x, pt.y);
      if (index === 0) {
        d += `M ${pos.x}% ${pos.y}%`;
      } else {
        d += ` L ${pos.x}% ${pos.y}%`;
      }
    });
    return d;
  };

  return (
    <div className="h-screen w-screen p-6 flex flex-col gap-6 bg-slate-950 text-white relative overflow-hidden font-sans">
      
      {/* Arka plan modern gradyanlar */}
      <div className="fixed top-[-10%] left-[-10%] w-[45%] h-[45%] bg-blue-500/10 blur-[150px] rounded-full pointer-events-none"></div>
      <div className="fixed bottom-[-10%] right-[-10%] w-[45%] h-[45%] bg-emerald-500/10 blur-[150px] rounded-full pointer-events-none"></div>
      
      {/* Grid Pattern */}
      <div className="fixed inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-30 pointer-events-none"></div>

      {/* Header */}
      <header className="flex justify-between items-center z-10 glass-panel p-4 px-8 border border-slate-800 bg-slate-900/60 backdrop-blur-md rounded-2xl shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-sky-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <svg className="w-6 h-6 text-white animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.364l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
            </svg>
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Yoldaki Mühendisler <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Rota Takibi</span>
            </h1>
            <p className="text-slate-400 text-xs font-medium">Otonom Sulama ve Bitki İzleme Dashboard</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {telemetry.isSimMode && (
            <span className="text-xs bg-amber-500/10 border border-amber-500/30 text-amber-400 px-3 py-1 rounded-lg font-mono">
              ⚡ SIMÜLASYON MODU
            </span>
          )}
          <div className={`px-4 py-1.5 rounded-full border flex items-center gap-2.5 transition-colors ${telemetry.status === 'Aktif' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-rose-500/10 border-rose-500/30 text-rose-400'}`}>
            <div className={`w-2 h-2 rounded-full ${telemetry.status === 'Aktif' ? 'bg-emerald-400 animate-ping' : 'bg-rose-500'}`}></div>
            <span className="text-xs font-bold tracking-wider uppercase font-mono">{telemetry.status}</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 z-10 overflow-hidden min-h-0">
        
        {/* Sol Kolon - Telemetri ve Loglar */}
        <div className="flex flex-col gap-6 overflow-hidden min-h-0">
          
          {/* Araç Durumu Kartı */}
          <div className="glass-panel p-6 flex flex-col gap-5 border border-slate-800 bg-slate-900/40 backdrop-blur-md rounded-2xl">
            <h2 className="text-lg font-bold border-b border-slate-800 pb-2 text-slate-200 flex items-center gap-2">
              <svg className="w-5 h-5 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
              Araç Telemetrisi
            </h2>
            
            {/* Batarya */}
            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-xs text-slate-300">
                <span className="flex items-center gap-1.5">🔋 Batarya</span>
                <span className="font-mono font-bold text-sky-400">{telemetry.battery.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-slate-800/80 h-2.5 rounded-full overflow-hidden p-0.5 border border-slate-700/30">
                <div 
                  className={`h-full rounded-full transition-all duration-500 ${telemetry.battery > 50 ? 'bg-emerald-500' : telemetry.battery > 20 ? 'bg-amber-500' : 'bg-rose-500'}`} 
                  style={{width: `${telemetry.battery}%`}}
                ></div>
              </div>
            </div>

            {/* Su Deposu */}
            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-xs text-slate-300">
                <span className="flex items-center gap-1.5">💧 Su Deposu</span>
                <span className="font-mono font-bold text-blue-400">{telemetry.waterLevel.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-slate-800/80 h-2.5 rounded-full overflow-hidden p-0.5 border border-slate-700/30">
                <div 
                  className="h-full bg-gradient-to-r from-blue-600 to-sky-400 rounded-full transition-all duration-500 shadow-[0_0_8px_rgba(56,189,248,0.4)]" 
                  style={{width: `${telemetry.waterLevel}%`}}
                ></div>
              </div>
            </div>

            {/* Koordinat */}
            <div className="grid grid-cols-2 gap-4 mt-2">
              <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 text-center">
                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-0.5">X Koordinatı</p>
                <p className="font-mono text-base font-bold text-slate-300">{telemetry.robotX.toFixed(2)} m</p>
              </div>
              <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 text-center">
                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-0.5">Y Koordinatı</p>
                <p className="font-mono text-base font-bold text-slate-300">{telemetry.robotY.toFixed(2)} m</p>
              </div>
            </div>

            {/* Mevcut Görev */}
            <div className="mt-1 p-4 bg-slate-950/60 rounded-xl border border-sky-950/50 shadow-inner">
              <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Mevcut Görev / Durum</p>
              <p className="text-sm font-mono text-sky-400 font-bold tracking-wide flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping"></span>
                {telemetry.currentTask}
              </p>
            </div>
          </div>

          {/* Sistem Logları */}
          <div className="glass-panel p-6 flex-1 flex flex-col border border-slate-800 bg-slate-900/40 backdrop-blur-md rounded-2xl min-h-0 overflow-hidden">
            <h2 className="text-lg font-bold border-b border-slate-800 pb-2 mb-4 text-slate-200 flex items-center gap-2">
              <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
              Sistem Günlükleri (Logs)
            </h2>
            <div 
              ref={logContainerRef} 
              className="flex-1 overflow-y-auto space-y-2.5 text-xs font-mono scrollbar-thin scrollbar-thumb-slate-800 pr-1"
            >
              {logs.length > 0 ? logs.map((l, index) => (
                <div key={l.id || index} className="p-2 rounded bg-slate-950/40 border border-slate-900/80 hover:bg-slate-950/70 transition-colors">
                  <span className="text-slate-500 mr-2">[{l.timestamp ? new Date(l.timestamp).toLocaleTimeString() : ''}]</span>
                  <span className="text-sky-400 font-bold mr-1.5">{l.module || 'Sistem'}:</span>
                  <span className={getLogLevelClass(l.level)}>[{l.level?.toUpperCase()}]</span>
                  <span className="text-slate-300 ml-2">{l.message}</span>
                </div>
              )) : (
                <div className="h-full flex items-center justify-center text-slate-600 italic">
                  Henüz log akışı bulunmamaktadır...
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Orta & Sağ Kolon - Canlı Harita Görünümü */}
        <div className="lg:col-span-2 flex flex-col gap-6 overflow-hidden min-h-0">
          
          {/* Canlı Harita */}
          <div className="glass-panel flex-1 flex flex-col p-1 border border-slate-800 bg-slate-900/40 backdrop-blur-md rounded-2xl relative overflow-hidden group">
            
            <div className="absolute top-4 left-4 z-10 px-3.5 py-1.5 bg-slate-950/80 backdrop-blur-md rounded-xl text-xs font-bold text-slate-200 border border-slate-800 shadow-lg">
              CANLI TAKİP HARİTASI
            </div>

            <div className="absolute top-4 right-4 z-10 px-3.5 py-1.5 bg-slate-950/80 backdrop-blur-md rounded-xl text-xs font-bold text-slate-400 border border-slate-800 shadow-lg font-mono">
              Koordinat Alanı: (-5m, +5m)
            </div>
            
            {/* Harita Grid */}
            <div className="w-full h-full min-h-[350px] bg-slate-950/80 rounded-2xl flex items-center justify-center relative border border-slate-900 shadow-inner overflow-hidden">
              
              {/* Center axis lines */}
              <div className="absolute w-full h-[1px] bg-slate-900/40 border-t border-dashed border-slate-800/80"></div>
              <div className="absolute h-full w-[1px] bg-slate-900/40 border-l border-dashed border-slate-800/80"></div>

              {/* Rota İz Çizgisi */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{zIndex: 1}}>
                <path 
                  d={buildSvgPath()} 
                  stroke="rgba(56, 189, 248, 0.4)" 
                  strokeWidth="3" 
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeDasharray="4,4"
                  fill="none"
                />
              </svg>

              {/* Bitkiler */}
              {plants.map((p, i) => {
                const pos = mapCoords(p.location_x, p.location_y);
                return (
                  <div
                    key={p.id || i}
                    className="absolute w-7 h-7 bg-emerald-500/20 border-2 border-emerald-500/60 rounded-full flex items-center justify-center shadow-[0_0_12px_rgba(16,185,129,0.3)] hover:scale-125 hover:border-emerald-400 transition-all cursor-pointer z-10"
                    style={{
                      top: `${pos.y}%`,
                      left: `${pos.x}%`,
                      transform: 'translate(-50%, -50%)'
                    }}
                    title={`Bitki: ${p.species}\nKonum: X:${p.location_x.toFixed(2)}, Y:${p.location_y.toFixed(2)}`}
                  >
                    <span className="text-xs">🌱</span>
                  </div>
                );
              })}

              {/* Robot Araba Sembolü */}
              <div 
                className="absolute w-12 h-12 bg-sky-500/10 border-2 border-sky-400 rounded-xl flex items-center justify-center shadow-[0_0_25px_#38bdf8] transition-all duration-300 ease-out z-20"
                style={{
                  top: `${robotPos.y}%`,
                  left: `${robotPos.x}%`,
                  transform: 'translate(-50%, -50%)'
                }}
              >
                <div className="absolute inset-0 bg-sky-500/5 rounded-lg animate-ping opacity-60"></div>
                <svg className="w-6 h-6 text-sky-400 rotate-0 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>

            </div>
          </div>

          {/* Alt Veri Tablosu */}
          <div className="glass-panel p-6 h-60 flex flex-col border border-slate-800 bg-slate-900/40 backdrop-blur-md rounded-2xl overflow-hidden">
            <h2 className="text-lg font-bold border-b border-slate-800 pb-2 mb-3 text-slate-200 flex items-center gap-2">
              <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
              Tespit Edilen Bitkiler Veritabanı
            </h2>
            <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900/80 text-slate-400 sticky top-0 border-b border-slate-800 z-10">
                  <tr>
                    <th className="p-3 font-semibold">ID</th>
                    <th className="p-3 font-semibold">Tür (Yapay Zeka)</th>
                    <th className="p-3 font-semibold">Koordinat (X, Y)</th>
                    <th className="p-3 font-semibold">Durum</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-900/40">
                  {plants.length > 0 ? plants.map((p, i) => (
                    <tr key={p.id || i} className="hover:bg-slate-900/30 transition-colors">
                      <td className="p-3 font-mono text-slate-500">#{p.id || i}</td>
                      <td className="p-3 font-medium text-slate-200 flex items-center gap-1.5">
                        <span className="text-emerald-400">🌱</span> {p.species || 'Ot/Bitki'}
                      </td>
                      <td className="p-3 font-mono text-sky-400">{p.location_x.toFixed(2)}, {p.location_y.toFixed(2)}</td>
                      <td className="p-3">
                        <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold font-mono">
                          Sulandı
                        </span>
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan="4" className="p-6 text-center text-slate-500 italic">
                        Henüz bitki kaydedilmedi...
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </main>

    </div>
  );
}

export default App;

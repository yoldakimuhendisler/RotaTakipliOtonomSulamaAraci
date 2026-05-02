import { useState, useEffect } from 'react';

function App() {
  const [telemetry, setTelemetry] = useState({
    battery: 100,
    waterLevel: 100,
    currentTask: 'Beklemede',
    status: 'Bağlı Değil'
  });
  const [plants, setPlants] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    // Sadece localhost üzerinden çalıştığını varsayalım (Backend 8000)
    // Gerçekte ws://192.168.50.1:8000/ws/telemetry olacak
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
          setTelemetry(prev => ({
            ...prev,
            battery: data.battery !== undefined ? data.battery : prev.battery,
            waterLevel: data.water_level !== undefined ? data.water_level : prev.waterLevel,
            currentTask: data.current_task || prev.currentTask
          }));
        } catch (e) {
          console.error("Telemetry parse hatası:", e);
        }
      };

      socket.onclose = () => {
        setTelemetry(prev => ({ ...prev, status: 'Bağlantı Koptu' }));
      };
      
      setWs(socket);
    } catch(e) {
      console.log("WebSocket bağlantı hatası, muhtemelen geliştirme ortamında.");
    }

    // Fetch plants
    fetch('/api/plants')
      .then(res => res.json())
      .then(data => {
        if(Array.isArray(data)) setPlants(data);
      })
      .catch(err => console.log("Bitkiler çekilemedi:", err));

    return () => {
      if (socket) socket.close();
    };
  }, []);

  return (
    <div className="h-screen w-screen p-6 flex flex-col gap-6 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-slate-900 bg-opacity-95 bg-blend-multiply relative overflow-y-auto">
      
      {/* Arka plan parlaklıkları */}
      <div className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/20 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="fixed bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-green-600/20 blur-[120px] rounded-full pointer-events-none"></div>

      {/* Header */}
      <header className="flex justify-between items-center z-10 glass-panel p-4 px-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white neon-glow">Yoldaki Mühendisler</h1>
          <p className="text-slate-400 text-sm">Otonom Sulama Aracı Yönetim Paneli</p>
        </div>
        <div className="flex items-center gap-4">
          <div className={`px-4 py-1.5 rounded-full border flex items-center gap-2 ${telemetry.status === 'Aktif' ? 'bg-green-500/10 border-green-500/50 text-green-400' : 'bg-red-500/10 border-red-500/50 text-red-400'}`}>
            <div className={`w-2.5 h-2.5 rounded-full ${telemetry.status === 'Aktif' ? 'bg-green-400 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-sm font-semibold tracking-wide uppercase">{telemetry.status}</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 z-10">
        
        {/* Sol Kolon - Telemetri */}
        <div className="flex flex-col gap-6">
          <div className="glass-panel p-6 flex flex-col gap-4">
            <h2 className="text-xl font-semibold border-b border-slate-700/50 pb-2">Araç Durumu</h2>
            
            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-sm text-slate-300">
                <span>Batarya</span>
                <span className="font-mono">{telemetry.battery}%</span>
              </div>
              <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-red-500 via-yellow-400 to-green-500 h-full transition-all duration-500" style={{width: `${telemetry.battery}%`}}></div>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-sm text-slate-300">
                <span>Su Tankı Seviyesi</span>
                <span className="font-mono">{telemetry.waterLevel}%</span>
              </div>
              <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-blue-600 to-blue-300 h-full transition-all duration-500 shadow-[0_0_10px_#3b82f6]" style={{width: `${telemetry.waterLevel}%`}}></div>
              </div>
            </div>

            <div className="mt-4 p-4 bg-slate-900/50 rounded-xl border border-slate-700/50">
              <p className="text-xs text-slate-400 uppercase tracking-widest mb-1">Mevcut Görev</p>
              <p className="text-lg font-mono text-neon-blue">{telemetry.currentTask}</p>
            </div>
          </div>

          <div className="glass-panel p-6 flex-1">
            <h2 className="text-xl font-semibold border-b border-slate-700/50 pb-2 mb-4">Sistem Logları</h2>
            <div className="h-full max-h-[300px] overflow-y-auto space-y-2 text-sm font-mono text-slate-300">
              <p><span className="text-green-400">[BİLGİ]</span> Sistem başlatıldı.</p>
              <p><span className="text-blue-400">[AĞ]</span> AI Server bekleniyor...</p>
              <p><span className="text-green-400">[BİLGİ]</span> Kamera yayını aktif.</p>
            </div>
          </div>
        </div>

        {/* Orta Kolon - Harita/Kamera Görünümü */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="glass-panel flex-1 flex flex-col p-1 overflow-hidden relative group">
            {/* Sahte bir Grid/Harita tasarımı */}
            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/graphy.png')] opacity-10"></div>
            
            <div className="absolute top-4 left-4 z-10 px-3 py-1 bg-black/50 backdrop-blur-sm rounded text-xs text-white border border-slate-700">
              CANLI HARİTA GÖRÜNÜMÜ
            </div>

            <div className="w-full h-full min-h-[400px] bg-slate-900/80 rounded-xl flex items-center justify-center relative border border-slate-700">
                {/* Robot Sembolü */}
                <div className="absolute w-12 h-12 bg-sky-500/20 border-2 border-sky-400 rounded-lg flex items-center justify-center shadow-[0_0_20px_#38bdf8] animate-bounce" style={{top: '40%', left: '40%'}}>
                   <svg className="w-6 h-6 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>

                {/* Örnek Bitkiler */}
                <div className="absolute w-6 h-6 bg-green-500/20 border-2 border-green-500 rounded-full flex items-center justify-center shadow-[0_0_15px_#22c55e]" style={{top: '20%', left: '70%'}}></div>
                <div className="absolute w-6 h-6 bg-red-500/20 border-2 border-red-500 rounded-full flex items-center justify-center shadow-[0_0_15px_#ef4444] animate-pulse" style={{top: '60%', left: '20%'}}></div>
                
                {/* Rota Çizgisi (Sahte) */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-30" style={{zIndex: 0}}>
                    <path d="M 40% 40% L 70% 20% L 20% 60%" stroke="#38bdf8" strokeWidth="2" strokeDasharray="5,5" fill="none"/>
                </svg>
            </div>
          </div>

          {/* Alt Veri Tablosu */}
          <div className="glass-panel p-6 h-64 overflow-hidden flex flex-col">
            <h2 className="text-xl font-semibold border-b border-slate-700/50 pb-2 mb-4">Tespit Edilen Bitkiler Veritabanı</h2>
            <div className="overflow-y-auto w-full">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/50 text-slate-400 sticky top-0">
                  <tr>
                    <th className="p-3">ID</th>
                    <th className="p-3">Tür (Yapay Zeka)</th>
                    <th className="p-3">Koordinat (X, Y)</th>
                    <th className="p-3">Durum</th>
                  </tr>
                </thead>
                <tbody>
                  {plants.length > 0 ? plants.map((p, i) => (
                    <tr key={p.id || i} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                      <td className="p-3">#{p.id || i}</td>
                      <td className="p-3 font-medium text-white">{p.species || 'Bilinmiyor'}</td>
                      <td className="p-3 font-mono">{p.location_x.toFixed(2)}, {p.location_y.toFixed(2)}</td>
                      <td className="p-3 text-green-400">Sulandı</td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan="4" className="p-4 text-center text-slate-500 italic">Henüz bitki kaydedilmedi...</td>
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

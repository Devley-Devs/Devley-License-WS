from datetime import timedelta
import platform, time, psutil, os

BOOT_TIME: int = int(time.time())

def bytes_to_human_readable(num_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if num_bytes < 1024:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.2f} TB"

async def GetSystemUsage(limits: dict, ws_clients: int = 0):
    process = psutil.Process(os.getpid())  # Get current Python process
    
    # CPU usage (per process, note: returns % of single core usage)
    cpu_usage = process.cpu_percent(interval=1)  # Blocking for 1 sec to get accurate reading
    
    # Memory usage
    mem_info = process.memory_info()

    mem_info = process.memory_full_info()

    # Working Set (private memory) is usually what Task Manager shows
    private_mem = getattr(mem_info, 'pss', None) or mem_info.uss  # Prefer pss if available
    if not private_mem:
        private_mem = mem_info.rss  # fallback

    mem_used = bytes_to_human_readable(private_mem)  # Resident Set Size (actual RAM usage)
    
    # Network usage (still system-wide unless using net_io_counters(pernic=True) and filtering)
    net_io = psutil.net_io_counters()
    net_sent = bytes_to_human_readable(net_io.bytes_sent)
    net_recv = bytes_to_human_readable(net_io.bytes_recv)
    
    # Uptime
    uptime = timedelta(seconds=int(time.time() - BOOT_TIME))
    
    return {
        "cpu_usage": round(cpu_usage / limits.get('cpu', 0.2), 2),
        "cpu_cores": limits.get("cpu"),
        "mem_used": mem_used,
        "mem_total": bytes_to_human_readable(limits.get("memory", 128) * (1024 ** 2)),
        "mem_percent": round(((private_mem / (1024 ** 2)) / limits.get("memory", 512)) * 100, 2),
        "net_sent": net_sent,
        "net_recv": net_recv,
        "uptime": str(uptime),
        "ws_clients": ws_clients
    }

async def UsageHTMLParsed(limits: dict, ws_clients: int = 0):
    data = await GetSystemUsage(limits=limits, ws_clients=ws_clients)
    style = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1450px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            animation: fadeInDown 0.8s ease-out;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 300;
            margin-bottom: 10px;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .status-badge {
            display: inline-block;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            padding: 5px 15px;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 10px;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            margin-bottom: 30px;
            gap: 15px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            animation: fadeInUp 0.8s ease-out;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .card-icon {
            font-size: 2rem;
            margin-right: 15px;
            opacity: 0.8;
        }
        
        .card-title {
            font-size: 1.4rem;
            font-weight: 600;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }
        
        .metric-label {
            font-size: 0.95rem;
            opacity: 0.8;
        }
        
        .metric-value {
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        .progress-bar {
            width: 100%;
            height: 12px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            overflow: hidden;
            margin-top: 15px;
        }
        
        .progress-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        .cpu-progress { background: linear-gradient(90deg, #FF6B6B, #FF8E53); }
        .ram-progress { background: linear-gradient(90deg, #4ECDC4, #44A08D); }
        .disk-progress { background: linear-gradient(90deg, #A8E6CF, #7FDBDA); }
        
        .chart-container {
            grid-column: 1 / -1;
            height: 300px;
            position: relative;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(45deg, #FF6B6B, #FF8E53);
            border: none;
            color: white;
            padding: 15px;
            border-radius: 50%;
            font-size: 1.2rem;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(255, 107, 107, 0.4);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .refresh-btn:hover {
            transform: scale(1.1) rotate(360deg);
            box-shadow: 0 6px 25px rgba(255, 107, 107, 0.6);
        }
        
        .system-info {
            text-align: center;
            margin-bottom: 20px;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .container {
                padding: 15px;
            }
        }
    """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta http-equiv="refresh" content="10">
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Devley License Server</title>
    <style>
        {style}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ Devley License Server</h1>
            <div class="status-badge">🟢 ONLINE • {data['uptime']}</div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-header"><div class="card-icon">🖥️</div><div class="card-title">CPU Usage</div></div>
                <div class="metric"><span class="metric-label">Usage</span><span class="metric-value">{data['cpu_usage']}%</span></div>
                <div class="metric"><span class="metric-label">Core</span><span class="metric-value">{data['cpu_cores']}</span></div>
                <div class="progress-bar"><div class="progress-fill cpu-progress" style="width: {data['cpu_usage']}%"></div></div>
            </div>

            <div class="card">
                <div class="card-header"><div class="card-icon">💾</div><div class="card-title">Memory Usage</div></div>
                <div class="metric"><span class="metric-label">Used</span><span class="metric-value">{data['mem_used']}</span></div>
                <div class="metric"><span class="metric-label">Total</span><span class="metric-value">{data['mem_total']}</span></div>
                <div class="metric"><span class="metric-label">Usage</span><span class="metric-value">{data['mem_percent']}%</span></div>
                <div class="progress-bar"><div class="progress-fill ram-progress" style="width: {data['mem_percent']}%"></div></div>
            </div>

            <div class="card">
                <div class="card-header"><div class="card-icon">🌐</div><div class="card-title">Network</div></div>
                <div class="metric"><span class="metric-label">Total Clients</span><span class="metric-value">{data['ws_clients']}</span></div>
                <div class="metric"><span class="metric-label">Sent</span><span class="metric-value">{data['net_sent']}</span></div>
                <div class="metric"><span class="metric-label">Received</span><span class="metric-value">{data['net_recv']}</span></div>
            </div>
        </div>
    </div>
</body>
</html>
"""
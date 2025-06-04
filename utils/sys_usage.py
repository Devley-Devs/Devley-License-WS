import platform, time, psutil
from datetime import timedelta

def bytes_to_human_readable(b):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(b)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == 'B':
                return f"{int(size)} {unit}"
            else:
                return f"{size:.2f} {unit}"
        size /= 1024

async def GetSystemUsage(ws_clients: int = 0):
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    
    virtual_mem = psutil.virtual_memory()
    mem_used = bytes_to_human_readable(virtual_mem.used)
    mem_total = bytes_to_human_readable(virtual_mem.total)
    mem_percent = virtual_mem.percent
    
    disk = psutil.disk_usage('/')
    disk_used = bytes_to_human_readable(disk.used)
    disk_total = bytes_to_human_readable(disk.total)
    disk_percent = disk.percent
    
    net_io = psutil.net_io_counters()
    net_sent = bytes_to_human_readable(net_io.bytes_sent)
    net_recv = bytes_to_human_readable(net_io.bytes_recv)
    
    boot_time = psutil.boot_time()
    uptime = timedelta(seconds=int(time.time() - boot_time))
    
    process_count = len(psutil.pids())
    
    return {
        "hostname": platform.node(),
        "system": platform.system(),
        "cpu_usage": cpu_usage,
        "cpu_cores": cpu_cores,
        "cpu_threads": cpu_threads,
        "cpu_freq": cpu_freq.current if cpu_freq else 0,
        "mem_used": mem_used,
        "mem_total": mem_total,
        "mem_percent": mem_percent,
        "disk_used": disk_used,
        "disk_total": disk_total,
        "disk_percent": disk_percent,
        "net_sent": net_sent,
        "net_recv": net_recv,
        "uptime": str(uptime),
        "process_count": process_count,
        "ws_clients": ws_clients
    }

async def UsageHTMLParsed(ws_clients: int = 0):
    data = await GetSystemUsage(ws_clients)
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
                <div class="metric"><span class="metric-label">Cores / Threads</span><span class="metric-value">{data['cpu_cores']} / {data['cpu_threads']}</span></div>
                <div class="metric"><span class="metric-label">Frequency</span><span class="metric-value">{int(data['cpu_freq'])} MHz</span></div>
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

            <div class="card">
                <div class="card-header"><div class="card-icon">💿</div><div class="card-title">Disk Usage</div></div>
                <div class="metric"><span class="metric-label">Used</span><span class="metric-value">{data['disk_used']}</span></div>
                <div class="metric"><span class="metric-label">Total</span><span class="metric-value">{data['disk_total']}</span></div>
                <div class="metric"><span class="metric-label">Usage</span><span class="metric-value">{data['disk_percent']}%</span></div>
                <div class="progress-bar"><div class="progress-fill disk-progress" style="width: {data['disk_percent']}%"></div></div>
            </div>
        </div>
    </div>
</body>
</html>
"""
# road-accidents-dashboard 

This dashboard visualizes road accident data in Switzerland, offering an interactive way to explore trends and statistics.  

## Installation of `uv`

`uv` is a universal runtime tool that simplifies running and managing Python applications. We use it to ensure easy setup and cross-platform compatibility for the dashboard.  

### macOS/Linux:  
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows:  
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Run the Dashboard  

1. Clone the repository and navigate to the project directory:  
   ```bash
   git clone https://github.com/gabrieltorresgamez/road-accidents-dashboard.git
   cd road-accidents-dashboard
   ```

2. Start the dashboard:  
   ```bash
   uv run marimo run dashboard.py
   ```

3. Open the displayed URL in your browser. (e. g. http://localhost:2718)
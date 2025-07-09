# AI-Powered Dispatch Planning & Space Optimization System

## 🖥️ Run Locally (Windows Example)

1. **Go to the project directory:**
   ```powershell
   cd "AI Project 2\dispatch_optimizer"
   ```
2. **Activate the environment (set PYTHONPATH):**
   ```powershell
   $env:PYTHONPATH="C:\AI Project 2"
   ```
3. **Run the app:**
   ```powershell
   streamlit run ui/app.py
   ```

Now you are ready to go! Open your browser to [http://localhost:8501](http://localhost:8501)

---

## 🚀 Deployment (Docker)

You can deploy this app easily using Docker:

```bash
git clone <your-repo-url>
cd dispatch_optimizer
# Build the Docker image
docker build -t dispatch-optimizer .
# Run the app (default port 8501)
docker run -p 8501:8501 dispatch-optimizer
```

The app will be available at [http://localhost:8501](http://localhost:8501)

---

## 🏁 Quickstart (Local)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install streamlit
   ```
2. **Run the app:**
   ```bash
   streamlit run dispatch_optimizer/ui/app.py
   ```
3. **Open your browser:**
   Go to [http://localhost:8501](http://localhost:8501)

---

## 📦 Usage Instructions

- **Upload your product CSV** at the top of the app. All tabs will use this data.
- **Adjust constraints/settings** in the sidebar for each optimization tab (Storage, Dispatch, Dynamic).
- **Add vehicles and drivers** in the Settings tab before running optimizations.
- **Download optimized plans** and view analytics in their respective tabs.
- **AI predictions** are shown automatically if the model is trained.

---

## 🖼️ Screenshots

> _Add screenshots of the main UI, optimization results, and analytics here._

---

## 📚 More Information

- For advanced usage, see the code in `dispatch_optimizer/`.
- To retrain the AI model, use `train_from_data_folder.py` or the Settings tab.
- For questions or issues, open an issue in this repository.

---

Enjoy optimizing your warehouse and dispatch operations with AI! 🚚🤖 
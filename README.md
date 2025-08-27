# SmithPy

SmithPy is a simple graphical tool for exploring radio‑frequency impedance matching with the Smith chart.

## What is a Smith chart?

A Smith chart is a diagram used by engineers to show how electrical impedance changes along transmission lines. SmithPy lets you add resistors, capacitors, inductors and transmission‑line segments and immediately see how they move on the chart.

## Quick start for beginners

Follow these steps even if you have never used Python before.

### 1. Install Python

1. Go to <https://www.python.org/downloads/>.
2. Download the latest **Python 3** release for your operating system.
3. Run the installer. On Windows check the option **Add Python to PATH**.

### 2. Get SmithPy

Download the project code:

- If you use Git:

  ```bash
  git clone <repository-url>
  ```

- Otherwise, click the **Download ZIP** button on the repository page and unzip the file.

### 3. Open a terminal in the project folder

- **Windows:** open *Command Prompt* and run `cd path\to\smithpy`
- **macOS / Linux:** open *Terminal* and run `cd path/to/smithpy`

### 4. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate it with:

- **Windows:** `venv\Scripts\activate`
- **macOS / Linux:** `source venv/bin/activate`

### 5. Install and run

```bash
pip install -e .
python -m smithpy
```

A window with the Smith chart should appear.

### 6. Run without installing

If you only want to try the program once:

```bash
python src/smithpy/app.py
```

## Troubleshooting

- If `python` is not recognized, restart your terminal or make sure Python was added to PATH during installation.
- If the application window does not appear, ensure you are running on a system with a graphical desktop environment.

## License

This project is licensed under the MIT License.

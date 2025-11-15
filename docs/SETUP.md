# BoE - Development Setup

## Prerequisites

- Python 3.11 or higher
- Git (for version control)

## Initial Setup

### 1. Create Virtual Environment

```bash
# Navigate to project directory
cd C:\projectboe

# Create virtual environment
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (CMD):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```


You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Game

Once development starts:

```bash
# Make sure venv is activated
python main.py
```

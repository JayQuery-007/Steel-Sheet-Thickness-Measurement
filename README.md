Steel Sheet Thickness Measurement System

Overview

A Streamlit-based dashboard to compute and visualize sheet thickness from
paired top/bottom sensor profiles. Features:
- Upload top and bottom CSV profiles
- Data cleaning (Basic or Statistical IQR)
- Interpolation to a common X-grid and thickness computation
- Pass/Fail classification against target thickness and tolerance
- Interactive plots, heatmap and downloadable Excel/PDF reports

Prerequisites

- Python 3.9+ (3.10 or 3.11 recommended)
- Git (optional)

Install dependencies

Create a virtual environment and install the requirements:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Run the application

From the project root (where `app.py` is located):

```powershell
venv\Scripts\Activate.ps1
streamlit run app.py
```

This will open the Streamlit UI in your browser. Upload two CSV files
(one for the top sensor and one for the bottom sensor) containing either
`X,Z` or `X,Y,Z` columns. Configure `Target Thickness` and `Tolerance`
from the sidebar and choose the data cleaning mode.

File structure

- `app.py` - Streamlit UI and orchestration
- `data_cleaner.py` - Data cleaning utilities
- `thickness_engine.py` - Interpolation and thickness calculations
- `heatmap_view.py` - Compact heatmap visualization
- `export_excel.py` - Excel report generator
- `export_pdf.py` - PDF report generator
- `requirements.txt` - Python package dependencies

Notes and Troubleshooting

- If PDF generation fails, ensure `reportlab` is installed in the
  environment.
- For Excel exports, `openpyxl` is required by pandas.
- If your CSV uses different sentinel values for invalid data, update
  `INVALID_VALUES` in `data_cleaner.py`.

License & Contact

This project is provided as-is. For questions or enhancements, open an
issue or contact the maintainer.

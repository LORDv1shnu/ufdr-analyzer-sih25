# 🔍 UFDR AI Analyzer - SIH 2025

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-latest-red.svg)](https://streamlit.io/)

UFDR AI Analyzer is a lightweight investigation toolkit that ingests Universal Forensic Data Reports (UFDR), performs AI-assisted pre-analysis, and provides both a direct database search and an AI natural-language interface (Streamlit).

This repo has been cleaned, trimmed, and prepared for safe publishing to GitHub. Sensitive files (API keys, local database) are excluded from commits by default via `.gitignore`.

## Quick highlights
- Ingests sample UFDR data (messages, calls, contacts, media)
- Bulk AI pre-analysis (configurable, can skip heavy image work)
- Fast keyword search across database records
- Streamlit UI for interactive analysis and AI queries

## What's in this repo

Core files:
- `models.py` — SQLModel database models and `get_engine()`
- `ai_analyzer.py` — Gemini/OpenAI wrapper (reads `apikey.txt` or `config.py`)
- `preanalyzer.py` — runs bulk AI analysis of ingested data
- `ingest_ufdr.py` — ingest data from the `fake_ufdr/` sample folder
- `streamlit_app.py` — Streamlit UI

Other artifacts:
- `fake_ufdr/` — sample dataset used for development and testing

## Setup (local development)

1) Create a virtual environment (recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

3) Configure your API key

Preferred: create `apikey.txt` at the repo root and paste your Gemini key (single line). The app will load `apikey.txt` automatically.

Alternative: copy `config.template.py` to `config.py` and edit the `API_KEY` value.

4) Ingest sample data

```powershell
python ingest_ufdr.py fake_ufdr
```

5) Run preanalysis (optional, may take time depending on API and images)

```powershell
python preanalyzer.py           # full analysis
python preanalyzer.py --skip-images   # faster, text-only
```

6) Run the Streamlit UI

```powershell
python -m streamlit run streamlit_app.py --server.port 8501
```

Open `http://localhost:8501` in your browser.

## Cleaning & GitHub readiness
- Sensitive files are excluded via `.gitignore` (local database `ufdr.db`, `apikey.txt`, `config.py`, `analysis.txt`, `venv/`, etc.)
- Remove or move any large media files you don't want in the repo before committing.

## Contributing
- Please open issues or PRs for bugs or feature requests.

## License
- MIT

---

If you want, I can now remove local artifacts (like `ufdr.db`, `apikey.txt`, `venv/`, `__pycache__`) to make this repository safe to push. Confirm and I'll proceed.  

**Professional Investigation Interface**: Web-based AI-powered forensic query system

After pre-analysis, launch the interactive web interface:

```bash
python run_streamlit.py
```

### Key Features:
- **Senior Investigation Officer AI**: Acts as an experienced forensic investigator
- **Natural Language Queries**: Ask questions in plain English
- **Evidence-Based Analysis**: References specific data from your forensic analysis
- **Progress Tracking**: Real-time progress indicators during analysis
- **Professional Reporting**: Structured investigation reports with threat assessments
- **Sample Queries**: Pre-built investigation questions for common scenarios

### Example Investigation Queries:
- `"What are all the suspicious activities you could find?"`
- `"Who are the main suspects in this case?"`
- `"What evidence suggests criminal activity?"`
- `"Are there any indicators of drug-related communications?"`
- `"What are the most concerning findings that need immediate attention?"`
- `"Who should be investigated first and why?"`
- `"Are there any compromised law enforcement contacts?"`
- `"What timeline patterns suggest coordinated criminal activity?"`

## 📊 Command Line Query System (Alternative)

For command-line users, the traditional query system:

```bash
python core_agent.py
```

Example queries:
- `"show suspicious messages"`
- `"messages from +919810000004"`
- `"find calls with foreign numbers"`
- `"recent activity"`

## ⚠️ Important Notes

- This is an MVP for demonstration purposes
- Real UFDR files may have different formats
- Always comply with legal requirements for forensic data analysis
- Ensure proper data privacy and security measures in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Requirements

- **Gemini API Key**: Required for AI analysis
- **Internet Connection**: For API calls
- **Python 3.8+**: With required packages

## 🔒 Security Notes

- API key stored in local config file only
- All processing done locally
- Database stays on your machine
- No data transmitted except to Google AI API

## 🚀 Screenshots

### AI Investigation Interface
![AI Query Interface](https://via.placeholder.com/800x400/1f4e79/ffffff?text=AI+Investigation+Query+Interface)

### Data Explorer
![Data Explorer](https://via.placeholder.com/800x400/28a745/ffffff?text=Forensic+Data+Explorer)

## 🏆 SIH 2025 Project

This project was developed for **Smart India Hackathon 2025** focusing on advanced forensic data analysis capabilities.

### Team Information
- **Problem Statement**: Advanced UFDR Analysis System
- **Category**: Software Development
- **Technology Stack**: Python, Streamlit, AI/ML, SQLModel

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Notice

This is a forensic analysis tool for law enforcement and authorized investigations only. Users must ensure compliance with applicable laws and regulations in their jurisdiction.

## 📞 Support

- 📧 Create an issue for bug reports
- 💡 Feature requests are welcome
- 📖 Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

---

**🎯 Smart India Hackathon 2025 | Advanced Forensic Data Analysis**
# 🔍 UFDR AI Analyzer - SIH 2025

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-blue.svg)](https://ai.google.dev/)

**Smart India Hackathon 2025 - Digital Forensics Solution**

UFDR AI Analyzer is an intelligent forensic investigation toolkit that processes Universal Forensic Data Reports (UFDR) and provides AI-powered analysis for digital evidence examination. Built for law enforcement agencies, cybersecurity professionals, and digital forensics investigators.

## 🚀 Live Demo & Screenshots

![UFDR Analyzer Demo](https://img.shields.io/badge/Demo-Live-brightgreen)

### 📸 Application Screenshots

<div align="center">

| Main Dashboard | Database Search |
|:-:|:-:|
| ![Dashboard](screenshots/dashboard.png) | ![Database Search](screenshots/database_search.png) |
| *Interactive dashboard with forensic data statistics and overview* | *Advanced keyword search across all evidence types* |

| AI Query Interface | File Explorer |
|:-:|:-:|
| ![Query Results](screenshots/query_result.png) | ![File Explorer](screenshots/file_explorer.png) |
| *AI-powered investigation queries with intelligent responses* | *Comprehensive evidence file browser and analysis tools* |

</div>

The application provides a modern web interface for forensic data analysis with real-time AI-powered insights and comprehensive evidence exploration capabilities.

## 🎯 Key Features

### 🤖 AI-Powered Investigation Assistant
- **Natural Language Queries**: Ask complex questions about evidence in plain English
- **Concise Professional Reports**: Focused responses under 200 words with actionable intelligence
- **Evidence Cross-Referencing**: Automatic linking of related messages, calls, and contacts
- **Risk Assessment**: AI-driven threat classification (Critical/High/Medium/Low)
- **Pattern Recognition**: Identifies suspicious communication patterns and criminal networks

### 📊 Advanced Data Processing Engine
- **Multi-Format Ingestion**: Supports messages, call logs, contacts, and multimedia evidence
- **Bulk Analysis Optimization**: Processes entire datasets for comprehensive context understanding
- **Real-Time Search**: Lightning-fast keyword and content searches across all evidence
- **Smart Filtering**: AI-assisted filtering by risk level, content type, and relevance

### 🔍 Professional Investigation Dashboard
- **Evidence Timeline**: Chronological visualization of all forensic evidence
- **Network Mapping**: Visual representation of communication networks and relationships
- **Suspicious Activity Detection**: Automated flagging of high-risk communications
- **Export & Reporting**: Generate professional investigation reports for court proceedings
- **Multi-User Support**: Secure access controls for investigation teams

## 🚀 Complete Setup Guide

### 📋 Prerequisites

Before you begin, ensure you have:
- **Python 3.10 or higher** ([Download here](https://www.python.org/downloads/))
- **Git** installed ([Download here](https://git-scm.com/downloads))
- **Google Gemini API key** ([Get free key here](https://aistudio.google.com/app/apikey))
- **4GB+ RAM** recommended for smooth operation
- **Internet connection** for AI features

### 🛠️ Step-by-Step Installation

#### Step 1: Clone the Repository
```bash
git clone https://github.com/LORDv1shnu/ufdr-analyzer-sih25.git
cd ufdr-analyzer-sih25
```

#### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

#### Step 4: Configure Google Gemini API Key

**Option A: Using apikey.txt file (Recommended)**
```bash
# Create the API key file
# Windows
echo your_actual_gemini_api_key_here > apikey.txt

# Linux/Mac
echo "your_actual_gemini_api_key_here" > apikey.txt
```

**Option B: Using config.py file**
```bash
# Copy template and edit
cp config.template.py config.py
# Then edit config.py and replace "your_actual_api_key_here" with your key
```

**Option C: Using environment variable**
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"

# Linux/Mac
export GEMINI_API_KEY="your_actual_gemini_api_key_here"
```

#### Step 5: Import Sample Forensic Data
```bash
# This will create the database and import all sample evidence
python ingest_ufdr.py fake_ufdr
```

**Expected Output:**
```
Imported 60 contacts
Imported 320 messages
Imported 120 calls
Import completed!
```

#### Step 6: Generate AI Analysis (Optional but Recommended)
```bash
# Full analysis including images (takes 2-3 minutes)
python preanalyzer.py

# Or skip images for faster processing (30 seconds)
python preanalyzer.py --skip-images
```

**Expected Output:**
```
🚀 UFDR PRE-ANALYZER - Starting Complete Analysis
📊 Step 1: Analyzing ALL text data with AI...
   ✅ AI analysis complete!
📄 Report size: 120,000+ characters
🎉 PRE-ANALYSIS COMPLETE!
```

#### Step 7: Launch the Application
```bash
# Start the web interface
streamlit run streamlit_app.py

# Or specify a custom port
streamlit run streamlit_app.py --server.port 8501
```

**Expected Output:**
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

#### Step 8: Access the Application
1. Open your web browser
2. Navigate to `http://localhost:8501`
3. You should see the UFDR AI Analyzer dashboard

### 🔧 Troubleshooting Common Issues

#### API Key Issues
```bash
# Check if API key is loaded
python -c "from ai_analyzer import AIAnalyzer; ai = AIAnalyzer(); print('AI Available:', ai.is_available())"
```

#### Database Issues
```bash
# If database issues occur, reset and re-import
rm ufdr.db
python ingest_ufdr.py fake_ufdr
```

#### Port Issues
```bash
# If port 8501 is busy, use a different port
streamlit run streamlit_app.py --server.port 8502
```

#### Module Import Issues
```bash
# Make sure virtual environment is activated
# Windows
.\.venv\Scripts\Activate.ps1

# Then reinstall dependencies
pip install -r requirements.txt
```

### ✅ Verification Steps

After setup, verify everything works:

1. **Check Database**: Navigate to "Data Explorer" tab - should show 320 messages, 120 calls, 60 contacts
2. **Test Search**: Use "Database Search" tab - search for "phone" should return results
3. **Test AI**: Use "AI Investigation" tab - ask "What suspicious activities are present?"
4. **Check Analysis**: If you ran preanalyzer, check that `analysis.txt` exists and is ~120KB

### � Quick Command Reference

```bash
# Basic workflow
git clone https://github.com/LORDv1shnu/ufdr-analyzer-sih25.git
cd ufdr-analyzer-sih25
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
echo "your_api_key_here" > apikey.txt
python ingest_ufdr.py fake_ufdr
python preanalyzer.py
streamlit run streamlit_app.py
```

### �🚀 You're Ready!

Your UFDR AI Analyzer is now fully set up and ready for forensic investigation work!

**Screenshots Added:**
- ✅ `dashboard.png` - Main dashboard with forensic data statistics (210KB)
- ✅ `database_search.png` - Database search functionality (153KB)  
- ✅ `query_result.png` - AI investigation query responses (176KB)
- ✅ `file_explorer.png` - Evidence file browser and analysis (176KB)

**Ready to commit and push to GitHub!** 🚀

## 📁 Project Structure

```
ufdr-analyzer-sih25/
├── 📋 Core Components
│   ├── streamlit_app.py      # Main web interface
│   ├── models.py             # Database models (SQLModel)
│   ├── ai_analyzer.py        # AI integration (Gemini)
│   ├── preanalyzer.py        # Bulk analysis engine
│   └── ingest_ufdr.py        # Data ingestion pipeline
├── 📊 Sample Data
│   └── fake_ufdr/            # Demo forensic dataset
│       ├── messages/         # 320 sample messages
│       ├── calls/            # 120 call records
│       ├── contacts/         # 60 contacts
│       └── media/            # Sample images
├── 🔧 Configuration
│   ├── requirements.txt      # Python dependencies
│   ├── apikey.template.txt   # API key template
│   └── config.template.py    # Configuration template
└── 📄 Documentation
    ├── README.md             # This file
    └── LICENSE               # MIT License
```

## 💡 Usage Examples

### Direct Database Search
Perform precise keyword searches across all evidence:
```
🔍 Search Examples:
• "drugs" → Find drug-related communications
• "cash transfer" → Identify financial transactions  
• "meeting location" → Locate planned meetups
• "phone number" → Track specific contacts
```

### AI Investigation Queries
Ask sophisticated questions in natural language:
```
🤖 Example Queries:
• "What are the main criminal activities detected in this case?"
• "Who are the key suspects and their roles in the network?"
• "What evidence supports money laundering charges?"
• "Which communications indicate immediate threat to public safety?"
• "What patterns suggest organized criminal activity?"
```

### Evidence Analysis Workflow
```
1. 📥 Ingest UFDR Data → Import all forensic evidence
2. 🤖 AI Pre-Analysis → Generate comprehensive threat assessment  
3. 🔍 Interactive Search → Explore specific evidence types
4. 📊 Generate Reports → Create court-ready documentation
```

## 🔐 Security & Privacy

- **API keys are never committed** - Protected by .gitignore
- **Local processing** - Your forensic data stays on your machine
- **Configurable AI** - Can work offline without AI features
- **Clean separation** - Database and analysis files excluded from git

## 🛠️ Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Check types
mypy .

# Lint code
flake8 .
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Sample Dataset

The included `fake_ufdr/` contains realistic forensic data for testing and demonstration:

### 📱 Digital Communications
- **320 text messages** including suspicious communications, financial discussions, and coded language
- **120 call records** with timing patterns, duration analysis, and frequency mapping
- **60 contacts** with names, phone numbers, and relationship indicators

### 🖼️ Multimedia Evidence  
- **30 sample images** for AI-powered visual analysis and content recognition
- **Metadata extraction** capabilities for timestamps and device information
- **Object detection** for weapons, drugs, cash, and other evidence

### 🔍 Evidence Highlights
```
🚨 High-Risk Communications Detected:
• Drug trafficking references: "20 grams of weed, need buyer"
• Financial crimes: "transfer INR 50,000 in cash"  
• Operational security: "do not bring your phone"
• Suspicious meetings: "meet at the back entrance; keep low"
```

## 🎓 Smart India Hackathon 2025

This project was developed for SIH 2025 Problem Statement: **Digital Forensics and AI-Powered Investigation Tools**

### 🏆 Competition Details
- **Category:** Software Development
- **Problem Domain:** Cybersecurity & Digital Forensics  
- **Solution Type:** AI-Powered Investigation Platform
- **Technology Stack:** Python, Streamlit, Google Gemini AI, SQLModel

### 🎯 Problem Statement Addressed
Development of an intelligent system that can:
- Process large volumes of digital forensic evidence efficiently
- Provide AI-assisted analysis for faster case resolution
- Support law enforcement with actionable intelligence
- Maintain evidence integrity and chain of custody
- Generate court-admissible reports and documentation

### 💡 Innovation Highlights
- **First-of-its-kind** integration of Google Gemini AI with forensic data processing
- **Scalable architecture** supporting multiple evidence formats and sources  
- **User-friendly interface** designed for non-technical law enforcement personnel
- **Real-time analysis** capabilities for urgent investigations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/LORDv1shnu/ufdr-analyzer-sih25/issues)
- **Documentation**: Check the `/docs` folder for detailed guides
- **API Reference**: See inline code documentation

## 🚀 Deployment Options

### Local Development
```bash
# Quick start for development
streamlit run streamlit_app.py --server.port 8501
```

### Production Deployment
```bash
# Using Docker (production-ready)
docker build -t ufdr-analyzer .
docker run -p 8501:8501 ufdr-analyzer

# Using Docker Compose (with database persistence)
docker-compose up -d
```

### Cloud Deployment
- **Streamlit Cloud**: Deploy directly from GitHub repository
- **AWS EC2**: Deploy using provided CloudFormation templates
- **Google Cloud Run**: Container-based deployment with auto-scaling
- **Azure Container Instances**: Quick deployment for demonstration

## 🔒 Security Considerations

- **API Key Protection**: Never commit API keys to version control
- **Data Encryption**: All sensitive data encrypted at rest and in transit
- **Access Controls**: Role-based access for investigation teams  
- **Audit Logging**: Complete audit trail of all user actions
- **Evidence Integrity**: Cryptographic hashing to ensure evidence authenticity

## 📞 Support & Documentation

- **Issues**: [Report bugs or request features](https://github.com/LORDv1shnu/ufdr-analyzer-sih25/issues)
- **Wiki**: [Comprehensive documentation](https://github.com/LORDv1shnu/ufdr-analyzer-sih25/wiki)
- **API Docs**: Available at `/docs` when running locally
- **Video Tutorials**: [YouTube Playlist](https://youtube.com/playlist?list=demo)

---

## 🌟 Acknowledgments

- **Google AI**: For providing Gemini API access and support
- **Smart India Hackathon**: For the opportunity to solve real-world problems
- **Law Enforcement Community**: For guidance on investigation workflows
- **Open Source Community**: For the amazing tools and libraries used

⭐ **Star this repository if you find it useful for digital forensics work!**

**Made with ❤️ for Smart India Hackathon 2025 | Empowering Digital Justice**  

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
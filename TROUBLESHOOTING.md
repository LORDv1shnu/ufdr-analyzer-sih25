# 🔧 UFDR Troubleshooting Guide

## 🌐 Network Connection Issues

### **Error**: `[Errno 11002] getaddrinfo failed`
**Cause**: DNS resolution or internet connectivity problem

**Solutions**:
1. **Check Internet Connection**
   ```bash
   # Test basic connectivity
   ping google.com
   ```

2. **Test AI Connection**
   - In Streamlit sidebar, click "🔧 Test AI Connection"
   - This will diagnose the specific issue

3. **Network Troubleshooting**
   - Restart your router/modem
   - Try using a different DNS server (8.8.8.8, 1.1.1.1)
   - Disable VPN temporarily
   - Check firewall settings

4. **Corporate/School Networks**
   - Contact network administrator
   - May need proxy configuration
   - Some networks block AI services

## 🔑 API Key Issues

### **Error**: `API Key Error` or `Authentication Failed`
**Solutions**:
1. **Verify API Key**
   ```bash
   # Check apikey.txt content
   type apikey.txt
   ```

2. **Get New API Key**
   - Visit: https://aistudio.google.com/app/apikey
   - Create new API key
   - Replace content in `apikey.txt`

3. **API Key Format**
   - Should start with `AIza`
   - No extra spaces or newlines
   - Keep it secure and private

## 🗄️ Database Issues

### **Error**: `Database not found` or `Table errors`
**Solutions**:
1. **Reingest Data**
   ```bash
   python ingest_ufdr.py fake_ufdr
   ```

2. **Delete and Recreate Database**
   ```bash
   del ufdr.db
   python ingest_ufdr.py fake_ufdr
   ```

## 🚀 Streamlit Issues

### **Error**: `Streamlit command not found`
**Solutions**:
1. **Use Python Module**
   ```bash
   python -m streamlit run streamlit_app.py
   ```

2. **Reinstall Streamlit**
   ```bash
   pip install --upgrade streamlit
   ```

### **Error**: `Port already in use`
**Solutions**:
1. **Use Different Port**
   ```bash
   python -m streamlit run streamlit_app.py --server.port 8502
   ```

2. **Kill Existing Process**
   - Close browser tabs
   - Restart terminal
   - Ctrl+C to stop running processes

## 🤖 AI Query Issues

### **Error**: `No response from AI` or timeouts
**Solutions**:
1. **Retry the Query**
   - System now has automatic retry logic
   - Wait a moment and try again

2. **Simplify Query**
   - Use shorter, more direct questions
   - Avoid very complex queries

3. **Check System Status**
   - Use connection test in sidebar
   - Verify analysis.txt exists

## 📊 Data Explorer Issues

### **Error**: `No data found` or empty tables
**Solutions**:
1. **Verify Data Ingestion**
   ```bash
   python validate_system.py
   ```

2. **Check Database**
   - Ensure ufdr.db exists
   - Run data ingestion again if needed

3. **Refresh Page**
   - F5 or Ctrl+R in browser
   - Clear browser cache if needed

## 🔍 General Troubleshooting Steps

### 1. **System Validation**
```bash
python validate_system.py
```

### 2. **Complete Restart**
```bash
# Stop all processes (Ctrl+C)
# Close browser
# Restart terminal
python run_streamlit.py
```

### 3. **Check Logs**
- Look at terminal output for errors
- Note specific error messages
- Check Streamlit error displays

### 4. **Environment Reset**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Test individual components
python -c "from ai_analyzer import AIAnalyzer; print('AI OK')"
python -c "import streamlit_app; print('Streamlit OK')"
```

## 📞 Getting Help

### **If Issues Persist**:
1. **Document the Error**
   - Screenshot error messages
   - Copy full error text
   - Note what you were trying to do

2. **Check System Info**
   ```bash
   python --version
   pip list | findstr streamlit
   ```

3. **Provide Context**
   - Operating system
   - Network environment (home/work/school)
   - When the error occurs

## ✅ Quick Fixes Checklist

- [ ] Internet connection working?
- [ ] API key in apikey.txt?
- [ ] Database exists (ufdr.db)?
- [ ] Analysis report exists (analysis.txt)?
- [ ] Latest dependencies installed?
- [ ] Tried restarting browser?
- [ ] Tried "Test AI Connection"?
- [ ] Checked firewall/antivirus?

---

**💡 Most issues are network-related and resolve by waiting and retrying!**
# AI-PULSE Technology Stack

## Core Technologies

### **Python 3.9+**
- Primary language for all components
- Async/await patterns for network operations
- Type hints used for function signatures

### **Web Scraping & Parsing**
- **BeautifulSoup4** (`>=4.12.2`): Primary HTML parsing
- **requests** (`>=2.31.0`): HTTP client for web scraping
- **lxml** (`>=4.9.3`): Fast XML/HTML parser backend
- **html5lib** (`>=1.1`): Alternative HTML parser
- **selectolax** (`>=0.3.17`): Optional fast HTML parsing

### **RSS Generation**
- **feedgen** (`>=0.9.0`): RSS/Atom feed generation library
- **python-dateutil** (`>=2.8.2`): Date/time parsing and formatting

### **Performance & Caching**
- **requests-cache** (`>=1.1.0`): Optional HTTP response caching
- **urllib3** (`>=2.0.4`): HTTP client optimizations

## Infrastructure & Automation

### **GitHub Actions**
- **Ubuntu Latest**: CI/CD runner environment
- **Python 3.11**: GitHub Actions Python version
- **4-hour schedule**: `cron: '0 */4 * * *'`
- **Monday full rescan**: `cron: '0 8 * * 1'`
- **Manual triggers**: `workflow_dispatch`

### **macOS Desktop Integration**
- **Built-in `subprocess`**: System notifications
- **Built-in `smtplib`**: Gmail email integration
- **JSON config files**: User preferences storage
- **Cron integration**: Automated monitoring

## Architecture Patterns

### **Modular Design**
- Separate parsers per content source
- Independent RSS generation per feed
- Combined feed aggregation
- Desktop integration as optional layer

### **Error Handling**
- Try/catch blocks around network operations
- Graceful degradation on parser failures
- Comprehensive logging with emoji indicators
- Retry logic for transient failures

### **Data Flow**
1. **Web Scraping**: Individual parsers → Raw HTML
2. **Content Extraction**: BeautifulSoup → Structured data
3. **RSS Generation**: feedgen → XML feeds
4. **Desktop Monitoring**: RSS parsing → Notifications
5. **Email Reports**: Article aggregation → Gmail delivery

## Development Tools

### **Code Quality** (Recommended)
- **Black**: Code formatting
- **Type hints**: Function signatures
- **Docstrings**: Public method documentation
- **pytest**: Testing framework

### **System Tools (macOS/Darwin)**
- **git**: Version control
- **curl**: HTTP testing
- **ls/find**: File operations
- **grep**: Text search
- **crontab**: Automation scheduling

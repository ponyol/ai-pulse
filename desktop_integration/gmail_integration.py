#!/usr/bin/env python3
"""
AI-PULSE Gmail Integration
Desktop integration for sending AI-PULSE summaries via email

This script provides Gmail integration for AI-PULSE:
- Sends weekly/daily summaries of Anthropic updates
- Integrates with existing Gmail workflow (like news reviews)
- Provides formatted email reports with categorized content

Author: AI-PULSE Project  
"""

import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import json
from typing import List, Dict
import sys
import os

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from desktop_integration.rss_monitor import RSSMonitor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('gmail-integration')

# Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': '',  # To be configured by user
    'sender_password': '',  # Use app-specific password
    'recipient_email': '',  # To be configured by user
}

CONFIG_FILE = Path.home() / '.ai_pulse_email_config.json'

class GmailIntegration:
    def __init__(self):
        self.config = self.load_config()
        self.monitor = RSSMonitor()
    
    def load_config(self) -> Dict:
        """Load email configuration"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    EMAIL_CONFIG.update(config)
                    return EMAIL_CONFIG
            except Exception as e:
                logger.error(f"Error loading email config: {e}")
        
        logger.warning("No email configuration found. Please run setup_email_config()")
        return EMAIL_CONFIG
    
    def setup_email_config(self, sender_email: str, sender_password: str, recipient_email: str = None):
        """Setup email configuration"""
        config = {
            'sender_email': sender_email,
            'sender_password': sender_password,
            'recipient_email': recipient_email or sender_email
        }
        
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            
            EMAIL_CONFIG.update(config)
            logger.info("✅ Email configuration saved")
            
        except Exception as e:
            logger.error(f"❌ Error saving email config: {e}")
    
    def format_email_content(self, articles: List[Dict], period: str = "Weekly") -> str:
        """Format articles into email content"""
        if not articles:
            return f"No new Anthropic updates found for this {period.lower()} report."
        
        # Group articles by category/source
        by_source = {}
        critical_articles = []
        
        for article in articles:
            source = article.get('feed_source', 'unknown')
            priority = article.get('priority', 'medium')
            
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(article)
            
            if priority == 'critical':
                critical_articles.append(article)
        
        # Build email content
        content = f"""
🤖 AI-PULSE {period} Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

📊 SUMMARY
• Total Articles: {len(articles)}
• Critical Updates: {len(critical_articles)}
• Sources Covered: {len(by_source)}

"""
        
        # Critical updates section
        if critical_articles:
            content += "🚨 CRITICAL UPDATES\n"
            content += "=" * 50 + "\n"
            for article in critical_articles[:5]:
                content += f"📌 {article['title']}\n"
                content += f"   🔗 {article['link']}\n"
                content += f"   📝 {article['description'][:200]}...\n\n"
        
        # By source sections
        source_order = ['anthropic_alignment', 'anthropic_engineering', 'anthropic_news', 'anthropic_complete']
        source_names = {
            'anthropic_alignment': '🧠 ALIGNMENT SCIENCE',
            'anthropic_engineering': '🔧 ENGINEERING',
            'anthropic_news': '📰 NEWS & ANNOUNCEMENTS',
            'anthropic_complete': '📋 COMPLETE FEED'
        }
        
        for source in source_order:
            if source in by_source and source != 'anthropic_complete':  # Skip complete to avoid duplicates
                articles_in_source = by_source[source]
                content += f"\n{source_names.get(source, source.upper())}\n"
                content += "=" * 50 + "\n"
                
                for article in articles_in_source[:10]:  # Limit per source
                    content += f"• {article['title']}\n"
                    content += f"  {article['link']}\n"
                    if article.get('description'):
                        content += f"  {article['description'][:150]}...\n"
                    content += "\n"
        
        content += f"""
---
🤖 This report was automatically generated by AI-PULSE
📊 RSS monitoring for Anthropic updates
⚙️  Configure at: github.com/your-username/ai-pulse
"""
        
        return content
    
    def send_email_report(self, articles: List[Dict], subject_prefix: str = "Weekly"):
        """Send email report with articles"""
        
        if not self.config.get('sender_email') or not self.config.get('sender_password'):
            logger.error("❌ Email configuration not set up. Run setup_email_config() first.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config['sender_email']
            msg['To'] = self.config['recipient_email']
            msg['Subject'] = f"🤖 AI-PULSE {subject_prefix} Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Format content
            body = self.format_email_content(articles, subject_prefix)
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['sender_email'], self.config['sender_password'])
                text = msg.as_string()
                server.sendmail(self.config['sender_email'], self.config['recipient_email'], text)
            
            logger.info(f"✅ Email report sent successfully to {self.config['recipient_email']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            return False
    
    def send_daily_digest(self):
        """Send daily digest of new articles"""
        logger.info("📨 Generating daily AI-PULSE digest")
        
        # Get articles from last 24 hours
        new_articles = self.monitor.run_check()
        
        if new_articles:
            self.send_email_report(new_articles, "Daily")
            logger.info(f"📧 Daily digest sent with {len(new_articles)} articles")
        else:
            logger.info("📭 No new articles for daily digest")
    
    def send_weekly_digest(self):
        """Send weekly digest of articles"""
        logger.info("📨 Generating weekly AI-PULSE digest")
        
        # For weekly digest, we'd need to track articles over time
        # For now, just send recent articles
        new_articles = self.monitor.run_check()
        
        if new_articles:
            self.send_email_report(new_articles, "Weekly")
            logger.info(f"📧 Weekly digest sent with {len(new_articles)} articles")
        else:
            logger.info("📭 No new articles for weekly digest")
    
    def test_email_setup(self):
        """Test email configuration"""
        test_articles = [{
            'title': 'AI-PULSE Email Test',
            'link': 'https://github.com/your-username/ai-pulse',
            'description': 'This is a test email to verify AI-PULSE Gmail integration is working correctly.',
            'feed_source': 'test',
            'priority': 'medium'
        }]
        
        success = self.send_email_report(test_articles, "Test")
        
        if success:
            logger.info("✅ Email test successful!")
        else:
            logger.error("❌ Email test failed!")
        
        return success

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-PULSE Gmail Integration')
    parser.add_argument('action', choices=['daily', 'weekly', 'test', 'setup'], 
                       help='Action to perform')
    parser.add_argument('--sender', help='Sender email address (for setup)')
    parser.add_argument('--password', help='Sender app password (for setup)')
    parser.add_argument('--recipient', help='Recipient email address (for setup)')
    
    args = parser.parse_args()
    
    integration = GmailIntegration()
    
    if args.action == 'setup':
        if not args.sender or not args.password:
            logger.error("❌ Setup requires --sender and --password arguments")
            return
        
        integration.setup_email_config(args.sender, args.password, args.recipient)
        
        # Test the setup
        integration.test_email_setup()
        
    elif args.action == 'test':
        integration.test_email_setup()
        
    elif args.action == 'daily':
        integration.send_daily_digest()
        
    elif args.action == 'weekly':
        integration.send_weekly_digest()

if __name__ == "__main__":
    main()

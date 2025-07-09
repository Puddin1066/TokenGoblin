#!/usr/bin/env python3
"""
Email Campaign Generator for Claude Token Resale System
Generates localized email templates from CSV data
"""

import csv
import os
import sys
import argparse
from typing import Dict, List, Optional
from pathlib import Path
from urllib.parse import quote_plus
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from email_campaign.localization.texts import EMAIL_TEMPLATES
from email_campaign.email_sender import EmailSender

logger = logging.getLogger(__name__)


class EmailCampaignGenerator:
    """Generate localized email campaigns from CSV data"""
    
    def __init__(self, output_dir: str = "email_output", bot_username: str = "ClaudeVendBot"):
        self.output_dir = Path(output_dir)
        self.bot_username = bot_username
        self.email_sender = EmailSender()
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def generate_deep_link(self, campaign_id: str, email: str, abstract_snippet: str) -> str:
        """Generate Telegram deep link"""
        # URL encode the payload
        payload = f"{campaign_id}|{email}|{abstract_snippet}"
        encoded_payload = quote_plus(payload)
        
        return f"https://t.me/{self.bot_username}?start={encoded_payload}"
    
    def generate_email_content(self, lead_data: Dict[str, str]) -> Dict[str, str]:
        """Generate email content for a single lead"""
        name = lead_data.get("name", "Researcher")
        email = lead_data.get("email", "")
        country = lead_data.get("country", "")
        abstract_snippet = lead_data.get("abstract_snippet", "")
        campaign_id = lead_data.get("campaignID", "")
        language = lead_data.get("language", "en")
        
        # Generate deep link
        deep_link = self.generate_deep_link(campaign_id, email, abstract_snippet)
        
        # Get email template for language
        template = EMAIL_TEMPLATES.get(language, EMAIL_TEMPLATES["en"])
        
        # Format subject
        subject = template["subject"].format(
            name=name,
            abstract_snippet=abstract_snippet
        )
        
        # Format body
        body = template["body"].format(
            name=name,
            abstract_snippet=abstract_snippet,
            deep_link=deep_link,
            email=email,
            country=country,
            campaign_id=campaign_id
        )
        
        return {
            "subject": subject,
            "body": body,
            "language": language,
            "deep_link": deep_link
        }
    
    def save_email_file(self, email: str, content: Dict[str, str]) -> Path:
        """Save email content to file"""
        # Sanitize email for filename
        safe_email = email.replace("@", "_at_").replace(".", "_")
        filename = f"email_{safe_email}.txt"
        filepath = self.output_dir / filename
        
        # Create email content
        email_content = f"""Subject: {content['subject']}

{content['body']}

---
Language: {content['language']}
Deep Link: {content['deep_link']}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(email_content)
        
        return filepath
    
    def process_csv(self, csv_file: str, send_emails: bool = False) -> List[Dict]:
        """Process CSV file and generate email campaigns"""
        results = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        # Generate email content
                        content = self.generate_email_content(row)
                        
                        # Save to file
                        filepath = self.save_email_file(row["email"], content)
                        
                        result = {
                            "email": row["email"],
                            "name": row.get("name", ""),
                            "campaign_id": row.get("campaignID", ""),
                            "language": row.get("language", "en"),
                            "filepath": str(filepath),
                            "subject": content["subject"],
                            "status": "success"
                        }
                        
                        # Send email if requested
                        if send_emails:
                            try:
                                sent = self.email_sender.send_email(
                                    to_email=row["email"],
                                    subject=content["subject"],
                                    body=content["body"],
                                    recipient_name=row.get("name", "")
                                )
                                result["sent"] = sent
                                result["send_status"] = "sent" if sent else "failed"
                            except Exception as e:
                                logger.error(f"Failed to send email to {row['email']}: {e}")
                                result["send_error"] = str(e)
                                result["sent"] = False
                                result["send_status"] = "error"
                        
                        results.append(result)
                        logger.info(f"Generated email for {row['email']}")
                        
                    except Exception as e:
                        logger.error(f"Error processing row {row}: {e}")
                        results.append({
                            "email": row.get("email", "unknown"),
                            "status": "error",
                            "error": str(e)
                        })
                        
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
        
        return results
    
    def generate_campaign_summary(self, results: List[Dict]) -> str:
        """Generate campaign summary report"""
        total = len(results)
        successful = len([r for r in results if r.get("status") == "success"])
        failed = total - successful
        sent = len([r for r in results if r.get("sent") == True])
        
        # Language breakdown
        languages = {}
        for result in results:
            if result.get("status") == "success":
                lang = result.get("language", "en")
                languages[lang] = languages.get(lang, 0) + 1
        
        report = f"""# Email Campaign Summary Report

## 📊 Statistics
- **Total leads processed:** {total}
- **Successful generations:** {successful}
- **Failed generations:** {failed}
- **Emails sent:** {sent}

## 🌍 Language Breakdown
"""
        
        for lang, count in languages.items():
            report += f"- **{lang.upper()}:** {count} emails\n"
        
        report += f"""
## 📁 Output Directory
{self.output_dir.absolute()}

## 📧 Generated Email Files
"""
        
        for result in results:
            if result.get("status") == "success":
                status_icon = "✅" if result.get("sent") else "📄"
                report += f"{status_icon} `{result['filepath']}` - {result['email']} ({result['language']})\n"
        
        if failed > 0:
            report += "\n## ❌ Failed Generations\n"
            for result in results:
                if result.get("status") == "error":
                    report += f"- {result['email']}: {result.get('error', 'Unknown error')}\n"
        
        return report
    
    def save_campaign_summary(self, results: List[Dict]) -> Path:
        """Save campaign summary to file"""
        summary_content = self.generate_campaign_summary(results)
        summary_path = self.output_dir / "campaign_summary.md"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        return summary_path
    
    def generate_mailchimp_csv(self, results: List[Dict]) -> Path:
        """Generate CSV for Mailchimp import"""
        csv_path = self.output_dir / "mailchimp_import.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Email', 'Name', 'Language', 'Campaign_ID', 'Subject', 'Deep_Link'])
            
            for result in results:
                if result.get("status") == "success":
                    writer.writerow([
                        result["email"],
                        result["name"],
                        result["language"],
                        result["campaign_id"],
                        result["subject"],
                        result.get("deep_link", "")
                    ])
        
        return csv_path
    
    def preview_email(self, lead_data: Dict[str, str]) -> str:
        """Preview email for a single lead"""
        content = self.generate_email_content(lead_data)
        
        preview = f"""
=== EMAIL PREVIEW ===

TO: {lead_data.get('email', '')}
SUBJECT: {content['subject']}
LANGUAGE: {content['language']}

{content['body']}

=====================
"""
        return preview


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Generate email campaigns from CSV data")
    parser.add_argument("csv_file", help="Path to CSV file with lead data")
    parser.add_argument("-o", "--output", default="email_output", help="Output directory (default: email_output)")
    parser.add_argument("-b", "--bot", default="ClaudeVendBot", help="Bot username (default: ClaudeVendBot)")
    parser.add_argument("-s", "--send", action="store_true", help="Send emails (requires SMTP configuration)")
    parser.add_argument("-p", "--preview", action="store_true", help="Preview first email only")
    parser.add_argument("-m", "--mailchimp", action="store_true", help="Generate Mailchimp CSV")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Validate input file
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file '{args.csv_file}' not found")
        sys.exit(1)
    
    # Initialize generator
    generator = EmailCampaignGenerator(output_dir=args.output, bot_username=args.bot)
    
    try:
        # Preview mode
        if args.preview:
            with open(args.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                first_row = next(reader)
                preview = generator.preview_email(first_row)
                print(preview)
                return
        
        # Process CSV
        print(f"Processing {args.csv_file}...")
        results = generator.process_csv(args.csv_file, send_emails=args.send)
        
        # Generate summary
        summary_path = generator.save_campaign_summary(results)
        
        # Generate Mailchimp CSV if requested
        if args.mailchimp:
            mailchimp_path = generator.generate_mailchimp_csv(results)
            print(f"📧 Mailchimp CSV: {mailchimp_path}")
        
        # Print results
        successful = len([r for r in results if r.get("status") == "success"])
        total = len(results)
        
        print(f"\n✅ Campaign generation complete!")
        print(f"📊 {successful}/{total} emails generated successfully")
        print(f"📁 Output directory: {generator.output_dir.absolute()}")
        print(f"📄 Summary report: {summary_path}")
        
        if args.send:
            sent = len([r for r in results if r.get("sent") == True])
            print(f"📧 {sent} emails sent successfully")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
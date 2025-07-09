#!/usr/bin/env python3
"""
GitHub Gist Generator for Claude Token Resale System
Generates personalized gist pages from CSV data
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

from gist_generator.localization.texts import LOCALIZATION_TEXTS
from gist_generator.github_uploader import GitHubUploader

logger = logging.getLogger(__name__)


class GistGenerator:
    """Generate personalized GitHub Gists from CSV data"""
    
    def __init__(self, output_dir: str = "output", bot_username: str = "ClaudeVendBot"):
        self.output_dir = Path(output_dir)
        self.bot_username = bot_username
        self.github_uploader = GitHubUploader()
        
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
    
    def get_localized_greeting(self, language: str) -> str:
        """Get localized greeting based on language"""
        if language == "ru":
            return LOCALIZATION_TEXTS["ru"]["greeting"]
        elif language == "zh":
            return LOCALIZATION_TEXTS["zh"]["greeting"]
        else:
            return ""  # Default to English (no additional greeting)
    
    def generate_gist_content(self, lead_data: Dict[str, str]) -> str:
        """Generate gist content for a single lead"""
        name = lead_data.get("name", "Researcher")
        email = lead_data.get("email", "")
        country = lead_data.get("country", "")
        abstract_snippet = lead_data.get("abstract_snippet", "")
        campaign_id = lead_data.get("campaignID", "")
        language = lead_data.get("language", "en")
        
        # Generate deep link
        deep_link = self.generate_deep_link(campaign_id, email, abstract_snippet)
        
        # Get localized greeting
        greeting = self.get_localized_greeting(language)
        
        # Generate content
        content = f"""# 🧠 Claude Token Access – For Dr. {name}

{greeting}

Your research on:
> "{abstract_snippet}"

…suggests you could benefit from Claude 3's reasoning capabilities.

## 🚀 Get Instant Access

Click the link below to purchase Claude tokens via Telegram:

🔗 **[Buy Claude Tokens Now]({deep_link})**

## 💡 About Claude Tokens

Claude tokens give you access to:
- **Advanced reasoning** for complex research problems
- **Long-context understanding** for analyzing papers
- **Multi-language support** for international collaboration
- **Reliable, consistent** AI assistance

## 🎯 Pricing

- **10,000 tokens** = $5.00 USD
- **50,000 tokens** = $20.00 USD  
- **100,000 tokens** = $35.00 USD

## 🔒 Secure Payment

- Pay via Telegram Payments (Card/PayPal)
- Cryptocurrency options available
- Instant token delivery
- 24/7 support

## 📊 Perfect for Research

Claude excels at:
- Literature review assistance
- Data analysis and interpretation
- Academic writing support
- Methodology development
- Research planning

---

*This page was generated automatically for researchers in the AI field. If you have any questions, please contact our support team.*

**Campaign ID:** `{campaign_id}`  
**Generated for:** {email}  
**Country:** {country}

---

### 🔗 Quick Access Links

- [Telegram Bot](https://t.me/{self.bot_username})
- [Documentation](https://docs.example.com)
- [Support](https://t.me/support)
- [Terms of Service](https://example.com/terms)

### 🌍 Multi-Language Support

This service is available in:
- **English** - Full support
- **Russian** - Русский язык поддерживается
- **Chinese** - 中文支持

---

*🔬 Accelerate your research with Claude's advanced AI capabilities*
"""
        
        return content
    
    def save_gist_file(self, email: str, content: str) -> Path:
        """Save gist content to file"""
        # Sanitize email for filename
        safe_email = email.replace("@", "_at_").replace(".", "_")
        filename = f"gist_{safe_email}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def process_csv(self, csv_file: str, upload_to_github: bool = False) -> List[Dict]:
        """Process CSV file and generate gists"""
        results = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        # Generate gist content
                        content = self.generate_gist_content(row)
                        
                        # Save to file
                        filepath = self.save_gist_file(row["email"], content)
                        
                        result = {
                            "email": row["email"],
                            "name": row.get("name", ""),
                            "campaign_id": row.get("campaignID", ""),
                            "filepath": str(filepath),
                            "status": "success"
                        }
                        
                        # Upload to GitHub if requested
                        if upload_to_github:
                            try:
                                gist_url = self.github_uploader.upload_gist(
                                    filename=filepath.name,
                                    content=content,
                                    description=f"Claude Token Access for {row.get('name', 'Researcher')}"
                                )
                                result["gist_url"] = gist_url
                                result["uploaded"] = True
                            except Exception as e:
                                logger.error(f"Failed to upload gist for {row['email']}: {e}")
                                result["upload_error"] = str(e)
                                result["uploaded"] = False
                        
                        results.append(result)
                        logger.info(f"Generated gist for {row['email']}")
                        
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
    
    def generate_summary_report(self, results: List[Dict]) -> str:
        """Generate summary report"""
        total = len(results)
        successful = len([r for r in results if r.get("status") == "success"])
        failed = total - successful
        uploaded = len([r for r in results if r.get("uploaded") == True])
        
        report = f"""# Gist Generation Summary Report

## 📊 Statistics
- **Total leads processed:** {total}
- **Successful generations:** {successful}
- **Failed generations:** {failed}
- **GitHub uploads:** {uploaded}

## 📁 Output Directory
{self.output_dir.absolute()}

## 🔗 Generated Files
"""
        
        for result in results:
            if result.get("status") == "success":
                report += f"- `{result['filepath']}` - {result['email']}"
                if result.get("gist_url"):
                    report += f" ([GitHub Gist]({result['gist_url']}))"
                report += "\n"
        
        if failed > 0:
            report += "\n## ❌ Failed Generations\n"
            for result in results:
                if result.get("status") == "error":
                    report += f"- {result['email']}: {result.get('error', 'Unknown error')}\n"
        
        return report
    
    def save_summary_report(self, results: List[Dict]) -> Path:
        """Save summary report to file"""
        report_content = self.generate_summary_report(results)
        report_path = self.output_dir / "generation_summary.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_path


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Generate GitHub Gists from CSV data")
    parser.add_argument("csv_file", help="Path to CSV file with lead data")
    parser.add_argument("-o", "--output", default="output", help="Output directory (default: output)")
    parser.add_argument("-b", "--bot", default="ClaudeVendBot", help="Bot username (default: ClaudeVendBot)")
    parser.add_argument("-u", "--upload", action="store_true", help="Upload to GitHub Gists")
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
    generator = GistGenerator(output_dir=args.output, bot_username=args.bot)
    
    try:
        # Process CSV
        print(f"Processing {args.csv_file}...")
        results = generator.process_csv(args.csv_file, upload_to_github=args.upload)
        
        # Generate summary report
        report_path = generator.save_summary_report(results)
        
        # Print results
        successful = len([r for r in results if r.get("status") == "success"])
        total = len(results)
        
        print(f"\n✅ Generation complete!")
        print(f"📊 {successful}/{total} gists generated successfully")
        print(f"📁 Output directory: {generator.output_dir.absolute()}")
        print(f"📄 Summary report: {report_path}")
        
        if args.upload:
            uploaded = len([r for r in results if r.get("uploaded") == True])
            print(f"🚀 {uploaded} gists uploaded to GitHub")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
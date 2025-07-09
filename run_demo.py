#!/usr/bin/env python3
"""
Demo script for Claude Token Resale System
Demonstrates gist generation and email campaign creation
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from gist_generator.generator import GistGenerator
from email_campaign.generator import EmailCampaignGenerator


def demo_gist_generator():
    """Demonstrate gist generator functionality"""
    print("🚀 Demo: Gist Generator")
    print("=" * 50)
    
    # Initialize generator
    generator = GistGenerator(output_dir="demo_gists", bot_username="ClaudeVendBot")
    
    # Process CSV file
    csv_file = "sample_leads.csv"
    if not os.path.exists(csv_file):
        print(f"❌ Sample CSV file not found: {csv_file}")
        return
    
    print(f"📄 Processing {csv_file}...")
    
    # Generate gists (without GitHub upload for demo)
    results = generator.process_csv(csv_file, upload_to_github=False)
    
    # Print results
    successful = len([r for r in results if r.get("status") == "success"])
    total = len(results)
    
    print(f"✅ Generated {successful}/{total} gists successfully")
    print(f"📁 Output directory: {generator.output_dir}")
    
    # Show sample gist content
    if results and results[0].get("status") == "success":
        sample_file = results[0]["filepath"]
        print(f"\n📝 Sample gist content ({sample_file}):")
        print("-" * 40)
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Show first 500 characters
                print(content[:500] + "..." if len(content) > 500 else content)
        except Exception as e:
            print(f"Error reading sample file: {e}")
    
    print("\n" + "=" * 50)


def demo_email_campaign():
    """Demonstrate email campaign generator functionality"""
    print("📧 Demo: Email Campaign Generator")
    print("=" * 50)
    
    # Initialize generator
    generator = EmailCampaignGenerator(output_dir="demo_emails", bot_username="ClaudeVendBot")
    
    # Process CSV file
    csv_file = "sample_leads.csv"
    if not os.path.exists(csv_file):
        print(f"❌ Sample CSV file not found: {csv_file}")
        return
    
    print(f"📄 Processing {csv_file}...")
    
    # Generate emails (without sending for demo)
    results = generator.process_csv(csv_file, send_emails=False)
    
    # Print results
    successful = len([r for r in results if r.get("status") == "success"])
    total = len(results)
    
    print(f"✅ Generated {successful}/{total} emails successfully")
    print(f"📁 Output directory: {generator.output_dir}")
    
    # Show language breakdown
    languages = {}
    for result in results:
        if result.get("status") == "success":
            lang = result.get("language", "en")
            languages[lang] = languages.get(lang, 0) + 1
    
    print("\n🌍 Language breakdown:")
    for lang, count in languages.items():
        print(f"  {lang.upper()}: {count} emails")
    
    # Show sample email content
    if results and results[0].get("status") == "success":
        sample_file = results[0]["filepath"]
        print(f"\n📧 Sample email content ({sample_file}):")
        print("-" * 40)
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Show first 800 characters
                print(content[:800] + "..." if len(content) > 800 else content)
        except Exception as e:
            print(f"Error reading sample file: {e}")
    
    print("\n" + "=" * 50)


def demo_deep_link_generation():
    """Demonstrate deep link generation"""
    print("🔗 Demo: Deep Link Generation")
    print("=" * 50)
    
    # Sample data
    sample_data = {
        "campaignID": "camp_ai2024",
        "email": "liwei@tsinghua.edu.cn",
        "abstract_snippet": "Prompt Optimization Methods for Large Language Models"
    }
    
    # Generate deep link
    gist_gen = GistGenerator(bot_username="ClaudeVendBot")
    deep_link = gist_gen.generate_deep_link(
        sample_data["campaignID"],
        sample_data["email"],
        sample_data["abstract_snippet"]
    )
    
    print(f"📋 Sample data:")
    print(f"  Campaign ID: {sample_data['campaignID']}")
    print(f"  Email: {sample_data['email']}")
    print(f"  Abstract: {sample_data['abstract_snippet']}")
    
    print(f"\n🔗 Generated deep link:")
    print(f"  {deep_link}")
    
    print(f"\n📱 How it works:")
    print("  1. User clicks the deep link")
    print("  2. Telegram opens with the bot")
    print("  3. Bot parses campaign data and shows personalized message")
    print("  4. User can purchase tokens directly in Telegram")
    
    print("\n" + "=" * 50)


def main():
    """Main demo function"""
    print("🧠 Claude Token Resale System - Demo")
    print("=" * 60)
    print()
    
    # Check if sample CSV exists
    if not os.path.exists("sample_leads.csv"):
        print("❌ Sample CSV file 'sample_leads.csv' not found")
        print("Please ensure the sample CSV file is in the current directory")
        return
    
    # Run demos
    try:
        demo_deep_link_generation()
        print()
        demo_gist_generator()
        print()
        demo_email_campaign()
        
        print("\n🎉 Demo completed!")
        print("\nNext steps:")
        print("1. Configure your bot token in .env file")
        print("2. Set up GitHub and email credentials (optional)")
        print("3. Run the Telegram bot with: python run.py")
        print("4. Test gist generation: python gist_generator/generator.py sample_leads.csv")
        print("5. Test email campaign: python email_campaign/generator.py sample_leads.csv")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
import os
import pickle
from collections import defaultdict, Counter
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate_gmail():
    """Authenticate and return Gmail service object"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
            else:
                client_config = {
                    "installed": {
                        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def get_inbox_categories(service):
    """Get emails from Primary, Social, and Promotions categories"""
    categories = {
        'Primary': 'category:primary',
        'Social': 'category:social',
        'Promotions': 'category:promotions'
    }

    all_emails = {}

    for category_name, query in categories.items():
        print(f"Fetching {category_name} emails...")

        try:
            messages = []
            next_page_token = None

            while True:
                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=500,  # Gmail API maximum
                    pageToken=next_page_token
                ).execute()

                batch_messages = results.get('messages', [])
                messages.extend(batch_messages)

                next_page_token = results.get('nextPageToken')
                if not next_page_token:
                    break

                print(f"  Fetched {len(messages)} emails so far...")

            all_emails[category_name] = messages
            print(f"Found {len(messages)} total emails in {category_name}")

        except Exception as e:
            print(f"Error fetching {category_name}: {e}")
            all_emails[category_name] = []

    return all_emails


def analyze_senders(service, all_emails):
    """Analyze sender information from all categories"""
    sender_stats = defaultdict(lambda: defaultdict(int))
    total_by_category = defaultdict(int)

    for category, messages in all_emails.items():
        print(f"\nAnalyzing senders in {category}...")

        for i, message in enumerate(messages):
            try:
                # Get email headers (sender info only, not content)
                email_data = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='metadata',  # Only metadata, not full content
                    metadataHeaders=['From', 'Subject']
                ).execute()

                # Extract sender from headers
                headers = email_data['payload'].get('headers', [])
                sender = None

                for header in headers:
                    if header['name'] == 'From':
                        sender = header['value']
                        break

                if sender:
                    # Clean sender format (extract email from "Name <email@domain.com>")
                    if '<' in sender and '>' in sender:
                        clean_sender = sender.split('<')[1].split('>')[0]
                    else:
                        clean_sender = sender

                    sender_stats[clean_sender][category] += 1
                    total_by_category[category] += 1

                # Progress indicator
                if (i + 1) % 50 == 0:
                    print(f"Processed {i + 1}/{len(messages)} emails in {category}")

            except Exception as e:
                print(f"Error processing message: {e}")
                continue

    return sender_stats, total_by_category


def display_results(sender_stats, total_by_category):
    """Display analysis results"""
    print("\n" + "=" * 80)
    print("GMAIL INBOX ANALYSIS RESULTS")
    print("=" * 80)

    print("\nEMAILS BY CATEGORY:")
    for category, count in total_by_category.items():
        print(f"{category}: {count} emails")

    # Top senders overall
    sender_totals = {}
    for sender, categories in sender_stats.items():
        sender_totals[sender] = sum(categories.values())

    print(f"\nTOP 20 SENDERS (Total emails):")
    print("-" * 60)
    for sender, total in sorted(sender_totals.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"{sender}: {total} emails")

        categories = sender_stats[sender]
        breakdown = []
        for cat in ['Primary', 'Social', 'Promotions']:
            if categories[cat] > 0:
                breakdown.append(f"{cat}: {categories[cat]}")

        if breakdown:
            print(f"  └─ {' | '.join(breakdown)}")
        print()


def main():
    """Main function to run the analysis"""
    print("Gmail Inbox Analyzer")
    print("This script will analyze your inbox without reading email content.")
    print("You'll need to authenticate with Google first.\n")

    try:
        service = authenticate_gmail()
        print("✓ Gmail authentication successful!")

        all_emails = get_inbox_categories(service)

        sender_stats, total_by_category = analyze_senders(service, all_emails)

        display_results(sender_stats, total_by_category)

        print("\nSaving detailed results to 'gmail_analysis.txt'...")
        with open('gmail_analysis.txt', 'w', encoding='utf-8') as f:
            f.write("Gmail Inbox Analysis Results\n")
            f.write("=" * 50 + "\n\n")

            f.write("SUMMARY BY CATEGORY:\n")
            for category, count in total_by_category.items():
                f.write(f"{category}: {count} emails\n")

            f.write("\nDETAILED SENDER BREAKDOWN:\n")
            f.write("-" * 40 + "\n")

            sender_totals = {}
            for sender, categories in sender_stats.items():
                sender_totals[sender] = sum(categories.values())

            for sender, total in sorted(sender_totals.items(), key=lambda x: x[1], reverse=True):
                f.write(f"\n{sender}: {total} total emails\n")
                categories = sender_stats[sender]
                for cat in ['Primary', 'Social', 'Promotions']:
                    if categories[cat] > 0:
                        f.write(f"  {cat}: {categories[cat]} emails\n")

        print("✓ Analysis complete! Check 'gmail_analysis.txt' for detailed results.")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Created credentials.json from Google Cloud Console")
        print("2. Enabled Gmail API")
        print("3. Installed required packages")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Smart Email Assistant for Level 33
AI-powered email management using Gemma 2 9B
"""

import subprocess
import json
import os
from datetime import datetime
from pathlib import Path


class EmailAssistant:
    """AI-powered email assistant using local LLM"""
    
    def __init__(self, model="gemma2:9b"):
        self.model = model
        self.ollama_url = "http://localhost:11434"
        self.email_cache = Path("workspace/email_cache")
        self.email_cache.mkdir(parents=True, exist_ok=True)
        
    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.ollama_url}/api/tags"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def query_llm(self, prompt, system_prompt=None):
        """Query the local LLM via Ollama"""
        if not self.check_ollama():
            return "Error: Ollama not running. Start with: ollama serve"
        
        # Build request
        request = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            request["system"] = system_prompt
        
        try:
            # Use curl to query Ollama API
            result = subprocess.run(
                ["curl", "-s", "-X", "POST",
                 f"{self.ollama_url}/api/generate",
                 "-d", json.dumps(request)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                return response.get('response', 'No response')
            else:
                return f"Error: {result.stderr}"
                
        except Exception as e:
            return f"Error querying LLM: {e}"
    
    def get_emails_via_applescript(self, mailbox="INBOX", limit=10):
        """
        Fetch emails using AppleScript
        
        Args:
            mailbox: Mailbox name
            limit: Number of emails to fetch
            
        Returns:
            List of email dictionaries
        """
        applescript = f'''
        tell application "Mail"
            set emailList to {{}}
            set theMessages to messages of mailbox "{mailbox}"
            
            repeat with i from 1 to (count of theMessages)
                if i > {limit} then exit repeat
                
                set theMessage to item i of theMessages
                set emailInfo to {{}}
                set emailInfo's subject to subject of theMessage
                set emailInfo's sender to sender of theMessage
                set emailInfo's dateReceived to date received of theMessage
                set emailInfo's content to content of theMessage
                set emailInfo's wasRead to read status of theMessage
                
                copy emailInfo to end of emailList
            end repeat
            
            return emailList
        end tell
        '''
        
        try:
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse AppleScript output (simplified)
                print("Emails fetched (parsing not fully implemented)")
                return []
            else:
                print(f"Error fetching emails: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def categorize_email(self, subject, sender, content):
        """
        Categorize email using AI
        
        Args:
            subject: Email subject
            sender: Email sender
            content: Email content (first 500 chars)
            
        Returns:
            Category: urgent, important, normal, spam, promotional
        """
        prompt = f"""Categorize this email into ONE category: urgent, important, normal, spam, or promotional.

Subject: {subject}
From: {sender}
Content preview: {content[:500]}

Category (one word only):"""
        
        system_prompt = "You are an email categorization assistant. Respond with only one word: urgent, important, normal, spam, or promotional."
        
        response = self.query_llm(prompt, system_prompt)
        
        # Extract category
        category = response.strip().lower()
        valid_categories = ['urgent', 'important', 'normal', 'spam', 'promotional']
        
        if category in valid_categories:
            return category
        else:
            return 'normal'  # Default
    
    def generate_reply(self, email_content, tone="professional"):
        """
        Generate email reply using AI
        
        Args:
            email_content: Original email content
            tone: Reply tone (professional, friendly, brief)
            
        Returns:
            Generated reply text
        """
        prompt = f"""Generate a {tone} email reply to the following email:

{email_content}

Reply:"""
        
        system_prompt = f"You are a helpful email assistant. Generate {tone} email replies that are clear and appropriate."
        
        return self.query_llm(prompt, system_prompt)
    
    def extract_action_items(self, email_content):
        """
        Extract action items from email
        
        Args:
            email_content: Email content
            
        Returns:
            List of action items
        """
        prompt = f"""Extract action items from this email. List each action item on a new line starting with '-'.

Email:
{email_content}

Action items:"""
        
        system_prompt = "You are an assistant that extracts action items from emails. Be concise and specific."
        
        response = self.query_llm(prompt, system_prompt)
        
        # Parse action items
        items = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                items.append(line[1:].strip())
        
        return items
    
    def summarize_email(self, email_content, max_length=100):
        """
        Generate email summary
        
        Args:
            email_content: Email content
            max_length: Maximum summary length in words
            
        Returns:
            Summary text
        """
        prompt = f"""Summarize this email in {max_length} words or less:

{email_content}

Summary:"""
        
        system_prompt = "You are a concise email summarization assistant."
        
        return self.query_llm(prompt, system_prompt)
    
    def detect_urgency(self, subject, content):
        """
        Detect if email is urgent
        
        Args:
            subject: Email subject
            content: Email content
            
        Returns:
            Urgency score (0-10) and reason
        """
        prompt = f"""Rate the urgency of this email on a scale of 0-10 and explain why.

Subject: {subject}
Content: {content[:500]}

Format: Score: X\nReason: ..."""
        
        system_prompt = "You are an email urgency detection assistant. Be objective and consider deadlines, importance, and sender."
        
        response = self.query_llm(prompt, system_prompt)
        
        # Parse response
        try:
            lines = response.split('\n')
            score_line = [l for l in lines if 'score' in l.lower()][0]
            score = int(''.join(filter(str.isdigit, score_line)))
            reason = '\n'.join([l for l in lines if 'reason' in l.lower()])
            return score, reason
        except:
            return 5, "Unable to determine urgency"
    
    def suggest_labels(self, subject, sender, content):
        """
        Suggest email labels/tags
        
        Args:
            subject: Email subject
            sender: Email sender
            content: Email content
            
        Returns:
            List of suggested labels
        """
        prompt = f"""Suggest 2-3 labels/tags for this email. Common labels: work, personal, finance, travel, shopping, urgent, follow-up, read-later.

Subject: {subject}
From: {sender}
Content: {content[:300]}

Labels (comma-separated):"""
        
        system_prompt = "You are an email labeling assistant. Suggest relevant, concise labels."
        
        response = self.query_llm(prompt, system_prompt)
        
        # Parse labels
        labels = [l.strip() for l in response.split(',')]
        return labels[:3]  # Max 3 labels
    
    def process_inbox(self, limit=10):
        """
        Process inbox emails with AI analysis
        
        Args:
            limit: Number of emails to process
            
        Returns:
            List of processed email data
        """
        print(f"Processing {limit} emails...\n")
        
        # Mock email data (replace with actual email fetching)
        mock_emails = [
            {
                'subject': 'Urgent: Project deadline tomorrow',
                'sender': 'boss@company.com',
                'content': 'We need to finalize the Q4 report by tomorrow EOD. Please send your section ASAP.'
            },
            {
                'subject': 'Weekly newsletter',
                'sender': 'newsletter@tech.com',
                'content': 'Check out this week\'s top tech news and updates...'
            },
            {
                'subject': 'Meeting notes from yesterday',
                'sender': 'colleague@company.com',
                'content': 'Here are the notes from yesterday\'s meeting. Action items: 1) Review proposal 2) Schedule follow-up'
            }
        ]
        
        processed = []
        
        for i, email in enumerate(mock_emails[:limit]):
            print(f"Processing email {i+1}/{len(mock_emails[:limit])}...")
            
            # Categorize
            category = self.categorize_email(
                email['subject'],
                email['sender'],
                email['content']
            )
            
            # Detect urgency
            urgency, reason = self.detect_urgency(
                email['subject'],
                email['content']
            )
            
            # Extract action items
            actions = self.extract_action_items(email['content'])
            
            # Suggest labels
            labels = self.suggest_labels(
                email['subject'],
                email['sender'],
                email['content']
            )
            
            processed.append({
                'subject': email['subject'],
                'sender': email['sender'],
                'category': category,
                'urgency': urgency,
                'urgency_reason': reason,
                'action_items': actions,
                'labels': labels
            })
            
            print(f"  Category: {category}")
            print(f"  Urgency: {urgency}/10")
            print(f"  Actions: {len(actions)}")
            print(f"  Labels: {', '.join(labels)}\n")
        
        return processed


# Test functionality
if __name__ == "__main__":
    print("=== Email Assistant Test ===\n")
    
    assistant = EmailAssistant()
    
    # Check Ollama
    print("Checking Ollama status...")
    if assistant.check_ollama():
        print("✓ Ollama is running\n")
    else:
        print("✗ Ollama not running. Start with: ollama serve\n")
        exit(1)
    
    # Test email processing
    print("Testing email processing...\n")
    results = assistant.process_inbox(limit=3)
    
    print("\n=== Processing Complete ===\n")
    print(f"Processed {len(results)} emails")
    
    # Show summary
    for i, email in enumerate(results):
        print(f"\nEmail {i+1}:")
        print(f"  Subject: {email['subject']}")
        print(f"  Category: {email['category']}")
        print(f"  Urgency: {email['urgency']}/10")
        if email['action_items']:
            print(f"  Action Items:")
            for action in email['action_items']:
                print(f"    - {action}")

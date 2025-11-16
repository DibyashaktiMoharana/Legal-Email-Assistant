import os
import json
from email_assistant import process_email


def load_file(filename):
    """Load file from project root directory."""
    path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Error: '{filename}' not found in project root.\n"
            f"Please create the file at: {path}"
        )
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    print("=" * 60)
    print("Legal Email Assistant - Demo")
    print("=" * 60)
    
    try:
        # Load sample data
        print("\nLoading sample email and contract...")
        email_text = load_file('sample_email.txt')
        contract_text = load_file('contract_snippet.txt')
        print("✓ Files loaded successfully")
        
        # Process email
        print("\nProcessing email...")
        analysis, reply = process_email(email_text, contract_text)
        
        # Display results
        print("\n" + "=" * 60)
        print("ANALYSIS")
        print("=" * 60)
        print(json.dumps(analysis, indent=2))
        
        print("\n" + "=" * 60)
        print("DRAFT REPLY")
        print("=" * 60)
        print(reply)
        print()
        
    except FileNotFoundError as e:
        print(f"\n{e}")
        print("\nPlease create these files in the project root directory:")
        print("  - sample_email.txt (sample email content)")
        print("  - contract_snippet.txt (relevant contract clauses)")
        print("\nRefer to README.md for file content examples.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

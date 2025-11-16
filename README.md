# Legal Email Assistant

implementation using Gemini API and LangGraph to analyze legal emails and draft professional replies.

## Assumptions

- Email text is provided in plain text format (not HTML)
- Contract clauses are provided as plain text snippets
- Users have valid Gemini API key with sufficient quota
- Email contains identifiable parties, questions, and reference to an agreement
- Contract text contains relevant clauses to answer the questions

## Dependencies

- `langgraph` - Workflow orchestration
- `google-generativeai` - Gemini API client
- `python-dotenv` - Environment variables

## Setup

### 1. Create `.env` file with your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Create sample files in project root

Create these two files directly in the project root (not in a subfolder):

#### `sample_email.txt`:

```
Subject: Termination of Services under MSA

Dear Counsel,

We refer to the Master Services Agreement dated 10 March 2023 between Acme Technologies Pvt. Ltd. ("Acme") and Brightwave Solutions LLP ("Brightwave").

Due to ongoing performance issues and repeated delays in delivery, we are considering termination of the Agreement for cause with effect from 1 December 2025.

Please confirm:
1. Whether we are contractually entitled to terminate for cause on the basis of repeated delays in delivery;
2. The minimum notice period required.

We would appreciate your advice by 18 November 2025.

Regards,
Priya Sharma
Legal Manager, Acme Technologies Pvt. Ltd.
```

#### `contract_snippet.txt`:

```
Clause 9 – Termination for Cause

9.1 Either Party may terminate this Agreement for cause upon thirty (30) days' written notice if the other Party commits a material breach.

9.2 Repeated failure to meet delivery timelines constitutes a material breach.

Clause 10 – Notice

10.1 All notices shall be given in writing and shall be effective upon receipt.

10.2 For termination, minimum thirty (30) days' prior written notice is required.
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the test

```bash
python test.py
```

## Project Structure

```
legal_email_assistant/
├── email_assistant.py          # Main code
├── test_demo.py                 # Test script
├── requirements.txt             # Dependencies
├── .env                         # Your Gemini API key (create this)
├── sample_email.txt             # Sample email (create this)
└── contract_snippet.txt         # Contract clauses (create this)
```

## Architecture

**LangGraph Workflow**: `START → analyze → draft → END`

**Components**:

- `get_llm()` - Initializes Gemini LLM
- `analyze_email()` - Extracts structured information
- `draft_reply()` - Generates professional legal response
- `EmailWorkflow` - LangGraph StateGraph coordinating analysis and drafting

## Usage

```python
from email_assistant import EmailWorkflow

workflow = EmailWorkflow()
analysis, draft_reply = workflow.process_email(email_text, contract_text)
```

## Sample Output

### Part 1: Analysis (JSON)

```json
{
  "intent": "legal_advice_request",
  "primary_topic": "termination_for_cause",
  "parties": {
    "client": "Acme Technologies Pvt. Ltd.",
    "counterparty": "Brightwave Solutions LLP"
  },
  "agreement_reference": {
    "type": "Master Services Agreement",
    "date": "10 March 2023"
  },
  "questions": [
    "Are we contractually entitled to terminate for cause due to repeated delays?",
    "What is the minimum notice period required?"
  ],
  "requested_due_date": "18 November 2025",
  "urgency_level": "medium"
}
```

### Part 2: Draft Reply (Email)

```
Dear Ms. Sharma,

Thank you for your email regarding the Master Services Agreement dated 10 March 2023
between Acme Technologies Pvt. Ltd. and Brightwave Solutions LLP.

Based on our review of the Agreement:

1. **Termination for Cause**: Under Clause 9.2, repeated failure to meet delivery
   timelines constitutes a material breach. Therefore, pursuant to Clause 9.1,
   Acme is contractually entitled to terminate the Agreement for cause.

2. **Notice Period**: Clause 9.1 read with Clause 10.2 requires a minimum of
   thirty (30) days' prior written notice for termination.

Please confirm if you would like us to prepare a formal termination notice for
your review.

Regards,
Your Legal Team
```

## Testing Different Scenarios

To test different legal scenarios, simply edit `sample_email.txt` and `contract_snippet.txt` with your own email and contract content, then run:

```bash
python test.py
```

---

**Author** - Dibyashakti Moharana

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=Dibyashakti&button_colour=FFDD00&font_colour=000000&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/Dibyashakti)

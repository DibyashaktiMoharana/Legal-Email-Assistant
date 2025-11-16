import os
import json
from typing import Dict, Any, Tuple, TypedDict
from dotenv import load_dotenv
import google.generativeai as genai
from langgraph.graph import StateGraph, START, END

load_dotenv()

def get_llm():
    """Initialize Gemini LLM."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash-lite')


class EmailState(TypedDict):
    """State passed between workflow nodes."""
    email_text: str
    contract_text: str
    analysis: Dict[str, Any]
    draft_reply: str
    error: str


ANALYSIS_PROMPT = """You are a legal email analysis expert. Extract structured information from the email.

Return ONLY valid JSON with this exact schema:
{{
  "intent": "string (e.g., legal_advice_request, contract_review, etc.)",
  "primary_topic": "string (main subject)",
  "parties": {{
    "client": "string (our client's name)",
    "counterparty": "string (other party's name)"
  }},
  "agreement_reference": {{
    "type": "string (e.g., Master Services Agreement)",
    "date": "string (date in natural format)"
  }},
  "questions": ["array of questions raised"],
  "requested_due_date": "string (deadline mentioned)",
  "urgency_level": "string (low/medium/high)"
}}

EMAIL TO ANALYZE:
{email_text}

Return ONLY the JSON, no markdown, no explanation."""


def analyze_email(email_text: str, llm) -> Dict[str, Any]:
    """Analyze email and extract structured information."""
    try:
        prompt = ANALYSIS_PROMPT.format(email_text=email_text)
        response = llm.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown formatting if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Clean up any remaining formatting
        response_text = response_text.strip()
        
        return json.loads(response_text)
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON response: {e}")
        print(f"Raw response (first 300 chars): {response_text[:300]}")
        raise
    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        raise


DRAFTING_PROMPT = """You are an expert legal email writer. Draft a professional legal response.

ORIGINAL EMAIL:
{email_text}

ANALYSIS (Structured Information):
{analysis}

RELEVANT CONTRACT CLAUSES:
{contract_text}

REQUIREMENTS:
- Professional legal tone
- Address the sender by name
- Answer all questions clearly
- Reference relevant contract clauses
- Avoid strong commitments or liability
- Write ONLY the email content, no additional commentary

Generate the complete email response now."""


def draft_reply(email_text: str, analysis: Dict[str, Any], contract_text: str, llm) -> str:
    """Draft professional legal email reply."""
    try:
        analysis_text = json.dumps(analysis, indent=2)
        prompt = DRAFTING_PROMPT.format(
            email_text=email_text,
            analysis=analysis_text,
            contract_text=contract_text
        )
        
        response = llm.generate_content(prompt)
        draft = response.text.strip()
        
        # Remove markdown formatting if present
        if draft.startswith("```"):
            lines = draft.split("\n")
            draft = "\n".join(lines[1:-1]) if len(lines) > 2 else draft
        
        return draft
        
    except Exception as e:
        print(f"[ERROR] Drafting failed: {e}")
        raise

class EmailWorkflow:

    def __init__(self):
        self.llm = get_llm()
        self.graph = self._build_graph()
    
    def _analyze_node(self, state: EmailState) -> EmailState:
        try:
            state["analysis"] = analyze_email(state["email_text"], self.llm)
        except Exception as e:
            state["error"] = f"Analysis failed: {str(e)}"
        return state
    
    def _draft_node(self, state: EmailState) -> EmailState:
        if not state.get("error"):
            try:
                state["draft_reply"] = draft_reply(
                    state["email_text"],
                    state["analysis"],
                    state["contract_text"],
                    self.llm
                )
            except Exception as e:
                state["error"] = f"Drafting failed: {str(e)}"
        return state
    
    def _build_graph(self) -> StateGraph:

        graph = StateGraph(EmailState)
        graph.add_node("analyze", self._analyze_node)
        graph.add_node("draft", self._draft_node)
        graph.add_edge(START, "analyze")
        graph.add_edge("analyze", "draft")
        graph.add_edge("draft", END)
        return graph.compile()
    
    def run(self, email_text: str, contract_text: str) -> Tuple[Dict[str, Any], str]:
        final_state = self.graph.invoke(EmailState(
            email_text=email_text,
            contract_text=contract_text,
            analysis={},
            draft_reply="",
            error=""
        ))
        
        if final_state.get("error"):
            raise Exception(final_state["error"])
        
        return final_state["analysis"], final_state["draft_reply"]


def process_email(email_text: str, contract_text: str) -> Tuple[Dict[str, Any], str]:

    workflow = EmailWorkflow()
    return workflow.run(email_text, contract_text)

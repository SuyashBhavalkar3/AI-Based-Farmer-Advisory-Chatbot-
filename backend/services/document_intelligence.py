"""Document intelligence service for analyzing uploaded documents."""

from typing import Dict, List, Any, Optional
from openai import OpenAI
from config.settings import settings
from logger.setup import get_logger
import json

logger = get_logger(__name__)


class DocumentIntelligenceService:
    """AI-powered document analysis and intelligence."""

    def __init__(self):
        """Initialize service."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def analyze_land_document(self, document_text: str) -> Dict[str, Any]:
        """
        Analyze land document for key information and risks.

        Returns:
            {
                "document_type": "Land Title", "Lease Agreement", etc.
                "key_information": extracted key details,
                "important_sections": highlighted sections,
                "risks": identified risks or warnings,
                "missing_items": potentially missing sections,
                "summary": plain-language summary
            }
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a document analysis expert for Indian land and legal documents.
                        Analyze the provided document and extract:
                        1. Document type (Land Title, Lease Agreement, Deed, etc.)
                        2. Key information (owner, area, location, rights, etc.)
                        3. Important sections and clauses
                        4. Potential risks or red flags
                        5. Missing important sections
                        6. Plain-language summary
                        
                        Return JSON with keys: document_type, key_information (dict), important_sections (list),
                        risks (list), missing_items (list), summary (string), legal_warnings (list)""",
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this land document:\n\n{document_text}",
                    },
                ],
                temperature=0.2,
                max_tokens=1500,
            )

            content = response.choices[0].message.content.strip()

            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, create structured response
                analysis = {
                    "document_type": "Unknown",
                    "summary": content,
                    "key_information": {},
                    "important_sections": [],
                    "risks": [],
                    "missing_items": [],
                }

            logger.info(f"Document analyzed: {analysis.get('document_type')}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return {
                "error": "Failed to analyze document",
                "document_type": "Unknown",
            }

    def highlight_important_sections(
        self,
        document_text: str,
        language: str = "en",
    ) -> Dict[str, Any]:
        """Extract and highlight critical sections from document."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Extract and highlight the most important/critical sections from this legal document.
                        Focus on sections that affect farmer's rights, obligations, and financial implications.
                        Return JSON with:
                        - critical_sections: list of important excerpts with explanations
                        - action_items: what the farmer needs to do
                        - important_dates: deadlines and dates mentioned
                        - financial_terms: any monetary obligations or benefits""",
                    },
                    {
                        "role": "user",
                        "content": f"Document:\n\n{document_text}",
                    },
                ],
                temperature=0.2,
                max_tokens=1200,
            )

            content = response.choices[0].message.content.strip()

            try:
                sections = json.loads(content)
            except json.JSONDecodeError:
                sections = {"critical_sections": [content]}

            logger.info(f"Highlighted important sections")
            return sections

        except Exception as e:
            logger.error(f"Error highlighting sections: {str(e)}")
            return {"error": "Failed to highlight sections"}

    def detect_missing_documents(
        self,
        scheme_name: str,
        uploaded_documents: List[str],
    ) -> Dict[str, Any]:
        """
        Detect which documents might be missing for a government scheme.

        Args:
            scheme_name: Name of government scheme
            uploaded_documents: List of document names/types already uploaded

        Returns:
            {
                "scheme": scheme name,
                "required_documents": list of required docs,
                "uploaded_documents": what farmer has,
                "missing_documents": what's missing,
                "recommendations": action plan
            }
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert on Indian government agricultural schemes.
                        List the typical required documents for the given scheme.
                        Compare with what the farmer has uploaded.
                        Return JSON with:
                        - scheme: scheme name
                        - required_documents: list of typical required docs
                        - missing_documents: docs not yet uploaded
                        - document_descriptions: brief desc of each missing doc
                        - where_to_get: guidance on obtaining missing docs""",
                    },
                    {
                        "role": "user",
                        "content": f"Scheme: {scheme_name}\nDocuments uploaded: {', '.join(uploaded_documents)}",
                    },
                ],
                temperature=0.2,
                max_tokens=800,
            )

            content = response.choices[0].message.content.strip()

            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                analysis = {"analysis": content}

            return analysis

        except Exception as e:
            logger.error(f"Error detecting missing documents: {str(e)}")
            return {"error": "Failed to analyze documents"}

    def explain_document_section(
        self,
        document_section: str,
        context: str = "",
    ) -> str:
        """Explain a specific section of a document in simple terms."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Explain this legal/official document section in simple, clear language.
                        - Avoid jargon
                        - Use examples when possible
                        - Highlight what the farmer needs to do
                        - Point out any potential risks or important points""",
                    },
                    {
                        "role": "user",
                        "content": f"Section to explain:\n{document_section}\n\nContext: {context}",
                    },
                ],
                temperature=0.3,
                max_tokens=600,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error explaining section: {str(e)}")
            return "Unable to explain this section."

    def generate_document_checklist(
        self,
        scheme_name: str,
    ) -> Dict[str, Any]:
        """Generate a printable checklist of documents needed for a scheme."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Create a detailed, farmer-friendly checklist for documents needed for this scheme.
                        Include:
                        - Document name
                        - Brief description of what it is
                        - Where to get it (government office, etc.)
                        - Typical processing time if applicable
                        - Cost (if any)
                        
                        Format as a structured checklist.""",
                    },
                    {
                        "role": "user",
                        "content": f"Create document checklist for: {scheme_name}",
                    },
                ],
                temperature=0.2,
                max_tokens=1000,
            )

            return {
                "scheme": scheme_name,
                "checklist": response.choices[0].message.content.strip(),
                "format": "text",
            }

        except Exception as e:
            logger.error(f"Error generating checklist: {str(e)}")
            return {
                "error": "Failed to generate checklist",
            }

    def scan_for_risks(
        self,
        document_text: str,
    ) -> Dict[str, Any]:
        """Scan document for potential legal risks and red flags."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Carefully scan this agricultural/land document for potential risks, red flags, and issues that might harm a farmer.
                        
                        Look for:
                        - Unfavorable terms
                        - Missing protections
                        - Unusual clauses
                        - Potential disputes
                        - Financial risks
                        - Loss of rights
                        
                        Return JSON with:
                        - risk_level: "High", "Medium", "Low"
                        - identified_risks: list of specific risks
                        - severity: high, medium, or low for each risk
                        - recommendations: what farmer should do
                        - seek_legal_help: whether farmer should get legal advice""",
                    },
                    {
                        "role": "user",
                        "content": f"Document:\n\n{document_text}",
                    },
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            content = response.choices[0].message.content.strip()

            try:
                risks = json.loads(content)
            except json.JSONDecodeError:
                risks = {
                    "risk_analysis": content,
                    "seek_legal_help": True,
                }

            logger.info(f"Risk scan completed: {risks.get('risk_level', 'Unknown')}")
            return risks

        except Exception as e:
            logger.error(f"Error scanning for risks: {str(e)}")
            return {
                "error": "Failed to scan document",
            }

"""Conversation intelligence service for summaries, memory, and insights."""

import json
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI
from database.models import (
    Conversation,
    Message,
    ConversationSummary,
    SourceCitation,
)
from config.settings import settings
from logger.setup import get_logger

logger = get_logger(__name__)


class ConversationIntelligenceService:
    """Provide advanced conversation features: memory, summaries, insights."""

    def __init__(self):
        """Initialize with OpenAI client."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_context_messages = 10  # Number of previous messages to use as context

    def generate_conversation_summary(
        self, db: Session, conversation_id: int
    ) -> Optional[ConversationSummary]:
        """Generate AI summary of entire conversation."""
        try:
            # Get all messages
            messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
                .all()
            )

            if not messages:
                logger.warning(f"No messages found for conversation {conversation_id}")
                return None

            # Build conversation text
            conversation_text = self._build_conversation_text(messages)

            # Generate summary
            summary_text = self._generate_summary_via_llm(conversation_text)

            # Extract key topics and schemes
            topics, schemes = self._extract_topics_and_schemes(summary_text)

            # Check if summary already exists and update or create
            existing_summary = (
                db.query(ConversationSummary)
                .filter(ConversationSummary.conversation_id == conversation_id)
                .first()
            )

            if existing_summary:
                existing_summary.summary = summary_text
                existing_summary.key_topics = json.dumps(topics)
                existing_summary.schemes_discussed = json.dumps(schemes)
                db.add(existing_summary)
            else:
                new_summary = ConversationSummary(
                    conversation_id=conversation_id,
                    summary=summary_text,
                    key_topics=json.dumps(topics),
                    schemes_discussed=json.dumps(schemes),
                )
                db.add(new_summary)

            db.commit()
            logger.info(f"Summary generated for conversation {conversation_id}")
            return existing_summary or new_summary

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None

    def _build_conversation_text(self, messages: List[Message]) -> str:
        """Build readable conversation text from messages."""
        text_parts = []
        for msg in messages:
            role = "Farmer" if msg.role == "user" else "Advisor"
            text_parts.append(f"{role}: {msg.content}")
        return "\n\n".join(text_parts)

    def _generate_summary_via_llm(self, conversation_text: str) -> str:
        """Generate summary using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an AI assistant that summarizes farmer advisory conversations.
                        Create a concise, factual summary focusing on:
                        1. Main topics discussed
                        2. Government schemes mentioned
                        3. Key advice given
                        4. Action items for the farmer
                        
                        Keep summary to 3-4 paragraphs maximum.""",
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize this conversation:\n\n{conversation_text}",
                    },
                ],
                temperature=0.3,
                max_tokens=500,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error in LLM summarization: {str(e)}")
            return "Unable to generate summary"

    def _extract_topics_and_schemes(self, summary: str) -> tuple:
        """Extract key topics and scheme mentions from summary."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Extract topics and government schemes from the text.
                        Return JSON with 'topics' (list) and 'schemes' (list).
                        Examples of topics: crop_advisory, land_rights, insurance, water_management, etc.""",
                    },
                    {"role": "user", "content": summary},
                ],
                temperature=0.1,
                max_tokens=200,
            )

            content = response.choices[0].message.content.strip()

            # Try to parse JSON
            try:
                data = json.loads(content)
                return data.get("topics", []), data.get("schemes", [])
            except json.JSONDecodeError:
                # Fallback if not valid JSON
                return [], []

        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            return [], []

    def add_source_citation(
        self,
        db: Session,
        message_id: int,
        source_text: str,
        document_name: Optional[str] = None,
        confidence_score: Optional[int] = None,
    ) -> SourceCitation:
        """Add source citation to a message."""
        try:
            citation = SourceCitation(
                message_id=message_id,
                source_text=source_text,
                document_name=document_name,
                confidence_score=min(100, max(0, confidence_score)) if confidence_score else None,
            )
            db.add(citation)
            db.commit()
            db.refresh(citation)
            logger.info(f"Citation added for message {message_id}")
            return citation

        except Exception as e:
            logger.error(f"Error adding citation: {str(e)}")
            db.rollback()
            raise

    def get_suggested_follow_up_questions(
        self, conversation_id: int, db: Session
    ) -> List[str]:
        """Generate smart follow-up questions based on conversation."""
        try:
            # Get last 3 messages for context
            messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(3)
                .all()
            )

            if not messages:
                return []

            # Build context
            context = " ".join([msg.content for msg in reversed(messages)])

            # Generate follow-ups
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Generate 3 smart follow-up questions that a farmer might ask next.
                        Questions should be:
                        - Practical and actionable
                        - Related to the conversation context
                        - Progressive (building on previous discussion)
                        
                        Return only questions, one per line.""",
                    },
                    {"role": "user", "content": context},
                ],
                temperature=0.7,
                max_tokens=200,
            )

            questions = response.choices[0].message.content.strip().split("\n")
            # Clean and filter questions
            questions = [
                q.strip().lstrip("•-•●○").strip() 
                for q in questions 
                if q.strip()
            ][:3]
            
            logger.info(f"Generated {len(questions)} follow-up questions")
            return questions

        except Exception as e:
            logger.error(f"Error generating follow-ups: {str(e)}")
            return []

    def simplify_for_low_literacy(self, text: str, language: str = "en") -> str:
        """Simplify text for low-literacy users."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""Simplify this text for a farmer with basic literacy.
                        Use simple words, short sentences, and practical examples.
                        Translate to {language} if needed.
                        Maintain accuracy but make it easy to understand.""",
                    },
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=len(text.split()) * 2,  # Allow some expansion
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error simplifying text: {str(e)}")
            return text

    def legally_simplify(self, legal_text: str) -> str:
        """Simplify legal/policy text into plain language."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Simplify legal/policy text into plain language.
                        - Explain each clause in simple terms
                        - Highlight what the farmer must do
                        - Point out important deadlines or conditions
                        - Use bullet points for clarity""",
                    },
                    {"role": "user", "content": legal_text},
                ],
                temperature=0.2,
                max_tokens=len(legal_text.split()) * 2,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error in legal simplification: {str(e)}")
            return legal_text

    def get_conversation_context(
        self, db: Session, conversation_id: int, exclude_current_message: bool = True
    ) -> str:
        """
        Retrieve previous messages as context for the current query.
        
        Args:
            db: Database session
            conversation_id: ID of the conversation
            exclude_current_message: If True, exclude the last user message (current query)
        
        Returns:
            Formatted string with conversation history for context
        """
        try:
            # Get last N messages (excluding the most recent for context building)
            query = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
            )
            
            # Get extra message if we need to exclude the current
            limit = self.max_context_messages + (1 if exclude_current_message else 0)
            messages = query.limit(limit).all()
            
            if not messages:
                return ""
            
            # Exclude current message if requested
            if exclude_current_message and messages:
                messages = messages[1:]  # Skip the most recent (current query)
            
            if not messages:
                return ""
            
            # Reverse to get chronological order
            messages = list(reversed(messages))
            
            # Build context string
            context_parts = []
            for msg in messages:
                role = "Farmer" if msg.role == "user" else "Agricultural Advisor"
                context_parts.append(f"{role}: {msg.content}")
            
            context_string = "\n\n".join(context_parts)
            logger.debug(f"Built conversation context with {len(messages)} previous messages")
            
            return context_string
        
        except Exception as e:
            logger.error(f"Error retrieving conversation context: {str(e)}")
            return ""

    def format_context_for_prompt(
        self, conversation_context: str, rag_context: str
    ) -> str:
        """
        Format conversation history and RAG context for inclusion in LLM prompt.
        
        Args:
            conversation_context: Previous messages in the conversation
            rag_context: Retrieved documents from RAG
        
        Returns:
            Formatted context string for the prompt
        """
        parts = []
        
        if conversation_context.strip():
            parts.append("## Conversation History\n" + conversation_context)
        
        if rag_context.strip():
            parts.append("## Relevant Information from Knowledge Base\n" + rag_context)
        
        return "\n\n".join(parts)

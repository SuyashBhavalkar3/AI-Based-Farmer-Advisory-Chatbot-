"""Analytics and insights service for user behavior and trends."""

from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database.models import (
    User,
    Conversation,
    Message,
    UserInsight,
    ConversationSummary,
)
from logger.setup import get_logger
from datetime import datetime, timedelta
import json

logger = get_logger(__name__)


class AnalyticsService:
    """Provide analytics and insights about user behavior."""

    @staticmethod
    def update_user_insights(db: Session, user_id: int) -> UserInsight:
        """Update user insights based on activity."""
        try:
            # Get or create insight record
            insight = db.query(UserInsight).filter(
                UserInsight.user_id == user_id
            ).first()

            if not insight:
                insight = UserInsight(user_id=user_id)

            # Calculate statistics
            conversation_count = (
                db.query(func.count(Conversation.id))
                .filter(Conversation.user_id == user_id, Conversation.is_deleted == False)
                .scalar()
            )

            message_count = (
                db.query(func.count(Message.id))
                .join(Conversation)
                .filter(Conversation.user_id == user_id)
                .scalar()
            )

            # Get most asked scheme (from summaries)
            most_asked_scheme = AnalyticsService._find_most_mentioned_scheme(
                db, user_id
            )

            # Determine primary interest
            primary_interest = AnalyticsService._determine_primary_interest(
                db, user_id
            )

            # Get preferred language
            preferred_language = (
                db.query(Conversation.language)
                .filter(Conversation.user_id == user_id)
                .group_by(Conversation.language)
                .order_by(desc(func.count(Conversation.id)))
                .first()
            )

            # Update insight
            insight.total_conversations = conversation_count
            insight.total_messages = message_count
            insight.most_asked_scheme = most_asked_scheme
            insight.primary_interest = primary_interest
            insight.preferred_language = (
                preferred_language[0] if preferred_language else "en"
            )
            insight.last_active = datetime.utcnow()

            db.add(insight)
            db.commit()
            db.refresh(insight)

            logger.info(f"Updated insights for user {user_id}")
            return insight

        except Exception as e:
            logger.error(f"Error updating insights: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def _find_most_mentioned_scheme(db: Session, user_id: int) -> str:
        """Find most frequently mentioned scheme in user's conversations."""
        try:
            summaries = (
                db.query(ConversationSummary.schemes_discussed)
                .join(Conversation)
                .filter(Conversation.user_id == user_id)
                .all()
            )

            if not summaries:
                return None

            scheme_counts = {}
            for summary in summaries:
                if summary.schemes_discussed:
                    try:
                        schemes = json.loads(summary.schemes_discussed)
                        for scheme in schemes:
                            scheme_counts[scheme] = scheme_counts.get(scheme, 0) + 1
                    except json.JSONDecodeError:
                        pass

            if scheme_counts:
                return max(scheme_counts, key=scheme_counts.get)

            return None

        except Exception as e:
            logger.error(f"Error finding most mentioned scheme: {str(e)}")
            return None

    @staticmethod
    def _determine_primary_interest(db: Session, user_id: int) -> str:
        """Determine primary interest based on conversation topics."""
        try:
            summaries = (
                db.query(ConversationSummary.key_topics)
                .join(Conversation)
                .filter(Conversation.user_id == user_id)
                .all()
            )

            if not summaries:
                return "general_advisory"

            topic_counts = {}
            for summary in summaries:
                if summary.key_topics:
                    try:
                        topics = json.loads(summary.key_topics)
                        for topic in topics:
                            topic_counts[topic] = topic_counts.get(topic, 0) + 1
                    except json.JSONDecodeError:
                        pass

            if topic_counts:
                return max(topic_counts, key=topic_counts.get)

            return "general_advisory"

        except Exception as e:
            logger.error(f"Error determining primary interest: {str(e)}")
            return "general_advisory"

    @staticmethod
    def get_user_dashboard(db: Session, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user dashboard data."""
        try:
            insight = db.query(UserInsight).filter(
                UserInsight.user_id == user_id
            ).first()

            # Get conversation metrics
            conversations = db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.is_deleted == False,
            )

            total_conversations = conversations.count()

            recent_conversations = conversations.order_by(
                Conversation.created_at.desc()
            ).limit(5).all()

            # Get message statistics
            messages = (
                db.query(Message)
                .join(Conversation)
                .filter(Conversation.user_id == user_id)
            )

            total_messages = messages.count()
            avg_messages_per_conversation = (
                total_messages / total_conversations if total_conversations > 0 else 0
            )

            # Get activity last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            activity_last_week = (
                db.query(func.count(Message.id))
                .join(Conversation)
                .filter(
                    Conversation.user_id == user_id,
                    Message.created_at >= week_ago,
                )
                .scalar()
            )

            return {
                "user_id": user_id,
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "avg_messages_per_conversation": round(
                    avg_messages_per_conversation, 2
                ),
                "activity_last_7_days": activity_last_week,
                "most_asked_scheme": insight.most_asked_scheme if insight else None,
                "primary_interest": insight.primary_interest if insight else None,
                "preferred_language": insight.preferred_language if insight else "en",
                "last_active": insight.last_active.isoformat() if insight and insight.last_active else None,
                "recent_conversations": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "created_at": c.created_at.isoformat(),
                        "message_count": len(c.messages),
                    }
                    for c in recent_conversations
                ],
            }

        except Exception as e:
            logger.error(f"Error building dashboard: {str(e)}")
            return {}

    @staticmethod
    def get_global_trends(db: Session) -> Dict[str, Any]:
        """Get global trends across all users (for admin dashboard)."""
        try:
            # Most discussed schemes
            all_summaries = db.query(ConversationSummary).all()

            scheme_counts = {}
            topic_counts = {}

            for summary in all_summaries:
                if summary.schemes_discussed:
                    try:
                        schemes = json.loads(summary.schemes_discussed)
                        for scheme in schemes:
                            scheme_counts[scheme] = scheme_counts.get(scheme, 0) + 1
                    except json.JSONDecodeError:
                        pass

                if summary.key_topics:
                    try:
                        topics = json.loads(summary.key_topics)
                        for topic in topics:
                            topic_counts[topic] = topic_counts.get(topic, 0) + 1
                    except json.JSONDecodeError:
                        pass

            # User statistics
            total_users = db.query(User).filter(User.is_active == True).count()
            total_conversations = db.query(Conversation).filter(
                Conversation.is_deleted == False
            ).count()
            total_messages = db.query(Message).count()

            return {
                "total_users": total_users,
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "avg_messages_per_conversation": (
                    total_messages / total_conversations if total_conversations > 0 else 0
                ),
                "trending_schemes": sorted(
                    scheme_counts.items(), key=lambda x: x[1], reverse=True
                )[:10],
                "trending_topics": sorted(
                    topic_counts.items(), key=lambda x: x[1], reverse=True
                )[:10],
                "languages_used": AnalyticsService._get_language_distribution(db),
            }

        except Exception as e:
            logger.error(f"Error getting global trends: {str(e)}")
            return {}

    @staticmethod
    def _get_language_distribution(db: Session) -> Dict[str, int]:
        """Get distribution of languages used."""
        try:
            distribution = (
                db.query(
                    Conversation.language,
                    func.count(Conversation.id),
                )
                .group_by(Conversation.language)
                .all()
            )

            return {lang: count for lang, count in distribution}

        except Exception as e:
            logger.error(f"Error getting language distribution: {str(e)}")
            return {}

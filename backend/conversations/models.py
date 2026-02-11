"""Conversation models."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

# Note: These models are consolidated in database/models.py
# This file is kept for import convenience if needed

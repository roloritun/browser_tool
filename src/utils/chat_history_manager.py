#!/usr/bin/env python3
"""
Chat History Manager
===================

Utility for managing and summarizing chat history to prevent context length exceeded errors
in browser automation demos and agent executions.

This module provides functionality to:
- Track conversation history between agent executions
- Summarize long conversations to maintain context while reducing token count
- Manage multiple scenario conversations
- Provide token counting and optimization
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import tiktoken  # Use tiktoken for OpenAI-compatible token counting

logger = logging.getLogger(__name__)

@dataclass
class ConversationEntry:
    """Single conversation entry with metadata"""
    timestamp: datetime
    role: str  # 'human', 'assistant', 'system'
    content: str
    scenario: str = ""
    tokens: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "role": self.role,
            "content": self.content,
            "scenario": self.scenario,
            "tokens": self.tokens
        }

@dataclass
class ChatHistoryManager:
    """Manages chat history with summarization capabilities"""
    
    max_total_tokens: int = 500  # EXTREMELY aggressive token limit (was 1000)
    max_entries_before_summarization: int = 1  # Summarize after EVERY entry (was 2)
    summary_target_tokens: int = 150  # Ultra-low summary target (was 300)
    conversation_history: List[ConversationEntry] = field(default_factory=list)
    summarized_history: str = ""
    llm: Optional[AzureChatOpenAI] = None
    
    def __post_init__(self):
        """Initialize the chat history manager"""
        if not self.llm:
            # Initialize a lightweight LLM for summarization
            import os
            self.llm = AzureChatOpenAI(
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-07-01-preview"),
                temperature=0.0,  # Deterministic summarization
                max_tokens=1000   # Conservative for summarization
            )
    
    def estimate_tokens(self, text: str) -> int:
        """Accurate token estimation using tiktoken for OpenAI models (gpt-4)"""
        try:
            enc = tiktoken.encoding_for_model("gpt-4")
            return len(enc.encode(text))
        except Exception:
            return len(text) // 4  # Fallback
    
    def add_conversation_entry(
        self, 
        role: str, 
        content: str, 
        scenario: str = ""
    ) -> None:
        """Add a conversation entry to the history with aggressive truncation"""
        # AGGRESSIVE CONTENT TRUNCATION to prevent large entries
        max_content_length = 1000  # Drastically limit individual entry size
        if len(content) > max_content_length:
            content = content[:max_content_length] + "... [TRUNCATED]"
            logger.warning(f"Content truncated from {len(content)} to {max_content_length} characters")
        
        entry = ConversationEntry(
            timestamp=datetime.now(),
            role=role,
            content=content,
            scenario=scenario,
            tokens=self.estimate_tokens(content)
        )
        
        self.conversation_history.append(entry)
        logger.debug(f"Added conversation entry: {role} ({entry.tokens} tokens)")
        
        # Check if summarization is needed - now triggers much more aggressively
        if self._needs_summarization():
            self._summarize_history()
    
    def _needs_summarization(self) -> bool:
        """Check if chat history needs summarization"""
        total_tokens = self._get_total_tokens()
        entry_count = len(self.conversation_history)
        
        return (
            total_tokens > self.max_total_tokens or 
            entry_count > self.max_entries_before_summarization
        )
    
    def _get_total_tokens(self) -> int:
        """Calculate total tokens in conversation history"""
        history_tokens = sum(entry.tokens for entry in self.conversation_history)
        summary_tokens = self.estimate_tokens(self.summarized_history)
        return history_tokens + summary_tokens
    
    def _summarize_history(self) -> None:
        """Summarize the conversation history to reduce token count"""
        if not self.conversation_history:
            return
        
        logger.info("🔄 Summarizing chat history to prevent context overflow...")
        
        try:
            # Prepare conversation for summarization
            conversation_text = self._format_conversation_for_summarization()
            
            # Create summarization prompt - ULTRA CONCISE
            summarization_prompt = f"""Provide a 50-word summary of this browser automation session focusing only on:
1. Current task/scenario
2. Key achievements 
3. Next steps

Conversation:
{conversation_text}

Ultra-concise summary (max 50 words):"""

            # Get summary from LLM
            messages = [
                SystemMessage(content="Create ultra-concise 50-word summaries of browser automation sessions."),
                HumanMessage(content=summarization_prompt)
            ]
            
            response = self.llm.invoke(messages)
            new_summary = response.content.strip()
            
            # Combine with existing summary if any - but keep it SHORT
            if self.summarized_history:
                combined_summary = f"Previous: {self.summarized_history}\nRecent: {new_summary}"
                
                # ALWAYS re-summarize if we have existing history to keep it minimal
                if self.estimate_tokens(combined_summary) > self.summary_target_tokens:
                    final_prompt = f"""Create a single 30-word summary:\n{combined_summary}\n\n30-word summary:"""
                    
                    final_messages = [
                        SystemMessage(content="Create 30-word summaries only."),
                        HumanMessage(content=final_prompt)
                    ]
                    
                    final_response = self.llm.invoke(final_messages)
                    self.summarized_history = final_response.content.strip()
                else:
                    self.summarized_history = combined_summary
            else:
                self.summarized_history = new_summary
            
            # Keep NO recent entries for maximum reduction (was 1)
            self.conversation_history.clear()  # COMPLETELY CLEAR
            
            summary_tokens = self.estimate_tokens(self.summarized_history)
            remaining_tokens = sum(entry.tokens for entry in self.conversation_history)
            
            logger.info(f"✅ Chat history summarized: {summary_tokens} summary tokens + {remaining_tokens} recent tokens")
        
        except Exception as e:
            logger.warning(f"⚠️ Failed to summarize chat history: {e}")
            # Fallback: CLEAR EVERYTHING to prevent context overflow
            self.conversation_history.clear()
            self.summarized_history = "Previous session context cleared due to error."
    
    def _format_conversation_for_summarization(self) -> str:
        """Format conversation history for summarization"""
        formatted_entries = []
        
        for entry in self.conversation_history:
            timestamp = entry.timestamp.strftime("%H:%M:%S")
            scenario_info = f" [{entry.scenario}]" if entry.scenario else ""
            formatted_entries.append(f"[{timestamp}]{scenario_info} {entry.role.capitalize()}: {entry.content}")
        
        return "\n".join(formatted_entries)
    
    def get_formatted_history(self) -> str:
        """Get formatted chat history for agent consumption - MINIMAL VERSION"""
        formatted_parts = []
        
        # Add summarized history if available - keep it short
        if self.summarized_history:
            # Truncate summary if too long
            summary = self.summarized_history
            if self.estimate_tokens(summary) > 100:  # Even stricter limit
                summary = summary[:400] + "..."
            formatted_parts.append(f"Context: {summary}")
        
        # NO recent conversation history - only summary for minimal tokens
        # This is the most aggressive approach to prevent context overflow
        
        return "\n".join(formatted_parts) if formatted_parts else "Starting fresh session."
    
    def add_scenario_start(self, scenario_name: str, task_description: str) -> None:
        """Mark the start of a new scenario"""
        self.add_conversation_entry(
            role="system",
            content=f"Starting scenario: {scenario_name}\nTask: {task_description}",
            scenario=scenario_name
        )
    
    def add_scenario_result(self, scenario_name: str, success: bool, result: str = "") -> None:
        """Mark the completion of a scenario"""
        status = "SUCCESS" if success else "FAILED"
        content = f"Scenario {scenario_name} completed with status: {status}"
        if result:
            content += f"\nResult: {result}"
        
        self.add_conversation_entry(
            role="system",
            content=content,
            scenario=scenario_name
        )
    
    def add_agent_invocation(self, task: str, result: Dict[str, Any], scenario: str = "") -> None:
        """Add an agent invocation and its result to the history"""
        # Add the task
        self.add_conversation_entry(
            role="human",
            content=f"Task: {task}",
            scenario=scenario
        )
        
        # Add the result
        output = result.get("output", "")
        error = result.get("error", "")
        
        if error:
            content = f"Error: {error}"
        else:
            content = f"Result: {output}"
        
        self.add_conversation_entry(
            role="assistant",
            content=content,
            scenario=scenario
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the chat history"""
        total_entries = len(self.conversation_history)
        total_tokens = self._get_total_tokens()
        
        return {
            "total_entries": total_entries,
            "total_tokens": total_tokens,
            "summarized_history_tokens": self.estimate_tokens(self.summarized_history),
            "recent_entries_tokens": sum(entry.tokens for entry in self.conversation_history),
            "has_summary": bool(self.summarized_history),
            "memory_pressure": total_tokens > (self.max_total_tokens * 0.8)
        }
    
    def clear_history(self) -> None:
        """Clear all chat history"""
        self.conversation_history.clear()
        self.summarized_history = ""
        logger.info("🧹 Chat history cleared")
    
    def export_history(self) -> Dict[str, Any]:
        """Export chat history for debugging/analysis"""
        return {
            "summarized_history": self.summarized_history,
            "conversation_history": [entry.to_dict() for entry in self.conversation_history],
            "stats": self.get_stats(),
            "exported_at": datetime.now().isoformat()
        }
    
    def emergency_context_check(self, max_safe_tokens: int = 2000) -> str:
        """EMERGENCY: Check context size and force minimal context if needed"""
        current_history = self.get_formatted_history()
        current_tokens = self.estimate_tokens(current_history)
        
        logger.info(f"🚨 Emergency context check: {current_tokens} tokens (max safe: {max_safe_tokens})")
        
        if current_tokens > max_safe_tokens:
            logger.warning(f"⚠️ EMERGENCY CONTEXT REDUCTION: {current_tokens} > {max_safe_tokens} tokens")
            
            # EMERGENCY: Clear everything and provide minimal context
            self.conversation_history.clear()
            self.summarized_history = "Emergency context reset - previous session cleared to prevent overflow."
            
            emergency_context = "Starting fresh due to context overflow prevention."
            logger.warning(f"🔥 EMERGENCY CONTEXT ACTIVE: {self.estimate_tokens(emergency_context)} tokens")
            return emergency_context
        
        return current_history

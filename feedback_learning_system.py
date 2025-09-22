#!/usr/bin/env python3
"""
Feedback Learning System for Jira-Figma Analyzer

This module learns from user feedback to continuously improve question generation quality.
It analyzes patterns in feedback to enhance AI prompts and question relevance.
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from feedback_system import FeedbackSystem
import statistics
from datetime import datetime

@dataclass
class LearningInsight:
    """Insights learned from user feedback."""
    insight_type: str  # 'prompt_improvement', 'topic_focus', 'question_pattern'
    confidence: float  # 0-1
    description: str
    action: str
    supporting_data: Dict[str, Any]

class FeedbackLearningSystem:
    """System that learns from feedback to improve question generation."""
    
    def __init__(self, feedback_system: FeedbackSystem):
        """Initialize the learning system."""
        self.feedback_system = feedback_system
        self.learning_storage = Path("learning_insights")
        self.learning_storage.mkdir(exist_ok=True)
        
        print("🧠 Feedback Learning System initialized")
    
    def analyze_feedback_patterns(self) -> List[LearningInsight]:
        """Analyze feedback patterns to generate learning insights."""
        insights = []
        
        # Analyze low-rated questions
        low_rated_insights = self._analyze_low_rated_questions()
        insights.extend(low_rated_insights)
        
        # Analyze topic-specific performance
        topic_insights = self._analyze_topic_performance()
        insights.extend(topic_insights)
        
        # Analyze comment patterns
        comment_insights = self._analyze_comment_patterns()
        insights.extend(comment_insights)
        
        # Save insights for future reference
        self._save_insights(insights)
        
        return insights
    
    def _analyze_low_rated_questions(self) -> List[LearningInsight]:
        """Analyze patterns in low-rated questions."""
        insights = []
        low_rated = self.feedback_system.get_low_rated_items(threshold=3)
        
        if len(low_rated) >= 3:  # Need sufficient data
            # Common themes in low-rated questions
            low_rated_topics = []
            generic_count = 0
            
            for item in low_rated:
                if 'questions' in item.get('analysis_type', ''):
                    # Analyze if questions are too generic
                    comment = item.get('comment', '').lower()
                    if any(word in comment for word in ['generic', 'basic', 'obvious', 'not specific']):
                        generic_count += 1
                    
                    # Extract topics from ticket titles
                    title = item.get('ticket_title', '').lower()
                    for topic in ['payment', 'auth', 'ui', 'api', 'database', 'chat', 'profile']:
                        if topic in title:
                            low_rated_topics.append(topic)
            
            # Generate insights based on patterns
            if generic_count >= 2:
                insights.append(LearningInsight(
                    insight_type="prompt_improvement",
                    confidence=0.8,
                    description="Users frequently rate questions as too generic",
                    action="Enhance AI prompts to generate more specific, context-aware questions",
                    supporting_data={"generic_complaints": generic_count, "total_low_rated": len(low_rated)}
                ))
            
            # Topic-specific low performance
            if low_rated_topics:
                topic_counts = {}
                for topic in low_rated_topics:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
                
                for topic, count in topic_counts.items():
                    if count >= 2:
                        insights.append(LearningInsight(
                            insight_type="topic_focus",
                            confidence=0.7,
                            description=f"Questions for {topic}-related tickets consistently low-rated",
                            action=f"Improve {topic}-specific question generation with better domain knowledge",
                            supporting_data={"topic": topic, "low_rated_count": count}
                        ))
        
        return insights
    
    def _analyze_topic_performance(self) -> List[LearningInsight]:
        """Analyze performance by topic areas."""
        insights = []
        summary = self.feedback_system.get_feedback_summary()
        
        # Look for topics with consistently low ratings
        for topic, data in summary.topic_specific_feedback.items():
            if data['average_rating'] < 3.0 and data['total_feedback'] >= 3:
                insights.append(LearningInsight(
                    insight_type="topic_focus",
                    confidence=0.8,
                    description=f"Topic '{topic}' has low average rating ({data['average_rating']:.1f}/5)",
                    action=f"Review and enhance question generation for {topic} domain",
                    supporting_data={"topic": topic, "rating": data['average_rating'], "count": data['total_feedback']}
                ))
        
        return insights
    
    def _analyze_comment_patterns(self) -> List[LearningInsight]:
        """Analyze patterns in user comments for improvement opportunities."""
        insights = []
        
        # Get all feedback with comments
        with sqlite3.connect(self.feedback_system.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT comment, rating, analysis_type, ticket_title 
                FROM feedback 
                WHERE comment IS NOT NULL AND comment != ''
                ORDER BY timestamp DESC
                LIMIT 50
            """)
            
            comments_data = cursor.fetchall()
        
        if not comments_data:
            return insights
        
        # Analyze comment patterns
        improvement_keywords = ['missing', 'should ask', 'need', 'important', 'forgot']
        generic_keywords = ['generic', 'basic', 'obvious', 'too simple']
        relevance_keywords = ['not relevant', 'irrelevant', 'wrong focus', 'off topic']
        
        improvement_mentions = 0
        generic_mentions = 0
        relevance_mentions = 0
        
        for comment, rating, analysis_type, title in comments_data:
            comment_lower = comment.lower()
            
            if any(keyword in comment_lower for keyword in improvement_keywords):
                improvement_mentions += 1
            if any(keyword in comment_lower for keyword in generic_keywords):
                generic_mentions += 1
            if any(keyword in comment_lower for keyword in relevance_keywords):
                relevance_mentions += 1
        
        # Generate insights based on comment patterns
        total_comments = len(comments_data)
        
        if improvement_mentions >= 3:
            insights.append(LearningInsight(
                insight_type="question_pattern",
                confidence=0.7,
                description=f"Users suggest missing questions in {improvement_mentions}/{total_comments} comments",
                action="Expand question coverage and add more comprehensive question templates",
                supporting_data={"improvement_mentions": improvement_mentions, "total_comments": total_comments}
            ))
        
        if generic_mentions >= 3:
            insights.append(LearningInsight(
                insight_type="prompt_improvement",
                confidence=0.8,
                description=f"Users complain about generic questions in {generic_mentions}/{total_comments} comments",
                action="Enhance AI prompts with more specific context and domain knowledge",
                supporting_data={"generic_mentions": generic_mentions, "total_comments": total_comments}
            ))
        
        if relevance_mentions >= 2:
            insights.append(LearningInsight(
                insight_type="question_pattern",
                confidence=0.7,
                description=f"Users report irrelevant questions in {relevance_mentions}/{total_comments} comments",
                action="Improve topic detection and question filtering for better relevance",
                supporting_data={"relevance_mentions": relevance_mentions, "total_comments": total_comments}
            ))
        
        return insights
    
    def _save_insights(self, insights: List[LearningInsight]):
        """Save learning insights for future reference."""
        insights_file = self.learning_storage / "feedback_insights.json"
        
        insights_data = []
        for insight in insights:
            insights_data.append({
                "insight_type": insight.insight_type,
                "confidence": insight.confidence,
                "description": insight.description,
                "action": insight.action,
                "supporting_data": insight.supporting_data,
                "timestamp": str(datetime.now())
            })
        
        with open(insights_file, 'w') as f:
            json.dump(insights_data, f, indent=2)
    
    def get_question_generation_improvements(self) -> Dict[str, Any]:
        """Get specific improvements for question generation based on feedback."""
        insights = self.analyze_feedback_patterns()
        
        improvements = {
            "prompt_enhancements": [],
            "topic_specific_improvements": {},
            "question_pattern_changes": [],
            "overall_recommendations": []
        }
        
        for insight in insights:
            if insight.insight_type == "prompt_improvement":
                improvements["prompt_enhancements"].append({
                    "description": insight.description,
                    "action": insight.action,
                    "confidence": insight.confidence
                })
            
            elif insight.insight_type == "topic_focus":
                topic = insight.supporting_data.get("topic", "general")
                improvements["topic_specific_improvements"][topic] = {
                    "issue": insight.description,
                    "action": insight.action,
                    "confidence": insight.confidence
                }
            
            elif insight.insight_type == "question_pattern":
                improvements["question_pattern_changes"].append({
                    "description": insight.description,
                    "action": insight.action,
                    "confidence": insight.confidence
                })
        
        # Generate overall recommendations
        if len(insights) >= 3:
            improvements["overall_recommendations"].append(
                "Multiple feedback patterns detected - consider comprehensive review of question generation system"
            )
        
        summary = self.feedback_system.get_feedback_summary()
        if summary.average_rating < 3.5:
            improvements["overall_recommendations"].append(
                f"Overall rating ({summary.average_rating:.1f}/5) below threshold - prioritize quality improvements"
            )
        
        return improvements
    
    def generate_enhanced_prompt_context(self, ticket_topics: List[str]) -> str:
        """Generate enhanced prompt context based on feedback learning."""
        improvements = self.get_question_generation_improvements()
        
        context_additions = []
        
        # Add prompt enhancements
        for enhancement in improvements["prompt_enhancements"]:
            if enhancement["confidence"] >= 0.7:
                context_additions.append(f"- {enhancement['action']}")
        
        # Add topic-specific improvements
        for topic in ticket_topics:
            if topic in improvements["topic_specific_improvements"]:
                improvement = improvements["topic_specific_improvements"][topic]
                if improvement["confidence"] >= 0.7:
                    context_additions.append(f"- For {topic}: {improvement['action']}")
        
        # Add question pattern improvements
        for pattern in improvements["question_pattern_changes"]:
            if pattern["confidence"] >= 0.7:
                context_additions.append(f"- {pattern['action']}")
        
        if context_additions:
            return "\n\nFEEDBACK-DRIVEN IMPROVEMENTS:\n" + "\n".join(context_additions)
        
        return ""

# Example usage and testing
if __name__ == "__main__":
    # Test the learning system
    feedback_system = FeedbackSystem()
    learning_system = FeedbackLearningSystem(feedback_system)
    
    insights = learning_system.analyze_feedback_patterns()
    improvements = learning_system.get_question_generation_improvements()
    
    print("🧠 Learning Insights:")
    for insight in insights:
        print(f"  • {insight.description} (confidence: {insight.confidence:.1f})")
    
    print("\n🔧 Improvements:")
    for category, items in improvements.items():
        if items:
            print(f"  {category}: {len(items) if isinstance(items, list) else len(items) if isinstance(items, dict) else items}") 
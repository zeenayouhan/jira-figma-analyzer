#!/usr/bin/env python3
"""
Feedback System for Jira-Figma Analyzer

This module handles collection and analysis of user feedback on the quality
of generated questions, test cases, and analysis results.
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics

@dataclass
class Feedback:
    """User feedback on analysis results."""
    feedback_id: str
    ticket_id: str
    analysis_type: str  # 'questions', 'test_cases', 'business_questions', 'design_questions', 'risks'
    rating: int  # 1-5 scale
    comment: str
    user_id: Optional[str]
    timestamp: str
    
    # Specific feedback details
    helpful_items: List[str]  # Which questions/items were helpful
    unhelpful_items: List[str]  # Which questions/items were not helpful
    missing_topics: List[str]  # What topics/questions were missing
    
    # Context
    ticket_title: str
    ticket_description: str
    detected_topics: List[str]

@dataclass
class FeedbackSummary:
    """Summary of feedback for analysis improvement."""
    total_feedback: int
    average_rating: float
    rating_distribution: Dict[int, int]
    common_complaints: List[str]
    common_praises: List[str]
    improvement_suggestions: List[str]
    topic_specific_feedback: Dict[str, Dict[str, Any]]

class FeedbackSystem:
    """Main class for collecting and analyzing user feedback."""
    
    def __init__(self, storage_dir: str = "feedback_storage"):
        """Initialize the feedback system."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.db_path = self.storage_dir / "feedback.db"
        self._init_database()
        
        print("📝 Feedback System initialized")
    
    def _init_database(self):
        """Initialize the feedback database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    ticket_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    user_id TEXT,
                    timestamp TEXT NOT NULL,
                    helpful_items TEXT,  -- JSON array
                    unhelpful_items TEXT,  -- JSON array
                    missing_topics TEXT,  -- JSON array
                    ticket_title TEXT,
                    ticket_description TEXT,
                    detected_topics TEXT  -- JSON array
                )
            ''')
            
            # Analysis improvements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS improvements (
                    improvement_id TEXT PRIMARY KEY,
                    feedback_id TEXT,
                    improvement_type TEXT,
                    description TEXT,
                    implemented BOOLEAN DEFAULT FALSE,
                    timestamp TEXT,
                    FOREIGN KEY (feedback_id) REFERENCES feedback (feedback_id)
                )
            ''')
            
            conn.commit()
    
    def collect_feedback(
        self,
        ticket_id: str,
        analysis_type: str,
        rating: int,
        comment: str = "",
        helpful_items: List[str] = None,
        unhelpful_items: List[str] = None,
        missing_topics: List[str] = None,
        user_id: str = None,
        ticket_title: str = "",
        ticket_description: str = "",
        detected_topics: List[str] = None
    ) -> str:
        """Collect feedback from user."""
        feedback_id = f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ticket_id[:8]}"
        
        feedback = Feedback(
            feedback_id=feedback_id,
            ticket_id=ticket_id,
            analysis_type=analysis_type,
            rating=rating,
            comment=comment,
            user_id=user_id,
            timestamp=datetime.now().isoformat(),
            helpful_items=helpful_items or [],
            unhelpful_items=unhelpful_items or [],
            missing_topics=missing_topics or [],
            ticket_title=ticket_title,
            ticket_description=ticket_description,
            detected_topics=detected_topics or []
        )
        
        self._store_feedback(feedback)
        print(f"📝 Feedback collected: {rating}/5 for {analysis_type}")
        
        return feedback_id
    
    def store_feedback(
        self,
        ticket_id: str,
        overall_rating: int,
        questions_rating: int,
        test_cases_rating: int,
        risks_rating: int,
        comment: str = ""
    ) -> str:
        """Store comprehensive feedback for all analysis aspects."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Store overall feedback
        overall_id = self.collect_feedback(
            ticket_id=ticket_id,
            analysis_type="overall",
            rating=overall_rating,
            comment=comment
        )
        
        # Store specific aspect feedback
        self.collect_feedback(
            ticket_id=ticket_id,
            analysis_type="questions",
            rating=questions_rating
        )
        
        self.collect_feedback(
            ticket_id=ticket_id,
            analysis_type="test_cases",
            rating=test_cases_rating
        )
        
        self.collect_feedback(
            ticket_id=ticket_id,
            analysis_type="risks",
            rating=risks_rating
        )
        
        print(f"📝 Comprehensive feedback stored for ticket {ticket_id}")
        return overall_id
    
    def _store_feedback(self, feedback: Feedback):
        """Store feedback in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO feedback (
                    feedback_id, ticket_id, analysis_type, rating, comment, user_id,
                    timestamp, helpful_items, unhelpful_items, missing_topics,
                    ticket_title, ticket_description, detected_topics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.feedback_id,
                feedback.ticket_id,
                feedback.analysis_type,
                feedback.rating,
                feedback.comment,
                feedback.user_id,
                feedback.timestamp,
                json.dumps(feedback.helpful_items),
                json.dumps(feedback.unhelpful_items),
                json.dumps(feedback.missing_topics),
                feedback.ticket_title,
                feedback.ticket_description,
                json.dumps(feedback.detected_topics)
            ))
            
            conn.commit()
    
    def get_feedback_summary(self, analysis_type: str = None, days: int = 30) -> FeedbackSummary:
        """Get summary of feedback for analysis improvement."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Base query
            query = '''
                SELECT rating, comment, helpful_items, unhelpful_items, missing_topics, detected_topics
                FROM feedback 
                WHERE timestamp > datetime('now', '-{} days')
            '''.format(days)
            
            params = []
            if analysis_type:
                query += ' AND analysis_type = ?'
                params.append(analysis_type)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
        
        if not results:
            return FeedbackSummary(
                total_feedback=0,
                average_rating=0.0,
                rating_distribution={},
                common_complaints=[],
                common_praises=[],
                improvement_suggestions=[],
                topic_specific_feedback={}
            )
        
        # Calculate statistics
        ratings = [row[0] for row in results]
        total_feedback = len(ratings)
        average_rating = statistics.mean(ratings)
        
        # Rating distribution
        rating_distribution = {}
        for rating in range(1, 6):
            rating_distribution[rating] = ratings.count(rating)
        
        # Analyze comments
        comments = [row[1] for row in results if row[1]]
        common_complaints = self._extract_complaints(comments)
        common_praises = self._extract_praises(comments)
        improvement_suggestions = self._extract_suggestions(comments)
        
        # Topic-specific feedback
        topic_specific_feedback = self._analyze_topic_feedback(results)
        
        return FeedbackSummary(
            total_feedback=total_feedback,
            average_rating=average_rating,
            rating_distribution=rating_distribution,
            common_complaints=common_complaints,
            common_praises=common_praises,
            improvement_suggestions=improvement_suggestions,
            topic_specific_feedback=topic_specific_feedback
        )
    
    def _extract_complaints(self, comments: List[str]) -> List[str]:
        """Extract common complaints from comments."""
        complaint_keywords = [
            'generic', 'not relevant', 'too basic', 'missing', 'unhelpful',
            'wrong', 'incorrect', 'useless', 'unclear', 'confusing'
        ]
        
        complaints = []
        for comment in comments:
            comment_lower = comment.lower()
            for keyword in complaint_keywords:
                if keyword in comment_lower:
                    # Extract sentence containing the complaint
                    sentences = comment.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            complaints.append(sentence.strip())
                            break
        
        return list(set(complaints))[:5]  # Top 5 unique complaints
    
    def _extract_praises(self, comments: List[str]) -> List[str]:
        """Extract common praises from comments."""
        praise_keywords = [
            'helpful', 'relevant', 'good', 'great', 'excellent', 'useful',
            'specific', 'detailed', 'comprehensive', 'accurate'
        ]
        
        praises = []
        for comment in comments:
            comment_lower = comment.lower()
            for keyword in praise_keywords:
                if keyword in comment_lower:
                    # Extract sentence containing the praise
                    sentences = comment.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            praises.append(sentence.strip())
                            break
        
        return list(set(praises))[:5]  # Top 5 unique praises
    
    def _extract_suggestions(self, comments: List[str]) -> List[str]:
        """Extract improvement suggestions from comments."""
        suggestion_keywords = [
            'should', 'could', 'need', 'suggest', 'recommend', 'improve',
            'add', 'include', 'consider', 'better'
        ]
        
        suggestions = []
        for comment in comments:
            comment_lower = comment.lower()
            for keyword in suggestion_keywords:
                if keyword in comment_lower:
                    # Extract sentence containing the suggestion
                    sentences = comment.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            suggestions.append(sentence.strip())
                            break
        
        return list(set(suggestions))[:5]  # Top 5 unique suggestions
    
    def _analyze_topic_feedback(self, results: List) -> Dict[str, Dict[str, Any]]:
        """Analyze feedback by detected topics."""
        topic_feedback = {}
        
        for row in results:
            rating = row[0]
            detected_topics = json.loads(row[5] or '[]')
            
            for topic in detected_topics:
                if topic not in topic_feedback:
                    topic_feedback[topic] = {
                        'ratings': [],
                        'count': 0
                    }
                
                topic_feedback[topic]['ratings'].append(rating)
                topic_feedback[topic]['count'] += 1
        
        # Calculate averages
        for topic in topic_feedback:
            ratings = topic_feedback[topic]['ratings']
            topic_feedback[topic]['average_rating'] = statistics.mean(ratings)
            topic_feedback[topic]['total_feedback'] = len(ratings)
        
        return topic_feedback
    
    def get_low_rated_items(self, threshold: int = 3, limit: int = 10) -> List[Dict[str, Any]]:
        """Get items that consistently receive low ratings."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ticket_id, analysis_type, rating, comment, unhelpful_items, detected_topics
                FROM feedback 
                WHERE rating <= ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (threshold, limit))
            
            results = cursor.fetchall()
        
        low_rated_items = []
        for row in results:
            unhelpful_items = json.loads(row[4] or '[]')
            detected_topics = json.loads(row[5] or '[]')
            
            low_rated_items.append({
                'ticket_id': row[0],
                'analysis_type': row[1],
                'rating': row[2],
                'comment': row[3],
                'unhelpful_items': unhelpful_items,
                'detected_topics': detected_topics
            })
        
        return low_rated_items
    
    def get_improvement_opportunities(self) -> Dict[str, Any]:
        """Get actionable improvement opportunities based on feedback."""
        summary = self.get_feedback_summary()
        low_rated = self.get_low_rated_items()
        
        opportunities = {
            'priority_areas': [],
            'quick_fixes': [],
            'long_term_improvements': [],
            'topic_specific_issues': {}
        }
        
        # Identify priority areas (low average rating)
        if summary.average_rating < 3.5:
            opportunities['priority_areas'].append({
                'area': 'Overall Question Quality',
                'current_rating': summary.average_rating,
                'issue': 'Questions are generally rated below satisfaction threshold',
                'action': 'Review and improve question generation algorithms'
            })
        
        # Quick fixes from common complaints
        for complaint in summary.common_complaints:
            if 'generic' in complaint.lower():
                opportunities['quick_fixes'].append({
                    'issue': 'Generic questions',
                    'action': 'Enhance topic-specific filtering and context utilization'
                })
            elif 'missing' in complaint.lower():
                opportunities['quick_fixes'].append({
                    'issue': 'Missing important questions',
                    'action': 'Expand question templates and improve domain coverage'
                })
        
        # Topic-specific issues
        for topic, feedback_data in summary.topic_specific_feedback.items():
            if feedback_data['average_rating'] < 3.0:
                opportunities['topic_specific_issues'][topic] = {
                    'rating': feedback_data['average_rating'],
                    'feedback_count': feedback_data['total_feedback'],
                    'action': f'Improve {topic}-specific question generation'
                }
        
        # Long-term improvements from suggestions
        opportunities['long_term_improvements'] = summary.improvement_suggestions
        
        return opportunities
    
    def export_feedback_data(self, format: str = 'json') -> str:
        """Export feedback data for external analysis."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM feedback ORDER BY timestamp DESC')
            
            columns = [description[0] for description in cursor.description]
            results = cursor.fetchall()
        
        data = []
        for row in results:
            data.append(dict(zip(columns, row)))
        
        if format == 'json':
            output_file = self.storage_dir / f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        print(f"📊 Feedback data exported to {output_file}")
        return str(output_file)
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get basic feedback statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total feedback count
            cursor.execute('SELECT COUNT(*) FROM feedback')
            total_feedback = cursor.fetchone()[0]
            
            # Average rating
            cursor.execute('SELECT AVG(rating) FROM feedback')
            avg_rating = cursor.fetchone()[0] or 0
            
            # Feedback by type
            cursor.execute('SELECT analysis_type, COUNT(*), AVG(rating) FROM feedback GROUP BY analysis_type')
            by_type = cursor.fetchall()
            
            # Recent feedback (last 7 days)
            cursor.execute('''
                SELECT COUNT(*), AVG(rating) 
                FROM feedback 
                WHERE timestamp > datetime('now', '-7 days')
            ''')
            recent_stats = cursor.fetchone()
        
        return {
            'total_feedback': total_feedback,
            'average_rating': round(avg_rating, 2),
            'feedback_by_type': [
                {
                    'type': row[0],
                    'count': row[1],
                    'avg_rating': round(row[2], 2)
                } for row in by_type
            ],
            'recent_feedback_count': recent_stats[0],
            'recent_average_rating': round(recent_stats[1] or 0, 2)
        } 
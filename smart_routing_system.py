"""
Smart Routing System for Jira-Figma Analyzer
Auto-assigns tickets to best-suited developers based on skills, workload, and performance
"""

import json
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import numpy as np
from collections import defaultdict
import os

@dataclass
class DeveloperProfile:
    """Developer profile with skills, workload, and performance data"""
    developer_id: str
    name: str
    email: str
    skills: Dict[str, float]  # skill_name -> proficiency_score (0-10)
    specializations: List[str]  # e.g., ['frontend', 'mobile', 'backend']
    current_workload: int  # current number of active tickets
    max_capacity: int  # maximum tickets they can handle
    performance_score: float  # overall performance (0-10)
    availability: str  # 'available', 'busy', 'unavailable'
    timezone: str
    working_hours: Dict[str, List[int]]  # day -> [start_hour, end_hour]
    preferred_ticket_types: List[str]  # e.g., ['bug', 'feature', 'enhancement']
    last_active: str
    success_rate: float  # percentage of completed tickets
    avg_completion_time: float  # average days to complete tickets
    created_at: str

@dataclass
class TicketRequirement:
    """Ticket requirements for matching"""
    ticket_id: str
    title: str
    description: str
    required_skills: List[str]
    complexity_level: int  # 1-10
    estimated_effort: int  # story points or hours
    priority: str  # 'low', 'medium', 'high', 'critical'
    ticket_type: str  # 'bug', 'feature', 'enhancement', 'task'
    deadline: Optional[str]
    figma_required: bool
    backend_required: bool
    frontend_required: bool
    mobile_required: bool
    testing_required: bool
    japanese_required: bool
    design_skills_required: bool

@dataclass
class AssignmentRecommendation:
    """Recommendation for ticket assignment"""
    ticket_id: str
    recommended_developer: str
    confidence_score: float  # 0-1
    reasoning: List[str]
    alternative_developers: List[Tuple[str, float]]  # (developer_id, score)
    estimated_completion_time: int  # days
    risk_factors: List[str]
    skill_gaps: List[str]
    workload_impact: str  # 'low', 'medium', 'high'

@dataclass
class WorkloadAnalysis:
    """Analysis of team workload distribution"""
    total_developers: int
    total_capacity: int
    current_utilization: float
    overloaded_developers: List[str]
    underutilized_developers: List[str]
    balanced_developers: List[str]
    recommended_reassignments: List[Dict]
    capacity_forecast: Dict[str, int]  # developer -> projected workload

class SmartRoutingSystem:
    """Smart routing system for optimal ticket assignment"""
    
    def __init__(self, db_path: str = "ticket_storage.db"):
        self.db_path = db_path
        self.developers_file = "developer_profiles.json"
        self.performance_file = "developer_performance.json"
        self.developers: Dict[str, DeveloperProfile] = {}
        self.performance_history: Dict[str, List[Dict]] = {}
        
        # Initialize database
        self._init_database()
        self._load_developers()
        self._load_performance_history()
        
        print("🎯 Smart Routing System initialized")
    
    def _init_database(self):
        """Initialize database tables for smart routing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Developer profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS developer_profiles (
                developer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                skills TEXT NOT NULL,
                specializations TEXT NOT NULL,
                current_workload INTEGER DEFAULT 0,
                max_capacity INTEGER DEFAULT 5,
                performance_score REAL DEFAULT 5.0,
                availability TEXT DEFAULT 'available',
                timezone TEXT DEFAULT 'UTC',
                working_hours TEXT NOT NULL,
                preferred_ticket_types TEXT NOT NULL,
                last_active TEXT NOT NULL,
                success_rate REAL DEFAULT 0.0,
                avg_completion_time REAL DEFAULT 0.0,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Assignment history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL,
                developer_id TEXT NOT NULL,
                assigned_at TEXT NOT NULL,
                completed_at TEXT,
                success_rating REAL,
                actual_completion_time REAL,
                skill_match_score REAL,
                workload_impact TEXT,
                notes TEXT
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                developer_id TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                recorded_at TEXT NOT NULL,
                context TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_developers(self):
        """Load developer profiles from file and database"""
        if os.path.exists(self.developers_file):
            with open(self.developers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for dev_data in data.get('developers', []):
                    dev = DeveloperProfile(**dev_data)
                    self.developers[dev.developer_id] = dev
        else:
            # Create sample developers if none exist
            self._create_sample_developers()
    
    def _load_performance_history(self):
        """Load performance history from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM assignment_history')
        assignments = cursor.fetchall()
        
        for assignment in assignments:
            dev_id = assignment[2]  # developer_id
            if dev_id not in self.performance_history:
                self.performance_history[dev_id] = []
            
            self.performance_history[dev_id].append({
                'ticket_id': assignment[1],
                'assigned_at': assignment[3],
                'completed_at': assignment[4],
                'success_rating': assignment[5],
                'actual_completion_time': assignment[6],
                'skill_match_score': assignment[7],
                'workload_impact': assignment[8],
                'notes': assignment[9]
            })
        
        conn.close()
    
    def _create_sample_developers(self):
        """Create sample developer profiles for testing"""
        sample_developers = [
            DeveloperProfile(
                developer_id="dev_001",
                name="Alice Johnson",
                email="alice@habitto.com",
                skills={
                    "react_native": 9.0,
                    "javascript": 8.5,
                    "mobile_ui": 9.5,
                    "figma": 8.0,
                    "japanese": 7.0,
                    "testing": 7.5,
                    "api_integration": 8.0
                },
                specializations=["frontend", "mobile"],
                current_workload=2,
                max_capacity=5,
                performance_score=8.5,
                availability="available",
                timezone="Asia/Tokyo",
                working_hours={"monday": [9, 18], "tuesday": [9, 18], "wednesday": [9, 18], "thursday": [9, 18], "friday": [9, 17]},
                preferred_ticket_types=["feature", "enhancement"],
                last_active=datetime.now().isoformat(),
                success_rate=92.0,
                avg_completion_time=3.2,
                created_at=datetime.now().isoformat()
            ),
            DeveloperProfile(
                developer_id="dev_002",
                name="Bob Smith",
                email="bob@habitto.com",
                skills={
                    "python": 9.5,
                    "django": 9.0,
                    "api_design": 9.5,
                    "database": 8.5,
                    "testing": 8.0,
                    "deployment": 7.5,
                    "japanese": 6.0
                },
                specializations=["backend", "api"],
                current_workload=1,
                max_capacity=4,
                performance_score=9.0,
                availability="available",
                timezone="UTC",
                working_hours={"monday": [8, 17], "tuesday": [8, 17], "wednesday": [8, 17], "thursday": [8, 17], "friday": [8, 16]},
                preferred_ticket_types=["bug", "feature"],
                last_active=datetime.now().isoformat(),
                success_rate=95.0,
                avg_completion_time=2.8,
                created_at=datetime.now().isoformat()
            ),
            DeveloperProfile(
                developer_id="dev_003",
                name="Carol Chen",
                email="carol@habitto.com",
                skills={
                    "react": 8.5,
                    "typescript": 8.0,
                    "ui_ux": 9.0,
                    "figma": 9.5,
                    "japanese": 9.5,
                    "accessibility": 8.5,
                    "testing": 8.0
                },
                specializations=["frontend", "design"],
                current_workload=3,
                max_capacity=6,
                performance_score=8.8,
                availability="busy",
                timezone="Asia/Tokyo",
                working_hours={"monday": [10, 19], "tuesday": [10, 19], "wednesday": [10, 19], "thursday": [10, 19], "friday": [10, 18]},
                preferred_ticket_types=["enhancement", "feature"],
                last_active=datetime.now().isoformat(),
                success_rate=88.0,
                avg_completion_time=4.1,
                created_at=datetime.now().isoformat()
            )
        ]
        
        for dev in sample_developers:
            self.developers[dev.developer_id] = dev
        
        self._save_developers()
    
    def _save_developers(self):
        """Save developer profiles to file"""
        data = {
            "developers": [asdict(dev) for dev in self.developers.values()],
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.developers_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_developer(self, developer: DeveloperProfile) -> bool:
        """Add a new developer to the system"""
        try:
            self.developers[developer.developer_id] = developer
            self._save_developers()
            self._save_developer_to_db(developer)
            print(f"✅ Developer {developer.name} added successfully")
            return True
        except Exception as e:
            print(f"❌ Error adding developer: {e}")
            return False
    
    def _save_developer_to_db(self, developer: DeveloperProfile):
        """Save developer to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO developer_profiles 
            (developer_id, name, email, skills, specializations, current_workload, 
             max_capacity, performance_score, availability, timezone, working_hours, 
             preferred_ticket_types, last_active, success_rate, avg_completion_time, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            developer.developer_id,
            developer.name,
            developer.email,
            json.dumps(developer.skills),
            json.dumps(developer.specializations),
            developer.current_workload,
            developer.max_capacity,
            developer.performance_score,
            developer.availability,
            developer.timezone,
            json.dumps(developer.working_hours),
            json.dumps(developer.preferred_ticket_types),
            developer.last_active,
            developer.success_rate,
            developer.avg_completion_time,
            developer.created_at
        ))
        
        conn.commit()
        conn.close()
    
    def analyze_ticket_requirements(self, ticket_data: Dict) -> TicketRequirement:
        """Analyze ticket data to extract requirements"""
        # Extract skills from ticket content
        required_skills = []
        complexity_level = 5  # default
        estimated_effort = 3  # default story points
        
        # Analyze title and description for skill requirements
        content = f"{ticket_data.get('title', '')} {ticket_data.get('description', '')}".lower()
        
        # Skill detection based on keywords
        skill_keywords = {
            "react_native": ["react native", "rn", "mobile app", "ios", "android"],
            "javascript": ["javascript", "js", "frontend", "ui"],
            "python": ["python", "backend", "api", "django", "flask"],
            "figma": ["figma", "design", "mockup", "prototype"],
            "japanese": ["japanese", "japan", "localization", "i18n"],
            "testing": ["test", "testing", "qa", "quality"],
            "api_integration": ["api", "integration", "endpoint", "rest"],
            "database": ["database", "sql", "data", "storage"],
            "ui_ux": ["ui", "ux", "user interface", "user experience"],
            "accessibility": ["accessibility", "a11y", "wcag", "screen reader"]
        }
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in content for keyword in keywords):
                required_skills.append(skill)
        
        # Determine complexity based on content analysis
        complexity_indicators = {
            "high": ["complex", "difficult", "challenging", "advanced", "sophisticated"],
            "medium": ["moderate", "standard", "typical", "normal"],
            "low": ["simple", "easy", "basic", "straightforward"]
        }
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in content for indicator in indicators):
                complexity_level = {"high": 8, "medium": 5, "low": 2}[level]
                break
        
        # Estimate effort based on complexity and content length
        content_length = len(content)
        if content_length > 1000:
            estimated_effort = min(8, complexity_level + 2)
        elif content_length > 500:
            estimated_effort = min(5, complexity_level + 1)
        else:
            estimated_effort = max(1, complexity_level - 1)
        
        # Determine ticket type
        ticket_type = "task"
        if "bug" in content or "fix" in content or "error" in content:
            ticket_type = "bug"
        elif "feature" in content or "new" in content or "add" in content:
            ticket_type = "feature"
        elif "improve" in content or "enhance" in content or "optimize" in content:
            ticket_type = "enhancement"
        
        # Determine priority
        priority = "medium"
        if "urgent" in content or "critical" in content or "asap" in content:
            priority = "critical"
        elif "high" in content or "important" in content:
            priority = "high"
        elif "low" in content or "minor" in content:
            priority = "low"
        
        return TicketRequirement(
            ticket_id=ticket_data.get('ticket_id', 'unknown'),
            title=ticket_data.get('title', ''),
            description=ticket_data.get('description', ''),
            required_skills=required_skills,
            complexity_level=complexity_level,
            estimated_effort=estimated_effort,
            priority=priority,
            ticket_type=ticket_type,
            deadline=ticket_data.get('deadline'),
            figma_required="figma" in content,
            backend_required=any(skill in content for skill in ["backend", "api", "database", "python"]),
            frontend_required=any(skill in content for skill in ["frontend", "ui", "react", "javascript"]),
            mobile_required=any(skill in content for skill in ["mobile", "react native", "ios", "android"]),
            testing_required="test" in content or "testing" in content,
            japanese_required="japanese" in content or "japan" in content,
            design_skills_required=any(skill in content for skill in ["design", "figma", "ui", "ux"])
        )
    
    def calculate_skill_match_score(self, developer: DeveloperProfile, requirements: TicketRequirement) -> float:
        """Calculate how well a developer's skills match ticket requirements"""
        if not requirements.required_skills:
            return 0.5  # neutral score if no specific skills required
        
        total_score = 0
        matched_skills = 0
        
        for required_skill in requirements.required_skills:
            if required_skill in developer.skills:
                skill_score = developer.skills[required_skill] / 10.0  # normalize to 0-1
                total_score += skill_score
                matched_skills += 1
            else:
                # Penalty for missing skills
                total_score += 0.1
        
        if matched_skills == 0:
            return 0.1
        
        # Calculate average score
        avg_score = total_score / len(requirements.required_skills)
        
        # Bonus for specialization match
        specialization_bonus = 0
        for spec in developer.specializations:
            if requirements.backend_required and spec == "backend":
                specialization_bonus += 0.1
            elif requirements.frontend_required and spec == "frontend":
                specialization_bonus += 0.1
            elif requirements.mobile_required and spec == "mobile":
                specialization_bonus += 0.1
            elif requirements.design_skills_required and spec == "design":
                specialization_bonus += 0.1
        
        final_score = min(1.0, avg_score + specialization_bonus)
        return final_score
    
    def calculate_workload_impact(self, developer: DeveloperProfile, requirements: TicketRequirement) -> str:
        """Calculate the impact of assigning this ticket to the developer"""
        current_utilization = developer.current_workload / developer.max_capacity
        
        # Estimate additional workload based on ticket complexity
        additional_load = requirements.estimated_effort / 10.0  # normalize
        projected_utilization = current_utilization + additional_load
        
        if projected_utilization > 1.0:
            return "high"  # would overload developer
        elif projected_utilization > 0.8:
            return "medium"  # would be busy but manageable
        else:
            return "low"  # minimal impact
    
    def calculate_availability_score(self, developer: DeveloperProfile) -> float:
        """Calculate developer availability score"""
        if developer.availability == "unavailable":
            return 0.0
        elif developer.availability == "busy":
            return 0.3
        else:  # available
            return 1.0
    
    def calculate_performance_score(self, developer: DeveloperProfile) -> float:
        """Calculate developer performance score"""
        # Base performance score
        base_score = developer.performance_score / 10.0
        
        # Success rate bonus
        success_bonus = developer.success_rate / 100.0 * 0.3
        
        # Completion time bonus (faster is better)
        time_bonus = max(0, (10 - developer.avg_completion_time) / 10.0 * 0.2)
        
        final_score = min(1.0, base_score + success_bonus + time_bonus)
        return final_score
    
    def find_best_developer(self, requirements: TicketRequirement) -> AssignmentRecommendation:
        """Find the best developer for a ticket"""
        if not self.developers:
            return AssignmentRecommendation(
                ticket_id=requirements.ticket_id,
                recommended_developer="none",
                confidence_score=0.0,
                reasoning=["No developers available"],
                alternative_developers=[],
                estimated_completion_time=0,
                risk_factors=["No developers in system"],
                skill_gaps=requirements.required_skills,
                workload_impact="unknown"
            )
        
        best_developer = None
        best_score = 0.0
        all_scores = []
        
        for dev_id, developer in self.developers.items():
            # Calculate various scores
            skill_score = self.calculate_skill_match_score(developer, requirements)
            availability_score = self.calculate_availability_score(developer)
            performance_score = self.calculate_performance_score(developer)
            workload_impact = self.calculate_workload_impact(developer, requirements)
            
            # Weighted final score
            weights = {
                'skill': 0.4,
                'availability': 0.3,
                'performance': 0.2,
                'workload': 0.1
            }
            
            workload_score = {"low": 1.0, "medium": 0.7, "high": 0.3}[workload_impact]
            
            final_score = (
                skill_score * weights['skill'] +
                availability_score * weights['availability'] +
                performance_score * weights['performance'] +
                workload_score * weights['workload']
            )
            
            all_scores.append((dev_id, developer.name, final_score, skill_score, availability_score, performance_score, workload_impact))
            
            if final_score > best_score:
                best_score = final_score
                best_developer = developer
        
        if not best_developer:
            return AssignmentRecommendation(
                ticket_id=requirements.ticket_id,
                recommended_developer="none",
                confidence_score=0.0,
                reasoning=["No suitable developers found"],
                alternative_developers=[],
                estimated_completion_time=0,
                risk_factors=["No developers available"],
                skill_gaps=requirements.required_skills,
                workload_impact="unknown"
            )
        
        # Generate reasoning
        reasoning = []
        if best_developer.skills:
            top_skills = sorted(best_developer.skills.items(), key=lambda x: x[1], reverse=True)[:3]
            reasoning.append(f"Strong skills: {', '.join([f'{skill}({score:.1f})' for skill, score in top_skills])}")
        
        if best_developer.performance_score > 8:
            reasoning.append(f"High performance score: {best_developer.performance_score:.1f}/10")
        
        if best_developer.success_rate > 90:
            reasoning.append(f"Excellent success rate: {best_developer.success_rate:.1f}%")
        
        if best_developer.availability == "available":
            reasoning.append("Currently available")
        
        # Identify skill gaps
        skill_gaps = []
        for required_skill in requirements.required_skills:
            if required_skill not in best_developer.skills or best_developer.skills[required_skill] < 5:
                skill_gaps.append(required_skill)
        
        # Identify risk factors
        risk_factors = []
        if best_developer.current_workload / best_developer.max_capacity > 0.8:
            risk_factors.append("High current workload")
        
        if skill_gaps:
            risk_factors.append(f"Missing skills: {', '.join(skill_gaps)}")
        
        if best_developer.availability == "busy":
            risk_factors.append("Developer is currently busy")
        
        # Sort alternatives by score
        alternatives = sorted(all_scores, key=lambda x: x[2], reverse=True)[1:4]  # top 3 alternatives
        
        # Estimate completion time
        base_time = requirements.estimated_effort * 0.5  # base estimate
        performance_multiplier = 2.0 - (best_developer.performance_score / 10.0)  # better performance = faster completion
        estimated_completion_time = int(base_time * performance_multiplier)
        
        return AssignmentRecommendation(
            ticket_id=requirements.ticket_id,
            recommended_developer=best_developer.developer_id,
            confidence_score=best_score,
            reasoning=reasoning,
            alternative_developers=[(dev_id, score) for dev_id, name, score, _, _, _, _ in alternatives],
            estimated_completion_time=estimated_completion_time,
            risk_factors=risk_factors,
            skill_gaps=skill_gaps,
            workload_impact=self.calculate_workload_impact(best_developer, requirements)
        )
    
    def analyze_workload_distribution(self) -> WorkloadAnalysis:
        """Analyze current workload distribution across the team"""
        if not self.developers:
            return WorkloadAnalysis(
                total_developers=0,
                total_capacity=0,
                current_utilization=0.0,
                overloaded_developers=[],
                underutilized_developers=[],
                balanced_developers=[],
                recommended_reassignments=[],
                capacity_forecast={}
            )
        
        total_capacity = sum(dev.max_capacity for dev in self.developers.values())
        total_workload = sum(dev.current_workload for dev in self.developers.values())
        current_utilization = total_workload / total_capacity if total_capacity > 0 else 0
        
        overloaded = []
        underutilized = []
        balanced = []
        
        for dev_id, developer in self.developers.items():
            utilization = developer.current_workload / developer.max_capacity
            
            if utilization > 0.9:
                overloaded.append(dev_id)
            elif utilization < 0.3:
                underutilized.append(dev_id)
            else:
                balanced.append(dev_id)
        
        # Generate reassignment recommendations
        recommended_reassignments = []
        for overloaded_dev in overloaded:
            for underutilized_dev in underutilized:
                if self.developers[overloaded_dev].current_workload > 1:
                    recommended_reassignments.append({
                        "from": overloaded_dev,
                        "to": underutilized_dev,
                        "reason": "Balance workload distribution"
                    })
        
        # Capacity forecast (simplified)
        capacity_forecast = {}
        for dev_id, developer in self.developers.items():
            # Simple forecast: current workload + 1 (assuming new tickets)
            capacity_forecast[dev_id] = min(developer.max_capacity, developer.current_workload + 1)
        
        return WorkloadAnalysis(
            total_developers=len(self.developers),
            total_capacity=total_capacity,
            current_utilization=current_utilization,
            overloaded_developers=overloaded,
            underutilized_developers=underutilized,
            balanced_developers=balanced,
            recommended_reassignments=recommended_reassignments,
            capacity_forecast=capacity_forecast
        )
    
    def record_assignment(self, ticket_id: str, developer_id: str, skill_match_score: float, workload_impact: str, notes: str = ""):
        """Record a ticket assignment for performance tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO assignment_history 
            (ticket_id, developer_id, assigned_at, skill_match_score, workload_impact, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            ticket_id,
            developer_id,
            datetime.now().isoformat(),
            skill_match_score,
            workload_impact,
            notes
        ))
        
        conn.commit()
        conn.close()
        
        # Update developer workload
        if developer_id in self.developers:
            self.developers[developer_id].current_workload += 1
            self.developers[developer_id].last_active = datetime.now().isoformat()
            self._save_developers()
    
    def record_completion(self, ticket_id: str, success_rating: float, actual_completion_time: float, notes: str = ""):
        """Record ticket completion for performance tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find the assignment record
        cursor.execute('''
            SELECT developer_id FROM assignment_history 
            WHERE ticket_id = ? AND completed_at IS NULL
            ORDER BY assigned_at DESC LIMIT 1
        ''', (ticket_id,))
        
        result = cursor.fetchone()
        if result:
            developer_id = result[0]
            
            # Update the assignment record
            cursor.execute('''
                UPDATE assignment_history 
                SET completed_at = ?, success_rating = ?, actual_completion_time = ?, notes = ?
                WHERE ticket_id = ? AND developer_id = ?
            ''', (
                datetime.now().isoformat(),
                success_rating,
                actual_completion_time,
                notes,
                ticket_id,
                developer_id
            ))
            
            # Update developer performance metrics
            self._update_developer_performance(developer_id, success_rating, actual_completion_time)
            
            # Decrease workload
            if developer_id in self.developers:
                self.developers[developer_id].current_workload = max(0, self.developers[developer_id].current_workload - 1)
                self._save_developers()
        
        conn.commit()
        conn.close()
    
    def _update_developer_performance(self, developer_id: str, success_rating: float, completion_time: float):
        """Update developer performance metrics"""
        if developer_id not in self.developers:
            return
        
        developer = self.developers[developer_id]
        
        # Update success rate (weighted average)
        current_success_rate = developer.success_rate
        new_success_rate = (current_success_rate * 0.8) + (success_rating * 20)  # 20% weight for new rating
        developer.success_rate = min(100.0, new_success_rate)
        
        # Update average completion time (weighted average)
        current_avg_time = developer.avg_completion_time
        new_avg_time = (current_avg_time * 0.8) + (completion_time * 0.2)  # 20% weight for new time
        developer.avg_completion_time = new_avg_time
        
        # Update performance score based on recent performance
        recent_performance = (success_rating / 5.0) * 10  # convert 1-5 rating to 0-10 scale
        current_performance = developer.performance_score
        new_performance = (current_performance * 0.9) + (recent_performance * 0.1)  # 10% weight for recent performance
        developer.performance_score = min(10.0, new_performance)
        
        self._save_developers()
    
    def get_developer_recommendations(self, ticket_data: Dict) -> Dict:
        """Get comprehensive developer recommendations for a ticket"""
        requirements = self.analyze_ticket_requirements(ticket_data)
        recommendation = self.find_best_developer(requirements)
        workload_analysis = self.analyze_workload_distribution()
        
        return {
            "ticket_analysis": {
                "ticket_id": requirements.ticket_id,
                "title": requirements.title,
                "required_skills": requirements.required_skills,
                "complexity_level": requirements.complexity_level,
                "estimated_effort": requirements.estimated_effort,
                "priority": requirements.priority,
                "ticket_type": requirements.ticket_type
            },
            "recommendation": {
                "recommended_developer": recommendation.recommended_developer,
                "developer_name": self.developers.get(recommendation.recommended_developer, DeveloperProfile("", "", "", {}, [], 0, 0, 0, "", "", {}, [], "", 0, 0, "")).name if recommendation.recommended_developer in self.developers else "Unknown",
                "confidence_score": recommendation.confidence_score,
                "reasoning": recommendation.reasoning,
                "estimated_completion_time": recommendation.estimated_completion_time,
                "risk_factors": recommendation.risk_factors,
                "skill_gaps": recommendation.skill_gaps,
                "workload_impact": recommendation.workload_impact
            },
            "alternatives": [
                {
                    "developer_id": dev_id,
                    "developer_name": self.developers[dev_id].name if dev_id in self.developers else "Unknown",
                    "score": score
                }
                for dev_id, score in recommendation.alternative_developers
            ],
            "workload_analysis": {
                "total_developers": workload_analysis.total_developers,
                "current_utilization": f"{workload_analysis.current_utilization:.1%}",
                "overloaded_developers": len(workload_analysis.overloaded_developers),
                "underutilized_developers": len(workload_analysis.underutilized_developers),
                "recommended_reassignments": len(workload_analysis.recommended_reassignments)
            }
        }
    
    def get_team_analytics(self) -> Dict:
        """Get comprehensive team analytics"""
        workload_analysis = self.analyze_workload_distribution()
        
        # Developer performance summary
        performance_summary = []
        for dev_id, developer in self.developers.items():
            performance_summary.append({
                "developer_id": dev_id,
                "name": developer.name,
                "performance_score": developer.performance_score,
                "success_rate": developer.success_rate,
                "current_workload": developer.current_workload,
                "max_capacity": developer.max_capacity,
                "utilization": f"{(developer.current_workload / developer.max_capacity):.1%}",
                "availability": developer.availability,
                "top_skills": sorted(developer.skills.items(), key=lambda x: x[1], reverse=True)[:3]
            })
        
        return {
            "team_overview": {
                "total_developers": len(self.developers),
                "total_capacity": workload_analysis.total_capacity,
                "current_utilization": f"{workload_analysis.current_utilization:.1%}",
                "overloaded_count": len(workload_analysis.overloaded_developers),
                "underutilized_count": len(workload_analysis.underutilized_developers)
            },
            "developers": performance_summary,
            "workload_distribution": {
                "overloaded": workload_analysis.overloaded_developers,
                "underutilized": workload_analysis.underutilized_developers,
                "balanced": workload_analysis.balanced_developers
            },
            "recommendations": workload_analysis.recommended_reassignments
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the smart routing system
    routing_system = SmartRoutingSystem()
    
    # Example ticket data
    sample_ticket = {
        "ticket_id": "HAB-123",
        "title": "Implement Japanese localization for mobile app login screen",
        "description": "Add Japanese language support to the React Native login screen with proper RTL layout and cultural considerations. Include form validation messages in Japanese.",
        "priority": "high"
    }
    
    # Get recommendations
    recommendations = routing_system.get_developer_recommendations(sample_ticket)
    
    print("🎯 Smart Routing Analysis")
    print("=" * 50)
    print(f"Ticket: {recommendations['ticket_analysis']['title']}")
    print(f"Required Skills: {', '.join(recommendations['ticket_analysis']['required_skills'])}")
    print(f"Complexity: {recommendations['ticket_analysis']['complexity_level']}/10")
    print()
    print("🏆 Recommended Developer:")
    print(f"  {recommendations['recommendation']['developer_name']} (Confidence: {recommendations['recommendation']['confidence_score']:.2f})")
    print(f"  Reasoning: {'; '.join(recommendations['recommendation']['reasoning'])}")
    print(f"  Estimated Time: {recommendations['recommendation']['estimated_completion_time']} days")
    print()
    print("📊 Team Workload:")
    print(f"  Utilization: {recommendations['workload_analysis']['current_utilization']}")
    print(f"  Overloaded: {recommendations['workload_analysis']['overloaded_developers']} developers")
    print(f"  Underutilized: {recommendations['workload_analysis']['underutilized_developers']} developers")

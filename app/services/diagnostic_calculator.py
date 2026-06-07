"""
Diagnostic Calculator Service
Calculates AI readiness scores and generates insights
"""

from typing import Dict, List, Tuple


# Question definitions
DIAGNOSTIC_QUESTIONS = {
    "q_strategy_1": {"section": "strategy", "weight": 25},
    "q_strategy_2": {"section": "strategy", "weight": 25},
    "q_strategy_3": {"section": "strategy", "weight": 25},
    "q_tech_1": {"section": "technology", "weight": 25},
    "q_tech_2": {"section": "technology", "weight": 25},
    "q_tech_3": {"section": "technology", "weight": 25},
    "q_people_1": {"section": "people", "weight": 25},
    "q_people_2": {"section": "people", "weight": 25},
    "q_people_3": {"section": "people", "weight": 25},
    "q_exec_1": {"section": "execution", "weight": 25},
    "q_exec_2": {"section": "execution", "weight": 25},
    "q_exec_3": {"section": "execution", "weight": 25},
}

SECTION_NAMES = {
    "strategy": "Strategy",
    "technology": "Technology",
    "people": "People",
    "execution": "Execution",
}


class DiagnosticCalculator:
    """
    Service for calculating diagnostic scores and generating results
    """

    @staticmethod
    def calculate_score(answers: Dict[str, int]) -> int:
        """
        Calculate diagnostic score from answers

        Args:
            answers: Dictionary with question IDs as keys and answers as values (0-4)

        Returns:
            Score 0-100
        """
        total_score = 0
        total_weight = 0

        for question_id, question_config in DIAGNOSTIC_QUESTIONS.items():
            if question_id in answers:
                answer_value = answers[question_id]
                weight = question_config["weight"]

                # Normalize answer to 0-4 scale
                normalized_answer = min(4, max(0, answer_value))
                total_score += normalized_answer * weight
                total_weight += weight

        # Calculate percentage (0-100)
        if total_weight > 0:
            score = (total_score / (total_weight * 4)) * 100
            return int(round(score))

        return 0

    @staticmethod
    def get_category(score: int) -> str:
        """
        Get category from score

        Args:
            score: Score 0-100

        Returns:
            Category name
        """
        if score >= 80:
            return "Advanced"
        elif score >= 60:
            return "Established"
        elif score >= 40:
            return "Emerging"
        else:
            return "Foundational"

    @staticmethod
    def get_category_explanation(score: int) -> str:
        """
        Get category explanation

        Args:
            score: Score 0-100

        Returns:
            Category explanation text
        """
        if score >= 80:
            return "Excellent! Your organization is well-prepared for AI adoption. You have a strong foundation across strategy, technology, people, and execution."
        elif score >= 60:
            return "Good! Your organization has a solid foundation for AI adoption. Focus on addressing key gaps to accelerate your AI maturity."
        elif score >= 40:
            return "Fair! Your organization can benefit from AI with focused preparation. Start with foundational elements before advanced initiatives."
        else:
            return "Needs Improvement! Your organization should focus on building AI readiness fundamentals before major transformation."

    @staticmethod
    def get_section_scores(answers: Dict[str, int]) -> Dict[str, float]:
        """
        Calculate average score for each section

        Args:
            answers: Dictionary of answers

        Returns:
            Dictionary with section names as keys and average scores as values
        """
        section_scores = {
            "strategy": {"total": 0, "count": 0},
            "technology": {"total": 0, "count": 0},
            "people": {"total": 0, "count": 0},
            "execution": {"total": 0, "count": 0},
        }

        for question_id, question_config in DIAGNOSTIC_QUESTIONS.items():
            if question_id in answers:
                section = question_config["section"]
                answer_value = min(4, max(0, answers[question_id]))
                section_scores[section]["total"] += answer_value
                section_scores[section]["count"] += 1

        # Calculate averages
        averages = {}
        for section, scores in section_scores.items():
            if scores["count"] > 0:
                averages[section] = scores["total"] / scores["count"]
            else:
                averages[section] = 0

        return averages

    @staticmethod
    def get_insights(answers: Dict[str, int], score: int) -> List[str]:
        """
        Generate insights based on answers and score

        Args:
            answers: Dictionary of answers
            score: Calculated score

        Returns:
            List of insight strings
        """
        insights = []

        # Get section scores
        section_scores = DiagnosticCalculator.get_section_scores(answers)

        # Find strengths and weaknesses
        sections_sorted = sorted(section_scores.items(), key=lambda x: x[1], reverse=True)

        if sections_sorted:
            strongest_section = sections_sorted[0]
            if strongest_section[1] >= 3:
                insights.append(
                    f"✓ Strength: Your {SECTION_NAMES[strongest_section[0]]} area shows strong capabilities."
                )

        if sections_sorted and sections_sorted[-1][1] < 2.5:
            weakest_section = sections_sorted[-1]
            insights.append(
                f"↑ Opportunity: Focus on improving your {SECTION_NAMES[weakest_section[0]]} capabilities."
            )

        # Add score-based insights
        if score >= 80:
            insights.append("🎯 You're ready for advanced AI initiatives and should consider strategic investments.")
        elif score >= 60:
            insights.append("📈 Build on your solid foundation by addressing identified gaps.")
        elif score >= 40:
            insights.append("🔧 Focus on foundational improvements to support future AI adoption.")
        else:
            insights.append("📚 Start with AI education and build basic capabilities before complex initiatives.")

        return insights

    @staticmethod
    def get_recommendations(score: int) -> List[str]:
        """
        Get recommendations based on score

        Args:
            score: Score 0-100

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if score >= 80:
            recommendations.extend([
                "You're ready for advanced AI solutions. Consider AI Blueprint for comprehensive implementation planning.",
                "Explore innovative use cases to drive competitive advantage.",
                "Establish centers of excellence to scale AI across the organization.",
                "Focus on governance and ethical AI practices as you scale.",
            ])
        elif score >= 60:
            recommendations.extend([
                "Your foundation is solid. Start with AI Snapshot to get detailed insights.",
                "Prioritize closing identified gaps in your weakest areas.",
                "Build internal capability and reduce reliance on external consultants.",
                "Launch pilot projects to build momentum and demonstrate value.",
            ])
        elif score >= 40:
            recommendations.extend([
                "Focus on modernizing your data infrastructure.",
                "Build your AI talent pipeline through hiring and training.",
                "Develop a clear, executive-aligned AI strategy.",
                "Start with low-risk pilot projects to build organizational confidence.",
            ])
        else:
            recommendations.extend([
                "Begin with AI education and awareness programs for leadership.",
                "Establish basic data governance and infrastructure foundations.",
                "Start recruiting or training your first AI team members.",
                "Identify one high-impact quick win to demonstrate AI value.",
                "Develop a realistic 12-24 month AI maturity roadmap.",
            ])

        return recommendations

    @staticmethod
    def validate_answers(answers: Dict[str, int]) -> Tuple[bool, str]:
        """
        Validate that all required questions are answered

        Args:
            answers: Dictionary of answers

        Returns:
            Tuple of (is_valid, error_message)
        """
        for question_id in DIAGNOSTIC_QUESTIONS.keys():
            if question_id not in answers:
                return False, f"Missing answer for question: {question_id}"

            answer = answers[question_id]
            if not isinstance(answer, (int, float)):
                return False, f"Invalid answer type for {question_id}: expected number"

            if answer < 0 or answer > 4:
                return False, f"Invalid answer value for {question_id}: expected 0-4"

        return True, ""

    @staticmethod
    def calculate_complete_result(answers: Dict[str, int]) -> Dict:
        """
        Calculate complete diagnostic result

        Args:
            answers: Dictionary of answers

        Returns:
            Complete result dictionary with score, category, insights, recommendations
        """
        # Validate
        is_valid, error_msg = DiagnosticCalculator.validate_answers(answers)
        if not is_valid:
            raise ValueError(error_msg)

        # Calculate score
        score = DiagnosticCalculator.calculate_score(answers)

        # Get category and explanation
        category = DiagnosticCalculator.get_category(score)
        category_explanation = DiagnosticCalculator.get_category_explanation(score)

        # Get insights and recommendations
        insights = DiagnosticCalculator.get_insights(answers, score)
        recommendations = DiagnosticCalculator.get_recommendations(score)

        return {
            "score": score,
            "category": category,
            "category_explanation": category_explanation,
            "insights": insights,
            "recommendations": recommendations,
        }

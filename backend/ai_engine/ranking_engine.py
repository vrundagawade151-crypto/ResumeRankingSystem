"""Ranking engine - compares resume data with job requirements and generates scores."""
import re
from collections import Counter


class RankingEngine:
    """
    Ranks candidates based on job match.
    Formula: 60% skill match + 20% experience match + 20% education match
    """

    def __init__(self, job_required_skills: str, job_experience: str = "", job_description: str = ""):
        self.job_required_skills = self._normalize_and_tokenize(job_required_skills)
        self.job_experience = job_experience or ""
        self.job_description = job_description or ""
        self.job_keywords = self._extract_keywords(job_description)

    def _normalize_and_tokenize(self, text: str) -> set:
        """Normalize and tokenize text into lowercase skills/keywords."""
        if not text:
            return set()
        text = text.lower().strip()
        # Split by common separators
        tokens = re.split(r'[,;.\s\n|\-/]+', text)
        return set(t.strip() for t in tokens if len(t.strip()) >= 2)

    def _extract_keywords(self, text: str) -> set:
        """Extract meaningful keywords from job description."""
        if not text:
            return set()
        return self._normalize_and_tokenize(text)

    def _calculate_skill_match(self, candidate_skills: str) -> float:
        """
        Calculate skill match percentage (0-100).
        Compares candidate skills with required skills.
        """
        if not self.job_required_skills:
            return 50.0  # No requirements = neutral score
        
        candidate_skill_set = self._normalize_and_tokenize(candidate_skills)
        
        # Also include job description keywords for broader matching
        all_required = self.job_required_skills | self.job_keywords
        if not all_required:
            return 50.0
        
        matches = 0
        for req in all_required:
            for cand in candidate_skill_set:
                if req in cand or cand in req:
                    matches += 1
                    break
        
        return min(100, (matches / len(all_required)) * 100) if all_required else 50.0

    def _calculate_experience_match(self, candidate_experience: str) -> float:
        """
        Calculate experience match (0-100).
        Looks for years of experience and relevance.
        """
        if not candidate_experience:
            return 0.0
        
        score = 50.0  # Base score
        
        # Extract years from candidate
        years_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)', candidate_experience.lower())
        candidate_years = int(years_match.group(1)) if years_match else 0
        
        # Extract required years from job
        job_years_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)', self.job_experience.lower())
        required_years = int(job_years_match.group(1)) if job_years_match else 0
        
        if required_years == 0:
            return min(100, 50 + candidate_years * 5)  # More experience = better
        
        if candidate_years >= required_years:
            score = 70 + min(30, (candidate_years - required_years) * 5)
        else:
            score = max(0, 50 - (required_years - candidate_years) * 15)
        
        return min(100, max(0, score))

    def _calculate_education_match(self, candidate_education: str) -> float:
        """
        Calculate education match (0-100).
        Checks for degree level and relevance.
        """
        if not candidate_education:
            return 0.0
        
        score = 50.0
        edu_lower = candidate_education.lower()
        
        # Degree level scoring
        if any(x in edu_lower for x in ['phd', 'doctorate', 'doctoral']):
            score = 95
        elif any(x in edu_lower for x in ['master', 'm.s', 'm.tech', 'mba', 'm.sc']):
            score = 85
        elif any(x in edu_lower for x in ['bachelor', 'b.tech', 'b.e', 'b.s', 'b.sc', 'bca']):
            score = 75
        elif any(x in edu_lower for x in ['diploma', 'associate']):
            score = 60
        elif any(x in edu_lower for x in ['high school', 'secondary']):
            score = 40
        
        # Relevance boost for tech/IT roles
        if any(x in edu_lower for x in ['computer', 'engineering', 'information technology', 'it']):
            score = min(100, score + 10)
        
        return min(100, score)

    def calculate_ranking(
        self,
        skills: str,
        education: str,
        experience: str,
        skill_weight: float = 0.6,
        experience_weight: float = 0.2,
        education_weight: float = 0.2
    ) -> dict:
        """
        Calculate overall ranking score.
        Returns dict with individual scores and total.
        """
        skill_score = self._calculate_skill_match(skills)
        experience_score = self._calculate_experience_match(experience)
        education_score = self._calculate_education_match(education)
        
        total_score = (
            skill_score * skill_weight +
            experience_score * experience_weight +
            education_score * education_weight
        )
        
        return {
            'skill_match_score': round(skill_score, 2),
            'experience_match_score': round(experience_score, 2),
            'education_match_score': round(education_score, 2),
            'ranking_score': round(total_score, 2)
        }

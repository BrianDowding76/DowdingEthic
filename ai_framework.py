# ai_framework.py
# Part of the DowdingEthic project
# Author: Brian Dowding
# Description: Core ethical decision-making logic for Intent-Aware AI

from typing import List, Tuple, Dict, Any

class AIEthicalFramework:
    """
    This class models a decision-making engine based on the Dowding Ethic:
    - Intentional Altruism
    - Informed Consequentialism
    - Voluntary Sacrifice
    - Transparency of Thought
    - Preference for Higher Values
    - Respect for Autonomy
    - Non-Exclusivity of Identity
    """

    def __init__(self):
        self.reason_log = {}  # Optional: track rationale for each decision made

    def evaluate_intent(self, option: Dict[str, Any]) -> float:
        """
        Assign a score based on the option's intent — prioritizing others' well-being?
        """
        return option.get("intent_score", 0.0)

    def project_outcomes(self, option: Dict[str, Any]) -> float:
        """
        Predict the long-term consequences of the action.
        """
        return option.get("outcome_score", 0.0)

    def check_if_sacrifice_uplifts_others(self, option: Dict[str, Any]) -> float:
        """
        Reward voluntary sacrifice if it reduces suffering for others.
        """
        return option.get("altruism_score", 0.0)

    def combine_scores(self, intent: float, outcome: float, altruism: float) -> float:
        """
        Aggregate the ethical weights. Adjust ratios to tune the personality.
        """
        return (intent * 0.4) + (outcome * 0.4) + (altruism * 0.2)

    def decide(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Choose the most ethical action from a list of candidates.
        Each option is a dict with keys: name, intent_score, outcome_score, altruism_score
        """
        scored = []
        for option in options:
            intent = self.evaluate_intent(option)
            outcome = self.project_outcomes(option)
            altruism = self.check_if_sacrifice_uplifts_others(option)
            score = self.combine_scores(intent, outcome, altruism)
            self.reason_log[option.get("name", "unnamed")] = {
                "intent": intent,
                "outcome": outcome,
                "altruism": altruism,
                "total": score
            }
            scored.append((option, score))

        # Return the best scoring option
        return max(scored, key=lambda x: x[1])[0]

    def explain_decision(self, option_name: str) -> Dict[str, float]:
        """
        Retrieve reasoning behind a decision.
        """
        return self.reason_log.get(option_name, {})

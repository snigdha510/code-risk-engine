import json
import re


class DecisionAgent:

    def __init__(self, llm_callable):
        """
        llm_callable: function(prompt: str) -> str
        """
        self.llm = llm_callable

    def evaluate(
        self,
        function_name,
        source_code,
        impact_size,
        depth,
        reverse_dependency,
        similar_functions
    ):
        similar_list = "\n".join(
            f"- {fn.name}" for fn in similar_functions
        )

        prompt = f"""
        You are a senior software architect performing risk analysis.

        Modified Function:
        {function_name}

        Source Code:
        {source_code}

        Structural Metrics:
        - Impact Size: {impact_size}
        - Dependency Depth: {depth}
        - Reverse Dependency Count: {reverse_dependency}

        Semantically Similar Functions:
        {similar_list}

        Return JSON in this exact format:

        {{
        "risk_level": "LOW | MEDIUM | HIGH",
        "confidence": 0.0-1.0,
        "reasoning": "short explanation",
        "recommended_tests": ["test1", "test2"]
        }}
        """


        response = self.llm(prompt)

        # 🔥 Extract JSON block from response
        try:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)

            raise ValueError("No JSON found")

        except Exception:
            return {
                "risk_level": "UNKNOWN",
                "confidence": 0.0,
                "reasoning": "LLM did not return valid JSON",
                "recommended_tests": []
            }
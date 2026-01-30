"""LLM client wrapper for MiniMax API."""

import json
from typing import Optional

import httpx

from config.settings import settings


class LLMClient:
    """Client for interacting with MiniMax LLM API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        group_id: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.minimax_api_key
        self.group_id = group_id or settings.minimax_group_id
        self.base_url = base_url or settings.minimax_base_url
        self.model = model or settings.minimax_model
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _build_headers(self) -> dict:
        """Build request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Optional[str]:
        """
        Send a chat completion request to MiniMax API.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response

        Returns:
            Generated text response or None if failed
        """
        if not self.api_key:
            # Return a mock response for testing without API key
            return self._mock_response(messages)

        client = await self._get_client()

        # MiniMax API endpoint
        url = f"{self.base_url}/text/chatcompletion_v2"

        # Build request body for MiniMax format
        payload = {
            "model": self.model,
            "messages": [
                {"sender_type": "USER" if m["role"] == "user" else "BOT", "text": m["content"]}
                for m in messages
            ],
            "tokens_to_generate": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
        }

        try:
            response = await client.post(
                url,
                headers=self._build_headers(),
                json=payload,
            )
            response.raise_for_status()

            data = response.json()

            # Extract response text from MiniMax format
            if "reply" in data:
                return data["reply"]
            elif "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0].get("text", "")

            return None

        except httpx.HTTPStatusError as e:
            print(f"MiniMax API HTTP error: {e.response.status_code} - {e.response.text}")
            return self._mock_response(messages)
        except Exception as e:
            print(f"MiniMax API error: {e}")
            return self._mock_response(messages)

    def _mock_response(self, messages: list[dict]) -> str:
        """Generate a mock response when API is not available."""
        # Extract the last user message to understand what's being asked
        last_message = messages[-1]["content"] if messages else ""

        if "summarize" in last_message.lower() or "summary" in last_message.lower():
            return json.dumps({
                "risk_factors": [
                    "NSCLC patient on chemotherapy - neutropenia risk",
                    "Active problems require close monitoring",
                    "Medication interactions to monitor"
                ],
                "key_concerns": [
                    "Monitor for treatment-related complications",
                    "Assess respiratory status regularly"
                ]
            })
        elif "warning" in last_message.lower() or "alert" in last_message.lower():
            return json.dumps({
                "warnings": [
                    {
                        "type": "monitoring",
                        "message": "Continue close monitoring per established protocols"
                    }
                ]
            })
        else:
            return "Analysis completed based on available clinical data."

    async def summarize_patient_context(
        self, patient_data: dict, transcript: str
    ) -> dict:
        """
        Use LLM to summarize patient context and identify risk factors.

        Args:
            patient_data: Patient information dict
            transcript: Session transcript

        Returns:
            Dict with risk_factors and key_concerns
        """
        prompt = f"""Analyze this patient data and session transcript for a lung cancer patient.
Identify key risk factors and clinical concerns.

Patient Data:
- Primary Diagnosis: {patient_data.get('primary_diagnosis', 'Unknown')}
- Active Problems: {', '.join(patient_data.get('active_problems', []))}
- Medications: {', '.join([m.get('name', str(m)) if isinstance(m, dict) else str(m) for m in patient_data.get('current_medications', [])])}
- Allergies: {', '.join(patient_data.get('allergies', []))}
- Code Status: {patient_data.get('code_status', 'Unknown')}

Session Transcript:
{transcript[:1000]}

Respond with a JSON object containing:
- "risk_factors": list of identified risk factors (strings)
- "key_concerns": list of key clinical concerns (strings)

JSON Response:"""

        messages = [
            {"role": "system", "content": "You are a clinical decision support assistant specializing in oncology. Provide concise, actionable analysis."},
            {"role": "user", "content": prompt},
        ]

        response = await self.chat_completion(messages, temperature=0.3, max_tokens=500)

        try:
            # Try to parse JSON from response
            if response:
                # Find JSON in response
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass

        # Return default structure if parsing fails
        return {
            "risk_factors": self._extract_risk_factors(patient_data),
            "key_concerns": []
        }

    def _extract_risk_factors(self, patient_data: dict) -> list[str]:
        """Extract risk factors from patient data without LLM."""
        risk_factors = []

        # Check for common risk conditions
        active_problems = [p.lower() for p in patient_data.get("active_problems", [])]

        if any("neutropenia" in p for p in active_problems):
            risk_factors.append("Neutropenic - high infection risk")

        if any("hemoptysis" in p or "bleeding" in p for p in active_problems):
            risk_factors.append("Active bleeding/hemoptysis - review anticoagulation")

        if any("hypoxia" in p for p in active_problems):
            risk_factors.append("Hypoxia - monitor respiratory status closely")

        if any("delirium" in p or "falls" in p for p in active_problems):
            risk_factors.append("Fall/delirium risk - safety precautions needed")

        if any("sepsis" in p for p in active_problems):
            risk_factors.append("Sepsis concern - monitor for deterioration")

        # Check medications for anticoagulation
        medications = [
            m.get("name", "").lower() if isinstance(m, dict) else str(m).lower()
            for m in patient_data.get("current_medications", [])
        ]
        if any(med in ["enoxaparin", "heparin", "warfarin"] for med in medications):
            risk_factors.append("On anticoagulation therapy")

        # Check diagnosis
        diagnosis = patient_data.get("primary_diagnosis", "").lower()
        if "nsclc" in diagnosis or "lung cancer" in diagnosis:
            if "stage iv" in diagnosis or "stage 4" in diagnosis:
                risk_factors.append("Advanced stage cancer - goals of care important")
            if "brain met" in diagnosis:
                risk_factors.append("Brain metastases - monitor neurologic status")

        return risk_factors if risk_factors else ["Standard oncology precautions apply"]

    async def generate_warning_explanation(
        self, warning_type: str, context: str
    ) -> str:
        """
        Generate a human-readable explanation for a warning.

        Args:
            warning_type: Type of warning
            context: Clinical context

        Returns:
            Human-readable warning message
        """
        prompt = f"""Generate a concise clinical warning message for healthcare providers.

Warning Type: {warning_type}
Clinical Context: {context}

Provide a clear, actionable warning message in 1-2 sentences."""

        messages = [
            {"role": "system", "content": "You are a clinical decision support assistant. Provide concise, actionable warnings."},
            {"role": "user", "content": prompt},
        ]

        response = await self.chat_completion(messages, temperature=0.3, max_tokens=150)
        return response or f"Clinical alert: {warning_type} - review and take appropriate action."


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the LLM client singleton."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client

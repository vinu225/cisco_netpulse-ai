"""OpenRouter & LLM Telemetry Connection Manager for NetPulse AI Engine."""

import json
import logging
import time
import re
from typing import Optional, List, Dict, Any
from openai import OpenAI
from src.config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL, LLM_TIMEOUT, LLM_TEMPERATURE, LLM_MAX_TOKENS

logger = logging.getLogger(__name__)

# Fallback AI model catalog for OpenRouter API requests
FALLBACK_MODEL_CATALOG = [
    "openrouter/auto",
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
]


class LLMClient:
    """Robust API Client handling LLM telemetry inference with dynamic model failover."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.primary_model = model or OPENROUTER_MODEL
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is unconfigured. Check .env settings.")
            
        self.openai_instance = OpenAI(
            api_key=self.api_key,
            base_url=OPENROUTER_BASE_URL,
            timeout=LLM_TIMEOUT
        )
        
    def diagnose(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Dispatch telemetry prompts to OpenRouter models with fallback sequence handling."""
        model_queue = [self.primary_model] + [m for m in FALLBACK_MODEL_CATALOG if m != self.primary_model]
        
        for candidate_model in model_queue:
            logger.info(f"Dispatching diagnostic request to model: {candidate_model}")
            parsed_payload = self._try_model(candidate_model, system_prompt, user_prompt)
            if parsed_payload is not None:
                return parsed_payload
            logger.warning(f"Model [{candidate_model}] execution failed or timed out. Failing over to next model...")
            time.sleep(0.5)
            
        logger.error("All AI models in queue failed. Returning safe fallback diagnosis.")
        return self._default_response()
        
    def _try_model(self, model_name: str, sys_prompt: str, usr_prompt: str) -> Optional[Dict[str, Any]]:
        """Attempt completion using specified model name."""
        try:
            chat_completion = self.openai_instance.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": usr_prompt}
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            raw_text = chat_completion.choices[0].message.content
            if not raw_text or not raw_text.strip():
                logger.warning(f"Model {model_name} returned empty text payload")
                return None
                
            logger.info(f"Model {model_name} returned valid response payload")
            return self._parse_json(raw_text)
            
        except Exception as err:
            logger.warning(f"Execution error on model {model_name}: {err}")
            return None
            
    def _parse_json(self, response_text: str) -> Dict[str, Any]:
        """Parse raw text response from LLM into dictionary payload with fallback repair."""
        # 1. Direct JSON parse
        try:
            data = json.loads(response_text)
            if isinstance(data, list):
                return data[0] if (data and isinstance(data[0], dict)) else self._default_response()
            return data
        except json.JSONDecodeError:
            pass
            
        # 2. Extract JSON object substring using Regex
        regex_json = re.search(r'\{.*\}', response_text, re.DOTALL)
        if regex_json:
            try:
                extracted = json.loads(regex_json.group())
                if isinstance(extracted, list):
                    return extracted[0] if (extracted and isinstance(extracted[0], dict)) else self._default_response()
                return extracted
            except json.JSONDecodeError:
                pass
                
        # 3. Clean common markdown code-block wrappers
        cleaned = response_text.strip()
        cleaned = re.sub(r'^```json\s*', '', cleaned)
        cleaned = re.sub(r'^```\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        
        try:
            repaired = json.loads(cleaned)
            if isinstance(repaired, list):
                return repaired[0] if (repaired and isinstance(repaired[0], dict)) else self._default_response()
            return repaired
        except json.JSONDecodeError as parse_err:
            logger.error(f"Failed to parse LLM JSON output snippet: {response_text[:300]}")
            raise ValueError(f"Malformed LLM JSON payload: {parse_err}")
            
    def _default_response(self) -> Dict[str, Any]:
        """Generate default fallback response schema on total service failure."""
        return {
            "predicted_fault": "Unresolvable Anomaly",
            "confidence": 0.0,
            "reasoning_summary": "AI inference engine failed to parse response payload from telemetry provider.",
            "evidence_used": [],
            "recommended_fix": "Manual engineer verification required.",
            "commands": [],
            "needs_more_evidence": True
        }


def create_llm_client() -> LLMClient:
    """Factory helper creating configured LLMClient instance."""
    return LLMClient()
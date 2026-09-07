"""Knowledge loading and sample story generation for the Streamlit demo."""

from __future__ import annotations

import json
import os
import re
from io import BytesIO
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")
# Keep the model in one place so it can be changed without touching UI code.
GEMINI_MODEL = "gemini-3.5-flash-lite"
KNOWLEDGE_FILES = (
    "Hanwha_Technology_Knowledge.md",
    "Hanwha_Technology_Process.md",
    "Hanwha_Story_Guide.md",
)


def load_knowledge() -> tuple[dict[str, str], list[str]]:
    """Load the existing Markdown sources as UTF-8 without changing them."""
    knowledge: dict[str, str] = {}
    missing: list[str] = []
    knowledge_dir = PROJECT_ROOT / "knowledge"

    for filename in KNOWLEDGE_FILES:
        path = knowledge_dir / filename
        if not path.is_file():
            missing.append(str(path.relative_to(PROJECT_ROOT)))
            continue
        try:
            knowledge[filename] = path.read_text(encoding="utf-8")
        except OSError:
            missing.append(str(path.relative_to(PROJECT_ROOT)))
    return knowledge, missing


SAMPLE_STORIES: dict[str, dict[str, Any]] = {
    "ocean": {
        "icon": "🚢",
        "name": "바다를 지키는 기술",
        "description": "바다 위 함정은 주변의 위험을 어떻게 발견하고 대응할까요?",
        "title": "파란바다 수호대와 다섯 친구",
        "story": """파란바다를 지나가던 수호선에는 서로 다른 재주를 가진 친구들이 살고 있었어요.\n\n가장 먼저 멀리눈이 바다를 살폈어요. 멀리 있는 작은 움직임도 놓치지 않는 관찰 친구였지요. 이상한 점을 발견하면, 따라별이 그곳을 계속 지켜보며 어디로 가는지 알려 주었어요.\n\n두 친구가 보낸 소식은 지혜부엉이에게 모였어요. 지혜부엉이는 여러 소식을 한 장의 큰 지도에 정리해 수호선 친구들이 지금 어떤 상황인지 차분히 알 수 있게 도와주었답니다.\n\n마지막으로 방패친구가 필요한 곳을 지키고, 수호선은 가장 알맞은 일을 선택했어요. 누군가 혼자서 해낸 일이 아니었어요. 보고, 살피고, 생각하고, 지키는 친구들이 손을 맞잡았기에 파란바다는 더 안전하고 평화로워졌답니다.""",
        "friends": [
            ("멀리눈", "감시·탐지 기술", "주변 상황을 살펴봄"),
            ("따라별", "추적·상황 파악", "발견한 대상을 계속 확인함"),
            ("지혜부엉이", "전투관리체계(CMS)", "정보를 모아 상황 판단을 도움"),
            ("방패친구", "방어·대응 체계", "안전과 보호를 지원함"),
        ],
        "flow": ["탐지", "추적", "정보 통합", "판단", "보호·대응"],
        "value": "바다를 지키는 기술은 여러 친구가 같은 그림을 보고 차분히 힘을 합치게 해요. 덕분에 필요한 순간에 더 정확하게 판단하고, 사람과 중요한 공간의 안전을 도울 수 있답니다.",
        "companies": ["한화오션", "한화시스템", "한화에어로스페이스"],
    },
    "space": {
        "icon": "🛰️",
        "name": "우주로 떠나는 위성",
        "description": "위성은 어떻게 우주로 올라가서 자신의 일을 할까요?",
        "title": "별빛 우체국으로 가는 위성 친구",
        "story": """어느 날, 작은 위성 친구 별이는 아주 높은 별빛 우체국에서 지구를 돕고 싶었어요. 하지만 혼자서는 하늘 높이 갈 수 없었지요.\n\n튼튼한 로켓버스가 별이를 조심조심 우주까지 데려다주었어요. 로켓버스 안의 엔진 친구들은 힘을 모아 멀고 높은 길을 힘차게 달렸답니다.\n\n우주에 도착한 별이는 자기 자리를 찾고, 지구를 바라보며 관찰하거나 소식을 전하는 일을 시작했어요. 지상에 있는 친구들은 별이가 보낸 소중한 정보를 받아 필요한 곳에 전달했지요.\n\n별이는 깨달았어요. 멋진 우주 여행은 로켓버스, 위성, 지상 친구들이 차례로 맡은 일을 잘했기 때문에 가능했다는 것을요. 서로의 힘이 이어지면, 아주 먼 우주도 우리와 가까워진답니다.""",
        "friends": [
            ("로켓버스", "우주 발사체 체계종합", "위성을 우주로 보냄"),
            ("힘센 엔진", "로켓 추진", "발사체가 움직일 힘을 만듦"),
            ("별이", "위성", "우주에서 관측·통신 일을 함"),
            ("지상 친구", "지상 활용", "위성 정보를 받아 활용함"),
        ],
        "flow": ["발사체", "위성", "관측·통신", "지상 활용"],
        "value": "우주 기술은 멀리 있는 곳을 살피고 소중한 정보를 전하는 데 도움을 줘요. 각 기술이 릴레이처럼 이어져서, 우주에서 얻은 정보가 우리 생활에 닿게 된답니다.",
        "companies": ["한화에어로스페이스", "한화시스템"],
    },
    "solar": {
        "icon": "☀️",
        "name": "햇빛의 에너지 여행",
        "description": "햇빛은 어떻게 전기가 되어 우리에게 올까요?",
        "title": "햇살 요정 루미의 반짝이는 여행",
        "story": """아침이 되자 햇살 요정 루미가 지붕 위에 살포시 내려앉았어요. 그곳에는 햇빛을 좋아하는 태양광 친구들이 기다리고 있었지요.\n\n태양광 친구들은 루미의 따뜻한 빛을 받아 깨끗한 전기로 바꾸었어요. 만들어진 전기는 필요한 곳으로 여행을 떠났지만, 햇빛이 잠시 쉬는 날도 있었답니다.\n\n그때 에너지 창고 친구 ESS가 나섰어요. 전기가 넉넉할 때는 소중히 보관하고, 필요할 때는 다시 꺼내 쓸 수 있게 도와주었지요.\n\n루미와 태양광 친구, 에너지 창고 친구가 힘을 합치자 집과 학교에 필요한 에너지를 더 똑똑하게 쓸 수 있었어요. 햇빛의 작은 반짝임은 모두가 함께 만드는 깨끗한 내일의 불빛이 되었답니다.""",
        "friends": [
            ("햇살 요정 루미", "태양 에너지", "전기를 만들 에너지를 건넴"),
            ("태양광 친구", "태양광 모듈", "햇빛을 전기로 바꿈"),
            ("에너지 창고 친구", "ESS", "전기를 보관하고 필요할 때 꺼냄"),
            ("에너지 길잡이", "에너지 활용", "필요한 곳에 전기를 연결함"),
        ],
        "flow": ["태양광", "전기 생산", "저장", "활용"],
        "value": "햇빛으로 만든 전기와 에너지 창고가 함께하면, 필요한 때에 에너지를 더 알뜰하게 사용할 수 있어요. 그래서 깨끗한 에너지를 오래 이어가는 데 도움을 준답니다.",
        "companies": ["한화솔루션", "한화에너지"],
    },
}


class StoryGenerationError(RuntimeError):
    """Safe, user-facing error for Gemini generation failures."""

    def __init__(self, message: str, kind: str = "api", detail: str = "") -> None:
        super().__init__(message)
        self.kind = kind
        self.detail = detail


class ImageGenerationError(RuntimeError):
    """Safe, user-facing error for optional illustration failures."""

    def __init__(self, message: str, kind: str = "image") -> None:
        super().__init__(message)
        self.kind = kind


def _knowledge_context(knowledge: dict[str, str]) -> str:
    return "\n\n".join(f"===== {name} =====\n{text}" for name, text in knowledge.items())


def _get_api_key() -> str | None:
    """Read the key from local environment or Streamlit Cloud Secrets."""
    for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        api_key = os.getenv(key_name)
        if api_key:
            return api_key.strip()
    try:
        import streamlit as st
        for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            value = st.secrets.get(key_name)
            if value:
                return str(value).strip()
    except Exception:
        pass
    return None


def _build_prompt(scenario: str, knowledge: dict[str, str], previous_story: dict[str, Any] | None = None) -> str:
    scenario_name = SAMPLE_STORIES.get(scenario, {}).get("name", scenario)
    scenario_description = SAMPLE_STORIES.get(scenario, {}).get("description", "")
    previous_context = ""
    if previous_story:
        previous_context = f"""
Previous generated version (use only to avoid repetition; keep its factual basis, but do not copy it):
- Title: {previous_story.get('story_title', '')}
- Opening excerpt: {str(previous_story.get('story', ''))[:500]}
"""
    return f"""You are Hanwha Tech Storyteller.

Translate how multiple Hanwha technologies connect to achieve one purpose into a story understandable to children aged 7-10.
Use the provided Knowledge as the primary factual source. Creative characters, dialogue and settings are allowed, but never invent Hanwha companies or technologies and never distort the role or relationship of real technologies.
Transformation: Technology -> Process -> Story -> Understanding -> Value.

Selected scenario: {scenario_name}
Scenario question: {scenario_description}

Rules:
    - Write a warm Korean children's story of 1,200-1,500 Korean characters (never summarize or shorten) with the flow: beginning -> mission/problem -> technology cooperation -> resolution -> value.
    - Divide the story into exactly 5 substantial paragraphs. Separate every paragraph with a blank line (two newline characters) in the JSON story string.
    - Minimize technical jargon and explain real technology after the story.
    - Keep the story warm, imaginative and fairy-tale-like. Creative character names, personification and playful nicknames are welcome when they are easy to understand from context.
    - Avoid only opaque or confusing coined words. When a technical term or playful nickname may be unfamiliar, explain its meaning naturally in the surrounding sentence while keeping the child-friendly tone.
- For defense content, focus on protection, safety, cooperation, risk discovery, accurate judgment and mission completion. Do not describe weapons operation, attack procedures, destruction or harm.
- Use only companies and technologies supported by the Knowledge. Do not add unsupported entities.
- Keep the same technical facts and process, but create a genuinely different title, character expressions, dialogue and event progression from any previous version.
- Return ONLY one valid JSON object. Do not wrap it in Markdown code fences and do not add commentary before or after it.

Required JSON schema:
{{
  "story_title": "string",
  "story": "string",
  "technologies": [{{"story_element": "string", "technology": "string", "role": "string"}}],
  "process": ["string"],
  "value": "string",
  "companies": ["string"]
}}

Knowledge:
{_knowledge_context(knowledge)}
{previous_context}
"""


def _parse_story(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    try:
        result = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        # Be tolerant if a model adds a short sentence around an otherwise valid JSON object.
        try:
            start, end = cleaned.find("{"), cleaned.rfind("}")
            if start < 0 or end <= start:
                raise ValueError
            result = json.loads(cleaned[start : end + 1])
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            print("Gemini JSON parsing error: invalid JSON response")
            raise StoryGenerationError("이야기 생성 중 오류가 발생했습니다. 터미널 로그를 확인해 주세요.", "parse") from exc
    required = ("story_title", "story", "technologies", "process", "value", "companies")
    if not isinstance(result, dict) or any(key not in result for key in required):
        raise StoryGenerationError("Gemini 응답 형식이 올바르지 않아요. 잠시 후 다시 시도해 주세요.", "parse")
    if not isinstance(result["technologies"], list) or not isinstance(result["process"], list) or not isinstance(result["companies"], list):
        print("Gemini JSON parsing error: required fields have invalid types")
        raise StoryGenerationError("이야기 생성 중 오류가 발생했습니다. 터미널 로그를 확인해 주세요.", "parse")
    print("JSON parsing success")
    return result


def generate_story(
    scenario: str,
    knowledge: dict[str, str],
    previous_story: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a story with Gemini using the loaded Markdown knowledge."""
    print(f"Gemini API request started (scenario={scenario}, model={GEMINI_MODEL})")
    api_key = _get_api_key()
    if not api_key:
        print("Gemini error: GEMINI_API_KEY is not set")
        raise StoryGenerationError("이야기 생성 중 오류가 발생했습니다. 터미널 로그를 확인해 주세요.", "missing_key")
    if scenario not in SAMPLE_STORIES:
        raise StoryGenerationError("선택한 시나리오를 찾지 못했어요.", "input")

    try:
        client = genai.Client(api_key=api_key)
        prompt = _build_prompt(scenario, knowledge, previous_story)
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            max_output_tokens=8192,
        )
        try:
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt, config=config)
        except Exception as model_error:
            # Some API keys do not have access to the newest model alias. Retry
            # with the widely available stable model before showing an error.
            model_message = str(model_error).lower()
            if GEMINI_MODEL != "gemini-2.5-flash" and any(token in model_message for token in ("404", "not_found", "not found", "permission")):
                print("Gemini primary model unavailable; retrying with gemini-2.5-flash")
                response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=config)
            else:
                raise
        print("Gemini response received")
        text = getattr(response, "text", None)
        if not text:
            raise StoryGenerationError("Gemini가 비어 있는 응답을 보냈어요. 잠시 후 다시 시도해 주세요.", "api")
        return _parse_story(text)
    except StoryGenerationError:
        raise
    except Exception as exc:
        message = str(exc).lower()
        safe_detail = str(exc).replace(api_key, "[REDACTED]")
        print(f"Gemini error: {type(exc).__name__}: {safe_detail}")
        if "429" in message or "quota" in message or "rate" in message or "resource exhausted" in message:
            raise StoryGenerationError("Gemini 사용량이 잠시 제한되었어요. 잠시 후 다시 시도해 주세요.", "rate_limit") from exc
        if "404" in message or "not_found" in message or "no longer available" in message:
            raise StoryGenerationError("현재 Gemini 모델을 사용할 수 없어요. GEMINI_MODEL 설정을 확인해 주세요.", "model") from exc
        if "timeout" in message or "connection" in message or "network" in message:
            raise StoryGenerationError("Gemini 서버와 연결하지 못했어요. 인터넷 연결을 확인한 뒤 다시 시도해 주세요.", "network") from exc
        raise StoryGenerationError("Gemini 이야기를 만들지 못했어요. API 설정과 네트워크를 확인한 뒤 다시 시도해 주세요.", "api", safe_detail) from exc


# Gemini image generation model confirmed through the installed google-genai SDK.
IMAGE_MODEL = "gemini-3.1-flash-image"


def generate_story_image(scenario: str, story: dict[str, Any]) -> bytes:
    """Generate one PNG illustration for a completed story.

    The current SDK supports image output through models.generate_content with
    response_modalities=["IMAGE"]. The returned bytes are kept in session_state.
    """
    api_key = _get_api_key()
    if not api_key:
        print("Gemini image error: GEMINI_API_KEY is not set")
        raise ImageGenerationError("삽화 생성에 필요한 API 키가 없습니다.", "missing_key")

    technologies = story.get("technologies", [])
    technology_context = ", ".join(
        f"{item.get('story_element', '')}({item.get('technology', '')})"
        for item in technologies if isinstance(item, dict)
    )
    prompt = f"""Create one landscape illustration for a Korean children's science story (ages 7-10).
Scenario: {scenario}
Story title: {story.get('story_title', '')}
Story scene summary: {str(story.get('story', ''))[:900]}
Main technology friends: {technology_context}

Style: warm, friendly, polished digital picture-book illustration; clean shapes; sophisticated but approachable; symbolic depiction of technology cooperation; no long text, labels, logos, or letters in the image.
For defense scenes, show protection, teamwork, safety, observation and wise decisions only. Do not show realistic weapons, attacks, explosions, destruction, injuries or damage.
"""
    print(f"Gemini image request started (model={IMAGE_MODEL})")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="4:3"),
            ),
        )
        print("Gemini image response received")
        for part in response.parts or []:
            if getattr(part, "inline_data", None):
                image = part.as_image()
                buffer = BytesIO()
                image.save(buffer, format="PNG")
                print("Gemini image bytes ready")
                return buffer.getvalue()
        raise ImageGenerationError("Gemini가 삽화를 반환하지 않았어요.", "empty")
    except ImageGenerationError:
        raise
    except Exception as exc:
        safe_detail = str(exc).replace(api_key, "[REDACTED]")
        print(f"Gemini image error: {type(exc).__name__}: {safe_detail}")
        message = str(exc).lower()
        if "429" in message or "quota" in message or "rate" in message:
            raise ImageGenerationError("이미지 생성 사용량이 제한되었습니다.", "rate_limit") from exc
        if "timeout" in message or "connection" in message or "network" in message:
            raise ImageGenerationError("이미지 생성 네트워크 오류가 발생했습니다.", "network") from exc
        raise ImageGenerationError("Gemini 삽화를 생성하지 못했어요.", "api") from exc

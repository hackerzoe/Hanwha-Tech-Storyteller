from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from utils import SAMPLE_STORIES, StoryGenerationError, generate_story, load_knowledge


PROJECT_ROOT = Path(__file__).resolve().parent
STORY_IMAGES = {
    "ocean": PROJECT_ROOT / "1.png",
    "space": PROJECT_ROOT / "2.png",
    "solar": PROJECT_ROOT / "3.png",
}
STORY_RESULT_IMAGES = {
    "ocean": PROJECT_ROOT / "11.png",
    "space": PROJECT_ROOT / "12.png",
    "solar": PROJECT_ROOT / "13.png",
}
STORY_MARKERS = {
    "ocean": '<svg class="marker-shield" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2 4 5v6c0 5.5 3.7 10.2 8 11 4.3-.8 8-5.5 8-11V5l-8-3Z"/></svg>',
    "space": "🚀",
    "solar": "☀",
}


def image_data_uri(path: Path) -> str:
    """Return a local image as a data URI so it can be used as an HTML background."""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


st.set_page_config(
    page_title="Hanwha Tech Storyteller",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def apply_style() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: linear-gradient(145deg, #f8fbff 0%, #fffdf6 100%); color: #162b49; }
        .block-container { max-width: 1050px; padding-top: .4rem; padding-bottom: 4rem; }
        #MainMenu, footer, header { visibility: hidden; }
        .brand { color: #0d2d53; font-size: 0.9rem; font-weight: 800; letter-spacing: .12em; }
        .hero { text-align: center; padding: 0 0 1.5rem; }
        .hero h1 { color: #0d2d53; font-size: clamp(2.1rem, 5vw, 3.6rem); margin: .45rem 0 .7rem; letter-spacing: -.055em; }
        .hero p { color: #5e7188; font-size: 1.08rem; line-height: 1.7; margin: 0; }
        .section-title { color: #0d2d53; font-size: 1.55rem; font-weight: 800; text-align: center; margin: 1.5rem 0 1.2rem; }
        .card { background: #ffffff; border: 1px solid #e1e8f0; border-radius: 18px; padding: 1.4rem; min-height: 185px; box-shadow: 0 7px 20px rgba(18, 52, 90, .055); }
        .card.selected { border: 2px solid #f2ab00; background: #fffaf0; box-shadow: 0 10px 25px rgba(242, 171, 0, .16); }
        .card-icon { font-size: 2.15rem; margin-bottom: .45rem; }
        .scenario-image { width: 100%; height: 155px; object-fit: cover; border-radius: 12px; margin-bottom: .9rem; }
        .scenario-visual { min-height: 370px; border-radius: 12px; overflow: hidden; background-position: center; background-size: cover; position: relative; display: flex; align-items: flex-start; }
        .scenario-visual::after { content: ""; position: absolute; inset: 0; background: transparent; }
        .scenario-overlay { position: relative; z-index: 1; width: 100%; padding: 3rem 1rem 1.5rem; text-align: left; }
        .scenario-marker { color: #f2a900; font-size: 1.5rem; font-weight: 800; line-height: 1; margin-bottom: .55rem; }
        .marker-shield { display: block; width: 1.35rem; height: 1.35rem; fill: currentColor; }
        .scenario-overlay .card-icon { margin-bottom: .3rem; }
        .selected-story-banner { min-height: 300px; border-radius: 16px; overflow: hidden; background-position: center; background-size: cover; position: relative; display: flex; align-items: center; justify-content: center; text-align: center; }
        .selected-story-banner::after { content: ""; position: absolute; inset: 0; background: transparent; }
        .selected-story-banner-content { position: relative; z-index: 1; padding: 2rem; }
        .story-image { width: 100%; max-height: 420px; object-fit: cover; border-radius: 16px; margin: 1rem 0 1.5rem; }
        .card-title { color: #102f54; font-size: 1.15rem; font-weight: 800; margin-bottom: .45rem; }
        .card-desc { color: #111827; font-size: .91rem; line-height: 1.6; }
        .selected-badge { color: #a36c00; font-size: .78rem; font-weight: 800; margin-top: .55rem; }
        div.stButton > button { border-radius: 10px; border: 1px solid #efad07; background: #ffbd10; color: #102f54; font-weight: 800; min-height: 2.75rem; width: 100%; }
        div.stButton > button:hover { border-color: #d39400; background: #ffd04c; color: #102f54; }
        /* One white scenario card with an in-card top-right action area. */
        div[class*="st-key-scenario-card-"] { position: relative !important; min-height: 430px; padding: 1.35rem !important; background: #fff; border: 1px solid #e1e8f0; border-radius: 18px; box-shadow: 0 7px 20px rgba(18, 52, 90, .055); }
        div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; }
        div[class*="st-key-scenario-card-"] .scenario-content { min-height: 185px; padding-top: .2rem; text-align: center; display: flex; flex-direction: column; justify-content: center; }
        div[class*="st-key-scenario-card-"] .scenario-content .card-icon { margin-bottom: .7rem; }
        div[class*="st-key-scenario-card-"] div.stButton { position: relative !important; top: -370px !important; z-index: 10 !important; margin: 0 !important; width: 150px !important; display: block !important; transform: translateX(calc(100% - 2.5rem)) !important; }
        div[class*="st-key-scenario-card-"] div.stButton > button { width: auto; min-width: 112px; min-height: 0; height: 2.15rem; white-space: nowrap; padding: .25rem .65rem; margin-right: .5rem; background: #f2a900; border-color: #e19b00; color: #fff; font-size: .7rem; }
        div[class*="st-key-scenario-card-"] div.stButton > button:hover { background: #d99200; color: #fff; }
        div[class*="st-key-scenario-card-"][class*="-selected"] { border: 2px solid #f2ab00; background: #fffaf0; box-shadow: 0 10px 25px rgba(242, 171, 0, .16); }
        .story-paper { background: #ffffff; border: 1px solid #e4eaf1; border-radius: 20px; padding: clamp(1.4rem, 4vw, 2.6rem); box-shadow: 0 10px 28px rgba(18, 52, 90, .06); }
        .story-title { color: #102f54; font-size: clamp(1.65rem, 4vw, 2.35rem); font-weight: 800; text-align: center; margin: .5rem 0 1.5rem; }
        .story-text { color: #344b66; font-size: 1.06rem; line-height: 2.05; white-space: pre-wrap; }
        .eyebrow { color: #b27a00; font-size: .78rem; font-weight: 800; letter-spacing: .1em; text-align: center; }
        .flow { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: .55rem; margin: 1.3rem 0 2rem; }
        .flow-step { background: #eaf2fa; color: #153d68; border-radius: 999px; padding: .6rem .9rem; font-size: .9rem; font-weight: 800; }
        .arrow { color: #eda900; font-size: 1.35rem; font-weight: 800; }
        .value-box { border-left: 5px solid #ffbd10; background: #fffaf0; border-radius: 0 15px 15px 0; padding: 1.15rem 1.3rem; color: #42576e; line-height: 1.8; }
        .company { display: inline-block; background: #0d2d53; color: #fff; border-radius: 999px; padding: .48rem .9rem; margin: .2rem .35rem .2rem 0; font-size: .88rem; font-weight: 700; }
        .knowledge-note { color: #708196; text-align: center; font-size: .78rem; margin-top: 1.3rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def get_knowledge() -> tuple[dict[str, str], list[str]]:
    return load_knowledge()


def choose_scenario(scenario: str, knowledge: dict[str, str]) -> None:
    st.session_state["selected_scenario"] = scenario
    st.session_state["generated_image"] = None
    st.session_state["image_notice"] = None
    try:
        with st.spinner("이야기 생성 중... 잠시만 기다려 주세요"):
            st.session_state["generated_story"] = generate_story(scenario, knowledge)
    except StoryGenerationError as error:
        st.session_state["generated_story"] = None
        st.session_state["generation_error"] = str(error)
        st.session_state["page"] = "home"
    else:
        st.session_state["generation_error"] = None
        st.session_state["page"] = "result"


def show_home() -> None:
    st.markdown(
        """<div class="hero"><h1>Hanwha Tech Storyteller</h1>
        <p><b>어려운 기술을 재미있는 이야기로 만나보세요.</b><br>
        한화의 다양한 기술이 서로 힘을 합쳐 어떤 가치를 만드는지 이야기로 알아볼까요?</p></div>""",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title">어떤 기술 이야기가 궁금한가요?</div>', unsafe_allow_html=True)

    selected = st.session_state.get("selected_scenario")
    columns = st.columns(3, gap="large")
    for column, (scenario_id, story) in zip(columns, SAMPLE_STORIES.items()):
        is_selected = scenario_id == selected
        with column:
            # Keep the selection button inside the bordered scenario area.
            card_key = f"scenario-card-{scenario_id}-selected" if is_selected else f"scenario-card-{scenario_id}"
            with st.container(key=card_key):
                story_image = STORY_IMAGES.get(scenario_id)
                image_uri = image_data_uri(story_image) if story_image and story_image.is_file() else ""
                description = story["description"]
                if scenario_id == "space":
                    description = description.replace("우주로 올라가서 자신의", "우주로 올라가서<br>자신의")
                    description = description.replace("\\n", "<br>")
                if image_uri:
                    st.markdown(
                        f'''<style>
                        div.st-key-{card_key} {{ background-image: url('{image_uri}') !important; background-size: cover !important; background-position: center !important; padding: 0 !important; overflow: hidden !important; }}
                        div.st-key-{card_key} .scenario-visual {{ border-radius: 0; }}
                        </style>''',
                        unsafe_allow_html=True,
                    )
                badge = '<div class="selected-badge">✓ 선택한 이야기</div>' if is_selected else ""
                st.markdown(
                    f'''<div class="scenario-visual" style="background-image:none"><div class="scenario-overlay">
                    <div class="scenario-marker">{STORY_MARKERS[scenario_id]}</div>
                    <div class="card-title">{story['name']}</div>
                    <div class="card-desc">{description}</div>{badge}</div></div>''',
                    unsafe_allow_html=True,
                )
                # Keep the action in-flow, below the card content, aligned right.
                button_spacer, button_area = st.columns([0.1, 3.9], gap="small")
                with button_area:
                    st.button("이 이야기로 →", key=f"select_{scenario_id}", on_click=choose_scenario, args=(scenario_id, st.session_state["knowledge"]))

    st.write("")
    if selected:
        selected_name = SAMPLE_STORIES[selected]["name"]
        selected_image = STORY_IMAGES.get(selected)
        selected_uri = image_data_uri(selected_image) if selected_image and selected_image.is_file() else ""
        st.markdown(
            f'''<div class="selected-story-banner" style="background-image:url('{selected_uri}')">
            <div class="selected-story-banner-content"><div class="card-title">{selected_name}</div><div class="card-desc">선택한 이야기로 정해졌어요</div></div></div>''',
            unsafe_allow_html=True,
        )
        if st.button("✨ 이야기 만나보기", key="show_story", type="primary"):
            with st.spinner("한화 기술을 재미있는 이야기로 번역하고 있어요..."):
                try:
                    result = generate_story(selected, st.session_state["knowledge"])
                except StoryGenerationError as error:
                    st.session_state["generated_story"] = None
                    st.session_state["page"] = "home"
                    # Keep detailed cause in the terminal, but do not expose tracebacks or secrets in UI.
                    print(f"Story generation failed ({error.kind})")
                    st.error("이야기 생성 중 오류가 발생했습니다. 터미널 로그를 확인해 주세요.")
                else:
                    st.session_state["generated_story"] = result
                    # Image generation is intentionally disabled for now: the current account's
                    # image quota is zero, while text generation is available and healthy.
                    st.session_state["generated_image"] = None
                    st.session_state["image_notice"] = None
                    st.session_state["page"] = "result"
                    print("Story saved to session_state['generated_story']")
                    st.rerun()
    else:
        st.caption("카드를 하나 골라 이야기의 문을 열어 보세요.")


    st.markdown('<div class="brand" style="text-align:center; margin-top:2rem;">HANWHA TECH EXPERIENCE</div>', unsafe_allow_html=True)


def show_story() -> None:
    result = st.session_state.get("generated_story")
    if not result:
        st.error("생성된 이야기가 없습니다. 메인 화면에서 다시 시도해 주세요.")
        return
    st.markdown('<div class="brand">HANWHA TECH EXPERIENCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">✨ 오늘의 기술 이야기</div>', unsafe_allow_html=True)
    selected_scenario = st.session_state.get("selected_scenario")
    story_image = STORY_RESULT_IMAGES.get(selected_scenario)
    if story_image and story_image.is_file():
        st.image(str(story_image), use_container_width=True)
    st.markdown(
        f'<div class="story-paper"><div class="story-title">{result["story_title"]}</div></div>',
        unsafe_allow_html=True,
    )
    image = st.session_state.get("generated_image")
    if image:
        st.image(image, use_container_width=True)
    elif st.session_state.get("image_notice"):
        st.info(st.session_state["image_notice"])
    story_text = str(result["story"]).replace("\\n", "\n")
    if "\n" in story_text and "\n\n" not in story_text:
        story_text = story_text.replace("\n", "\n\n")
    elif "\n" not in story_text:
        sentences = [sentence.strip() for sentence in story_text.split("。") if sentence.strip()]
        story_text = "。\n\n".join("。".join(sentences[index:index + 2]) for index in range(0, len(sentences), 2))
    st.markdown(f'<div class="story-paper"><div class="story-text">{story_text}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">이야기 속 진짜 기술</div>', unsafe_allow_html=True)
    st.dataframe(
        result["technologies"],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown('<div class="section-title">기술 친구들은 이렇게 힘을 합쳐요</div>', unsafe_allow_html=True)
    flow_html = []
    for index, step in enumerate(result["process"]):
        flow_html.append(f'<span class="flow-step">{step}</span>')
        if index < len(result["process"]) - 1:
            flow_html.append('<span class="arrow">→</span>')
    st.markdown(f'<div class="flow">{"".join(flow_html)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">이 기술이 만드는 가치</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="value-box">{result["value"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">함께하는 한화 기술</div>', unsafe_allow_html=True)
    companies = "".join(f'<span class="company">{company}</span>' for company in result["companies"])
    st.markdown(f'<div style="text-align:center">{companies}</div>', unsafe_allow_html=True)
    st.write("")
    regenerate_col, back_col = st.columns(2, gap="medium")
    with regenerate_col:
        regenerate = st.button("🔄 다시 이야기 만들기", key="regenerate_story", type="primary")
    with back_col:
        go_back = st.button("← 다른 이야기 만나보기", key="back_to_home")

    if regenerate:
        selected_scenario = st.session_state.get("selected_scenario")
        previous_story = st.session_state.get("generated_story")
        with st.spinner("새로운 기술 이야기를 만들고 있어요..."):
            try:
                regenerated = generate_story(
                    selected_scenario,
                    st.session_state["knowledge"],
                    previous_story=previous_story,
                )
            except StoryGenerationError as error:
                # Keep the previous result intact on failure.
                print(f"Story regeneration failed ({error.kind})")
                st.error("이야기 생성 중 오류가 발생했습니다. 기존 이야기를 유지합니다.")
            else:
                st.session_state["generated_story"] = regenerated
                st.session_state["generated_image"] = None
                st.session_state["image_notice"] = None
                print("Regenerated story replaced session_state['generated_story']")
                st.rerun()

    if go_back:
        st.session_state["page"] = "home"
        st.session_state["selected_scenario"] = None
        st.session_state["generated_story"] = None
        st.session_state["generated_image"] = None
        st.session_state["image_notice"] = None
        st.rerun()


def main() -> None:
    apply_style()
    knowledge, missing_files = get_knowledge()
    if missing_files:
        st.warning("Knowledge 파일을 찾을 수 없습니다: " + ", ".join(missing_files))

    st.session_state.knowledge = knowledge
    if "selected_scenario" not in st.session_state:
        st.session_state["selected_scenario"] = None
    if "generated_story" not in st.session_state:
        st.session_state["generated_story"] = None
    if "generated_image" not in st.session_state:
        st.session_state["generated_image"] = None
    if "image_notice" not in st.session_state:
        st.session_state["image_notice"] = None
    if "page" not in st.session_state:
        st.session_state["page"] = "home"

    if st.session_state["page"] == "result":
        show_story()
    else:
        show_home()

    st.markdown('<div class="knowledge-note">샘플 이야기 모드 · 다음 단계에서 Knowledge와 LLM을 연결할 수 있습니다.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

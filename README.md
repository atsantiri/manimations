atsantiri - ACTAR animation with Manim (https://docs.manim.community)

- Install Manim using uv following the instructions on https://docs.manim.community/en/stable/installation/uv.html
- Activate the uv virtual environment:
    - If running for the first time, in the manimations directory run: uv sync
    - If you have executed the script before and the manimations/.venv directory exists, then : source .venv/bin/activate
- Execute script:
    - cd actar
    - manim -pql actar_decay.py ACTARDecay
"""
CK3 DNA Generator - Flet 0.84 + Ollama
Sin llama-cpp-python, usa la API REST de Ollama en https://vea1ql81travn6-11434.proxy.runpod.net/
"""

import flet as ft
import threading
import base64
import json
import re
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# ── Crusader Kings 3 color palette ───────────────────────────────────────────
BG      = "#0e0b08"   # Deep black parchment
PANEL   = "#181410"   # Dark aged wood
CARD    = "#251c0f"   # Leather brown
ACCENT  = "#c8922a"   # CK3 heraldic gold
ACCENT2 = "#8b1a1a"   # Royal crimson
TXT     = "#e8d5a3"   # Warm parchment
MUTED   = "#7a6548"   # Aged ink
SUCCESS = "#7ab648"   # Heraldic green
WARN    = "#d4801a"   # Amber
BORDER  = "#5a3e20"   # Gold-tinted border
GOLD_DIM= "#6b4f1a"   # Dimmed gold for inactive

# ── Estado ────────────────────────────────────────────────────────────────────
class State:
    image_path = ""
    gender = "female"
    dna_result = ""
    ollama_model = "llava"

state = State()

# ── Prompt ────────────────────────────────────────────────────────────────────
def build_prompt(gender):
    return f"""Look at this face photo carefully and analyze the actual person's features.
Gender: {gender}.

Respond ONLY with valid JSON (no markdown, no explanation). Use ONLY the allowed values listed below.

{{
  "face_shape": "<oval|round|square|heart|diamond>",
  "skin_tone": "<very_light|light|medium|olive|brown|dark>",
  "eye_color": "<blue|blue_green|green|hazel|brown|dark_brown>",
  "hair_color": "<blonde|light_brown|brown|dark_brown|black|red|auburn>",
  "nose_type": "<small|medium|wide|narrow|upturned>",
  "jaw_type": "<soft|medium|strong|square>",
  "cheekbones": "<low|medium|high|prominent>",
  "eye_shape": "<almond|round|hooded|deep_set|wide_set>",
  "lips": "<thin|medium|full>",
  "age_estimate": "<young|young_adult|adult|middle|older>"
}}

Analyze the REAL person in the photo. Do NOT copy the placeholder values in angle brackets."""

# ── DNA builder ───────────────────────────────────────────────────────────────
def build_dna_from_analysis(analysis, gender):
    import random
    HAIR = {"blonde":"210 210 210 210","light_brown":"190 190 190 190","brown":"180 207 180 207",
            "dark_brown":"150 170 150 170","black":"120 140 120 140","red":"30 30 30 30","auburn":"35 20 25 25"}
    SKIN = {"very_light":"220 170 220 170","light":"200 155 200 155","medium":"141 103 141 103",
            "olive":"160 110 160 110","brown":"100 65 100 65","dark":"80 45 80 45"}
    EYE  = {"blue":"200 200 200 200","blue_green":"170 190 170 190","green":"100 100 100 100",
            "hazel":"90 90 90 90","brown":"28 132 28 132","dark_brown":"15 80 15 80"}

    hair = HAIR.get(analysis.get("hair_color","brown"), "180 207 180 207")
    skin = SKIN.get(analysis.get("skin_tone","medium"),  "141 103 141 103")
    eye  = EYE.get(analysis.get("eye_color","brown"),    "28 132 28 132")

    jaw   = analysis.get("jaw_type","medium")
    lips  = analysis.get("lips","medium")
    nose  = analysis.get("nose_type","medium")
    cheek = analysis.get("cheekbones","medium")
    eye_s = analysis.get("eye_shape","almond")

    jaw_a   = 149 if jaw in ("strong","square") else 108 if jaw=="soft" else 128
    jaw_w   = 117 if jaw=="soft" else 134 if jaw=="square" else 128
    lip_u   = 200 if lips=="full" else 80 if lips=="thin" else 128
    lip_l   = 80  if lips=="thin" else 150 if lips=="full" else 94
    nose_f  = 108 if nose=="upturned" else 140 if nose=="wide" else 120
    cheek_h = 38  if cheek in ("high","prominent") else 100 if cheek=="low" else 70
    eye_sz  = 71  if eye_s=="hooded" else 100 if eye_s=="round" else 85
    eye_fold= 164 if eye_s=="almond" else 100

    seed = random.randint(1000000000, 9999999999)
    g = 128
    dna = (
        f'ruler_designer_{seed}={{\n'
        f'\ttype={gender}\n\tid=0\n\trandom_seed=0\n'
        f'\tgenes={{\n'
        f'\t\thair_color={{ {hair} }}\n'
        f'\t\tskin_color={{ {skin} }}\n'
        f'\t\teye_color={{ {eye} }}\n'
        f'\t\tgene_chin_forward={{ "chin_forward_neg" {g} "chin_forward_neg" {g} }}\n'
        f'\t\tgene_chin_height={{ "chin_height_neg" {g} "chin_height_neg" {g} }}\n'
        f'\t\tgene_chin_width={{ "chin_width_pos" {g} "chin_width_pos" {g} }}\n'
        f'\t\tgene_eye_angle={{ "eye_angle_neg" {g} "eye_angle_neg" {g} }}\n'
        f'\t\tgene_eye_depth={{ "eye_depth_neg" {g} "eye_depth_neg" {g} }}\n'
        f'\t\tgene_eye_height={{ "eye_height_pos" {g} "eye_height_pos" {g} }}\n'
        f'\t\tgene_eye_distance={{ "eye_distance_pos" {g} "eye_distance_pos" {g} }}\n'
        f'\t\tgene_eye_shut={{ "eye_shut_neg" {g} "eye_shut_neg" {g} }}\n'
        f'\t\tgene_forehead_angle={{ "forehead_angle_pos" {g} "forehead_angle_pos" {g} }}\n'
        f'\t\tgene_forehead_brow_height={{ "forehead_brow_height_pos" {g} "forehead_brow_height_pos" {g} }}\n'
        f'\t\tgene_forehead_roundness={{ "forehead_roundness_neg" {g} "forehead_roundness_neg" {g} }}\n'
        f'\t\tgene_forehead_width={{ "forehead_width_neg" {g} "forehead_width_neg" {g} }}\n'
        f'\t\tgene_forehead_height={{ "forehead_height_neg" {g} "forehead_height_neg" {g} }}\n'
        f'\t\tgene_head_height={{ "head_height_neg" {g} "head_height_neg" {g} }}\n'
        f'\t\tgene_head_width={{ "head_width_pos" {g} "head_width_pos" {g} }}\n'
        f'\t\tgene_head_profile={{ "head_profile_pos" {g} "head_profile_pos" {g} }}\n'
        f'\t\tgene_head_top_height={{ "head_top_height_pos" {g} "head_top_height_pos" {g} }}\n'
        f'\t\tgene_head_top_width={{ "head_top_width_pos" {g} "head_top_width_pos" {g} }}\n'
        f'\t\tgene_jaw_angle={{ "jaw_angle_pos" {jaw_a} "jaw_angle_pos" {jaw_a} }}\n'
        f'\t\tgene_jaw_forward={{ "jaw_forward_pos" {g} "jaw_forward_pos" {g} }}\n'
        f'\t\tgene_jaw_height={{ "jaw_height_neg" {g} "jaw_height_neg" {g} }}\n'
        f'\t\tgene_jaw_width={{ "jaw_width_neg" {jaw_w} "jaw_width_neg" {jaw_w} }}\n'
        f'\t\tgene_mouth_corner_depth={{ "mouth_corner_depth_pos" {g} "mouth_corner_depth_pos" {g} }}\n'
        f'\t\tgene_mouth_corner_height={{ "mouth_corner_height_pos" {g} "mouth_corner_height_pos" {g} }}\n'
        f'\t\tgene_mouth_forward={{ "mouth_forward_neg" {g} "mouth_forward_neg" {g} }}\n'
        f'\t\tgene_mouth_height={{ "mouth_height_pos" {g} "mouth_height_pos" {g} }}\n'
        f'\t\tgene_mouth_width={{ "mouth_width_neg" {g} "mouth_width_neg" {g} }}\n'
        f'\t\tgene_mouth_upper_lip_size={{ "mouth_upper_lip_size_pos" {lip_u} "mouth_upper_lip_size_pos" {lip_u} }}\n'
        f'\t\tgene_mouth_lower_lip_size={{ "mouth_lower_lip_size_neg" {lip_l} "mouth_lower_lip_size_neg" {lip_l} }}\n'
        f'\t\tgene_mouth_open={{ "mouth_open_neg" 3 "mouth_open_neg" 3 }}\n'
        f'\t\tgene_neck_length={{ "neck_length_neg" {g} "neck_length_neg" {g} }}\n'
        f'\t\tgene_neck_width={{ "neck_width_neg" {g} "neck_width_neg" {g} }}\n'
        f'\t\tgene_bs_cheek_forward={{ "cheek_forward_pos" {g} "cheek_forward_pos" {g} }}\n'
        f'\t\tgene_bs_cheek_height={{ "cheek_height_neg" {cheek_h} "cheek_height_neg" {cheek_h} }}\n'
        f'\t\tgene_bs_cheek_width={{ "cheek_width_neg" {g} "cheek_width_neg" {g} }}\n'
        f'\t\tgene_bs_nose_forward={{ "nose_forward_neg" {nose_f} "nose_forward_neg" {nose_f} }}\n'
        f'\t\tgene_bs_nose_height={{ "nose_height_neg" {g} "nose_height_neg" {g} }}\n'
        f'\t\tgene_bs_nose_length={{ "nose_length_pos" {g} "nose_length_pos" {g} }}\n'
        f'\t\tgene_bs_nose_size={{ "nose_size_neg" {g} "nose_size_neg" {g} }}\n'
        f'\t\tgene_bs_nose_tip_width={{ "nose_tip_width_neg" {g} "nose_tip_width_neg" {g} }}\n'
        f'\t\tgene_bs_jaw_def={{ "jaw_def_neg" {g} "jaw_def_neg" {g} }}\n'
        f'\t\tgene_bs_eye_fold_shape={{ "eye_fold_shape_pos" {eye_fold} "eye_fold_shape_pos" {eye_fold} }}\n'
        f'\t\tgene_bs_eye_size={{ "eye_size_pos" {eye_sz} "eye_size_pos" {eye_sz} }}\n'
        f'\t\tface_detail_cheek_def={{ "cheek_def_02" {g} "cheek_def_02" {g} }}\n'
        f'\t\tface_detail_eye_socket={{ "eye_socket_03" {g} "eye_socket_03" {g} }}\n'
        f'\t\tface_detail_nasolabial={{ "nasolabial_03" {g} "nasolabial_03" {g} }}\n'
        f'\t\tface_detail_nose_tip_def={{ "nose_tip_def" {g} "nose_tip_def" {g} }}\n'
        f'\t\tface_detail_temple_def={{ "temple_def" {g} "temple_def" {g} }}\n'
        f'\t\tcomplexion={{ "complexion_3" {g} "complexion_3" {g} }}\n'
        f'\t\tgene_height={{ "normal_height" {g} "normal_height" {g} }}\n'
        f'\t\tgene_age={{ "old_4" 50 "old_4" 50 }}\n'
        f'\t\tgene_eyebrows_shape={{ "far_spacing_low_thickness" {g} "far_spacing_low_thickness" {g} }}\n'
        f'\t\tgene_eyebrows_fullness={{ "layer_2_high_thickness" {g} "layer_2_high_thickness" {g} }}\n'
        f'\t\tgene_hair_type={{ "hair_wavy" {g} "hair_wavy" {g} }}\n'
        f'\t\teye_accessory={{ "normal_eyes" 199 "normal_eyes" 199 }}\n'
        f'\t\tteeth_accessory={{ "normal_teeth" 0 "normal_teeth" 0 }}\n'
        f'\t\televishas_accessory={{ "normal_eyelashes" 195 "normal_eyelashes" 195 }}\n'
        f'\t\thairstyles={{ "western_hairstyles_straight" 255 "all_hairstyles" 0 }}\n'
        f'\t}}\n'
        f'\toverride={{\n\t\tportrait_modifier_overrides={{\n'
        f'\t\t\tcustom_hair={"female_hair_western_10" if gender == "female" else "male_hair_western_10"}\n'
        f'\t\t}}\n\t}}\n\tentity={{ 0 0 }}\n}}'
    )
    return dna

# ── Ollama inference ──────────────────────────────────────────────────────────
def run_ollama(image_path, gender):
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        payload = {
            "model": state.ollama_model,
            "prompt": build_prompt(gender),
            "images": [img_b64],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 300}
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://vea1ql81travn6-11434.proxy.runpod.net/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode())

        raw = result.get("response", "")
        print("\n====== RAW OLLAMA OUTPUT ======")
        print(raw[:400])
        print("================================\n")

        clean = re.sub(r"```json|```", "", raw).strip()
        match = re.search(r'\{[\s\S]*\}', clean)
        if match:
            try:
                analysis = json.loads(match.group())
            except json.JSONDecodeError:
                analysis = {}
        else:
            analysis = {}

        # Fallback si el modelo no devolvió campos válidos
        if not analysis.get("hair_color"):
            t = raw.lower()
            analysis["hair_color"] = "black" if "black hair" in t else "blonde" if "blonde" in t else "brown"
            analysis["eye_color"]  = "blue" if "blue" in t else "green" if "green" in t else "brown"
            analysis["skin_tone"]  = "light" if ("fair" in t or "light skin" in t) else "medium"

        dna = build_dna_from_analysis(analysis, gender)
        return True, analysis, dna

    except urllib.error.URLError:
        return False, {}, "Ollama not responding. Is it running? Run: ollama serve"
    except Exception as e:
        return False, {}, str(e)

def check_ollama():
    try:
        req = urllib.request.Request("https://vea1ql81travn6-11434.proxy.runpod.net/api/tags")
        with urllib.request.urlopen(req, timeout=5) as r:
            return True, json.loads(r.read())
    except:
        return False, {}

def check_ollama_gpu():
    try:
        req = urllib.request.Request("https://vea1ql81travn6-11434.proxy.runpod.net/api/ps")
        with urllib.request.urlopen(req, timeout=5) as r:
            models = json.loads(r.read()).get("models", [])

        model_name = state.ollama_model
        if ":" not in model_name:
            model_name += ":latest"
        model = next((m for m in models if m.get("name") == model_name), None)
        if not model:
            return "unavailable"

        vram_size = int(model.get("size_vram", 0))
        if vram_size <= 0:
            return "CPU"
        return "GPU" if vram_size >= int(model.get("size", 0)) else "GPU + CPU"
    except Exception:
        return "unavailable"

# ── App ───────────────────────────────────────────────────────────────────────
async def main(page: ft.Page):
    page.title = "CK3 DNA Generator"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.window.width = 980
    page.window.height = 740
    page.padding = 0

    # ── Controles ─────────────────────────────────────────────────────────────
    model_dropdown = ft.Dropdown(
        value="llava",
        options=[
            ft.dropdown.Option("llava", "llava (recommended)"),
            ft.dropdown.Option("llava:13b", "llava:13b (more accurate)"),
            ft.dropdown.Option("llava:34b", "llava:34b (best quality)"),
            ft.dropdown.Option("moondream", "moondream (fastest)"),
        ],
        bgcolor=CARD, color=TXT,
        border_color=BORDER, focused_border_color=ACCENT,
        width=260, height=45,
    )
    model_dropdown.on_change = lambda e: setattr(state, "ollama_model", e.control.value)

    ollama_status = ft.Text("Checking Ollama...", color=MUTED, size=12)
    ollama_dot    = ft.Container(width=8, height=8, border_radius=4, bgcolor=WARN)

    img_display = ft.Image(src="placeholder", width=370, height=220,
                           fit="cover", border_radius=10, visible=False)
    img_ph = ft.Container(
        width=370, height=220, bgcolor=CARD, border_radius=10,
        content=ft.Column([
            ft.Icon(ft.Icons.PERSON, size=50, color=MUTED),
            ft.Text("No image", color=MUTED, size=12),
        ], alignment=ft.MainAxisAlignment.CENTER,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )

    btn_female = ft.FilledButton("Female", width=115,
        style=ft.ButtonStyle(bgcolor=ACCENT, color="#0e0b08",
                             shape=ft.RoundedRectangleBorder(radius=3)),
        on_click=lambda e: set_gender("female"))
    btn_male = ft.FilledButton("Male", width=115,
        style=ft.ButtonStyle(bgcolor=CARD, color=TXT,
                             shape=ft.RoundedRectangleBorder(radius=3)),
        on_click=lambda e: set_gender("male"))

    gen_btn = ft.FilledButton("✦  Generate DNA", icon=ft.Icons.AUTO_AWESOME,
        style=ft.ButtonStyle(bgcolor=ACCENT2, color=TXT,
                             shape=ft.RoundedRectangleBorder(radius=3)),
        on_click=lambda e: threading.Thread(target=analysis_thread, daemon=True).start(),
        disabled=True)
    gen_status  = ft.Text("", color=MUTED, size=12)
    gen_spinner = ft.ProgressRing(width=18, height=18, stroke_width=2,
                                  color=ACCENT, visible=False)

    traits_wrap = ft.Row(wrap=True, spacing=6, run_spacing=6)
    dna_field = ft.TextField(
        multiline=True, min_lines=5, max_lines=10, read_only=True,
        bgcolor=CARD, border_color=BORDER, color=ACCENT,
        text_style=ft.TextStyle(size=11),
        hint_text="DNA code will appear here...",
        hint_style=ft.TextStyle(color=MUTED, size=11),
        expand=True,
    )
    copy_btn = ft.FilledButton("Copy DNA", icon=ft.Icons.COPY,
        style=ft.ButtonStyle(bgcolor=GOLD_DIM, color=TXT,
                             shape=ft.RoundedRectangleBorder(radius=3)),
        on_click=lambda e: copy_dna(), disabled=True)
    copy_status = ft.Text("", color=SUCCESS, size=12)

    # ── FilePicker async ──────────────────────────────────────────────────────
    async def pick_image(e):
        files = await ft.FilePicker().pick_files(
            dialog_title="Select image",
            allowed_extensions=["jpg", "jpeg", "png", "webp"],
        )
        if files:
            state.image_path = files[0].path
            img_display.src = state.image_path
            img_display.visible = True
            img_ph.visible = False
            gen_btn.disabled = False
            gen_status.value = ""
            page.update()

    # ── Acciones ──────────────────────────────────────────────────────────────
    def set_gender(g):
        state.gender = g
        btn_female.style.bgcolor = ACCENT if g == "female" else CARD
        btn_female.style.color   = "#0e0b08" if g == "female" else TXT
        btn_male.style.bgcolor   = ACCENT if g == "male" else CARD
        btn_male.style.color     = "#0e0b08" if g == "male" else TXT
        page.update()

    def check_ollama_status():
        ok, data = check_ollama()
        if ok:
            models = [m["name"] for m in data.get("models", [])]
            has_llava = any("llava" in m for m in models)
            ollama_dot.bgcolor = SUCCESS
            ollama_status.value = f"Ollama running — models: {', '.join(models) if models else 'none'}"
            if not has_llava:
                ollama_status.value += " ⚠ llava not installed, run: ollama pull llava"
                ollama_status.color = WARN
            else:
                ollama_status.color = SUCCESS
        else:
            ollama_dot.bgcolor = ACCENT
            ollama_status.value = "Ollama not detected — run: ollama serve"
            ollama_status.color = ACCENT
        page.update()

    def analysis_thread():
        gen_btn.disabled = True
        gen_spinner.visible = True
        gen_status.value = "Sending image to Ollama..."
        gen_status.color = WARN
        traits_wrap.controls.clear()
        dna_field.value = ""
        copy_btn.disabled = True
        copy_status.value = ""
        page.update()

        ok, analysis, dna = run_ollama(state.image_path, state.gender)
        gen_spinner.visible = False

        if ok:
            state.dna_result = dna
            acceleration = check_ollama_gpu()
            gen_status.value = f"Done ({acceleration})"
            gen_status.color = WARN if acceleration == "CPU" else SUCCESS

            labels = {
                "face_shape": "Face", "skin_tone": "Skin", "eye_color": "Eyes",
                "hair_color": "Hair", "nose_type": "Nose", "jaw_type": "Jaw",
                "cheekbones": "Cheeks", "eye_shape": "Eye Shape",
                "lips": "Lips", "age_estimate": "Age",
            }
            for k, lbl in labels.items():
                val = str(analysis.get(k, "—")).replace("_", " ")
                traits_wrap.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(lbl.upper(), size=9, color=MUTED),
                            ft.Text(val, size=13, color=ACCENT,
                                    weight=ft.FontWeight.W_600),
                        ], spacing=2, tight=True),
                        bgcolor=CARD,
                        border=ft.border.all(1, BORDER),
                        border_radius=3,
                        padding=ft.Padding(12, 8, 12, 8),
                    )
                )
            dna_field.value = dna
            copy_btn.disabled = False
        else:
            gen_status.value = f"Error: {dna}"
            gen_status.color = ACCENT

        gen_btn.disabled = False
        page.update()

    def copy_dna():
        if state.dna_result:
            subprocess.Popen(['clip'], stdin=subprocess.PIPE).communicate(
                state.dna_result.encode('utf-8')
            )
            copy_status.value = "Copied!"
            page.update()

    # Verificar Ollama al arrancar
    threading.Thread(target=check_ollama_status, daemon=True).start()

    # ── Layout ────────────────────────────────────────────────────────────────
    def card(content):
        return ft.Container(
            content=content, bgcolor=PANEL, border_radius=4, padding=16,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=8, color="#00000066",
                                offset=ft.Offset(0, 2)),
        )
    def lbl(txt):
        return ft.Text(txt, size=10, color=ACCENT, weight=ft.FontWeight.W_700)

    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CASTLE, color=ACCENT, size=22),
                ft.Text("CK3 DNA Generator", size=18,
                        weight=ft.FontWeight.BOLD, color=TXT),
                ft.Container(
                    content=ft.Text("✦ PORTRAIT FORGE ✦", size=9,
                                    color=MUTED),
                    margin=ft.Margin(10, 0, 0, 0),
                ),
                ft.Container(expand=True),
                ft.Text("Ollama · local inference", size=11, color=MUTED),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=0, tight=True),
        bgcolor=PANEL, padding=ft.Padding(20, 14, 20, 14),
        border=ft.Border.only(bottom=ft.BorderSide(1, ACCENT)),
    )

    left = ft.Container(width=420, padding=16, content=ft.Column([
        # Ollama status
        card(ft.Column([
            lbl("⚔  OLLAMA STATUS"),
            ft.Container(height=8),
            ft.Row([ollama_dot, ollama_status], spacing=8,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=10),
            lbl("⚙  MODEL"),
            ft.Container(height=6),
            model_dropdown,
        ], spacing=0, tight=True)),

        ft.Container(height=12),

        # Image card — image full width, controls in separate rows
        card(ft.Column([
            lbl("🖼  REFERENCE IMAGE"),
            ft.Container(height=10),
            ft.Stack([img_ph, img_display]),
            ft.Container(height=10),
            # Row 1: Load image button
            ft.FilledButton("Load image", icon=ft.Icons.IMAGE,
                style=ft.ButtonStyle(bgcolor=CARD, color=TXT),
                on_click=pick_image,
                width=370),
            ft.Container(height=8),
            # Row 2: Gender label + both buttons visible
            ft.Row([
                ft.Text("Gender:", color=MUTED, size=12, width=55),
                btn_female,
                btn_male,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            ft.Container(height=8),
            # Row 3: Generate + status
            ft.Row([
                gen_btn,
                ft.Container(expand=True),
                gen_spinner,
                gen_status,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        ], spacing=0, tight=True)),
    ], spacing=0))

    right = ft.Container(
        expand=True,
        padding=ft.Padding(0, 16, 16, 16),
        content=ft.Column([
            card(ft.Column([
                lbl("📜  DETECTED TRAITS"),
                ft.Container(height=10),
                traits_wrap,
            ], spacing=0, tight=True)),
            ft.Container(height=12),
            card(ft.Column([
                lbl("🧬  DNA CODE — paste in CK3 Portrait Editor"),
                ft.Container(height=8),
                dna_field,
                ft.Container(height=8),
                ft.Row([copy_btn, copy_status], spacing=10,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=4),
                ft.Text("CK3 → Console (~) → portrait_editor → Paste Persistent DNA",
                        size=11, color=MUTED),
            ], spacing=0, tight=True)),
        ], spacing=0),
    )

    page.add(ft.Column([
        header,
        ft.Row([left, right], expand=True,
               vertical_alignment=ft.CrossAxisAlignment.START),
    ], expand=True, spacing=0))


if __name__ == "__main__":
    ft.run(
        main,
        host="0.0.0.0",
        port=8080,
    )
from manim import *

YELLOW_ = "#F28B05"
GREEN_ = "#3C7D22"
BLUE_ = "#4A90D9"
PAD_ = "#C0C0C0"
CFA_ = "#9C2D2D"

# Geomtry. Beam travels along +x.
TILE = 0.5  # Se detector
GAP = 0.06  # gap b/w Si
THICK = 0.06  # wall thickness
BOX = 4.0
WALL_H = 4 * (TILE + GAP)
CFA_CENTRE = np.array([-WALL_H / 2 - 1.0, 0, WALL_H / 2])
IMPLANT_ORIGIN = CFA_CENTRE - np.array([0.5, 0, 0])
PAD_Z = WALL_H + 0.2


def make_wall(
    center, normal_axis, n_cols, n_rows, color, tile_h=TILE, tile_v=TILE, gap=GAP
):
    wall = VGroup()
    pitch_h = tile_h + gap
    pitch_v = tile_v + gap
    for c in range(n_cols):
        for r in range(n_rows):
            h = (c - (n_cols - 1) / 2) * pitch_h
            v = (r - (n_rows - 1) / 2) * pitch_v
            if normal_axis == "y":
                dims, off = [tile_h, THICK, tile_v], np.array([h, 0, v])
            else:
                dims, off = [THICK, tile_h, tile_v], np.array([0, h, v])
            p = Prism(
                dimensions=dims,
                fill_color=color,
                fill_opacity=0.2,
                stroke_color=color,
                stroke_width=2,
            )
            p.move_to(np.array(center) + off)
            wall.add(p)
    return wall


def make_pad_plane(center, size=BOX, n_pix=50, color=PAD_):
    plane = VGroup()

    # base = Square(
    #     side_length=size,
    #     fill_color=color,
    #     fill_opacity=0.08,
    #     stroke_color=color,
    #     stroke_width=2,
    # )
    base = Prism(
        dimensions=[size, size, THICK],
        fill_color=color,
        fill_opacity=0.08,
        stroke_color=color,
        stroke_width=2,
    )
    plane.add(base)

    step = size / n_pix
    for i in range(1, n_pix):
        o = -size / 2 + i * step
        plane.add(
            Line(
                [o, -size / 2, 0],
                [o, size / 2, 0],
                stroke_color=color,
                stroke_width=0.5,
                stroke_opacity=0.6,
            )
        )
        plane.add(
            Line(
                [-size / 2, o, 0],
                [size / 2, o, 0],
                stroke_color=color,
                stroke_width=0.5,
                stroke_opacity=0.6,
            )
        )

    plane.move_to(center)
    return plane


def make_cfa(center, radius=0.2, width=THICK, color=CFA_):
    cfa = VGroup()
    cfa.add(Cylinder(radius, height=width, direction=(1, 0, 0)))
    cfa.set_fill(color, 0.3)
    cfa.move_to(center)
    return cfa


def label(text, color, pos):
    t = Text(text, color=color, weight=BOLD, font_size=24)
    t.move_to(pos)
    return t


class ACTARDecay(ThreeDScene):
    def construct(self):

        # self.set_camera_orientation(phi=70 * DEGREES, theta=-100 * DEGREES, zoom=1.2)
        self.set_camera_orientation(phi=70 * DEGREES, theta=-150 * DEGREES, zoom=1.0)
        self.make_geometry()

        # self.begin_ambient_camera_rotation(rate=-0.5)
        # self.wait(2)
        # self.stop_ambient_camera_rotation()
        # self.move_camera(theta=-120 * DEGREES, run_time=2)

        self.implant()

    def make_geometry(self):

        # dimensions
        z0 = WALL_H / 2
        cfa_centre = (-WALL_H / 2 - 1.0, 0, WALL_H / 2)

        # Si walls and labels
        si_l0 = make_wall((0, BOX / 2, z0), "y", 3, 4, YELLOW_, tile_h=0.7)
        si_r0 = make_wall((0, -BOX / 2, z0), "y", 3, 4, BLUE_, tile_h=0.7)
        si_f0 = make_wall((BOX / 2 + 0.2, 0, z0), "x", 4, 3, GREEN_)

        lab_l0 = label("Si_L0", YELLOW_, (0, BOX / 2 - 0.3, WALL_H + 0.6))
        lab_r0 = label("Si_R0", BLUE_, (BOX / 4, -BOX / 2 - 0.5, 0))  # wall_h + 0.7))
        lab_f0 = label("Si_F0", GREEN_, (BOX / 2 + 0.2, -BOX / 4, WALL_H + 0.5))

        # pad plane
        pad = make_pad_plane((0, 0, PAD_Z), size=3.7)

        # cfa
        cfa = make_cfa(cfa_centre)

        # Create physical objects
        self.add_fixed_orientation_mobjects(lab_l0, lab_r0, lab_f0)
        self.add(si_l0, si_r0, si_f0, pad, cfa)

    def start_ionization(
        self,
        particle,
        color,
        start=None,
        spacing=0.05,
        spread=0.01,
        per_step=3,
        radius=0.004,
        seed=1,
    ):
        electrons = VGroup()
        self.add(electrons)
        rng = np.random.default_rng(seed)
        last = [
            np.array(particle.get_center() if start is None else start, dtype=float)
        ]

        def ionization(group):
            pos = particle.get_center()
            while True:
                delta = pos - last[0]
                dist = np.linalg.norm(delta)
                if pos[0] < CFA_CENTRE[0]:  # nothing ionizes before the CFA
                    return
                if dist < spacing:
                    break
                direction = delta / dist
                for _ in range(per_step):
                    offset = rng.normal(0, spread, 3)
                    along = rng.uniform(0, spacing) * direction
                    group.add(
                        Dot3D(
                            point=last[0] + along + offset,
                            radius=radius,
                            color=color,
                            resolution=(6, 6),
                        )
                    )
                last[0] = last[0] + spacing * direction

        electrons.add_updater(ionization)
        return electrons

    def stop_ionization(self, electrons):
        electrons.clear_updaters()

    def drift_to_pad(self, *groups, run_time=4):
        self.play(
            *[dot.animate.set_z(PAD_Z + THICK) for g in groups for dot in g],
            run_time=run_time,
        )

    def implant(self):

        # Create implant
        implant = Dot3D(
            point=IMPLANT_ORIGIN, radius=0.05, color=YELLOW, resolution=(6, 6)
        )
        self.play(FadeIn(implant))

        # Move implant to stopping point and ionise gas
        stopping_point = np.array([3 * BOX / 4, 0, 0])
        electrons = self.start_ionization(implant, YELLOW, start=CFA_CENTRE)
        self.play(implant.animate.shift(stopping_point), run_time=3, rate_func=linear)
        self.stop_ionization(electrons)
        self.drift_to_pad(electrons)
        self.wait(2)

        # Decay
        stopping_point = implant.get_center()
        heavy = Dot3D(
            point=stopping_point, radius=0.05, color=PURE_MAGENTA, resolution=(6, 6)
        )
        light = Dot3D(point=stopping_point, radius=0.01, color=TEAL, resolution=(6, 6))

        self.play(
            TransformFromCopy(implant, heavy),
            TransformFromCopy(implant, light),
            FadeOut(implant, run_time=0),
            run_time=0.3,
        )

        # Silicon Point for light and random L1 for heavy
        sp = np.array([1.0, -BOX / 2, 1.8])
        heavy_dir = np.array([0.5, 1.0, -0.3])
        heavy_dir = heavy_dir / np.linalg.norm(heavy_dir)
        heavy_stop = stopping_point + 1.0 * heavy_dir

        # Move decay products
        heavy_e = self.start_ionization(heavy, PURE_MAGENTA, seed=2)
        light_e = self.start_ionization(light, TEAL, seed=3)
        self.play(
            heavy.animate.move_to(heavy_stop),
            light.animate.move_to(sp),
            run_time=1.5,
            rate_functions=linear,
        )
        self.stop_ionization(heavy_e)
        self.stop_ionization(light_e)
        mark = Circle(radius=0.05, color=TEAL, fill_opacity=0.9, stroke_width=0)
        mark.rotate(PI / 2, axis=RIGHT)
        mark.move_to([sp[0], -BOX / 2 + THICK / 2 + 0.005, sp[2]])
        self.play(FadeIn(mark, scale=3))
        self.drift_to_pad(heavy_e, light_e)
        self.wait(2)

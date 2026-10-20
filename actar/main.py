from manim import *

YELLOW_ = "#F2B705"
GREEN_ = "#3C7D22"
BLUE_ = "#4A90D9"
PAD_ = "#C0C0C0"  # pad plane colour

# Geomtry. Beam travels along +x.
TILE = 0.5  # Se detector
GAP = 0.06  # gap b/w Si
THICK = 0.06  # wall thickness
BOX = 4.0


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
                fill_opacity=0.25,
                stroke_color=color,
                stroke_width=2,
            )
            p.move_to(np.array(center) + off)
            wall.add(p)
    return wall


def make_pad_plane(center, size=BOX , n_pix=50, color=PAD_):
    plane = VGroup()

    base = Square(
        side_length=size,
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


class SiliconWalls(ThreeDScene):
    def construct(self):

        self.set_camera_orientation(phi=70 * DEGREES, theta=-150 * DEGREES, zoom=1.2)
        
        #Si wall dimensions
        wall_h = 4 * (TILE + GAP)
        f0_h = 3 * (TILE + GAP)
        z0 = wall_h / 2

        # Si walls and labels
        si_l0 = make_wall((0, BOX / 2, z0), "y", 3, 4, YELLOW_, tile_h=0.7)
        si_r0 = make_wall((0, -BOX / 2, z0), "y", 3, 4, BLUE_, tile_h=0.7)
        si_f0 = make_wall((BOX / 2 + 0.2, 0, z0), "x", 4, 3, GREEN_)
        
        def label(text, color, pos):
            t = Text(text, color=color, weight=BOLD, font_size=24)
            t.move_to(pos)
            return t
        lab_l0 = label("Si_L0", YELLOW_, (0, BOX / 2 - 0.3, wall_h + 0.6))
        lab_r0 = label("Si_R0", BLUE_, (BOX/4, -BOX / 2 -0.5 , 0 ))#wall_h + 0.7))
        lab_f0 = label("Si_F0", GREEN_, (BOX / 2 + 0.2, -BOX/4, wall_h + 0.5))

        # pad plane
        pad = make_pad_plane((0, 0, wall_h+0.2), size=3.7)

        # Create physical objects
        self.add_fixed_orientation_mobjects(lab_l0, lab_r0, lab_f0)
        self.add(si_l0, si_r0, si_f0, pad)

        self.begin_ambient_camera_rotation(rate=0.05)
        self.wait(2)
        self.stop_ambient_camera_rotation()

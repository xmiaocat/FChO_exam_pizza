#!/usr/bin/env python

from dataclasses import dataclass, field
import math
from pathlib import Path
import random
import time
try:
    import tomllib
except ImportError:
    import toml as tomllib
import pygame
import pygame.gfxdraw as gfx

_IMG_ROOT = 'images'
_ASSET_CACHE = {}


def load_pizza_image(name: str) -> pygame.Surface:
    path = Path(__file__).parent / _IMG_ROOT / name
    key  = str(path)
    if key not in _ASSET_CACHE:
        img = pygame.image.load(path).convert_alpha()
        _ASSET_CACHE[key] = img
    return _ASSET_CACHE[key]


def get_tick_text(total_hours: float, div_hour: float, 
                  tick_count: int) -> list[str]:
    tol = 1e-6
    sec_hours = [i * div_hour for i in range(tick_count)] + [total_hours]
    
    tick_text = []
    for h in sec_hours:
        if abs(h % 1.0) < tol:
            # whole hours
            txt = f'{int(h)}'
        elif abs((2 * h) % 1.0) < tol:
            # half hours
            whole_h = int(h)
            whole_txt = f'{whole_h}' if whole_h else ''
            txt = f'{whole_txt}½'
        elif abs((3 * h) % 1.0) < tol:
            # third hours
            whole_h = int(h)
            whole_txt = f'{whole_h}' if whole_h else ''
            tmp = 3 * (h % 1.0)
            if abs(tmp - 1.0) < tol:
                txt = f'{whole_txt}⅓'
            else:
                txt = f'{whole_txt}⅔'
        elif abs((4 * h) % 1.0) < tol:
            # quarter hours
            whole_h = int(h)
            whole_txt = f'{whole_h}' if whole_h else ''
            tmp = 4 * (h % 1.0)
            if abs(tmp - 1.0) < tol:
                txt = f'{whole_txt}¼'
            elif abs(tmp - 3.0) < tol:
                txt = f'{whole_txt}¾'
        elif abs((5 * h) % 1.0) < tol:
            # fifth hours
            whole_h = int(h)
            whole_txt = f'{whole_h}' if whole_h else ''
            tmp = 5 * (h % 1.0)
            if abs(tmp - 1.0) < tol:
                txt = f'{whole_txt}⅕'
            elif abs(tmp - 2.0) < tol:
                txt = f'{whole_txt}⅖'
            elif abs(tmp - 3.0) < tol:
                txt = f'{whole_txt}⅗'
            elif abs(tmp - 4.0) < tol:
                txt = f'{whole_txt}⅘'
        elif abs((6 * h) % 1.0) < tol:
            # sixth hours
            whole_h = int(h)
            whole_txt = f'{whole_h}' if whole_h else ''
            tmp = 6 * (h % 1.0)
            if abs(tmp - 1.0) < tol:
                txt = f'{whole_txt}⅙'
            elif abs(tmp - 5.0) < tol:
                txt = f'{whole_txt}⅚'
        elif abs((8 * h) % 1.0) < tol:
            # eighth hours
            whole_h = int(h)
            whole_txt = f'{whole_h}' if whole_h else ''
            tmp = 8 * (h % 1.0)
            if abs(tmp - 1.0) < tol:
                txt = f'{whole_txt}⅛'
            elif abs(tmp - 3.0) < tol:
                txt = f'{whole_txt}⅜'
            elif abs(tmp - 5.0) < tol:
                txt = f'{whole_txt}⅝'
            elif abs(tmp - 7.0) < tol:
                txt = f'{whole_txt}⅞'
        else:
            # other fractions
            txt = f'{h:.2f}'
        tick_text.append(txt)
    
    return tick_text


def draw_filled_wedge(
    surf: pygame.Surface,
    centre: tuple[int, int],
    radius: int,
    ang0: float,
    ang1: float,
    colour: tuple[int, int, int, int],
    step: float = 1.0,
) -> None:
    nstep = int((ang1 - ang0) / step)
    angles = [math.radians(ang0 + i * step) for i in range(nstep + 1)]
    pts = [centre]
    for ang in angles:
        pts.append((centre[0] + radius * math.cos(ang),
                    centre[1] + radius * math.sin(ang)))

    if len(pts) < 3:
        return  # not enough points to form a polygon
    gfx.filled_polygon(surf, pts, colour)
    gfx.aapolygon(surf, pts, colour)      # thin AA outline


@dataclass
class TimerConfig:
    div_hour: float = 0.5
    start_second: int | None = None
    pizza_images: list[str] | str = field(
        default_factory=lambda: ['000_default.png']
    )
    pizza_init_idx: int | None = 0
    pizza_change_interval: float | None = None
    pizza_change_policy: str = 'random'
    canvas_size: int = 800
    pizza_radius: int = 300
    font_name: str = 'gillsansmt'
    font_size: int = 56
    line_width: int = 5
    separator_dash_length: int = 5
    separator_gap_length: int = 3
    separator_line_width: int = 2
    clock_padding: int = 15
    clock_background_color: tuple[int, int, int, int] = (0, 0, 0, 180)
    background_color: tuple[int, int, int, int] = (0, 0, 0, 255)
    foreground_color: tuple[int, int, int, int] = (255, 255, 255, 255)

    def __post_init__(self):
        # Parse configuration parameters
        self.pizza_change_policy = self.pizza_change_policy.lower()

        # Validate configuration parameters
        if self.div_hour <= 0:
            raise ValueError('div_hour must be positive')
        if self.canvas_size <= 0:
            raise ValueError('canvas_size must be positive')
        if self.pizza_radius <= 0:
            raise ValueError('pizza_radius must be positive')
        if self.line_width <= 0:
            raise ValueError('line_width must be positive')
        if self.separator_dash_length < 0:
            raise ValueError('separator_dash_length cannot be negative')
        if self.separator_gap_length < 0:
            raise ValueError('separator_gap_length cannot be negative')
        if self.separator_line_width <= 0:
            raise ValueError('separator_line_width must be positive')
        if self.clock_padding < 0:
            raise ValueError('clock_padding cannot be negative')
        if isinstance(self.pizza_images, str):
            if self.pizza_images == 'all':
                self.pizza_images = sorted(
                    (p.name for p in Path(_IMG_ROOT).glob('*.png')),
                    key=lambda name: name,
                )
            else:
                self.pizza_images = [self.pizza_images]
        elif isinstance(self.pizza_images, list):
            assert len(self.pizza_images) > 0, \
                'pizza_images cannot be an empty list'
            assert all(isinstance(img, str) for img in self.pizza_images), \
                'All items in pizza_images must be strings'
        else:
            raise TypeError('pizza_images must be a string '
                            'or a list of strings')
        if self.pizza_change_policy not in ('random', 'cycle'):
            raise ValueError('pizza_change_policy must be ' 
                             '"random" or "cycle"')
        
        # Set default values for optional parameters
        if self.pizza_change_interval is None:
            self.pizza_change_interval = self.div_hour


class PizzaTimer(object):

    def __init__(self, total_hours: float, cfg: dict | None = None):
        assert total_hours > 0, 'total_hours must be positive'

        self.total_hours = total_hours
        cfg = cfg or {}
        self.config = TimerConfig(**cfg)
        
        pygame.init()
        self._init_canvas()
        self._init_clock()
        self._init_font()
        self._init_pizzas()
        self._init_sections()
    
    def _compute_layout(self, sw: int, sh: int) -> None:
        self.screen_off_x = (sw - self.config.canvas_size) // 2
        self.screen_off_y = (sh - self.config.canvas_size) // 2

    def _init_canvas(self) -> None:
        self.canvas = pygame.Surface(
            (self.config.canvas_size, self.config.canvas_size),
            flags=pygame.SRCALPHA,
        )
        self.screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        self._compute_layout(*self.screen.get_size())
        
    def _init_clock(self) -> None:
        self.clock = pygame.time.Clock()
        self.total_sec = int(self.total_hours * 3600)
        if self.config.start_second is None:
            self.start = time.time()
        else:
            self.start = time.time() - (total_sec - self.config.start_second)

    def _init_font(self) -> None:
        self.font = pygame.font.SysFont(self.config.font_name, 
                                        self.config.font_size)
        num_width, num_height = self.font.size('0')
        self.num_radius = 0.5 * math.sqrt(num_width**2 + num_height**2)
   
    def _init_pizzas(self) -> None:
        self.pizza_size = (2 * self.config.pizza_radius, 
                           2 * self.config.pizza_radius)
        self.pizza_cx = self.config.canvas_size // 2
        self.pizza_cy = self.config.canvas_size // 2
        self.mask = pygame.Surface(self.pizza_size, pygame.SRCALPHA)

        self.pizza_images = []
        for img_name in self.config.pizza_images:
            try:
                img = load_pizza_image(img_name)
            except FileNotFoundError:
                print(f'Warning: Pizza image "{img_name}" not found.')
                continue
            img = pygame.transform.smoothscale(img, self.pizza_size)
            self.pizza_images.append(img)
        
        self.npizza = len(self.pizza_images)
        if self.npizza == 0:
            raise ValueError('No valid pizza images found.')
        if self.config.pizza_init_idx is None:
            self.config.pizza_init_idx = random.randint(0, self.npizza - 1)
        self.current_pizza_idx = self.config.pizza_init_idx % self.npizza
        self.pizza_change_sec = self.config.pizza_change_interval * 3600
        self._last_pizza_interval = 0

    def _init_sections(self) -> None:
        full_divs, remainder = divmod(self.total_hours, self.config.div_hour)
        full_divs = int(full_divs)
        
        if remainder > 1e-8:
            self.tick_count = full_divs + 1
        else:
            self.tick_count = full_divs or 1

        step_deg = (self.config.div_hour / self.total_hours) * 360.0
        angle_offset = -90.0

        self.sec_angles = [
            math.radians(angle_offset + i * step_deg)
            for i in range(self.tick_count)
        ]

        self.sec_length = (
            self.config.pizza_radius
            - (self.config.line_width // 2)
        )

        self.tick_text = get_tick_text(
            self.total_hours,
            self.config.div_hour,
            self.tick_count,
        )

    def run(self) -> None:
        running = True
        while running:
            running = self._handle_events()
            self._update_timer()
            self._draw_frame()
            
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()

    def _handle_events(self) -> bool:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return False
            elif ev.type == pygame.VIDEORESIZE:
                self._compute_layout(ev.w, ev.h)
        return True
    
    def _update_pizza_image(self, elapsed: float) -> None:
        if not self.config.pizza_change_interval or self.npizza <= 1:
            return
        
        intervals = int(elapsed // self.pizza_change_sec)
        
        if self.config.pizza_change_policy == 'cycle':
            self.current_pizza_idx = (
                self.config.pizza_init_idx + intervals
            ) % self.npizza

        elif self.config.pizza_change_policy == 'random':
            if intervals != self._last_pizza_interval:
                choices = list(range(self.npizza))
                choices.remove(self.current_pizza_idx)
                self.current_pizza_idx = random.choice(choices)
                self._last_pizza_interval = intervals

    def _update_timer(self) -> None:
        elapsed = time.time() - self.start
        self.progress = min(1.0, elapsed / self.total_sec)
        self.remain = max(0, self.total_sec - int(elapsed))
        
        if 0.0 < self.progress < 1.0:
            self._update_pizza_image(elapsed)
    
    def _draw_frame(self) -> None:
        self.canvas.fill(self.config.background_color)
        if self.progress > 0:
            self._draw_pizza()
            self._draw_segments()
            self._draw_tick_text()
            self._draw_separator()
            self._draw_clock()
            
            self.screen.fill(self.config.background_color)
            self.screen.blit(self.canvas, 
                             (self.screen_off_x, self.screen_off_y))
    
    def _draw_pizza(self) -> None:
        self.mask.fill((0, 0, 0, 0))
        cx, cy  = self.pizza_size[0] // 2, self.pizza_size[1] // 2
        radius  = self.pizza_size[0] // 2
        end_ang = -90 + self.progress * 360

        draw_filled_wedge(
            self.mask,
            (cx, cy),
            radius,
            -90, end_ang,
            (255, 255, 255, 255),
            step=0.2,
        )

        pizza_visible = self.pizza_images[self.current_pizza_idx].copy()
        pizza_visible.blit(self.mask, (0, 0), 
                           special_flags=pygame.BLEND_RGBA_MULT)
        self.canvas.blit(
            pizza_visible,
            pizza_visible.get_rect(center=(self.pizza_cx, self.pizza_cy)),
        )

    def _draw_segments(self) -> None:
        for ang in self.sec_angles:
            x_end = self.pizza_cx + self.sec_length * math.cos(ang)
            y_end = self.pizza_cy + self.sec_length * math.sin(ang)
            pygame.draw.line(
                self.canvas,
                self.config.foreground_color,
                (self.pizza_cx, self.pizza_cy),
                (x_end, y_end),
                self.config.line_width,
            )
    
        pygame.draw.circle(
            self.canvas,
            self.config.foreground_color,
            (self.pizza_cx, self.pizza_cy),
            self.config.pizza_radius,
            self.config.line_width,
        )
    
    def _draw_tick_text(self) -> None:
        radius = self.config.pizza_radius + 1.5 * self.num_radius
        
        # draw all labels except the first and last
        for i, (ang, txt) in enumerate(
            zip(self.sec_angles[1:], self.tick_text[1:-1])
        ):
            x = self.pizza_cx + radius * math.cos(ang)
            y = self.pizza_cy + radius * math.sin(ang)
            mark = self.font.render(txt, True, self.config.foreground_color)
            rect = mark.get_rect(center=(x, y))
            self.canvas.blit(mark, rect)
        
        # draw the first and last labels
        y = self.pizza_cy - radius
        for idx, sgn in zip((0, -1), (1, -1)):
            txt = self.tick_text[idx]
            w, _ = self.font.size(txt)
            x = self.pizza_cx + sgn * (
                0.5 * w + 0.05 * self.config.pizza_radius
            )
            mark = self.font.render(txt, True, self.config.foreground_color)
            rect = mark.get_rect(center=(x, y))
            self.canvas.blit(mark, rect)
    
    def _draw_separator(self) -> None:
        x0 = self.pizza_cx
        y0 = self.pizza_cy - self.config.pizza_radius
        top = max(
            0, 
            self.config.canvas_size / 2 - self.config.pizza_radius \
                - 2.3 * self.num_radius
        )
        
        y = y0
        while y > top:
            y2 = max(y - self.config.separator_dash_length, 0)
            pygame.draw.line(
                self.canvas,
                self.config.foreground_color,
                (x0, y),
                (x0, y2),
                self.config.separator_line_width,
            )
            y = y2 - self.config.separator_gap_length
    
    def _draw_clock(self) -> None:
        rem_h, tmp = divmod(self.remain, 3600) 
        rem_m, rem_s = divmod(tmp, 60)
        clock_txt = self.font.render(
            f'{rem_h:01d}:{rem_m:02d}:{rem_s:02d}', 
            True, 
            self.config.foreground_color,
        )
        text_rect = clock_txt.get_rect(center=(self.pizza_cx, self.pizza_cy))
        
        bg_rect = pygame.Rect(
            text_rect.left - self.config.clock_padding,
            text_rect.top  - self.config.clock_padding,
            text_rect.width + 2 * self.config.clock_padding,
            text_rect.height + 2 * self.config.clock_padding,
        )
        bg_surf = pygame.Surface(
            (bg_rect.width, bg_rect.height), pygame.SRCALPHA,
        )
        bg_surf.fill(self.config.clock_background_color)
        
        self.canvas.blit(bg_surf, (bg_rect.left, bg_rect.top))
        self.canvas.blit(clock_txt, text_rect)


def noneify(obj):
    if isinstance(obj, dict):
        return {k: noneify(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [noneify(v) for v in obj]
    elif isinstance(obj, str) and obj.lower() == "none":
        return None
    else:
        return obj


def load_toml_config(path: str) -> (float, dict):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f'Config file not found: {path!r}')
    with p.open('rb') as f:
        data = tomllib.load(f)
    total_hours = data.get('total_hours', 3.5)
    cfg = data.get('config', {})

    return total_hours, cfg


def main():
    from dataclasses import fields
    import sys
    import warnings

    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
    total_hours, raw_cfg = load_toml_config(config_path)
    raw_cfg = noneify(raw_cfg)

    valid_keys = {f.name for f in fields(TimerConfig)}
    invalid_keys = set(raw_cfg) - valid_keys
    if invalid_keys:
        warnings.warn(
            f"Ignoring unknown config keys: {', '.join(sorted(invalid_keys))}",
            UserWarning
        )
    filtered_cfg = {k: v for k, v in raw_cfg.items() if k in valid_keys}
    
    timer = PizzaTimer(total_hours, cfg=filtered_cfg)
    timer.run()


if __name__ == '__main__':
    main()


from datetime import datetime, timedelta
import calendar
import colorsys
import argparse
from enum import Enum, auto
from rich.text import Text
from rich.panel import Panel
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class TimeCategory(Enum):
    YEAR = auto()
    MONTH = auto()
    WEEK = auto()
    DAY = auto()
    HOUR = auto()
    MINUTE = auto()

    @classmethod
    def from_string(cls, s: str):
        lookup = {
            "year": cls.YEAR,
            "month": cls.MONTH,
            "week": cls.WEEK,
            "day": cls.DAY,
            "hour": cls.HOUR,
            "min": cls.MINUTE,
            "minute": cls.MINUTE,
        }
        return lookup.get(s.lower())


class AppConfig:
    PANEL_PADDING = 4
    INCOMPLETE_STYLE = "grey37"
    GRADIENTS = {
        TimeCategory.YEAR: (0.16, 0.3),
        TimeCategory.MONTH: (0.7, 0.75),
        TimeCategory.WEEK: (0.3, 0.4),
        TimeCategory.DAY: (0.55, 0.65),
        TimeCategory.HOUR: (0.8, 0.9),
        TimeCategory.MINUTE: (0.0, 0.1),
    }


class ProgressVisualizer:
    @staticmethod
    def render(percentage: float, category: TimeCategory, current: int, total: int, width: int) -> Text:
        bar_width = max(10, width - AppConfig.PANEL_PADDING)
        filled = int(round(bar_width * percentage / 100))
        empty = bar_width - filled
        gradient_start, gradient_end = AppConfig.GRADIENTS[category]
        bar = ProgressVisualizer._create_gradient_segment(gradient_start, gradient_end, filled)
        bar.append("─" * empty, style=AppConfig.INCOMPLETE_STYLE)
        text = Text(f"{percentage:.1f}% ({current}/{total})", style="bold white")
        return ProgressVisualizer._center_text(bar, text)

    @staticmethod
    def _create_gradient_segment(hue_start: float, hue_end: float, filled: int) -> Text:
        segment = Text()
        for i in range(filled):
            hue = hue_start + (i / max(1, (filled - 1))) * (hue_end - hue_start)
            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            segment.append("|", style=f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}")
        return segment

    @staticmethod
    def _center_text(bar: Text, text: Text) -> Text:
        start_pos = (len(bar.plain) - len(text.plain)) // 2
        return bar[:start_pos] + text + bar[start_pos+len(text.plain):]


class TimeProgressCalculator:
    @staticmethod
    def get_all_progress(now: datetime):
        return {
            TimeCategory.YEAR: TimeProgressCalculator._year_progress(now),
            TimeCategory.MONTH: TimeProgressCalculator._month_progress(now),
            TimeCategory.WEEK: TimeProgressCalculator._week_progress(now),
            TimeCategory.DAY: TimeProgressCalculator._day_progress(now),
            TimeCategory.HOUR: TimeProgressCalculator._hour_progress(now),
            TimeCategory.MINUTE: TimeProgressCalculator._minute_progress(now),
        }

    @staticmethod
    def _calculate_progress(start: datetime, end: datetime, now: datetime, unit: str):
        total_seconds = (end - start).total_seconds()
        elapsed_seconds = (now - start).total_seconds()
        progress = (elapsed_seconds / total_seconds) * 100

        if unit == "year":
            return progress, (now - start).days + 1, (end - start).days
        elif unit == "month":
            return progress, now.day, calendar.monthrange(now.year, now.month)[1]
        elif unit == "week":
            return progress, now.weekday() + 1, 7
        elif unit == "day":
            seconds_today = now.hour * 3600 + now.minute * 60 + now.second
            return progress, seconds_today, 86400
        elif unit == "hour":
            seconds_this_hour = now.minute * 60 + now.second
            return progress, seconds_this_hour, 3600
        elif unit == "minute":
            return progress, now.second, 60

    @staticmethod
    def _year_progress(now):
        start = datetime(now.year, 1, 1)
        end = datetime(now.year + 1, 1, 1)
        return TimeProgressCalculator._calculate_progress(start, end, now, "year")

    @staticmethod
    def _month_progress(now):
        start = datetime(now.year, now.month, 1)
        if now.month == 12:
            end = datetime(now.year + 1, 1, 1)
        else:
            end = datetime(now.year, now.month + 1, 1)
        return TimeProgressCalculator._calculate_progress(start, end, now, "month")

    @staticmethod
    def _week_progress(now):
        start = now - timedelta(days=now.weekday())
        start = datetime(start.year, start.month, start.day)
        end = start + timedelta(days=7)
        return TimeProgressCalculator._calculate_progress(start, end, now, "week")

    @staticmethod
    def _day_progress(now):
        start = datetime(now.year, now.month, now.day)
        end = start + timedelta(days=1)
        progress = ((now - start).total_seconds() / (end - start).total_seconds()) * 100
        return progress, now.hour, 24

    @staticmethod
    def _hour_progress(now):
        start = now.replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        progress = ((now - start).total_seconds() / (end - start).total_seconds()) * 100
        return progress, now.minute, 60

    @staticmethod
    def _minute_progress(now):
        start = now.replace(second=0, microsecond=0)
        end = start + timedelta(minutes=1)
        return TimeProgressCalculator._calculate_progress(start, end, now, "minute")


class TimeVisualizerApp(App):
    BINDINGS = [("q", "quit", "Quit the application"), ("ctrl+c", "quit", "Quit the application")]

    def __init__(self, interval: float = 0.1, show_categories=None, **kwargs):
        super().__init__(**kwargs)
        self.refresh_interval = interval
        self.show_categories = set(show_categories) if show_categories else set(TimeCategory)

    def compose(self) -> ComposeResult:
        self.panels = {}
        for category in TimeCategory:
            panel = Static()
            panel.display = category in self.show_categories
            self.panels[category] = panel
        yield Vertical(*self.panels.values())

    def on_mount(self) -> None:
        self.update_display()
        self.set_interval(self.refresh_interval, self.update_display)

    def update_display(self) -> None:
        progress_data = TimeProgressCalculator.get_all_progress(datetime.now())
        for category, panel in self.panels.items():
            if panel.display:
                progress, current, total = progress_data[category]
                rendered = ProgressVisualizer.render(progress, category, current, total, self.size.width)
                panel.update(create_category_panel(category, rendered))

    def on_key(self, event: events.Key) -> None:
        if event.key in "123456":
            idx = int(event.key) - 1
            category = list(TimeCategory)[idx]
            panel = self.panels[category]
            panel.display = not panel.display
            self.refresh(layout=True)
        elif event.key == "q":
            self.exit()


def create_category_panel(category: TimeCategory, content: Text) -> Panel:
    avg_hue = sum(AppConfig.GRADIENTS[category]) / 2
    r, g, b = colorsys.hsv_to_rgb(avg_hue, 1, 1)
    border_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    return Panel(content, title=f"[bold {border_color}]{category.name.title()}",
                 border_style=border_color, title_align="left")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Timi - Shows progress bars for time intervals."
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.1,
        help="Set refresh interval in seconds (default: 0.1)"
    )
    parser.add_argument(
        "--show",
        nargs="*",
        default=None,
        help="Categories to show: min hour day week month year"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Timi - Time visualizer - v1.0"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.show:
        show_categories = [TimeCategory.from_string(s) for s in args.show]
        show_categories = [c for c in show_categories if c is not None]
    else:
        show_categories = list(TimeCategory)

    TimeVisualizerApp(interval=args.interval, show_categories=show_categories).run()


if __name__ == "__main__":
    main()



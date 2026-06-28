# ============================================================
#   RAMGARH MESS MANAGEMENT SYSTEM
#   Framework : Kivy
#   Run       : python ramgarh_mess_system.py  (Sublime Text / CMD)
#   DB        : SQLite  (auto-created as mess_feedback.db)
# ============================================================

import sqlite3
import os
from datetime import datetime

# ---------- Kivy Config (must be BEFORE any kivy import) ----
from kivy.config import Config
Config.set('graphics', 'width',  '480')
Config.set('graphics', 'height', '860')
Config.set('graphics', 'resizable', True)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.metrics import dp

# ─────────────────────── COLOUR PALETTE (White Theme) ───────
BG       = (1.00, 1.00, 1.00, 1)   # white background
CARD     = (0.93, 0.95, 1.00, 1)   # light blue-grey card
ACCENT   = (0.85, 0.35, 0.05, 1)   # orange-red
ACCENT2  = (0.10, 0.45, 0.78, 1)   # deep blue
RED      = (0.80, 0.10, 0.10, 1)
GREEN    = (0.05, 0.60, 0.30, 1)
TXT      = (0.08, 0.08, 0.14, 1)   # near-black text
TGREY    = (0.40, 0.40, 0.50, 1)   # grey text
STAR_ON  = (0.95, 0.65, 0.05, 1)
STAR_OFF = (0.72, 0.72, 0.78, 1)

Window.clearcolor = BG

# ─────────────────────── DATABASE ──────────────────────────
DB = "mess_feedback.db"

def get_conn():
    return sqlite3.connect(DB)

def init_db():
    with get_conn() as con:
        c = con.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                reg_no      TEXT NOT NULL,
                date        TEXT NOT NULL,
                meal_time   TEXT NOT NULL,
                taste       INTEGER DEFAULT 0,
                quality     INTEGER DEFAULT 0,
                hygiene     INTEGER DEFAULT 0,
                menu_follow INTEGER DEFAULT 0,
                avg_rating  REAL    DEFAULT 0,
                complaint   TEXT,
                alert_sent  INTEGER DEFAULT 0,
                submitted_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_id INTEGER,
                reg_no      TEXT,
                avg_rating  REAL,
                meal_time   TEXT,
                date        TEXT,
                message     TEXT,
                created_at  TEXT
            )
        """)
        con.commit()

# ─────────────────────── HELPERS ───────────────────────────
def bg(widget, color):
    with widget.canvas.before:
        Color(*color)
        widget._r = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(size=lambda w, v: setattr(w._r, 'size', v),
                pos =lambda w, v: setattr(w._r, 'pos',  v))

def btn(text, color=ACCENT, fg=(1,1,1,1), fs=20, h=dp(62)):
    return Button(
        text=text, size_hint=(1, None), height=h,
        background_normal='', background_color=color,
        color=fg, font_size=fs, bold=True,
    )

def lbl(text, fs=17, color=TXT, bold=False, h=dp(34)):
    return Label(
        text=text, size_hint=(1, None), height=h,
        color=color, font_size=fs, bold=bold,
        halign='left', valign='middle',
        text_size=(Window.width - dp(40), None),
    )

def inp(hint, h=dp(54)):
    return TextInput(
        hint_text=hint, size_hint=(1, None), height=h,
        background_color=(0.88, 0.93, 1.00, 1),
        foreground_color=TXT,
        hint_text_color=TGREY,
        cursor_color=ACCENT,
        padding=[dp(14), dp(14)],
        font_size=18,
    )

# ─────────────────────── STAR RATER ────────────────────────
class StarRating(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation='horizontal',
                         size_hint=(1, None), height=dp(56),
                         spacing=dp(8), **kw)
        self.rating = 0
        self.stars  = []
        for i in range(1, 6):
            b = Button(text='★', font_size=36, bold=True,
                       background_normal='', background_color=(0,0,0,0),
                       color=STAR_OFF)
            b.star_val = i
            b.bind(on_release=self._tap)
            self.stars.append(b)
            self.add_widget(b)

    def _tap(self, b):
        self.rating = b.star_val
        for s in self.stars:
            s.color = STAR_ON if s.star_val <= self.rating else STAR_OFF

    def reset(self):
        self.rating = 0
        for s in self.stars:
            s.color = STAR_OFF

# ─────────────────────── CARD ──────────────────────────────
class Card(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.padding  = [dp(16), dp(14)]
        self.spacing  = dp(8)
        bg(self, CARD)

# ═══════════════════════════════════════════════════════════
#  SCREEN 1 — HOME
# ═══════════════════════════════════════════════════════════
class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical',
                         padding=dp(22), spacing=dp(18))
        bg(root, BG)

        # Banner
        banner = BoxLayout(size_hint=(1, None), height=dp(130))
        with banner.canvas.before:
            Color(*ACCENT)
            banner._r = RoundedRectangle(size=banner.size,
                                         pos=banner.pos, radius=[dp(16)])
        banner.bind(size=lambda w,v: setattr(w._r,'size',v),
                    pos =lambda w,v: setattr(w._r,'pos', v))
        banner.add_widget(Label(
            text='🍽  RAMGARH\nMESS MANAGEMENT\nSYSTEM',
            font_size=22, bold=True,
            color=(1,1,1,1),
            halign='center', valign='middle',
            text_size=(Window.width - dp(60), None),
        ))
        root.add_widget(banner)

        root.add_widget(lbl('Welcome! Rate your meal & help us improve.',
                            fs=17, color=TGREY))

        b1 = btn('📝   Give Feedback / Rating', ACCENT2)
        b2 = btn('📋   View Complaint Box',     (0.45, 0.45, 0.65, 1))
        b3 = btn('🚨   Management Alerts',      RED)

        b1.bind(on_release=lambda *_: self._go('feedback'))
        b2.bind(on_release=lambda *_: self._go('complaints'))
        b3.bind(on_release=lambda *_: self._go('alerts'))

        for b in [b1, b2, b3]:
            root.add_widget(b)

        root.add_widget(Widget())
        root.add_widget(lbl('Ramgarh Hostel  •  Jharkhand',
                            fs=15, color=TGREY))
        self.add_widget(root)

    def _go(self, name):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = name

# ═══════════════════════════════════════════════════════════
#  SCREEN 2 — FEEDBACK FORM
# ═══════════════════════════════════════════════════════════
class FeedbackScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        outer = BoxLayout(orientation='vertical')
        bg(outer, BG)

        # Topbar
        topbar = BoxLayout(size_hint=(1, None), height=dp(64),
                           padding=[dp(12), 0])
        bg(topbar, CARD)
        bk = Button(text='←  Back', size_hint=(None,1), width=dp(110),
                    background_normal='', background_color=(0,0,0,0),
                    color=ACCENT, font_size=18, bold=True)
        bk.bind(on_release=lambda *_: self._home())
        topbar.add_widget(bk)
        topbar.add_widget(Label(text='Meal Feedback Form',
                                color=TXT, font_size=20, bold=True))
        outer.add_widget(topbar)

        scroll = ScrollView(size_hint=(1,1))
        body   = BoxLayout(orientation='vertical',
                           padding=[dp(18), dp(14)], spacing=dp(12),
                           size_hint_y=None)
        body.bind(minimum_height=body.setter('height'))

        # ── Student info ─────────────────────────────────────
        body.add_widget(lbl('Student Name  *', fs=18, color=ACCENT, bold=True, h=dp(32)))
        self.i_name = inp('Enter your full name')
        body.add_widget(self.i_name)

        body.add_widget(lbl('Registration Number  *', fs=18, color=ACCENT, bold=True, h=dp(32)))
        self.i_reg  = inp('e.g.  RH2024001')
        body.add_widget(self.i_reg)

        body.add_widget(lbl('Date  *', fs=18, color=ACCENT, bold=True, h=dp(32)))
        today = datetime.now().strftime('%d-%m-%Y')
        self.i_date = inp(f'DD-MM-YYYY  (e.g. {today})')
        self.i_date.text = today
        body.add_widget(self.i_date)

        body.add_widget(lbl('Meal Time  *', fs=18, color=ACCENT, bold=True, h=dp(32)))
        self.spin = Spinner(
            text='Select Meal Time',
            values=['Morning  (Breakfast)', 'Afternoon  (Lunch)', 'Evening  (Dinner)'],
            size_hint=(1, None), height=dp(54),
            background_normal='',
            background_color=(0.88, 0.93, 1.00, 1),
            color=TXT, font_size=18,
        )
        body.add_widget(self.spin)

        body.add_widget(Widget(size_hint_y=None, height=dp(8)))

        # ── Rating cards ─────────────────────────────────────
        cats = [
            ('🌶   Taste',          'taste'),
            ('💎   Food Quality',   'quality'),
            ('🧼   Hygiene',        'hygiene'),
            ('📋   Menu Followed',  'menu_follow'),
        ]
        self.raters = {}
        for cat_lbl, key in cats:
            card = Card(size_hint=(1, None), height=dp(116))
            card.add_widget(lbl(cat_lbl, fs=17, color=TXT, bold=True, h=dp(28)))
            sr = StarRating()
            card.add_widget(sr)
            card.add_widget(lbl('Tap stars  ·  1 = Poor    5 = Excellent',
                                fs=14, color=TGREY, h=dp(24)))
            self.raters[key] = sr
            body.add_widget(card)

        # ── Complaint ────────────────────────────────────────
        body.add_widget(lbl('Complaint / Suggestion  (optional)',
                            fs=18, color=ACCENT, bold=True, h=dp(32)))
        self.i_complaint = TextInput(
            hint_text='Describe any issue or suggestion...',
            size_hint=(1, None), height=dp(100),
            background_color=(0.88, 0.93, 1.00, 1),
            foreground_color=TXT,
            hint_text_color=TGREY,
            cursor_color=ACCENT,
            padding=[dp(14), dp(14)],
            font_size=17,
            multiline=True,
        )
        body.add_widget(self.i_complaint)

        body.add_widget(Widget(size_hint_y=None, height=dp(8)))

        sub = btn('✅   Submit Feedback', GREEN, h=dp(66))
        sub.font_size = 20
        sub.bind(on_release=self._submit)
        body.add_widget(sub)
        body.add_widget(Widget(size_hint_y=None, height=dp(24)))

        scroll.add_widget(body)
        outer.add_widget(scroll)
        self.add_widget(outer)

    # ── Submit logic ─────────────────────────────────────────
    def _submit(self, *_):
        name      = self.i_name.text.strip()
        reg       = self.i_reg.text.strip()
        date      = self.i_date.text.strip()
        meal_time = self.spin.text

        if not name:
            return self._pop('⚠ Missing', 'Please enter your Name.')
        if not reg:
            return self._pop('⚠ Missing', 'Please enter Registration Number.')
        if not date:
            return self._pop('⚠ Missing', 'Please enter Date.')
        if 'Select' in meal_time:
            return self._pop('⚠ Missing', 'Please select a Meal Time.')

        ratings = {k: r.rating for k, r in self.raters.items()}
        if any(v == 0 for v in ratings.values()):
            return self._pop('⚠ Incomplete', 'Please rate ALL 4 categories.')

        avg = sum(ratings.values()) / 4
        complaint    = self.i_complaint.text.strip()
        submitted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with get_conn() as con:
            c = con.cursor()
            c.execute("""
                INSERT INTO feedback
                    (name,reg_no,date,meal_time,taste,quality,
                     hygiene,menu_follow,avg_rating,complaint,submitted_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (name, reg, date, meal_time,
                  ratings['taste'], ratings['quality'],
                  ratings['hygiene'], ratings['menu_follow'],
                  avg, complaint, submitted_at))
            fid = c.lastrowid

            alert_sent = 0
            if avg < 3.0:
                alert_sent = 1
                msg = (f"LOW QUALITY ALERT!\n"
                       f"Student : {name} ({reg})\n"
                       f"Meal    : {meal_time}\n"
                       f"Date    : {date}\n"
                       f"Avg     : {avg:.1f}/5\n"
                       f"Note    : {complaint or 'None'}")
                c.execute("""
                    INSERT INTO alerts
                        (feedback_id,reg_no,avg_rating,meal_time,date,message,created_at)
                    VALUES (?,?,?,?,?,?,?)
                """, (fid, reg, avg, meal_time, date, msg, submitted_at))
                c.execute("UPDATE feedback SET alert_sent=1 WHERE id=?", (fid,))
            con.commit()

        if alert_sent:
            self._pop('✅ Submitted + Alert',
                      f'Feedback submitted!\n\nAvg Rating: ⭐ {avg:.1f}/5\n\n'
                      f'🚨 LOW RATING ALERT sent to Management!',
                      ok_color=RED)
        else:
            self._pop('✅ Thank You!',
                      f'Feedback submitted!\n\nAvg Rating: ⭐ {avg:.1f}/5\n\n'
                      f'Thank you, {name}!',
                      ok_color=GREEN)
        self._clear()

    def _clear(self):
        self.i_name.text      = ''
        self.i_reg.text       = ''
        self.i_date.text      = datetime.now().strftime('%d-%m-%Y')
        self.spin.text        = 'Select Meal Time'
        self.i_complaint.text = ''
        for r in self.raters.values():
            r.reset()

    def _pop(self, title, msg, ok_color=ACCENT2):
        content = BoxLayout(orientation='vertical',
                            padding=dp(18), spacing=dp(12))
        bg(content, CARD)
        content.add_widget(Label(
            text=msg, color=TXT, font_size=17,
            halign='center', valign='middle',
            text_size=(Window.width * 0.74, None),
        ))
        ok = btn('OK', ok_color, h=dp(56))
        p  = Popup(title=title, content=content,
                   size_hint=(0.88, None), height=dp(300),
                   background='', separator_color=ACCENT,
                   title_color=TXT, title_size=18)
        ok.bind(on_release=p.dismiss)
        content.add_widget(ok)
        p.open()

    def _home(self):
        self.manager.transition = SlideTransition(direction='right') 
        self.manager.current = 'home'

# ═══════════════════════════════════════════════════════════
#  SCREEN 3 — COMPLAINT BOX
# ═══════════════════════════════════════════════════════════
class ComplaintsScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self._build()

    def _build(self):
        outer = BoxLayout(orientation='vertical')
        bg(outer, BG)

        topbar = BoxLayout(size_hint=(1,None), height=dp(64), padding=[dp(12),0])
        bg(topbar, CARD)
        bk = Button(text='←  Back', size_hint=(None,1), width=dp(110),
                    background_normal='', background_color=(0,0,0,0),
                    color=ACCENT, font_size=18, bold=True)
        bk.bind(on_release=lambda *_: self._home())
        topbar.add_widget(bk)
        topbar.add_widget(Label(text='📋  Complaint Box',
                                color=TXT, font_size=20, bold=True))
        outer.add_widget(topbar)

        scroll = ScrollView(size_hint=(1,1))
        body   = BoxLayout(orientation='vertical',
                           padding=[dp(14), dp(12)], spacing=dp(12),
                           size_hint_y=None)
        body.bind(minimum_height=body.setter('height'))

        with get_conn() as con:
            c = con.cursor()
            c.execute("""
                SELECT name,reg_no,date,meal_time,
                       taste,quality,hygiene,menu_follow,
                       avg_rating,complaint,alert_sent,submitted_at
                FROM feedback ORDER BY id DESC
            """)
            rows = c.fetchall()

        if not rows:
            body.add_widget(Label(text='No feedback submitted yet.',
                                  color=TGREY, font_size=18,
                                  halign='center', valign='middle',
                                  text_size=(Window.width - dp(40), None)))
        else:
            body.add_widget(lbl(f'Total Records: {len(rows)}',
                                fs=18, color=ACCENT2, bold=True, h=dp(32)))
            for row in rows:
                (name, reg, date, meal_time,
                 taste, quality, hygiene, menu_fol,
                 avg, complaint, alert_sent, sub_at) = row

                card_h = dp(260 if complaint else 234)
                card   = Card(size_hint=(1, None), height=card_h)

                hdr_color = RED if alert_sent else ACCENT2
                alert_tag = '  🚨 ALERT' if alert_sent else ''

                card.add_widget(Label(
                    text=f'{name}  |  {reg}{alert_tag}',
                    color=hdr_color, font_size=17, bold=True,
                    size_hint=(1,None), height=dp(30),
                    halign='left', valign='middle',
                    text_size=(Window.width - dp(60), None),
                ))
                card.add_widget(Label(
                    text=f'Date: {date}   •   {meal_time}',
                    color=TGREY, font_size=15,
                    size_hint=(1,None), height=dp(24),
                    halign='left', valign='middle',
                    text_size=(Window.width - dp(60), None),
                ))

                # 2-column ratings grid
                grid = GridLayout(cols=2, size_hint=(1,None), height=dp(80),
                                  spacing=[dp(4), dp(4)])
                for lbl_t, val in [('Taste',taste),('Quality',quality),
                                   ('Hygiene',hygiene),('Menu',menu_fol)]:
                    grid.add_widget(Label(
                        text=f'{lbl_t}: {"⭐"*val} ({val}/5)',
                        color=TXT, font_size=15,
                        halign='left', valign='middle',
                        text_size=((Window.width - dp(60)) / 2, None),
                    ))
                card.add_widget(grid)

                card.add_widget(Label(
                    text=f'Average Rating:  {"⭐"*int(round(avg))}  {avg:.1f} / 5',
                    color=ACCENT, font_size=17, bold=True,
                    size_hint=(1,None), height=dp(30),
                    halign='left', valign='middle',
                    text_size=(Window.width - dp(60), None),
                ))

                card.add_widget(Label(
                    text=f'Submitted: {sub_at}',
                    color=TGREY, font_size=13,
                    size_hint=(1,None), height=dp(22),
                    halign='left', valign='middle',
                    text_size=(Window.width - dp(60), None),
                ))

                if complaint:
                    card.add_widget(Label(
                        text=f'💬  {complaint}',
                        color=(0.65, 0.25, 0.05, 1), font_size=15,
                        size_hint=(1,None), height=dp(36),
                        halign='left', valign='middle',
                        text_size=(Window.width - dp(60), None),
                    ))

                body.add_widget(card)

        body.add_widget(Widget(size_hint_y=None, height=dp(24)))
        scroll.add_widget(body)
        outer.add_widget(scroll)
        self.add_widget(outer)

    def _home(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

# ═══════════════════════════════════════════════════════════
#  SCREEN 4 — MANAGEMENT ALERTS
# ═══════════════════════════════════════════════════════════
class AlertsScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self._build()

    def _build(self):
        outer = BoxLayout(orientation='vertical')
        bg(outer, BG)

        topbar = BoxLayout(size_hint=(1,None), height=dp(64), padding=[dp(12),0])
        bg(topbar, CARD)
        bk = Button(text='←  Back', size_hint=(None,1), width=dp(110),
                    background_normal='', background_color=(0,0,0,0),
                    color=ACCENT, font_size=18, bold=True)
        bk.bind(on_release=lambda *_: self._home())
        topbar.add_widget(bk)
        topbar.add_widget(Label(text='🚨  Management Alerts',
                                color=TXT, font_size=20, bold=True))
        outer.add_widget(topbar)

        # Info strip
        strip = BoxLayout(size_hint=(1,None), height=dp(44), padding=[dp(14),0])
        bg(strip, (1.00, 0.90, 0.90, 1))
        strip.add_widget(Label(
            text='Auto-alert fires when Average Rating < 3 / 5',
            color=RED, font_size=16, bold=True,
            halign='left', valign='middle',
            text_size=(Window.width - dp(30), None),
        ))
        outer.add_widget(strip)

        scroll = ScrollView(size_hint=(1,1))
        body   = BoxLayout(orientation='vertical',
                           padding=[dp(14), dp(12)], spacing=dp(12),
                           size_hint_y=None)
        body.bind(minimum_height=body.setter('height'))

        with get_conn() as con:
            c = con.cursor()
            c.execute("""
                SELECT reg_no,avg_rating,meal_time,date,message,created_at
                FROM alerts ORDER BY id DESC
            """)
            rows = c.fetchall()

        if not rows:
            body.add_widget(Label(
                text='No alerts yet.\n(Alerts appear when Avg Rating < 3)',
                color=TGREY, font_size=18,
                halign='center', valign='middle',
                text_size=(Window.width - dp(40), None),
            ))
        else:
            body.add_widget(lbl(f'Total Alerts: {len(rows)}',
                                fs=19, color=RED, bold=True, h=dp(34)))
            for row in rows:
                reg_no, avg, meal_time, date, message, created_at = row

                card = Card(size_hint=(1,None), height=dp(180))

                card.add_widget(Label(
                    text='🚨  LOW QUALITY ALERT',
                    color=RED, font_size=18, bold=True,
                    size_hint=(1,None), height=dp(32),
                    halign='left', valign='middle',
                    text_size=(Window.width - dp(60), None),  
                ))
                card.add_widget(Label(
                    text=f'Reg No: {reg_no}     Avg Rating: {avg:.1f} / 5',
                    color=TXT, font_size=17,
                    size_hint=(1,None), height=dp(28),
                    halign='left', valign='middle',
                    text_size=(Window.width - dp(60), None),
                ))
                card.add_widget(Label(
                    text=f'{meal_time}   •   Date: {date}',
                    color=TGREY, font_size=16,
                    size_hint=(1,None), height=dp(26),
                    halign='left', valign='middle',
                    text_size=(Window.width - dp(60), None),
                ))
                card.add_widget(Label(
                    text=f'Reported: {created_at}',
                    color=TGREY, font_size=14,
                    size_hint=(1,None), height=dp(22),
                    halign='left', valign='middle',
                    text_size=(Window.width - dp(60), None),
                ))

                def make_show(m):
                    def show(*_):
                        content = BoxLayout(orientation='vertical',
                                            padding=dp(18), spacing=dp(12))
                        bg(content, CARD)
                        content.add_widget(Label(
                            text=m, color=TXT, font_size=16,
                            halign='left', valign='top',
                            text_size=(Window.width * 0.78, None),
                        ))
                        ok = btn('Close', RED, h=dp(56))
                        p = Popup(title='Alert Detail', content=content,
                                  size_hint=(0.90, None), height=dp(360),
                                  background='', separator_color=RED,
                                  title_color=TXT, title_size=18)
                        ok.bind(on_release=p.dismiss)
                        content.add_widget(ok)
                        p.open()
                    return show

                db_btn = btn('View Full Details',
                             (0.88, 0.82, 0.82, 1), fg=RED, fs=16, h=dp(46))
                db_btn.bind(on_release=make_show(message))
                card.add_widget(db_btn)

                body.add_widget(card)

        body.add_widget(Widget(size_hint_y=None, height=dp(24)))
        scroll.add_widget(body)
        outer.add_widget(scroll)
        self.add_widget(outer)

    def _home(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

# ═══════════════════════════════════════════════════════════
#  APP
# ═══════════════════════════════════════════════════════════
class MessApp(App):
    def build(self):
        init_db()
        self.title = 'Ramgarh Mess Management System'
        sm = ScreenManager()
        sm.add_widget(HomeScreen      (name='home'))
        sm.add_widget(FeedbackScreen  (name='feedback'))
        sm.add_widget(ComplaintsScreen(name='complaints'))
        sm.add_widget(AlertsScreen    (name='alerts'))
        return sm

if __name__ == '__main__':
    MessApp().run()
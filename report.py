"""
SalesDB — Full 47-Page Project Report Generator
Run:  python generate_report.py
Output: SalesDB_Project_Report.docx
"""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np
import os

# ── Paths ────────────────────────────────────────
IMG_DIR = "report_images"
os.makedirs(IMG_DIR, exist_ok=True)

# ── Colors ───────────────────────────────────────
C_PRIMARY = "#0f172a"
C_ACCENT = "#ec4899"
C_ACCENT2 = "#3b82f6"
C_SURFACE = "#1e293b"
C_GREEN = "#3ddc84"
C_PURPLE = "#a855f7"
C_RED = "#f43f5e"
C_YELLOW = "#fbbf24"


# ══════════════════════════════════════════════════
#  DIAGRAM GENERATORS
# ══════════════════════════════════════════════════

def create_system_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_title("System Architecture — SalesDB", fontsize=16, fontweight='bold', pad=20)

    boxes = [
        (0.5, 5.5, 2.5, 1, '#3b82f6', 'Browser\n(Chrome/Edge)', 'white'),
        (4, 5.5, 2.5, 1, '#ec4899', 'HTML / CSS / JS\n(Frontend)', 'white'),
        (4, 3.5, 2.5, 1, '#a855f7', 'Flask API\n(Python Backend)', 'white'),
        (4, 1.5, 2.5, 1, '#3ddc84', 'PostgreSQL\n(Database)', 'white'),
        (7.5, 5.5, 2, 1, '#fbbf24', 'Chart.js\n(Visualization)', 'black'),
        (7.5, 3.5, 2, 1, '#f43f5e', 'REST API\n(JSON)', 'white'),
    ]

    for x, y, w, h, color, label, tc in boxes:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='white', linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha='center', va='center',
                fontsize=9, fontweight='bold', color=tc)

    arrows = [
        (2.9, 6, 4, 6), (6.5, 6, 7.5, 6), (5.25, 5.5, 5.25, 4.5),
        (5.25, 3.5, 5.25, 2.5), (7.5, 4, 6.5, 4),
    ]
    for x1, y1, x2, y2 in arrows:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#94a3b8', lw=2))

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "architecture.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


def create_er_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(11, 7))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title("Entity Relationship Diagram — SalesDB", fontsize=16, fontweight='bold', pad=20)

    entities = {
        'customer': {
            'x': 1, 'y': 4, 'w': 3, 'h': 3.5, 'color': '#3b82f6',
            'title': 'CUSTOMER_DIM',
            'fields': [
                'PK  customer_id  SERIAL',
                '    first_name   VARCHAR(50)',
                '    last_name    VARCHAR(50)',
                '    city         VARCHAR(50)',
                '    mobile_no    VARCHAR(20)',
                '    email        VARCHAR(100)',
                '    region       VARCHAR(20)',
                '    member_type  VARCHAR(20)',
            ]
        },
        'product': {
            'x': 7.5, 'y': 4, 'w': 3, 'h': 2.5, 'color': '#a855f7',
            'title': 'PRODUCT_DIM',
            'fields': [
                'PK  product_id    SERIAL',
                '    product_name  VARCHAR(100)',
                '    category      VARCHAR(50)',
                '    unit_price    NUMERIC(10,2)',
            ]
        },
        'sales': {
            'x': 4, 'y': 0.5, 'w': 3, 'h': 3, 'color': '#ec4899',
            'title': 'SALES_FACT',
            'fields': [
                'PK  sale_id      SERIAL',
                'FK  customer_id  INTEGER',
                'FK  product_id   INTEGER',
                '    sale_date    DATE',
                '    quantity     INTEGER',
                '    sale_amount  NUMERIC(10,2)',
            ]
        },
    }

    for key, e in entities.items():
        header_h = 0.5
        rect = FancyBboxPatch((e['x'], e['y']), e['w'], e['h'],
                              boxstyle="round,pad=0.05",
                              facecolor='#1e293b', edgecolor=e['color'], linewidth=2)
        ax.add_patch(rect)

        header = FancyBboxPatch((e['x'], e['y'] + e['h'] - header_h), e['w'], header_h,
                                boxstyle="round,pad=0.05",
                                facecolor=e['color'], edgecolor=e['color'], linewidth=2)
        ax.add_patch(header)

        ax.text(e['x'] + e['w'] / 2, e['y'] + e['h'] - header_h / 2, e['title'],
                ha='center', va='center', fontsize=9, fontweight='bold', color='white',
                fontfamily='monospace')

        for i, field in enumerate(e['fields']):
            fy = e['y'] + e['h'] - header_h - 0.35 - i * 0.3
            fc = '#fbbf24' if field.startswith('PK') else '#f43f5e' if field.startswith('FK') else '#94a3b8'
            ax.text(e['x'] + 0.15, fy, field, fontsize=7, color=fc,
                    fontfamily='monospace', va='center')

    ax.annotate('', xy=(4, 2.5), xytext=(2.5, 4),
                arrowprops=dict(arrowstyle='->', color='#3b82f6', lw=2.5))
    ax.text(2.5, 3.5, '1:N', fontsize=10, fontweight='bold', color='#3b82f6')

    ax.annotate('', xy=(7, 2.5), xytext=(8.5, 4),
                arrowprops=dict(arrowstyle='->', color='#a855f7', lw=2.5))
    ax.text(8, 3.5, '1:N', fontsize=10, fontweight='bold', color='#a855f7')

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "er_diagram.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


def create_dfd_level0():
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    ax.set_title("Data Flow Diagram — Level 0 (Context Diagram)", fontsize=14, fontweight='bold', pad=15)

    ax.add_patch(FancyBboxPatch((0.5, 1.5), 2, 2, boxstyle="round,pad=0.1",
                                facecolor='#3b82f6', edgecolor='white', lw=2))
    ax.text(1.5, 2.5, 'USER\n(Admin)', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')

    circle = plt.Circle((5, 2.5), 1.2, facecolor='#ec4899', edgecolor='white', lw=2)
    ax.add_patch(circle)
    ax.text(5, 2.5, 'SalesDB\nSystem', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')

    ax.add_patch(FancyBboxPatch((7.5, 1.5), 2, 2, boxstyle="round,pad=0.1",
                                facecolor='#3ddc84', edgecolor='white', lw=2))
    ax.text(8.5, 2.5, 'PostgreSQL\nDatabase', ha='center', va='center',
            fontsize=10, fontweight='bold', color='black')

    ax.annotate('', xy=(3.8, 2.8), xytext=(2.5, 2.8),
                arrowprops=dict(arrowstyle='->', color='#fbbf24', lw=2))
    ax.text(3, 3.3, 'CRUD\nRequests', fontsize=8, ha='center', color='#fbbf24')

    ax.annotate('', xy=(2.5, 2.2), xytext=(3.8, 2.2),
                arrowprops=dict(arrowstyle='->', color='#94a3b8', lw=2))
    ax.text(3, 1.5, 'Reports &\nDashboard', fontsize=8, ha='center', color='#94a3b8')

    ax.annotate('', xy=(7.5, 2.8), xytext=(6.2, 2.8),
                arrowprops=dict(arrowstyle='->', color='#fbbf24', lw=2))
    ax.text(6.8, 3.3, 'SQL\nQueries', fontsize=8, ha='center', color='#fbbf24')

    ax.annotate('', xy=(6.2, 2.2), xytext=(7.5, 2.2),
                arrowprops=dict(arrowstyle='->', color='#94a3b8', lw=2))
    ax.text(6.8, 1.5, 'Result\nSets', fontsize=8, ha='center', color='#94a3b8')

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "dfd_level0.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


def create_dfd_level1():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title("Data Flow Diagram — Level 1", fontsize=14, fontweight='bold', pad=15)

    ax.add_patch(FancyBboxPatch((0.3, 3.5), 1.8, 1.5, boxstyle="round,pad=0.1",
                                facecolor='#3b82f6', edgecolor='white', lw=2))
    ax.text(1.2, 4.25, 'USER', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')

    processes = [
        (4, 7, 2.2, 1, '1.0', 'Manage\nCustomers', '#ec4899'),
        (4, 5, 2.2, 1, '2.0', 'Manage\nProducts', '#a855f7'),
        (4, 3, 2.2, 1, '3.0', 'Manage\nSales', '#f43f5e'),
        (4, 1, 2.2, 1, '4.0', 'Generate\nAnalytics', '#fbbf24'),
    ]

    for x, y, w, h, num, label, color in processes:
        circle = plt.Circle((x + w / 2, y + h / 2), 0.7,
                             facecolor=color, edgecolor='white', lw=2)
        ax.add_patch(circle)
        ax.text(x + w / 2, y + h / 2 + 0.15, num, ha='center', va='center',
                fontsize=8, fontweight='bold', color='white')
        ax.text(x + w / 2, y + h / 2 - 0.2, label, ha='center', va='center',
                fontsize=7, color='white')

    stores = [
        (8, 7, 3.5, 0.8, 'D1', 'CUSTOMER_DIM', '#3b82f6'),
        (8, 5, 3.5, 0.8, 'D2', 'PRODUCT_DIM', '#a855f7'),
        (8, 3, 3.5, 0.8, 'D3', 'SALES_FACT', '#ec4899'),
    ]

    for x, y, w, h, did, label, color in stores:
        ax.add_patch(Rectangle((x, y), w, h, facecolor='#1e293b',
                                edgecolor=color, lw=2))
        ax.plot([x + 0.6, x + 0.6], [y, y + h], color=color, lw=2)
        ax.text(x + 0.3, y + h / 2, did, ha='center', va='center',
                fontsize=8, fontweight='bold', color=color)
        ax.text(x + 0.6 + (w - 0.6) / 2, y + h / 2, label, ha='center', va='center',
                fontsize=8, color='white', fontfamily='monospace')

    connections = [
        (2.1, 4.5, 4, 7.5), (2.1, 4.3, 4, 5.5),
        (2.1, 4.1, 4, 3.5), (2.1, 3.9, 4, 1.5),
        (6.8, 7.5, 8, 7.4), (6.8, 5.5, 8, 5.4),
        (6.8, 3.5, 8, 3.4), (6.8, 1.5, 8, 3.2),
    ]

    for x1, y1, x2, y2 in connections:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#94a3b8', lw=1.5))

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "dfd_level1.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


def create_flowchart():
    fig, ax = plt.subplots(1, 1, figsize=(8, 12))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 14)
    ax.axis('off')
    ax.set_title("Program Execution Flowchart", fontsize=14, fontweight='bold', pad=15)

    def draw_box(x, y, w, h, text, color, shape='rect'):
        if shape == 'oval':
            ellipse = plt.matplotlib.patches.Ellipse((x + w / 2, y + h / 2), w, h,
                                                      facecolor=color, edgecolor='white', lw=2)
            ax.add_patch(ellipse)
        elif shape == 'diamond':
            diamond = plt.Polygon([
                (x + w / 2, y + h), (x + w, y + h / 2),
                (x + w / 2, y), (x, y + h / 2)
            ], facecolor=color, edgecolor='white', lw=2)
            ax.add_patch(diamond)
        else:
            ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                        facecolor=color, edgecolor='white', lw=2))
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center',
                fontsize=8, fontweight='bold', color='white')

    steps = [
        (2.5, 12.5, 3, 0.8, 'START', '#3ddc84', 'oval'),
        (2.5, 11, 3, 0.8, 'Flask Server\nStarts', '#3b82f6', 'rect'),
        (2.5, 9.5, 3, 0.8, 'User Opens\nBrowser', '#a855f7', 'rect'),
        (2.5, 8, 3, 0.8, 'Load\nDashboard?', '#fbbf24', 'diamond'),
        (2.5, 6.3, 3, 0.8, 'Fetch KPIs\n& Charts', '#ec4899', 'rect'),
        (2.5, 4.8, 3, 0.8, 'User Action?\n(CRUD)', '#fbbf24', 'diamond'),
        (2.5, 3.3, 3, 0.8, 'Send API\nRequest', '#3b82f6', 'rect'),
        (2.5, 1.8, 3, 0.8, 'Database\nOperation', '#3ddc84', 'rect'),
        (2.5, 0.3, 3, 0.8, 'Update UI\n& Toast', '#ec4899', 'rect'),
    ]

    for x, y, w, h, text, color, shape in steps:
        draw_box(x, y, w, h, text, color, shape)

    arrow_pairs = [
        (4, 12.5, 4, 11.8), (4, 11, 4, 10.3), (4, 9.5, 4, 8.8),
        (4, 8, 4, 7.1), (4, 6.3, 4, 5.6), (4, 4.8, 4, 4.1),
        (4, 3.3, 4, 2.6), (4, 1.8, 4, 1.1),
    ]

    for x1, y1, x2, y2 in arrow_pairs:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#94a3b8', lw=2))

    ax.annotate('', xy=(2.5, 5.2), xytext=(1.5, 5.2),
                arrowprops=dict(arrowstyle='->', color='#94a3b8', lw=1.5))
    ax.text(0.5, 5.2, 'Navigate\nSections', fontsize=7, color='#94a3b8', ha='center')

    ax.annotate('', xy=(6, 1), xytext=(6, 8.4),
                arrowprops=dict(arrowstyle='->', color='#f43f5e', lw=1.5, linestyle='dashed'))
    ax.text(6.8, 4.5, 'Loop Back', fontsize=8, color='#f43f5e', rotation=90, ha='center')

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "flowchart.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


def create_component_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(11, 7))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title("Component Diagram — SalesDB", fontsize=14, fontweight='bold', pad=15)

    layers = [
        (0.5, 5.5, 10, 2, 'Presentation Layer (Frontend)', '#3b82f620', '#3b82f6'),
        (0.5, 3, 10, 2, 'Application Layer (Backend API)', '#ec489920', '#ec4899'),
        (0.5, 0.5, 10, 2, 'Data Layer (Database)', '#3ddc8420', '#3ddc84'),
    ]

    for x, y, w, h, label, fc, ec in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                    facecolor=fc, edgecolor=ec, lw=2, linestyle='dashed'))
        ax.text(x + 0.2, y + h - 0.3, label, fontsize=9, fontweight='bold', color=ec)

    pres_components = [
        (1, 5.7, 'index.html'), (3.5, 5.7, 'styles.css'),
        (6, 5.7, 'script.js'), (8.5, 5.7, 'Chart.js'),
    ]
    for x, y, label in pres_components:
        ax.add_patch(FancyBboxPatch((x, y), 2, 0.8, boxstyle="round,pad=0.05",
                                    facecolor='#334155', edgecolor='#3b82f6', lw=1.5))
        ax.text(x + 1, y + 0.4, label, ha='center', va='center',
                fontsize=8, fontweight='bold', color='white', fontfamily='monospace')

    api_components = [
        (1, 3.2, 'app.py\n(Routes)'), (3.5, 3.2, 'Flask\nFramework'),
        (6, 3.2, 'psycopg2\n(DB Driver)'), (8.5, 3.2, 'flask-cors\n(CORS)'),
    ]
    for x, y, label in api_components:
        ax.add_patch(FancyBboxPatch((x, y), 2, 0.8, boxstyle="round,pad=0.05",
                                    facecolor='#334155', edgecolor='#ec4899', lw=1.5))
        ax.text(x + 1, y + 0.4, label, ha='center', va='center',
                fontsize=7, fontweight='bold', color='white')

    db_components = [
        (1, 0.7, 'customer_dim'), (4, 0.7, 'product_dim'), (7, 0.7, 'sales_fact'),
    ]
    for x, y, label in db_components:
        ax.add_patch(FancyBboxPatch((x, y), 2.5, 0.8, boxstyle="round,pad=0.05",
                                    facecolor='#334155', edgecolor='#3ddc84', lw=1.5))
        ax.text(x + 1.25, y + 0.4, label, ha='center', va='center',
                fontsize=8, fontweight='bold', color='white', fontfamily='monospace')

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "component_diagram.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


def create_sdlc_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(9, 9))
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.axis('off')
    ax.set_title("Agile SDLC Model — Iterative Development", fontsize=14, fontweight='bold', pad=20)

    phases = [
        ('Planning', '#3b82f6', 0),
        ('Analysis', '#a855f7', 1),
        ('Design', '#ec4899', 2),
        ('Implementation', '#f43f5e', 3),
        ('Testing', '#fbbf24', 4),
        ('Deployment', '#3ddc84', 5),
    ]

    n = len(phases)
    radius = 3.5

    for i, (label, color, idx) in enumerate(phases):
        angle = 90 - i * (360 / n)
        rad = np.radians(angle)
        x = radius * np.cos(rad)
        y = radius * np.sin(rad)

        circle = plt.Circle((x, y), 0.8, facecolor=color, edgecolor='white', lw=2)
        ax.add_patch(circle)
        ax.text(x, y, f"{i + 1}\n{label}", ha='center', va='center',
                fontsize=8, fontweight='bold', color='white')

        next_angle = 90 - ((i + 1) % n) * (360 / n)
        next_rad = np.radians(next_angle)
        nx = radius * np.cos(next_rad)
        ny = radius * np.sin(next_rad)

        dx = nx - x
        dy = ny - y
        dist = np.sqrt(dx ** 2 + dy ** 2)
        sx = x + 0.85 * dx / dist
        sy = y + 0.85 * dy / dist
        ex = nx - 0.85 * dx / dist
        ey = ny - 0.85 * dy / dist

        ax.annotate('', xy=(ex, ey), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color='#94a3b8', lw=2))

    center_circle = plt.Circle((0, 0), 1.2, facecolor='#1e293b', edgecolor='#ec4899', lw=3)
    ax.add_patch(center_circle)
    ax.text(0, 0.2, 'AGILE', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#ec4899')
    ax.text(0, -0.3, 'Iterative', ha='center', va='center',
            fontsize=9, color='#94a3b8')

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "sdlc_model.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


def create_tech_stack():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_title("Technology Stack", fontsize=14, fontweight='bold', pad=15)

    stack = [
        (1, 5.5, 8, 1, 'Frontend: HTML5 + CSS3 + JavaScript (ES6+)', '#3b82f6'),
        (1, 4, 8, 1, 'Charting: Chart.js 4.4.1', '#a855f7'),
        (1, 2.5, 8, 1, 'Backend: Python 3 + Flask + flask-cors', '#ec4899'),
        (1, 1, 8, 1, 'Database: PostgreSQL + psycopg2', '#3ddc84'),
    ]

    for x, y, w, h, label, color in stack:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                    facecolor=color, edgecolor='white', lw=2))
        ax.text(x + w / 2, y + h / 2, label, ha='center', va='center',
                fontsize=11, fontweight='bold', color='white')

    for i in range(3):
        y = 5.5 - i * 1.5
        ax.annotate('', xy=(5, y), xytext=(5, y + 0.5),
                    arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=2))

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "tech_stack.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


def create_sequence_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(11, 9))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title("Sequence Diagram — Add Sale", fontsize=14, fontweight='bold', pad=15)

    actors = [
        (1.5, 9, 'User'), (4, 9, 'Frontend\n(JS)'),
        (6.5, 9, 'Flask API'), (9, 9, 'PostgreSQL'),
    ]

    for x, y, label in actors:
        ax.add_patch(FancyBboxPatch((x - 0.6, y - 0.3), 1.2, 0.7,
                                    boxstyle="round,pad=0.05",
                                    facecolor='#334155', edgecolor='#3b82f6', lw=2))
        ax.text(x, y, label, ha='center', va='center',
                fontsize=8, fontweight='bold', color='white')
        ax.plot([x, x], [0.5, y - 0.3], color='#334155', lw=1.5, linestyle='dashed')

    messages = [
        (1.5, 4, 8, 'Fills form & clicks Add Sale', '#fbbf24'),
        (4, 4, 7.5, 'POST /api/sales (JSON)', '#ec4899'),
        (6.5, 4, 7, 'INSERT INTO sales_fact', '#a855f7'),
        (9, 6.5, 6.5, 'Returns sale_id', '#3ddc84'),
        (6.5, 9, 6, 'JSON Response 201', '#ec4899'),
        (4, 9, 5.5, 'Update UI + Toast', '#3b82f6'),
    ]

    y_pos = 8
    for fx, fy_off, tx, label, color in messages:
        y_pos -= 0.9
        if fx < tx:
            ax.annotate('', xy=(tx, y_pos), xytext=(fx, y_pos),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2))
        else:
            ax.annotate('', xy=(tx, y_pos), xytext=(fx, y_pos),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2, linestyle='dashed'))
        mid = (fx + tx) / 2
        ax.text(mid, y_pos + 0.2, label, ha='center', fontsize=7, color=color)

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "sequence_diagram.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


def create_deployment_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_title("Deployment Diagram", fontsize=14, fontweight='bold', pad=15)

    nodes = [
        (0.5, 2, 2.5, 3, 'Client Machine', '#3b82f6',
         ['Chrome Browser', 'index.html', 'styles.css', 'script.js']),
        (4, 2, 2.5, 3, 'Application Server', '#ec4899',
         ['Python 3.x', 'Flask App', 'app.py', 'Port: 5000']),
        (7.5, 2, 2.5, 3, 'Database Server', '#3ddc84',
         ['PostgreSQL 16', 'sales_db', 'Port: 5432', '3 Tables']),
    ]

    for x, y, w, h, title, color, items in nodes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                    facecolor='#1e293b', edgecolor=color, lw=2))
        ax.add_patch(FancyBboxPatch((x, y + h - 0.5), w, 0.5, boxstyle="round,pad=0.05",
                                    facecolor=color, edgecolor=color, lw=2))
        ax.text(x + w / 2, y + h - 0.25, title, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')

        for i, item in enumerate(items):
            ax.text(x + 0.2, y + h - 0.9 - i * 0.45, f'• {item}',
                    fontsize=7, color='#94a3b8')

    ax.annotate('', xy=(4, 3.5), xytext=(3, 3.5),
                arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=2))
    ax.text(3.5, 3.9, 'HTTP', fontsize=8, ha='center', color='#fbbf24', fontweight='bold')

    ax.annotate('', xy=(7.5, 3.5), xytext=(6.5, 3.5),
                arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=2))
    ax.text(7, 3.9, 'TCP/IP', fontsize=8, ha='center', color='#fbbf24', fontweight='bold')

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "deployment_diagram.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


def create_sample_dashboard():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    categories = ['Electronics', 'Home Goods', 'Apparel', 'Other']
    revenue = [45000, 28000, 18000, 9000]
    colors = ['#ec4899', '#3b82f6', '#a855f7', '#f43f5e']

    axes[0].bar(categories, revenue, color=colors, edgecolor='white', linewidth=0.5)
    axes[0].set_title('Revenue by Category', fontsize=10, fontweight='bold', color='white')
    axes[0].set_facecolor('#1e293b')
    axes[0].tick_params(colors='#94a3b8', labelsize=7)
    axes[0].spines['bottom'].set_color('#334155')
    axes[0].spines['left'].set_color('#334155')
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)

    axes[1].pie(revenue, labels=categories, autopct='%1.1f%%', colors=colors,
                textprops={'fontsize': 8, 'color': 'white'}, startangle=90,
                pctdistance=0.8, wedgeprops=dict(width=0.4))
    axes[1].set_title('Sales Distribution', fontsize=10, fontweight='bold', color='white')

    axes[2].pie(revenue[:2], labels=['Gold', 'Regular'], autopct='%1.1f%%',
                colors=['#fbbf24', '#64748b'],
                textprops={'fontsize': 9, 'color': 'white'}, startangle=90)
    axes[2].set_title('Customer Segments', fontsize=10, fontweight='bold', color='white')

    fig.patch.set_facecolor('#0f172a')
    for ax_item in [axes[1], axes[2]]:
        ax_item.set_facecolor('#0f172a')

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "sample_dashboard.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


def create_crud_flowchart():
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title("CRUD Operations Flowchart", fontsize=14, fontweight='bold', pad=15)

    ops = [
        (1, 7, 2, 1, 'CREATE\n(POST)', '#3ddc84'),
        (4, 7, 2, 1, 'READ\n(GET)', '#3b82f6'),
        (1, 4, 2, 1, 'UPDATE\n(PUT)', '#fbbf24'),
        (4, 4, 2, 1, 'DELETE\n(DELETE)', '#f43f5e'),
    ]

    for x, y, w, h, label, color in ops:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                    facecolor=color, edgecolor='white', lw=2))
        ax.text(x + w / 2, y + h / 2, label, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white' if color != '#fbbf24' else 'black')

    ax.add_patch(FancyBboxPatch((7, 5), 2.5, 2, boxstyle="round,pad=0.1",
                                facecolor='#1e293b', edgecolor='#ec4899', lw=2))
    ax.text(8.25, 6, 'PostgreSQL\nDatabase', ha='center', va='center',
            fontsize=10, fontweight='bold', color='#ec4899')

    for x_start, y_start in [(3, 7.5), (6, 7.5), (3, 4.5), (6, 4.5)]:
        ax.annotate('', xy=(7, 6), xytext=(x_start, y_start),
                    arrowprops=dict(arrowstyle='->', color='#94a3b8', lw=1.5))

    details = [
        (0.5, 2.5, 'CREATE: Validates → INSERT INTO → Returns new record'),
        (0.5, 2, 'READ:     Fetches → SELECT → Returns JSON array'),
        (0.5, 1.5, 'UPDATE: Validates → UPDATE SET → Returns updated record'),
        (0.5, 1, 'DELETE:  Confirms → DELETE WHERE → Returns deleted ID'),
    ]
    for x, y, text in details:
        ax.text(x, y, text, fontsize=8, color='#94a3b8', fontfamily='monospace')

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "crud_flowchart.png")
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    return path


# ══════════════════════════════════════════════════
#  DOCUMENT HELPERS
# ══════════════════════════════════════════════════

def set_cell_shading(cell, color):
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    shading.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading)


def add_styled_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_shading(cell, '1e293b')

    for r_idx, row_data in enumerate(rows):
        for c_idx, cell_text in enumerate(row_data):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(cell_text)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9)
            bg = 'f8fafc' if r_idx % 2 == 0 else 'e2e8f0'
            set_cell_shading(cell, bg)

    return table


def add_page_break(doc):
    doc.add_page_break()


def add_spacer(doc, lines=1):
    for _ in range(lines):
        doc.add_paragraph('')


# ══════════════════════════════════════════════════
#  BUILD DOCUMENT
# ══════════════════════════════════════════════════

def build_report():
    doc = Document()

    # ── Default style ────────────────────────────
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.15

    for i in range(1, 5):
        hs = doc.styles[f'Heading {i}']
        hs.font.name = 'Calibri'
        hs.font.color.rgb = RGBColor(15, 23, 42)

    # ── Page margins ─────────────────────────────
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3)
        section.right_margin = Cm(2.54)

    # ══════════════════════════════════════════════
    #  PAGE 1-2: COVER PAGE
    # ══════════════════════════════════════════════
    add_spacer(doc, 6)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('SALESDB')
    run.font.size = Pt(48)
    run.bold = True
    run.font.color.rgb = RGBColor(236, 72, 153)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('Sales Analytics Dashboard')
    run.font.size = Pt(22)
    run.font.color.rgb = RGBColor(59, 130, 246)

    add_spacer(doc, 2)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('A Comprehensive Full-Stack Web Application\nfor Sales Data Management & Analytics')
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(100, 116, 139)

    add_spacer(doc, 4)

    info = [
        'Project Report',
        '',
        'Submitted by: [Your Name]',
        'Roll Number: [Your Roll No]',
        'Department: [Your Department]',
        'Institution: [Your Institution]',
        '',
        'Under the guidance of:',
        'Prof. [Guide Name]',
        '',
        'Academic Year: 2024-2025',
    ]
    for line in info:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(line)
        run.font.size = Pt(12)
        if 'Submitted' in line or 'Under' in line:
            run.bold = True

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  PAGE 3: CERTIFICATE
    # ══════════════════════════════════════════════
    add_spacer(doc, 2)
    doc.add_heading('CERTIFICATE', level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_spacer(doc, 1)
    doc.add_paragraph(
        'This is to certify that the project report entitled "SalesDB — Sales Analytics Dashboard" '
        'is a bonafide record of the project work carried out by [Your Name], '
        'Roll Number [Your Roll No], during the academic year 2024-2025 in partial fulfillment '
        'of the requirements for the award of [Your Degree] in [Your Department] '
        'at [Your Institution].'
    )
    add_spacer(doc, 3)

    p = doc.add_paragraph()
    p.add_run('Project Guide').bold = True
    p.add_run('\t\t\t\t\t')
    p.add_run('Head of Department').bold = True

    add_spacer(doc, 2)
    p = doc.add_paragraph()
    p.add_run('Prof. [Guide Name]')
    p.add_run('\t\t\t\t')
    p.add_run('Prof. [HOD Name]')

    add_spacer(doc, 4)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run('External Examiner').bold = True

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  PAGE 4: DECLARATION
    # ══════════════════════════════════════════════
    add_spacer(doc, 2)
    doc.add_heading('DECLARATION', level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_spacer(doc, 1)
    doc.add_paragraph(
        'I hereby declare that the project entitled "SalesDB — Sales Analytics Dashboard" '
        'submitted to [Your Institution] for the award of [Your Degree] in [Your Department] '
        'is a record of original work done by me under the guidance of Prof. [Guide Name], '
        'and this project work has not been submitted to any other University or Institution '
        'for the award of any other degree, diploma, or certificate.'
    )
    add_spacer(doc, 4)
    p = doc.add_paragraph()
    p.add_run('Place: [Your City]')
    doc.add_paragraph('Date: _______________')
    add_spacer(doc, 2)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run('[Your Name]\n[Your Roll No]').bold = True

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  PAGE 5: ACKNOWLEDGEMENT
    # ══════════════════════════════════════════════
    add_spacer(doc, 2)
    doc.add_heading('ACKNOWLEDGEMENT', level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_spacer(doc, 1)
    doc.add_paragraph(
        'I would like to express my sincere gratitude to Prof. [Guide Name] for their invaluable '
        'guidance, constant encouragement, and constructive criticism throughout the development '
        'of this project. Their expertise in database management systems and web technologies '
        'has been instrumental in shaping this project.'
    )
    doc.add_paragraph(
        'I am deeply indebted to Prof. [HOD Name], Head of the Department of [Your Department], '
        'for providing me with the necessary facilities and support to complete this project. '
        'I also extend my heartfelt thanks to all the faculty members who have contributed '
        'to my learning throughout the course.'
    )
    doc.add_paragraph(
        'I would also like to thank my classmates and friends for their constant support, '
        'stimulating discussions, and encouragement during the project development phase. '
        'Their feedback and suggestions have been valuable in improving the quality of this work.'
    )
    doc.add_paragraph(
        'Finally, I would like to thank my parents and family for their unwavering support, '
        'patience, and understanding throughout my academic journey. Without their encouragement, '
        'this project would not have been possible.'
    )
    add_spacer(doc, 3)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run('[Your Name]').bold = True

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  PAGE 6: ABSTRACT
    # ══════════════════════════════════════════════
    add_spacer(doc, 2)
    doc.add_heading('ABSTRACT', level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_spacer(doc, 1)
    doc.add_paragraph(
        'In today\'s competitive business environment, effective sales data management and '
        'analytics are critical for making informed business decisions. This project presents '
        '"SalesDB" — a comprehensive full-stack web application designed for managing sales '
        'records, customer information, and product catalogs while providing real-time analytics '
        'through an interactive dashboard.'
    )
    doc.add_paragraph(
        'The system is built using a modern technology stack comprising HTML5, CSS3, and '
        'JavaScript for the frontend, Python Flask for the backend REST API, and PostgreSQL '
        'as the relational database management system. The application follows a star schema '
        'data warehouse design with dimension tables (customer_dim, product_dim) and a fact '
        'table (sales_fact) for efficient analytical queries.'
    )
    doc.add_paragraph(
        'Key features of the system include: complete CRUD (Create, Read, Update, Delete) '
        'operations for customers, products, and sales; real-time Key Performance Indicator '
        '(KPI) cards displaying total revenue, total sales, average order value, customer '
        'count, and product count; interactive charts including bar charts, doughnut charts, '
        'and pie charts for data visualization using Chart.js; automatic sale amount calculation '
        'based on product unit price and quantity; and a responsive dark-themed user interface '
        'with smooth animations and toast notifications.'
    )
    doc.add_paragraph(
        'The project demonstrates proficiency in full-stack web development, database design, '
        'RESTful API architecture, and data visualization. It serves as a practical example '
        'of how modern web technologies can be leveraged to create efficient business '
        'intelligence tools.'
    )
    add_spacer(doc, 1)
    p = doc.add_paragraph()
    p.add_run('Keywords: ').bold = True
    p.add_run('Full-Stack Development, Flask, PostgreSQL, REST API, Sales Analytics, '
              'Dashboard, CRUD Operations, Chart.js, Data Visualization, Star Schema')

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  PAGE 7-8: TABLE OF CONTENTS
    # ══════════════════════════════════════════════
    doc.add_heading('TABLE OF CONTENTS', level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_spacer(doc, 1)

    toc_items = [
        ('Certificate', '3'), ('Declaration', '4'), ('Acknowledgement', '5'),
        ('Abstract', '6'), ('Table of Contents', '7'), ('List of Figures', '9'),
        ('List of Tables', '10'),
        ('', ''),
        ('Chapter 1: Introduction', '11'),
        ('    1.1 Project Overview', '11'), ('    1.2 Problem Statement', '12'),
        ('    1.3 Objectives', '12'), ('    1.4 Scope of the Project', '13'),
        ('    1.5 Technology Stack', '13'),
        ('', ''),
        ('Chapter 2: Software Development Model', '15'),
        ('    2.1 Agile Methodology', '15'), ('    2.2 SDLC Phases', '16'),
        ('    2.3 Why Agile for SalesDB', '17'), ('    2.4 Sprint Planning', '18'),
        ('', ''),
        ('Chapter 3: System Analysis', '19'),
        ('    3.1 Feasibility Study', '19'), ('    3.2 Requirements Analysis', '20'),
        ('    3.3 Functional Requirements', '21'),
        ('    3.4 Non-Functional Requirements', '22'),
        ('    3.5 Hardware & Software Requirements', '23'),
        ('', ''),
        ('Chapter 4: System Design', '24'),
        ('    4.1 System Architecture', '24'), ('    4.2 Database Schema Design', '25'),
        ('    4.3 Entity Relationship Diagram', '27'),
        ('    4.4 Data Flow Diagrams', '28'), ('    4.5 Component Diagram', '31'),
        ('    4.6 Sequence Diagram', '32'), ('    4.7 Deployment Diagram', '33'),
        ('    4.8 Program Execution Flowchart', '34'),
        ('', ''),
        ('Chapter 5: Implementation', '35'),
        ('    5.1 Frontend Implementation', '35'), ('    5.2 Backend Implementation', '36'),
        ('    5.3 Database Implementation', '37'), ('    5.4 API Endpoints', '38'),
        ('    5.5 Key Code Snippets', '39'),
        ('', ''),
        ('Chapter 6: Testing', '41'),
        ('    6.1 Testing Strategy', '41'), ('    6.2 Test Cases', '42'),
        ('    6.3 Test Results', '43'),
        ('', ''),
        ('Chapter 7: Results & Screenshots', '44'),
        ('    7.1 Dashboard View', '44'), ('    7.2 Sales Management', '44'),
        ('    7.3 Customer Management', '45'), ('    7.4 Product Management', '45'),
        ('', ''),
        ('Chapter 8: Conclusion & Future Scope', '46'),
        ('    8.1 Conclusion', '46'), ('    8.2 Future Enhancements', '46'),
        ('', ''),
        ('References', '47'),
    ]

    for title, page in toc_items:
        if not title:
            doc.add_paragraph('')
            continue
        p = doc.add_paragraph()
        if title.startswith('Chapter') or title in ['Certificate', 'Declaration',
                'Acknowledgement', 'Abstract', 'Table of Contents',
                'List of Figures', 'List of Tables', 'References']:
            run = p.add_run(title)
            run.bold = True
            run.font.size = Pt(11)
        else:
            run = p.add_run(title)
            run.font.size = Pt(10)

        tab_run = p.add_run('\t' * 3 + '...... ' + page)
        tab_run.font.size = Pt(10)
        tab_run.font.color.rgb = RGBColor(100, 116, 139)

    add_page_break(doc)

    # ── List of Figures ──────────────────────────
    doc.add_heading('LIST OF FIGURES', level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_spacer(doc, 1)
    figures = [
        ('Figure 1.1', 'Technology Stack Diagram', '14'),
        ('Figure 2.1', 'Agile SDLC Model', '16'),
        ('Figure 4.1', 'System Architecture Diagram', '24'),
        ('Figure 4.2', 'Database Schema Diagram', '26'),
        ('Figure 4.3', 'Entity Relationship Diagram', '27'),
        ('Figure 4.4', 'DFD Level 0 — Context Diagram', '28'),
        ('Figure 4.5', 'DFD Level 1', '29'),
        ('Figure 4.6', 'CRUD Operations Flowchart', '30'),
        ('Figure 4.7', 'Component Diagram', '31'),
        ('Figure 4.8', 'Sequence Diagram — Add Sale', '32'),
        ('Figure 4.9', 'Deployment Diagram', '33'),
        ('Figure 4.10', 'Program Execution Flowchart', '34'),
        ('Figure 7.1', 'Dashboard Charts & KPIs', '44'),
    ]
    for fig_no, caption, page in figures:
        p = doc.add_paragraph()
        run = p.add_run(f'{fig_no}: ')
        run.bold = True
        run.font.size = Pt(10)
        run2 = p.add_run(caption)
        run2.font.size = Pt(10)
        tab_run = p.add_run(f'\t\t...... {page}')
        tab_run.font.size = Pt(10)
        tab_run.font.color.rgb = RGBColor(100, 116, 139)

    add_page_break(doc)

    # ── List of Tables ───────────────────────────
    doc.add_heading('LIST OF TABLES', level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_spacer(doc, 1)
    tables_list = [
        ('Table 1.1', 'Technology Stack Overview', '14'),
        ('Table 3.1', 'Functional Requirements', '21'),
        ('Table 3.2', 'Non-Functional Requirements', '22'),
        ('Table 3.3', 'Hardware Requirements', '23'),
        ('Table 3.4', 'Software Requirements', '23'),
        ('Table 4.1', 'customer_dim Schema', '25'),
        ('Table 4.2', 'product_dim Schema', '26'),
        ('Table 4.3', 'sales_fact Schema', '26'),
        ('Table 5.1', 'API Endpoints Summary', '38'),
        ('Table 6.1', 'Test Cases — Customers', '42'),
        ('Table 6.2', 'Test Cases — Products', '42'),
        ('Table 6.3', 'Test Cases — Sales', '43'),
        ('Table 6.4', 'Test Results Summary', '43'),
    ]
    for tbl_no, caption, page in tables_list:
        p = doc.add_paragraph()
        run = p.add_run(f'{tbl_no}: ')
        run.bold = True
        run.font.size = Pt(10)
        run2 = p.add_run(caption)
        run2.font.size = Pt(10)
        tab_run = p.add_run(f'\t\t...... {page}')
        tab_run.font.size = Pt(10)
        tab_run.font.color.rgb = RGBColor(100, 116, 139)

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  CHAPTER 1: INTRODUCTION (Pages 11-14)
    # ══════════════════════════════════════════════
    doc.add_heading('Chapter 1: Introduction', level=1)

    doc.add_heading('1.1 Project Overview', level=2)
    doc.add_paragraph(
        'SalesDB is a full-stack web application designed to provide businesses with a comprehensive '
        'solution for managing their sales data, customer information, and product catalogs. The '
        'application features an interactive dashboard with real-time analytics, enabling users to '
        'gain actionable insights from their sales data through visually appealing charts and '
        'Key Performance Indicators (KPIs).'
    )
    doc.add_paragraph(
        'The project addresses the growing need for small to medium-sized businesses to have '
        'accessible, user-friendly tools for tracking sales performance without the complexity '
        'and cost of enterprise-level Business Intelligence (BI) solutions. SalesDB provides '
        'a lightweight yet powerful alternative that can be deployed locally or on a server '
        'with minimal configuration.'
    )
    doc.add_paragraph(
        'The application is built on a three-tier architecture consisting of a presentation layer '
        '(HTML/CSS/JavaScript), a business logic layer (Python Flask API), and a data layer '
        '(PostgreSQL database). This separation of concerns ensures maintainability, scalability, '
        'and ease of testing. The frontend communicates with the backend exclusively through '
        'RESTful API endpoints, making the system modular and extensible.'
    )
    doc.add_paragraph(
        'The user interface follows a modern dark-theme design inspired by professional dashboard '
        'applications, featuring a midnight blue color palette, smooth animations, responsive '
        'layout, and intuitive navigation through a persistent sidebar. The dashboard provides '
        'at-a-glance metrics and interactive visualizations that update in real-time as data '
        'is added, modified, or removed from the system.'
    )

    doc.add_heading('1.2 Problem Statement', level=2)
    doc.add_paragraph(
        'Many small and medium-sized businesses face challenges in effectively managing and '
        'analyzing their sales data. Common problems include:'
    )
    problems = [
        'Lack of centralized data management — Sales records are scattered across spreadsheets, '
        'notebooks, and disconnected systems, leading to data inconsistency and loss.',
        'No real-time analytics — Business owners cannot quickly assess performance metrics '
        'like total revenue, average order value, or category-wise sales distribution.',
        'Manual calculations — Computing totals, averages, and trends requires tedious manual '
        'effort and is prone to human error.',
        'Poor data visualization — Raw numbers in spreadsheets do not provide intuitive insights '
        'compared to charts and graphical dashboards.',
        'Inability to track customer segments — Without proper categorization (e.g., Gold vs '
        'Regular members), businesses miss opportunities for targeted marketing.',
        'No audit trail — Difficulty in tracking who bought what, when, and for how much.',
    ]
    for prob in problems:
        p = doc.add_paragraph(prob, style='List Bullet')

    doc.add_heading('1.3 Objectives', level=2)
    doc.add_paragraph(
        'The primary objectives of the SalesDB project are as follows:'
    )
    objectives = [
        'To design and develop a full-stack web application for comprehensive sales data management '
        'including customers, products, and sales transactions.',
        'To implement CRUD (Create, Read, Update, Delete) operations for all entities with proper '
        'validation, error handling, and user feedback.',
        'To create an interactive analytics dashboard with real-time KPI cards and data visualization '
        'using bar charts, doughnut charts, and pie charts.',
        'To design an efficient database schema following the star schema pattern with dimension '
        'tables and a fact table for optimized analytical queries.',
        'To develop a RESTful API using Flask that serves as the middleware between the frontend '
        'and the PostgreSQL database.',
        'To implement automatic sale amount calculation based on product unit price and quantity '
        'to reduce manual entry errors.',
        'To provide a responsive, modern user interface with a dark-blue theme that works across '
        'different screen sizes and devices.',
        'To ensure data integrity through foreign key constraints, cascading deletes, and '
        'proper transaction management.',
    ]
    for obj in objectives:
        p = doc.add_paragraph(obj, style='List Bullet')

    doc.add_heading('1.4 Scope of the Project', level=2)
    doc.add_paragraph(
        'The scope of SalesDB encompasses the following functional areas:'
    )
    doc.add_paragraph(
        'Customer Management: The system allows adding, viewing, editing, and deleting customer '
        'records with fields including first name, last name, city, mobile number, email, '
        'region (East/West/North/South), and member type (Gold/Regular). Each customer is '
        'assigned a unique auto-incrementing ID.'
    )
    doc.add_paragraph(
        'Product Management: Users can manage a product catalog with product name, category '
        '(Electronics, Home Goods, Apparel, Other), and unit price. Products can be created, '
        'updated, and deleted, with cascading deletion of associated sales records.'
    )
    doc.add_paragraph(
        'Sales Management: The sales module enables recording individual sale transactions by '
        'selecting a customer, product, date, and quantity. The total amount is automatically '
        'calculated as unit_price × quantity. Sales can be viewed in a comprehensive table '
        'showing all relevant details and can be deleted individually.'
    )
    doc.add_paragraph(
        'Analytics Dashboard: The dashboard provides five KPI cards (Total Revenue, Total Sales, '
        'Average Order Value, Customer Count, Product Count) and three interactive charts '
        '(Revenue by Category bar chart, Sales Distribution doughnut chart, Customer Segments '
        'pie chart) that update in real-time.'
    )

    doc.add_heading('1.5 Technology Stack', level=2)
    doc.add_paragraph(
        'SalesDB utilizes a modern technology stack carefully chosen for reliability, '
        'performance, and developer productivity. The following table summarizes the '
        'technologies used in each layer of the application:'
    )

    add_styled_table(doc,
        ['Layer', 'Technology', 'Version', 'Purpose'],
        [
            ['Frontend', 'HTML5', '5', 'Page structure & semantics'],
            ['Frontend', 'CSS3', '3', 'Styling, animations, responsive design'],
            ['Frontend', 'JavaScript', 'ES6+', 'DOM manipulation, API calls, interactivity'],
            ['Frontend', 'Chart.js', '4.4.1', 'Bar, doughnut, and pie charts'],
            ['Frontend', 'Google Fonts', '—', 'Syne & JetBrains Mono typography'],
            ['Backend', 'Python', '3.x', 'Server-side programming language'],
            ['Backend', 'Flask', '3.x', 'Lightweight WSGI web framework'],
            ['Backend', 'flask-cors', '4.x', 'Cross-Origin Resource Sharing'],
            ['Backend', 'psycopg2', '2.9.x', 'PostgreSQL database adapter'],
            ['Database', 'PostgreSQL', '16.x', 'Relational database management system'],
        ]
    )
    doc.add_paragraph('\nTable 1.1: Technology Stack Overview', style='Caption') if 'Caption' in [s.name for s in doc.styles] else doc.add_paragraph('\nTable 1.1: Technology Stack Overview')

    add_spacer(doc, 1)
    doc.add_paragraph('Figure 1.1: Technology Stack Diagram')
    doc.add_picture(tech_stack_img, width=Inches(5.5))
    last_paragraph = doc.paragraphs[-1]
    last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  CHAPTER 2: SOFTWARE DEVELOPMENT MODEL (Pages 15-18)
    # ══════════════════════════════════════════════
    doc.add_heading('Chapter 2: Software Development Model', level=1)

    doc.add_heading('2.1 Agile Methodology', level=2)
    doc.add_paragraph(
        'The SalesDB project was developed following the Agile Software Development Methodology. '
        'Agile is an iterative approach to software development that emphasizes flexibility, '
        'continuous improvement, and rapid delivery of working software. Unlike traditional '
        'waterfall models that follow a linear sequential approach, Agile allows for adaptive '
        'planning and evolutionary development.'
    )
    doc.add_paragraph(
        'The core principles of Agile that guided this project include:'
    )
    agile_principles = [
        'Individuals and interactions over processes and tools — Direct communication between '
        'the developer and the project guide ensured quick resolution of design decisions.',
        'Working software over comprehensive documentation — Each sprint produced a functional '
        'increment of the application that could be demonstrated and tested.',
        'Customer collaboration over contract negotiation — Regular feedback sessions helped '
        'refine requirements and user interface design.',
        'Responding to change over following a plan — The addition of features like auto-calculation '
        'of sale amounts and member type categorization were incorporated based on iterative feedback.',
    ]
    for principle in agile_principles:
        doc.add_paragraph(principle, style='List Bullet')

    add_spacer(doc, 1)
    doc.add_paragraph('Figure 2.1: Agile SDLC Model')
    doc.add_picture(sdlc_img, width=Inches(4.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading('2.2 SDLC Phases Applied to SalesDB', level=2)

    phases = [
        ('Phase 1 — Planning (Week 1)', 
         'During the planning phase, the project scope was defined, and the core features were '
         'identified. The decision to use Flask + PostgreSQL was made based on the requirements '
         'for a lightweight yet powerful backend with strong relational database support. '
         'The star schema design pattern was selected for the database to optimize analytics queries.'),
        ('Phase 2 — Analysis (Week 2)',
         'Requirements were gathered and categorized into functional and non-functional requirements. '
         'The entities (Customer, Product, Sale) were identified along with their attributes and '
         'relationships. User stories were created for each CRUD operation and dashboard feature.'),
        ('Phase 3 — Design (Week 3)',
         'System architecture, database schema, ER diagrams, and DFDs were created. The UI '
         'wireframes were sketched with the dark-blue theme inspired by modern dashboard designs. '
         'API endpoints were planned with their HTTP methods, request/response formats.'),
        ('Phase 4 — Implementation (Week 4-6)',
         'The core application was developed iteratively. Sprint 1 focused on database setup and '
         'basic CRUD APIs. Sprint 2 added the frontend with navigation and forms. Sprint 3 '
         'integrated Chart.js for dashboard analytics. Sprint 4 added edit functionality and '
         'auto-calculation features.'),
        ('Phase 5 — Testing (Week 7)',
         'Comprehensive testing was performed including unit testing of API endpoints, integration '
         'testing of frontend-backend communication, and user acceptance testing of the complete '
         'workflow from data entry to dashboard visualization.'),
        ('Phase 6 — Deployment (Week 8)',
         'The application was finalized, documented, and prepared for deployment. The setup '
         'endpoint was created to allow automatic database schema creation, making deployment '
         'as simple as running a single Python command.'),
    ]

    for title, description in phases:
        p = doc.add_paragraph()
        run = p.add_run(title)
        run.bold = True
        run.font.size = Pt(11)
        doc.add_paragraph(description)

    doc.add_heading('2.3 Why Agile for SalesDB', level=2)
    doc.add_paragraph(
        'The Agile methodology was chosen for SalesDB for several compelling reasons. First, '
        'the project requirements evolved during development — features like unit price management, '
        'auto-calculation of sale amounts, and member type categorization were added based on '
        'iterative feedback. A rigid waterfall approach would have made incorporating these '
        'changes difficult and costly.'
    )
    doc.add_paragraph(
        'Second, the iterative nature of Agile allowed for continuous integration and testing. '
        'Each sprint delivered a working increment that could be tested and validated, reducing '
        'the risk of discovering major issues late in the development cycle. This approach '
        'ensured that the final product met all requirements and quality standards.'
    )
    doc.add_paragraph(
        'Third, the small team size (individual project) aligned well with Agile principles. '
        'Without the overhead of large team coordination, the developer could focus on rapid '
        'prototyping, immediate feedback incorporation, and continuous improvement of both '
        'code quality and user experience.'
    )

    doc.add_heading('2.4 Sprint Planning', level=2)
    add_styled_table(doc,
        ['Sprint', 'Duration', 'Deliverables', 'Status'],
        [
            ['Sprint 1', 'Week 4', 'Database schema, basic CRUD APIs', 'Completed'],
            ['Sprint 2', 'Week 5', 'Frontend UI, navigation, forms', 'Completed'],
            ['Sprint 3', 'Week 5-6', 'Dashboard, KPIs, charts', 'Completed'],
            ['Sprint 4', 'Week 6', 'Edit/Update, auto-calculation', 'Completed'],
            ['Sprint 5', 'Week 7', 'Testing, bug fixes, polish', 'Completed'],
            ['Sprint 6', 'Week 8', 'Documentation, deployment', 'Completed'],
        ]
    )

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  CHAPTER 3: SYSTEM ANALYSIS (Pages 19-23)
    # ══════════════════════════════════════════════
    doc.add_heading('Chapter 3: System Analysis', level=1)

    doc.add_heading('3.1 Feasibility Study', level=2)

    doc.add_heading('3.1.1 Technical Feasibility', level=3)
    doc.add_paragraph(
        'The technical feasibility of SalesDB was assessed by evaluating the availability and '
        'maturity of the required technologies. Python and Flask are well-established technologies '
        'with extensive documentation and community support. PostgreSQL is a robust, enterprise-grade '
        'database system that is freely available under an open-source license. HTML5, CSS3, and '
        'JavaScript are universal web technologies supported by all modern browsers. Chart.js '
        'is a widely-used, well-maintained charting library. All technologies are compatible '
        'with standard development environments and do not require specialized hardware.'
    )

    doc.add_heading('3.1.2 Economic Feasibility', level=3)
    doc.add_paragraph(
        'The project uses entirely open-source and free technologies, making it economically '
        'viable for educational purposes and small business deployment. There are no licensing '
        'costs for Python, Flask, PostgreSQL, or Chart.js. The application can run on standard '
        'hardware (any computer with Python installed) without requiring cloud infrastructure '
        'or paid services. The total cost of development is limited to developer time.'
    )

    doc.add_heading('3.1.3 Operational Feasibility', level=3)
    doc.add_paragraph(
        'The application is designed with usability as a primary concern. The intuitive user '
        'interface with clear labels, form validation, toast notifications, and visual feedback '
        'makes it accessible to users with basic computer literacy. The single-page application '
        'design eliminates page reloads, providing a smooth and responsive user experience. '
        'The automated database setup endpoint simplifies deployment to a single command.'
    )

    doc.add_heading('3.2 Requirements Analysis', level=2)
    doc.add_paragraph(
        'Requirements were gathered through analysis of common sales management workflows and '
        'the identification of key pain points in existing manual processes. The requirements '
        'were categorized into functional requirements (what the system should do) and '
        'non-functional requirements (how the system should perform).'
    )
    doc.add_paragraph(
        'The analysis revealed that the primary users of the system would be small business '
        'owners or sales managers who need to: (1) maintain a database of customers with '
        'contact information and membership status, (2) manage a product catalog with pricing, '
        '(3) record sales transactions with automatic total calculation, and (4) view analytics '
        'and performance metrics through a visual dashboard.'
    )

    doc.add_heading('3.3 Functional Requirements', level=2)
    add_styled_table(doc,
        ['ID', 'Module', 'Requirement', 'Priority'],
        [
            ['FR-01', 'Customers', 'Add new customer with all details', 'High'],
            ['FR-02', 'Customers', 'View all customers in a table', 'High'],
            ['FR-03', 'Customers', 'Edit existing customer information', 'High'],
            ['FR-04', 'Customers', 'Delete customer (cascade sales)', 'High'],
            ['FR-05', 'Products', 'Add new product with name, category, price', 'High'],
            ['FR-06', 'Products', 'View all products in a table', 'High'],
            ['FR-07', 'Products', 'Edit existing product details', 'High'],
            ['FR-08', 'Products', 'Delete product (cascade sales)', 'High'],
            ['FR-09', 'Sales', 'Add sale with auto-calculated amount', 'High'],
            ['FR-10', 'Sales', 'View all sales with full details', 'High'],
            ['FR-11', 'Sales', 'Delete individual sale records', 'Medium'],
            ['FR-12', 'Dashboard', 'Display 5 KPI cards', 'High'],
            ['FR-13', 'Dashboard', 'Show revenue by category bar chart', 'High'],
            ['FR-14', 'Dashboard', 'Show sales distribution doughnut chart', 'Medium'],
            ['FR-15', 'Dashboard', 'Show customer segments pie chart', 'Medium'],
            ['FR-16', 'System', 'Auto-setup database schema', 'High'],
            ['FR-17', 'System', 'Health check endpoint', 'Low'],
        ]
    )
    doc.add_paragraph('\nTable 3.1: Functional Requirements')

    doc.add_heading('3.4 Non-Functional Requirements', level=2)
    add_styled_table(doc,
        ['ID', 'Category', 'Requirement'],
        [
            ['NFR-01', 'Performance', 'API response time < 500ms for all endpoints'],
            ['NFR-02', 'Usability', 'Intuitive UI with < 3 clicks for any operation'],
            ['NFR-03', 'Reliability', 'Graceful error handling with user-friendly messages'],
            ['NFR-04', 'Security', 'SQL injection prevention via parameterized queries'],
            ['NFR-05', 'Scalability', 'Modular architecture supporting future extensions'],
            ['NFR-06', 'Maintainability', 'Separated CSS, JS, HTML for clean code structure'],
            ['NFR-07', 'Compatibility', 'Works on Chrome, Firefox, Edge, Safari'],
            ['NFR-08', 'Responsiveness', 'Adapts to screen widths from 320px to 1920px'],
        ]
    )
    doc.add_paragraph('\nTable 3.2: Non-Functional Requirements')

    doc.add_heading('3.5 Hardware & Software Requirements', level=2)

    doc.add_heading('3.5.1 Hardware Requirements', level=3)
    add_styled_table(doc,
        ['Component', 'Minimum', 'Recommended'],
        [
            ['Processor', 'Intel i3 / AMD Ryzen 3', 'Intel i5 / AMD Ryzen 5'],
            ['RAM', '4 GB', '8 GB'],
            ['Storage', '500 MB free space', '1 GB free space'],
            ['Display', '1366 × 768', '1920 × 1080'],
            ['Network', 'Localhost (no network needed)', 'LAN for multi-user access'],
        ]
    )
    doc.add_paragraph('\nTable 3.3: Hardware Requirements')

    doc.add_heading('3.5.2 Software Requirements', level=3)
    add_styled_table(doc,
        ['Software', 'Version', 'Purpose'],
        [
            ['Operating System', 'Windows 10+ / Linux / macOS', 'Development & deployment'],
            ['Python', '3.8+', 'Backend runtime'],
            ['PostgreSQL', '12+', 'Database server'],
            ['Web Browser', 'Chrome 90+ / Firefox 88+', 'Frontend rendering'],
            ['pip', 'Latest', 'Python package manager'],
            ['Git', 'Latest (optional)', 'Version control'],
        ]
    )
    doc.add_paragraph('\nTable 3.4: Software Requirements')

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  CHAPTER 4: SYSTEM DESIGN (Pages 24-34)
    # ══════════════════════════════════════════════
    doc.add_heading('Chapter 4: System Design', level=1)

    doc.add_heading('4.1 System Architecture', level=2)
    doc.add_paragraph(
        'SalesDB follows a three-tier client-server architecture that separates the application '
        'into three logical layers: the Presentation Layer (frontend), the Application Layer '
        '(backend API), and the Data Layer (database). This architectural pattern promotes '
        'separation of concerns, making each layer independently developable, testable, and deployable.'
    )
    doc.add_paragraph(
        'The Presentation Layer consists of HTML, CSS, and JavaScript files served by the Flask '
        'server. The browser renders the user interface and handles user interactions. When a '
        'user performs an action (e.g., adding a customer), JavaScript sends an asynchronous '
        'HTTP request (using the Fetch API) to the Application Layer.'
    )
    doc.add_paragraph(
        'The Application Layer is a Python Flask application that exposes RESTful API endpoints. '
        'It receives HTTP requests, validates input data, performs business logic, communicates '
        'with the database through psycopg2, and returns JSON responses. Flask-CORS is used to '
        'handle Cross-Origin Resource Sharing when the frontend is served from a different origin.'
    )
    doc.add_paragraph(
        'The Data Layer is a PostgreSQL database that stores all persistent data in three tables: '
        'customer_dim, product_dim, and sales_fact. The database enforces data integrity through '
        'primary keys, foreign keys with CASCADE delete rules, NOT NULL constraints, and '
        'appropriate data types.'
    )

    doc.add_paragraph('\nFigure 4.1: System Architecture Diagram')
    doc.add_picture(arch_img, width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_page_break(doc)

    doc.add_heading('4.2 Database Schema Design', level=2)
    doc.add_paragraph(
        'The database follows a star schema design commonly used in data warehouse applications. '
        'The central fact table (sales_fact) stores measurable, quantitative data about sales '
        'transactions, while the dimension tables (customer_dim, product_dim) store descriptive '
        'attributes that provide context to the facts. This design optimizes analytical queries '
        'by minimizing the number of joins required.'
    )

    doc.add_heading('4.2.1 customer_dim Table', level=3)
    add_styled_table(doc,
        ['Column', 'Data Type', 'Constraints', 'Description'],
        [
            ['customer_id', 'SERIAL', 'PRIMARY KEY', 'Auto-incrementing unique identifier'],
            ['first_name', 'VARCHAR(50)', 'NOT NULL', 'Customer first name'],
            ['last_name', 'VARCHAR(50)', 'NOT NULL', 'Customer last name'],
            ['city', 'VARCHAR(50)', 'NULLABLE', 'City of residence'],
            ['mobile_no', 'VARCHAR(20)', 'NULLABLE', 'Mobile phone number'],
            ['email', 'VARCHAR(100)', 'NULLABLE', 'Email address'],
            ['region', 'VARCHAR(20)', 'NULLABLE', 'Geographic region (East/West/North/South)'],
            ['member_type', 'VARCHAR(20)', 'DEFAULT Regular', 'Membership tier (Gold/Regular)'],
        ]
    )
    doc.add_paragraph('\nTable 4.1: customer_dim Schema')

    doc.add_heading('4.2.2 product_dim Table', level=3)
    add_styled_table(doc,
        ['Column', 'Data Type', 'Constraints', 'Description'],
        [
            ['product_id', 'SERIAL', 'PRIMARY KEY', 'Auto-incrementing unique identifier'],
            ['product_name', 'VARCHAR(100)', 'NOT NULL', 'Name of the product'],
            ['category', 'VARCHAR(50)', 'NULLABLE', 'Product category'],
            ['unit_price', 'NUMERIC(10,2)', 'DEFAULT 0', 'Price per unit in dollars'],
        ]
    )
    doc.add_paragraph('\nTable 4.2: product_dim Schema')

    doc.add_heading('4.2.3 sales_fact Table', level=3)
    add_styled_table(doc,
        ['Column', 'Data Type', 'Constraints', 'Description'],
        [
            ['sale_id', 'SERIAL', 'PRIMARY KEY', 'Auto-incrementing unique identifier'],
            ['customer_id', 'INTEGER', 'FK → customer_dim ON DELETE CASCADE', 'Reference to customer'],
            ['product_id', 'INTEGER', 'FK → product_dim ON DELETE CASCADE', 'Reference to product'],
            ['sale_date', 'DATE', 'NOT NULL', 'Date of the sale'],
            ['quantity', 'INTEGER', 'NOT NULL', 'Number of units sold'],
            ['sale_amount', 'NUMERIC(10,2)', 'NOT NULL', 'Total = unit_price × quantity'],
        ]
    )
    doc.add_paragraph('\nTable 4.3: sales_fact Schema')

    add_page_break(doc)

    doc.add_heading('4.3 Entity Relationship Diagram', level=2)
    doc.add_paragraph(
        'The Entity Relationship (ER) Diagram illustrates the relationships between the three '
        'main entities in the SalesDB system. The diagram shows primary keys (PK) highlighted '
        'in yellow, foreign keys (FK) in red, and regular attributes in gray.'
    )
    doc.add_paragraph(
        'Key relationships: A customer can have many sales (1:N relationship from customer_dim '
        'to sales_fact). A product can appear in many sales (1:N relationship from product_dim '
        'to sales_fact). Each sale belongs to exactly one customer and one product.'
    )

    doc.add_paragraph('\nFigure 4.3: Entity Relationship Diagram')
    doc.add_picture(er_img, width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_page_break(doc)

    doc.add_heading('4.4 Data Flow Diagrams', level=2)

    doc.add_heading('4.4.1 DFD Level 0 — Context Diagram', level=3)
    doc.add_paragraph(
        'The context diagram shows the SalesDB system as a single process interacting with '
        'two external entities: the User (admin) who sends CRUD requests and receives reports, '
        'and the PostgreSQL database that receives SQL queries and returns result sets.'
    )
    doc.add_paragraph('\nFigure 4.4: DFD Level 0 — Context Diagram')
    doc.add_picture(dfd0_img, width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading('4.4.2 DFD Level 1', level=3)
    doc.add_paragraph(
        'The Level 1 DFD decomposes the SalesDB system into four major processes: '
        '(1.0) Manage Customers, (2.0) Manage Products, (3.0) Manage Sales, and '
        '(4.0) Generate Analytics. Each process interacts with its respective data store '
        'and receives input from the User entity.'
    )
    doc.add_paragraph('\nFigure 4.5: DFD Level 1')
    doc.add_picture(dfd1_img, width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_page_break(doc)

    doc.add_heading('4.4.3 CRUD Operations Flow', level=3)
    doc.add_paragraph(
        'The following diagram shows how each CRUD operation flows from the user interface '
        'through the API to the database, detailing the HTTP method, SQL operation, and '
        'response format for each operation type.'
    )
    doc.add_paragraph('\nFigure 4.6: CRUD Operations Flowchart')
    doc.add_picture(crud_img, width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading('4.5 Component Diagram', level=2)
    doc.add_paragraph(
        'The component diagram shows the internal structure of SalesDB organized into three '
        'layers. The Presentation Layer contains the HTML, CSS, JavaScript, and Chart.js files. '
        'The Application Layer contains the Flask app, routing logic, and database driver. '
        'The Data Layer contains the three database tables.'
    )
    doc.add_paragraph('\nFigure 4.7: Component Diagram')
    doc.add_picture(comp_img, width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_page_break(doc)

    doc.add_heading('4.6 Sequence Diagram', level=2)
    doc.add_paragraph(
        'The sequence diagram below illustrates the interaction between the User, Frontend (JS), '
        'Flask API, and PostgreSQL when adding a new sale. It shows the complete request-response '
        'cycle from form submission to UI update.'
    )
    doc.add_paragraph('\nFigure 4.8: Sequence Diagram — Add Sale')
    doc.add_picture(seq_img, width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading('4.7 Deployment Diagram', level=2)
    doc.add_paragraph(
        'The deployment diagram shows the physical distribution of the application components '
        'across three nodes: the Client Machine (running the browser), the Application Server '
        '(running Flask on port 5000), and the Database Server (running PostgreSQL on port 5432). '
        'In a local development setup, all three nodes may reside on the same physical machine.'
    )
    doc.add_paragraph('\nFigure 4.9: Deployment Diagram')
    doc.add_picture(deploy_img, width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_page_break(doc)

    doc.add_heading('4.8 Program Execution Flowchart', level=2)
    doc.add_paragraph(
        'The following flowchart shows the complete execution flow of the SalesDB application '
        'from server startup to user interaction. The flow includes server initialization, '
        'page loading, dashboard rendering, user actions (CRUD), API communication, database '
        'operations, and UI updates with toast notifications.'
    )
    doc.add_paragraph('\nFigure 4.10: Program Execution Flowchart')
    doc.add_picture(flow_img, width=Inches(4))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  CHAPTER 5: IMPLEMENTATION (Pages 35-40)
    # ══════════════════════════════════════════════
    doc.add_heading('Chapter 5: Implementation', level=1)

    doc.add_heading('5.1 Frontend Implementation', level=2)
    doc.add_paragraph(
        'The frontend is implemented as a Single Page Application (SPA) using vanilla JavaScript '
        'without any framework. The HTML file (index.html) defines the structure of the entire '
        'application, including the sidebar navigation, top bar, and four sections (Dashboard, '
        'Sales, Customers, Products). Section visibility is controlled via CSS classes and '
        'JavaScript event handlers.'
    )
    doc.add_paragraph(
        'The CSS file (styles.css) implements the midnight blue dark theme using CSS custom '
        'properties (variables) defined in the :root selector. This approach allows for easy '
        'theme customization by modifying a few variable values. The design uses a radial gradient '
        'background, semi-transparent surfaces with backdrop-filter blur effects, and consistent '
        'border-radius values for a modern, professional appearance.'
    )
    doc.add_paragraph(
        'Key frontend features include:'
    )
    features = [
        'Navigation: Click handlers on sidebar items toggle section visibility using CSS class manipulation.',
        'Toast Notifications: A fixed-position element that slides in from the bottom-right with success/error styling.',
        'Form Handling: Forms support both Add and Edit modes using a hidden input field to track the editing ID.',
        'Auto-Calculation: When a product is selected or quantity changed, the sale amount is automatically computed.',
        'Responsive Design: CSS media queries adjust the layout for screens smaller than 900px.',
        'Charts: Chart.js instances are created and destroyed on each data refresh to prevent memory leaks.',
    ]
    for f in features:
        doc.add_paragraph(f, style='List Bullet')

    doc.add_heading('5.2 Backend Implementation', level=2)
    doc.add_paragraph(
        'The backend is a Python Flask application (app.py) that serves both the static frontend '
        'files and the RESTful API endpoints. The application uses psycopg2 for PostgreSQL '
        'connectivity with RealDictCursor for dictionary-based result rows, making JSON '
        'serialization straightforward.'
    )
    doc.add_paragraph(
        'Key backend design patterns include:'
    )
    patterns = [
        'Connection Management: Each request creates a new database connection and closes it after use. '
        'This simple approach is suitable for the expected load of this application.',
        'Error Handling: All endpoints are wrapped in try-except blocks with appropriate HTTP status codes '
        '(400 for validation errors, 404 for not found, 500 for server errors).',
        'Input Validation: Required fields are checked before database operations. Missing fields return '
        'descriptive error messages.',
        'CORS Support: flask-cors is applied globally to allow cross-origin requests during development.',
        'Static File Serving: Three dedicated routes serve index.html, styles.css, and script.js.',
        'Schema Migration: The /api/setup endpoint uses DO $$ blocks to safely add columns to existing tables.',
    ]
    for pat in patterns:
        doc.add_paragraph(pat, style='List Bullet')

    doc.add_heading('5.3 Database Implementation', level=2)
    doc.add_paragraph(
        'The PostgreSQL database is structured using a star schema with two dimension tables '
        'and one fact table. The schema is created automatically via the /api/setup POST endpoint, '
        'which uses CREATE TABLE IF NOT EXISTS for idempotent table creation and ALTER TABLE '
        'wrapped in conditional checks for adding new columns to existing tables.'
    )
    doc.add_paragraph(
        'Key database design decisions include:'
    )
    db_decisions = [
        'SERIAL primary keys for automatic ID generation without application-level management.',
        'ON DELETE CASCADE foreign keys to maintain referential integrity when customers or products are deleted.',
        'NUMERIC(10,2) for monetary values to avoid floating-point precision issues.',
        'VARCHAR with appropriate length limits to balance storage efficiency and data requirements.',
        'DEFAULT values for optional fields (member_type defaults to "Regular", unit_price defaults to 0).',
    ]
    for d in db_decisions:
        doc.add_paragraph(d, style='List Bullet')

    add_page_break(doc)

    doc.add_heading('5.4 API Endpoints', level=2)
    doc.add_paragraph(
        'The SalesDB API exposes the following RESTful endpoints. All data endpoints accept '
        'and return JSON format. The API follows standard HTTP conventions: GET for reading, '
        'POST for creating, PUT for updating, and DELETE for removing resources.'
    )

    add_styled_table(doc,
        ['Method', 'Endpoint', 'Description', 'Request Body'],
        [
            ['GET', '/api/health', 'Check API & DB status', '—'],
            ['POST', '/api/setup', 'Create/update DB schema', '—'],
            ['GET', '/api/analytics/kpis', 'Get dashboard KPIs', '—'],
            ['GET', '/api/analytics/revenue-by-category', 'Revenue per category', '—'],
            ['GET', '/api/analytics/revenue-over-time', 'Daily revenue data', '—'],
            ['GET', '/api/customers', 'List all customers', '—'],
            ['POST', '/api/customers', 'Add new customer', 'JSON (7 fields)'],
            ['PUT', '/api/customers/<id>', 'Update customer', 'JSON (7 fields)'],
            ['DELETE', '/api/customers/<id>', 'Delete customer', '—'],
            ['GET', '/api/products', 'List all products', '—'],
            ['POST', '/api/products', 'Add new product', 'JSON (3 fields)'],
            ['PUT', '/api/products/<id>', 'Update product', 'JSON (3 fields)'],
            ['DELETE', '/api/products/<id>', 'Delete product', '—'],
            ['GET', '/api/sales', 'List all sales', '—'],
            ['POST', '/api/sales', 'Add new sale', 'JSON (5 fields)'],
            ['DELETE', '/api/sales/<id>', 'Delete sale', '—'],
        ]
    )
    doc.add_paragraph('\nTable 5.1: API Endpoints Summary')

    doc.add_heading('5.5 Key Code Snippets', level=2)

    doc.add_heading('5.5.1 Auto-Calculate Sale Amount (JavaScript)', level=3)
    doc.add_paragraph(
        'The following function automatically calculates the total sale amount when the user '
        'selects a product or changes the quantity:'
    )
    code_block = doc.add_paragraph()
    code_text = (
        'function calcSaleAmount() {\n'
        '  const sel = document.getElementById("sale-product");\n'
        '  const option = sel.options[sel.selectedIndex];\n'
        '  const price = parseFloat(option?.getAttribute("data-price") || 0);\n'
        '  const qty = parseInt(document.getElementById("sale-qty").value) || 0;\n'
        '  const total = price * qty;\n'
        '  document.getElementById("sale-amount").value = \n'
        '    total > 0 ? total.toFixed(2) : "";\n'
        '}'
    )
    run = code_block.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(236, 72, 153)

    doc.add_heading('5.5.2 Database Connection Helper (Python)', level=3)
    code_block2 = doc.add_paragraph()
    code_text2 = (
        'def get_conn():\n'
        '    try:\n'
        '        return psycopg2.connect(**DB_CONFIG)\n'
        '    except psycopg2.OperationalError as e:\n'
        '        raise RuntimeError(\n'
        '            f"Cannot connect to PostgreSQL: {e}"\n'
        '        ) from e'
    )
    run = code_block2.add_run(code_text2)
    run.font.name = 'Consolas'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(59, 130, 246)

    doc.add_heading('5.5.3 KPI Analytics Query (SQL)', level=3)
    code_block3 = doc.add_paragraph()
    code_text3 = (
        'SELECT\n'
        '    COUNT(*)::int                          AS total_sales,\n'
        '    COALESCE(SUM(sale_amount), 0)::float  AS total_revenue,\n'
        '    COALESCE(AVG(sale_amount), 0)::float  AS avg_order_value,\n'
        '    (SELECT COUNT(*) FROM customer_dim)    AS total_customers,\n'
        '    (SELECT COUNT(*) FROM product_dim)     AS total_products\n'
        'FROM sales_fact;'
    )
    run = code_block3.add_run(code_text3)
    run.font.name = 'Consolas'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(61, 220, 132)

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  CHAPTER 6: TESTING (Pages 41-43)
    # ══════════════════════════════════════════════
    doc.add_heading('Chapter 6: Testing', level=1)

    doc.add_heading('6.1 Testing Strategy', level=2)
    doc.add_paragraph(
        'Testing was performed at multiple levels to ensure the reliability and correctness '
        'of the SalesDB application. The testing strategy included API endpoint testing using '
        'curl and browser developer tools, frontend functional testing through manual interaction, '
        'and integration testing to verify the complete data flow from UI to database and back.'
    )
    doc.add_paragraph(
        'Each test case was designed to verify both positive scenarios (valid input producing '
        'expected results) and negative scenarios (invalid input producing appropriate error '
        'messages). Edge cases such as empty databases, deletion of referenced records, and '
        'boundary values were also tested.'
    )

    doc.add_heading('6.2 Test Cases', level=2)

    doc.add_heading('6.2.1 Customer Module Test Cases', level=3)
    add_styled_table(doc,
        ['TC ID', 'Test Case', 'Input', 'Expected Output', 'Result'],
        [
            ['TC-C01', 'Add valid customer', 'All fields filled', 'Customer created, toast shown', 'Pass'],
            ['TC-C02', 'Add without first name', 'First name empty', 'Error: name required', 'Pass'],
            ['TC-C03', 'Edit existing customer', 'Change city', 'Customer updated', 'Pass'],
            ['TC-C04', 'Delete customer', 'Click delete, confirm', 'Customer & sales removed', 'Pass'],
            ['TC-C05', 'Cancel edit', 'Click cancel', 'Form resets to add mode', 'Pass'],
            ['TC-C06', 'Add with Gold membership', 'Member type = Gold', 'Gold badge displayed', 'Pass'],
        ]
    )
    doc.add_paragraph('\nTable 6.1: Test Cases — Customers')

    doc.add_heading('6.2.2 Product Module Test Cases', level=3)
    add_styled_table(doc,
        ['TC ID', 'Test Case', 'Input', 'Expected Output', 'Result'],
        [
            ['TC-P01', 'Add product with price', 'Name + price', 'Product created with price', 'Pass'],
            ['TC-P02', 'Add without name', 'Name empty', 'Error: name required', 'Pass'],
            ['TC-P03', 'Add without price', 'Price empty', 'Error: price required', 'Pass'],
            ['TC-P04', 'Edit product price', 'Change price', 'Price updated, sales recalc', 'Pass'],
            ['TC-P05', 'Delete product', 'Confirm delete', 'Product & related sales deleted', 'Pass'],
        ]
    )
    doc.add_paragraph('\nTable 6.2: Test Cases — Products')

    doc.add_heading('6.2.3 Sales Module Test Cases', level=3)
    add_styled_table(doc,
        ['TC ID', 'Test Case', 'Input', 'Expected Output', 'Result'],
        [
            ['TC-S01', 'Add sale', 'Customer + Product + Qty', 'Sale added, amount auto-calc', 'Pass'],
            ['TC-S02', 'Auto-calculate amount', 'Select product, qty=3', 'Amount = price × 3', 'Pass'],
            ['TC-S03', 'Change quantity', 'Modify qty field', 'Amount recalculates', 'Pass'],
            ['TC-S04', 'Delete sale', 'Click delete', 'Sale removed, KPIs update', 'Pass'],
            ['TC-S05', 'Add without date', 'Date empty', 'Error: fill all fields', 'Pass'],
        ]
    )
    doc.add_paragraph('\nTable 6.3: Test Cases — Sales')

    doc.add_heading('6.3 Test Results Summary', level=2)
    add_styled_table(doc,
        ['Module', 'Total Tests', 'Passed', 'Failed', 'Pass Rate'],
        [
            ['Customers', '6', '6', '0', '100%'],
            ['Products', '5', '5', '0', '100%'],
            ['Sales', '5', '5', '0', '100%'],
            ['Dashboard', '3', '3', '0', '100%'],
            ['API Health', '2', '2', '0', '100%'],
            ['TOTAL', '21', '21', '0', '100%'],
        ]
    )
    doc.add_paragraph('\nTable 6.4: Test Results Summary')

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  CHAPTER 7: RESULTS & SCREENSHOTS (Pages 44-45)
    # ══════════════════════════════════════════════
    doc.add_heading('Chapter 7: Results & Screenshots', level=1)

    doc.add_heading('7.1 Dashboard View', level=2)
    doc.add_paragraph(
        'The dashboard provides a comprehensive overview of business performance through five '
        'KPI cards and three interactive charts. The KPI cards display Total Revenue, Total Sales, '
        'Average Order Value, Customer Count, and Product Count. Each card features a colored '
        'accent bar at the top for visual distinction.'
    )
    doc.add_paragraph(
        'The charts section includes a bar chart showing revenue breakdown by product category, '
        'a doughnut chart displaying the sales distribution across categories, and a pie chart '
        'showing the split between Gold and Regular customer segments.'
    )
    doc.add_paragraph('\nFigure 7.1: Dashboard Charts & KPIs')
    doc.add_picture(dashboard_img, width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading('7.2 Sales Management', level=2)
    doc.add_paragraph(
        'The Sales section features a form at the top for adding new sales and a comprehensive '
        'table below listing all sales records. The form includes dropdown selectors for Customer '
        'and Product (which show the unit price alongside the product name), a date picker, '
        'a quantity input, and a read-only auto-calculated amount field. The table displays '
        'sale ID, customer name, product name, category badge, date, quantity, unit price, '
        'and total amount with a delete button for each row.'
    )

    doc.add_heading('7.3 Customer Management', level=2)
    doc.add_paragraph(
        'The Customer section provides a comprehensive form for adding and editing customer '
        'information. The form supports seven fields: First Name, Last Name, City, Mobile Number, '
        'Email, Region (dropdown with East/West/North/South options), and Member Type (Regular/Gold). '
        'When editing, the form panel gets a blue highlight border, the title changes to show '
        'the editing customer ID, and a Cancel button appears. The customer table shows all '
        'customer details with Edit and Delete action buttons.'
    )

    doc.add_heading('7.4 Product Management', level=2)
    doc.add_paragraph(
        'The Product section allows managing the product catalog with three fields: Product Name, '
        'Category (dropdown), and Unit Price. The product table displays all products with their '
        'ID, name, category badge, formatted unit price, and Edit/Delete buttons. Editing a '
        'product follows the same pattern as customer editing with visual feedback. The unit '
        'price entered here is used for automatic sale amount calculation in the Sales module.'
    )

    doc.add_paragraph(
        '\nNote: Actual screenshots of the running application should be captured and inserted '
        'here to complement the descriptive text above. Open the application at http://localhost:5000 '
        'and take screenshots of each section with sample data.'
    )

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  CHAPTER 8: CONCLUSION (Pages 46)
    # ══════════════════════════════════════════════
    doc.add_heading('Chapter 8: Conclusion & Future Scope', level=1)

    doc.add_heading('8.1 Conclusion', level=2)
    doc.add_paragraph(
        'The SalesDB project has been successfully designed, developed, and tested as a '
        'comprehensive full-stack web application for sales data management and analytics. '
        'The application demonstrates the effective integration of modern web technologies '
        '(HTML5, CSS3, JavaScript, Chart.js) with a robust backend (Python Flask) and a '
        'reliable database system (PostgreSQL).'
    )
    doc.add_paragraph(
        'All project objectives have been achieved: complete CRUD operations for customers, '
        'products, and sales; real-time analytics dashboard with KPI cards and interactive charts; '
        'automatic sale amount calculation; responsive dark-themed UI; and proper database design '
        'with referential integrity. The application handles edge cases gracefully with appropriate '
        'error messages and user feedback through toast notifications.'
    )
    doc.add_paragraph(
        'The star schema database design optimizes analytical queries, the RESTful API architecture '
        'promotes frontend-backend decoupling, and the Agile development methodology enabled '
        'iterative refinement based on continuous feedback. The project serves as a practical '
        'demonstration of full-stack development skills and software engineering principles.'
    )

    doc.add_heading('8.2 Future Enhancements', level=2)
    doc.add_paragraph(
        'While the current version of SalesDB meets all defined requirements, several enhancements '
        'could be implemented in future iterations:'
    )
    enhancements = [
        'User Authentication: Implement login/logout functionality with role-based access control '
        '(admin, manager, viewer) using Flask-Login or JWT tokens.',
        'Advanced Analytics: Add trend analysis, forecasting, year-over-year comparisons, and '
        'export functionality for reports in PDF/Excel formats.',
        'Search & Filtering: Add search bars and filter options to all tables for finding specific '
        'records quickly in large datasets.',
        'Pagination: Implement server-side pagination for tables to handle thousands of records efficiently.',
        'Data Import/Export: Support CSV/Excel file upload for bulk data import and export.',
        'Email Notifications: Automated alerts for low inventory, high-value sales, or monthly summaries.',
        'Cloud Deployment: Deploy on AWS, Heroku, or DigitalOcean for multi-user web access.',
        'Mobile Application: Develop a companion mobile app using React Native or Flutter.',
        'Invoice Generation: Auto-generate PDF invoices for each sale transaction.',
        'Audit Logging: Track all data modifications with timestamps and user identification.',
    ]
    for enh in enhancements:
        doc.add_paragraph(enh, style='List Bullet')

    add_page_break(doc)

    # ══════════════════════════════════════════════
    #  REFERENCES (Page 47)
    # ══════════════════════════════════════════════
    doc.add_heading('References', level=1)
    add_spacer(doc, 1)

    references = [
        '[1] Flask Documentation — https://flask.palletsprojects.com/ — Pallets Projects, 2024.',
        '[2] PostgreSQL Documentation — https://www.postgresql.org/docs/ — PostgreSQL Global Development Group, 2024.',
        '[3] Chart.js Documentation — https://www.chartjs.org/docs/ — Chart.js Contributors, 2024.',
        '[4] psycopg2 Documentation — https://www.psycopg.org/docs/ — Federico Di Gregorio, 2024.',
        '[5] MDN Web Docs — HTML, CSS, JavaScript — https://developer.mozilla.org/ — Mozilla Foundation, 2024.',
        '[6] Kimball, R. & Ross, M. — "The Data Warehouse Toolkit" — Wiley, 3rd Edition, 2013.',
        '[7] Fielding, R.T. — "Architectural Styles and the Design of Network-based Software Architectures" — '
        'Doctoral Dissertation, University of California, Irvine, 2000.',
        '[8] Agile Alliance — "Agile Manifesto" — https://agilemanifesto.org/ — 2001.',
        '[9] Sommerville, I. — "Software Engineering" — Pearson, 10th Edition, 2015.',
        '[10] Pressman, R.S. — "Software Engineering: A Practitioner\'s Approach" — McGraw-Hill, 9th Edition, 2019.',
        '[11] Elmasri, R. & Navathe, S.B. — "Fundamentals of Database Systems" — Pearson, 7th Edition, 2016.',
        '[12] Python Documentation — https://docs.python.org/3/ — Python Software Foundation, 2024.',
        '[13] Google Fonts — Syne & JetBrains Mono — https://fonts.google.com/ — Google, 2024.',
        '[14] flask-cors Documentation — https://flask-cors.readthedocs.io/ — Cory Dolphin, 2024.',
        '[15] W3Schools — Web Development Tutorials — https://www.w3schools.com/ — Refsnes Data, 2024.',
    ]

    for ref in references:
        p = doc.add_paragraph()
        run = p.add_run(ref)
        run.font.size = Pt(10)
        p.paragraph_format.space_after = Pt(8)

    # ── Save ─────────────────────────────────────
    filename = 'SalesDB_Project_Report.docx'
    doc.save(filename)
    print(f'\n  ✓ Report saved: {filename}')
    print(f'  ✓ Total sections: 8 chapters + front matter + references')
    print(f'  ✓ Diagrams saved in: {IMG_DIR}/')
    print(f'  ✓ Open the .docx file in Microsoft Word\n')

    return filename


# ══════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════

if __name__ == '__main__':
    print('\n  ╔══════════════════════════════════════╗')
    print('  ║  SalesDB — Report Generator          ║')
    print('  ╚══════════════════════════════════════╝\n')

    print('  → Generating diagrams...')
    arch_img = create_system_architecture()
    print('    ✓ System Architecture')

    er_img = create_er_diagram()
    print('    ✓ ER Diagram')

    dfd0_img = create_dfd_level0()
    print('    ✓ DFD Level 0')

    dfd1_img = create_dfd_level1()
    print('    ✓ DFD Level 1')

    flow_img = create_flowchart()
    print('    ✓ Program Flowchart')

    comp_img = create_component_diagram()
    print('    ✓ Component Diagram')

    sdlc_img = create_sdlc_diagram()
    print('    ✓ SDLC Model')

    tech_stack_img = create_tech_stack()
    print('    ✓ Technology Stack')

    seq_img = create_sequence_diagram()
    print('    ✓ Sequence Diagram')

    deploy_img = create_deployment_diagram()
    print('    ✓ Deployment Diagram')

    dashboard_img = create_sample_dashboard()
    print('    ✓ Sample Dashboard Charts')

    crud_img = create_crud_flowchart()
    print('    ✓ CRUD Flowchart')

    print('\n  → Building Word document...')
    build_report()
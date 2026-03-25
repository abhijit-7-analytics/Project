"""
SalesDB — 18-Slide Presentation Generator (with Auth, Charts, Diagrams & Screenshots)
Run:  python generate_ppt.py
Output: SalesDB_Presentation.pptx + ppt_images/ folder
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
import os

IMG_DIR = "ppt_images"
os.makedirs(IMG_DIR, exist_ok=True)

# ── Colors ───────────────────────────────
BG_DARK  = RGBColor(15, 23, 42)
BG_CARD  = RGBColor(30, 41, 59)
PINK     = RGBColor(236, 72, 153)
BLUE     = RGBColor(59, 130, 246)
PURPLE   = RGBColor(168, 85, 247)
RED      = RGBColor(244, 63, 94)
GREEN    = RGBColor(61, 220, 132)
YELLOW   = RGBColor(251, 191, 36)
WHITE    = RGBColor(248, 250, 252)
MUTED    = RGBColor(148, 163, 184)
DARK_BDR = RGBColor(51, 65, 85)

MC_BG='#0f172a'; MC_CARD='#1e293b'; MC_BORDER='#334155'
MC_PINK='#ec4899'; MC_BLUE='#3b82f6'; MC_PURPLE='#a855f7'
MC_RED='#f43f5e'; MC_GREEN='#3ddc84'; MC_YELLOW='#fbbf24'
MC_WHITE='#f8fafc'; MC_MUTED='#94a3b8'


# ══════════════════════════════════════════
#  IMAGE GENERATORS
# ══════════════════════════════════════════

def gen_tech_stack():
    fig, ax = plt.subplots(figsize=(9,5))
    ax.set_xlim(0,9); ax.set_ylim(0,6); ax.axis('off')
    stack = [
        (0.5,4.5,8,0.9,'Frontend: HTML5 + CSS3 + JavaScript + Chart.js',MC_BLUE),
        (0.5,3.2,8,0.9,'Backend: Python 3 + Flask + flask-cors',MC_PINK),
        (0.5,1.9,8,0.9,'Security: Flask Sessions + login_required decorator',MC_YELLOW),
        (0.5,0.6,8,0.9,'Database: PostgreSQL 16 (Star Schema)',MC_GREEN),
    ]
    for x,y,w,h,label,color in stack:
        ax.add_patch(FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor='white', lw=2))
        tc = 'white' if color != MC_YELLOW else 'black'
        ax.text(x+w/2,y+h/2,label, ha='center', va='center',
                fontsize=11, fontweight='bold', color=tc)
    for i in range(3):
        y=4.5-i*1.3
        ax.annotate('', xy=(4.5,y), xytext=(4.5,y+0.4),
                    arrowprops=dict(arrowstyle='<->', color=MC_MUTED, lw=2.5))
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"tech_stack.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_architecture():
    fig, ax = plt.subplots(figsize=(10,6))
    ax.set_xlim(0,10); ax.set_ylim(0,7); ax.axis('off')
    boxes = [
        (0.3,5.2,2.5,1.2,MC_BLUE,'Browser\n(Client)','white'),
        (3.5,5.2,2.8,1.2,MC_PINK,'HTML / CSS / JS\n(Frontend)','white'),
        (3.5,3.2,2.8,1.2,MC_PURPLE,'Flask API\n(Backend)','white'),
        (3.5,1.2,2.8,1.2,MC_GREEN,'PostgreSQL\n(Database)','white'),
        (7.2,5.2,2.3,1.2,MC_YELLOW,'Chart.js\n(Charts)','black'),
        (7.2,3.2,2.3,1.2,MC_RED,'Auth / Session\n(Security)','white'),
    ]
    for x,y,w,h,color,label,tc in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0.12",
                     facecolor=color, edgecolor='white', lw=2.5))
        ax.text(x+w/2,y+h/2,label, ha='center', va='center',
                fontsize=10, fontweight='bold', color=tc)
    arrows=[(2.8,5.8,3.5,5.8),(6.3,5.8,7.2,5.8),(4.9,5.2,4.9,4.4),
            (4.9,3.2,4.9,2.4),(7.2,3.8,6.3,3.8)]
    for x1,y1,x2,y2 in arrows:
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle='->', color=MC_MUTED, lw=2.5))
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"architecture.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_er_diagram():
    fig, ax = plt.subplots(figsize=(12,7))
    ax.set_xlim(0,12); ax.set_ylim(0,8); ax.axis('off')
    entities = {
        'customer': {'x':0.5,'y':3.5,'w':3.2,'h':4,'color':MC_BLUE,'title':'CUSTOMER_DIM',
            'fields':['PK  customer_id  SERIAL','    first_name   VARCHAR(50)',
                      '    last_name    VARCHAR(50)','    city         VARCHAR(50)',
                      '    mobile_no    VARCHAR(20)','    email        VARCHAR(100)',
                      '    region       VARCHAR(20)','    member_type  VARCHAR(20)']},
        'sales': {'x':4.5,'y':0.5,'w':3.2,'h':3.5,'color':MC_PINK,'title':'SALES_FACT',
            'fields':['PK  sale_id      SERIAL','FK  customer_id  INTEGER',
                      'FK  product_id   INTEGER','    sale_date    DATE',
                      '    quantity     INTEGER','    sale_amount  NUMERIC(10,2)']},
        'product': {'x':8.5,'y':3.5,'w':3.2,'h':2.8,'color':MC_PURPLE,'title':'PRODUCT_DIM',
            'fields':['PK  product_id    SERIAL','    product_name  VARCHAR(100)',
                      '    category      VARCHAR(50)','    unit_price    NUMERIC(10,2)']},
    }
    for key, e in entities.items():
        hh=0.55
        ax.add_patch(FancyBboxPatch((e['x'],e['y']),e['w'],e['h'],
                     boxstyle="round,pad=0.06", facecolor=MC_CARD, edgecolor=e['color'], lw=2.5))
        ax.add_patch(FancyBboxPatch((e['x'],e['y']+e['h']-hh),e['w'],hh,
                     boxstyle="round,pad=0.06", facecolor=e['color'], edgecolor=e['color'], lw=2.5))
        ax.text(e['x']+e['w']/2, e['y']+e['h']-hh/2, e['title'],
                ha='center', va='center', fontsize=10, fontweight='bold',
                color='white', fontfamily='monospace')
        for i, field in enumerate(e['fields']):
            fy=e['y']+e['h']-hh-0.4-i*0.35
            fc=MC_YELLOW if field.startswith('PK') else MC_RED if field.startswith('FK') else MC_MUTED
            ax.text(e['x']+0.2, fy, field, fontsize=8, color=fc, fontfamily='monospace', va='center')
    ax.annotate('', xy=(4.5,2.8), xytext=(2.8,3.5), arrowprops=dict(arrowstyle='->', color=MC_BLUE, lw=3))
    ax.text(3,3.3,'1 : N', fontsize=12, fontweight='bold', color=MC_BLUE)
    ax.annotate('', xy=(7.7,2.8), xytext=(9.5,3.5), arrowprops=dict(arrowstyle='->', color=MC_PURPLE, lw=3))
    ax.text(9,3.3,'1 : N', fontsize=12, fontweight='bold', color=MC_PURPLE)
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"er_diagram.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_dfd_level0():
    fig, ax = plt.subplots(figsize=(10,5))
    ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis('off')
    ax.add_patch(FancyBboxPatch((0.3,1.5),2,2, boxstyle="round,pad=0.1", facecolor=MC_BLUE, edgecolor='white', lw=2))
    ax.text(1.3,2.5,'USER\n(Admin)', ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    c=plt.Circle((5,2.5),1.3, facecolor=MC_PINK, edgecolor='white', lw=2.5); ax.add_patch(c)
    ax.text(5,2.5,'SalesDB\nSystem', ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    ax.add_patch(FancyBboxPatch((7.5,1.5),2,2, boxstyle="round,pad=0.1", facecolor=MC_GREEN, edgecolor='white', lw=2))
    ax.text(8.5,2.5,'PostgreSQL\nDatabase', ha='center', va='center', fontsize=12, fontweight='bold', color='black')
    ax.annotate('', xy=(3.7,2.8), xytext=(2.3,2.8), arrowprops=dict(arrowstyle='->', color=MC_YELLOW, lw=2))
    ax.text(2.8,3.5,'Login +\nCRUD', fontsize=9, ha='center', color=MC_YELLOW)
    ax.annotate('', xy=(2.3,2.2), xytext=(3.7,2.2), arrowprops=dict(arrowstyle='->', color=MC_MUTED, lw=2))
    ax.text(2.8,1.2,'Dashboard\n& Reports', fontsize=9, ha='center', color=MC_MUTED)
    ax.annotate('', xy=(7.5,2.8), xytext=(6.3,2.8), arrowprops=dict(arrowstyle='->', color=MC_YELLOW, lw=2))
    ax.text(6.8,3.5,'SQL\nQueries', fontsize=9, ha='center', color=MC_YELLOW)
    ax.annotate('', xy=(6.3,2.2), xytext=(7.5,2.2), arrowprops=dict(arrowstyle='->', color=MC_MUTED, lw=2))
    ax.text(6.8,1.2,'Result\nSets', fontsize=9, ha='center', color=MC_MUTED)
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"dfd_level0.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_dfd_level1():
    fig, ax = plt.subplots(figsize=(12,8))
    ax.set_xlim(0,12); ax.set_ylim(0,9); ax.axis('off')
    ax.add_patch(FancyBboxPatch((0.2,3.5),1.8,1.5, boxstyle="round,pad=0.1", facecolor=MC_BLUE, edgecolor='white', lw=2))
    ax.text(1.1,4.25,'USER', ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    procs=[
        (4,7.2,2.2,1,'0.0','Authenticate\n(Login)',MC_YELLOW),
        (4,5.5,2.2,1,'1.0','Manage\nCustomers',MC_PINK),
        (4,3.8,2.2,1,'2.0','Manage\nProducts',MC_PURPLE),
        (4,2.1,2.2,1,'3.0','Manage\nSales',MC_RED),
        (4,0.4,2.2,1,'4.0','Generate\nAnalytics',MC_GREEN),
    ]
    for x,y,w,h,num,label,color in procs:
        c=plt.Circle((x+w/2, y+h/2), 0.68, facecolor=color, edgecolor='white', lw=2)
        ax.add_patch(c)
        tc='white' if color!=MC_YELLOW else 'black'
        ax.text(x+w/2, y+h/2+0.18, num, ha='center', va='center', fontsize=8, fontweight='bold', color=tc)
        ax.text(x+w/2, y+h/2-0.18, label, ha='center', va='center', fontsize=6.5, color=tc)
    stores=[
        (8,6,3.5,0.7,'D1','SESSION_STORE',MC_YELLOW),
        (8,4.8,3.5,0.7,'D2','CUSTOMER_DIM',MC_BLUE),
        (8,3.6,3.5,0.7,'D3','PRODUCT_DIM',MC_PURPLE),
        (8,2.4,3.5,0.7,'D4','SALES_FACT',MC_PINK),
    ]
    for x,y,w,h,did,label,color in stores:
        ax.add_patch(Rectangle((x,y),w,h, facecolor=MC_CARD, edgecolor=color, lw=2))
        ax.plot([x+0.6,x+0.6],[y,y+h], color=color, lw=2)
        ax.text(x+0.3, y+h/2, did, ha='center', va='center', fontsize=7, fontweight='bold', color=color)
        ax.text(x+0.6+(w-0.6)/2, y+h/2, label, ha='center', va='center', fontsize=8, color='white', fontfamily='monospace')
    conns=[(2,4.5,4,7.7),(2,4.3,4,6),(2,4.1,4,4.3),(2,3.9,4,2.6),(2,3.7,4,0.9),
           (6.88,7.7,8,6.35),(6.88,6,8,5.15),(6.88,4.3,8,3.95),(6.88,2.6,8,2.75),(6.88,0.9,8,2.55)]
    for x1,y1,x2,y2 in conns:
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle='->', color=MC_MUTED, lw=1.3))
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"dfd_level1.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_crud_flowchart():
    fig, ax = plt.subplots(figsize=(10,6))
    ax.set_xlim(0,10); ax.set_ylim(0,7); ax.axis('off')
    ops=[
        (0.5,4.5,2,1.2,'CREATE\n(POST)',MC_GREEN),
        (3,4.5,2,1.2,'READ\n(GET)',MC_BLUE),
        (5.5,4.5,2,1.2,'UPDATE\n(PUT)',MC_YELLOW),
        (8,4.5,2,1.2,'DELETE\n(DELETE)',MC_RED),
    ]
    for x,y,w,h,label,color in ops:
        ax.add_patch(FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0.1", facecolor=color, edgecolor='white', lw=2))
        tc='white' if color!=MC_YELLOW else 'black'
        ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=11, fontweight='bold', color=tc)
    # Auth gate
    ax.add_patch(FancyBboxPatch((3,6),4,0.7, boxstyle="round,pad=0.1", facecolor=MC_YELLOW, edgecolor='white', lw=2))
    ax.text(5,6.35,'🔒 login_required (except GET)', ha='center', va='center', fontsize=9, fontweight='bold', color='black')
    ax.add_patch(FancyBboxPatch((3,1),4,2, boxstyle="round,pad=0.15", facecolor=MC_CARD, edgecolor=MC_PINK, lw=3))
    ax.text(5,2,'PostgreSQL\nDatabase', ha='center', va='center', fontsize=14, fontweight='bold', color=MC_PINK)
    for xs in [1.5,4,6.5,9]:
        ax.annotate('', xy=(5,3), xytext=(xs,4.5), arrowprops=dict(arrowstyle='->', color=MC_MUTED, lw=2))
    ax.annotate('', xy=(5,5.7), xytext=(5,6), arrowprops=dict(arrowstyle='->', color=MC_YELLOW, lw=2))
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"crud_flow.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_sequence_diagram():
    fig, ax = plt.subplots(figsize=(11,8))
    ax.set_xlim(0,11); ax.set_ylim(0,10); ax.axis('off')
    actors=[(1.5,9.2,'User'),(4,9.2,'Frontend\n(JS)'),(6.5,9.2,'Flask API'),(9,9.2,'PostgreSQL')]
    for x,y,label in actors:
        ax.add_patch(FancyBboxPatch((x-0.7,y-0.35),1.4,0.8, boxstyle="round,pad=0.05",
                     facecolor=MC_CARD, edgecolor=MC_BLUE, lw=2))
        ax.text(x,y,label, ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        ax.plot([x,x],[0.5,y-0.35], color=MC_BORDER, lw=1.5, ls='dashed')
    msgs=[
        (1.5,9,8,'Selects product, enters qty',MC_YELLOW,True),
        (4,9,7.5,'calcSaleAmount() runs',MC_GREEN,True),
        (1.5,4,7,'Clicks "Add Sale"',MC_YELLOW,True),
        (4,4,6.5,'POST /api/sales (JSON)',MC_PINK,True),
        (6.5,4,6,'Check session → OK',MC_YELLOW,True),
        (6.5,4,5.5,'INSERT INTO sales_fact',MC_PURPLE,True),
        (9,6.5,5,'Returns sale_id',MC_GREEN,False),
        (6.5,9,4.5,'JSON Response {sale_id}',MC_PINK,False),
        (4,9,4,'Update table + toast ✓',MC_BLUE,False),
    ]
    y_pos=8.2
    for fx,fy_off,tx,label,color,forward in msgs:
        y_pos-=0.78
        if forward:
            ax.annotate('', xy=(tx,y_pos), xytext=(fx,y_pos), arrowprops=dict(arrowstyle='->', color=color, lw=2))
        else:
            ax.annotate('', xy=(tx,y_pos), xytext=(fx,y_pos), arrowprops=dict(arrowstyle='->', color=color, lw=2, ls='dashed'))
        mid=(fx+tx)/2
        ax.text(mid, y_pos+0.22, label, ha='center', fontsize=7, color=color)
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"sequence.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_flowchart():
    fig, ax = plt.subplots(figsize=(7,12))
    ax.set_xlim(0,7); ax.set_ylim(0,14); ax.axis('off')
    def box(x,y,w,h,text,color,shape='rect'):
        if shape=='oval':
            e=plt.matplotlib.patches.Ellipse((x+w/2,y+h/2),w,h, facecolor=color, edgecolor='white', lw=2)
            ax.add_patch(e)
        elif shape=='diamond':
            d=plt.Polygon([(x+w/2,y+h),(x+w,y+h/2),(x+w/2,y),(x,y+h/2)], facecolor=color, edgecolor='white', lw=2)
            ax.add_patch(d)
        else:
            ax.add_patch(FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0.05", facecolor=color, edgecolor='white', lw=2))
        ax.text(x+w/2,y+h/2,text, ha='center', va='center', fontsize=7.5, fontweight='bold', color='white')
    steps=[
        (2,12.5,3,0.65,'START',MC_GREEN,'oval'),
        (2,11.2,3,0.65,'Flask Starts',MC_BLUE,'rect'),
        (2,10,3,0.65,'Browser Opens',MC_PURPLE,'rect'),
        (2,8.8,3,0.65,'Load Dashboard\n(Public)',MC_PINK,'rect'),
        (2,7.5,3,0.65,'Click Protected\nPage?',MC_YELLOW,'diamond'),
        (2,6.2,3,0.65,'Show Login\nOverlay',MC_YELLOW,'rect'),
        (2,4.9,3,0.65,'Validate\nCredentials',MC_RED,'diamond'),
        (2,3.7,3,0.65,'Create Session\n(30 min)',MC_GREEN,'rect'),
        (2,2.5,3,0.65,'Access CRUD\nPages',MC_BLUE,'rect'),
        (2,1.3,3,0.65,'Perform Actions',MC_PINK,'rect'),
    ]
    for x,y,w,h,text,color,shape in steps:
        box(x,y,w,h,text,color,shape)
    for i in range(len(steps)-1):
        ax.annotate('', xy=(3.5,steps[i+1][1]+steps[i+1][3]),
                    xytext=(3.5,steps[i][1]),
                    arrowprops=dict(arrowstyle='->', color=MC_MUTED, lw=1.8))
    ax.annotate('', xy=(5.8,1.7), xytext=(5.8,8.8+0.32),
                arrowprops=dict(arrowstyle='->', color=MC_RED, lw=1.5, ls='dashed'))
    ax.text(6.3,5,'Session\nExpiry\nLoop', fontsize=7, color=MC_RED, ha='center')
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"flowchart.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_dashboard_charts():
    fig, axes = plt.subplots(1,3, figsize=(14,4.5))
    cats=['Electronics','Home Goods','Apparel','Other']
    rev=[45200,28100,17800,8900]; colors=[MC_PINK,MC_BLUE,MC_PURPLE,MC_RED]
    axes[0].bar(cats, rev, color=colors, edgecolor='white', lw=0.5, width=0.6)
    axes[0].set_title('Revenue by Category', fontsize=11, fontweight='bold', color='white', pad=10)
    axes[0].set_facecolor(MC_CARD)
    axes[0].tick_params(colors=MC_MUTED, labelsize=8)
    for sp in ['top','right']: axes[0].spines[sp].set_visible(False)
    for sp in ['bottom','left']: axes[0].spines[sp].set_color(MC_BORDER)
    axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f'${x/1000:.0f}K'))
    axes[1].pie(rev, labels=cats, autopct='%1.1f%%', colors=colors,
                textprops={'fontsize':8,'color':'white'}, startangle=90,
                pctdistance=0.8, wedgeprops=dict(width=0.4, edgecolor=MC_BG, linewidth=2))
    axes[1].set_title('Sales Distribution', fontsize=11, fontweight='bold', color='white', pad=10)
    axes[2].pie([42,58], labels=['Gold\n42%','Regular\n58%'],
                colors=[MC_YELLOW,'#475569'], textprops={'fontsize':10,'color':'white'},
                startangle=90, wedgeprops=dict(edgecolor=MC_BG, linewidth=2))
    axes[2].set_title('Customer Segments', fontsize=11, fontweight='bold', color='white', pad=10)
    fig.patch.set_facecolor(MC_BG)
    for a in axes: a.set_facecolor(MC_BG) if a!=axes[0] else None
    plt.tight_layout(pad=2)
    p=os.path.join(IMG_DIR,"dashboard_charts.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_kpi_cards():
    fig, ax = plt.subplots(figsize=(12,2.2))
    ax.set_xlim(0,12); ax.set_ylim(0,2.2); ax.axis('off')
    kpis=[
        (0.1,'TOTAL REVENUE','$100,000',MC_PINK),(2.5,'TOTAL SALES','245',MC_BLUE),
        (4.9,'AVG ORDER','$408.16',MC_PURPLE),(7.3,'CUSTOMERS','48',MC_RED),(9.7,'PRODUCTS','12',MC_GREEN),
    ]
    for x,label,value,color in kpis:
        ax.add_patch(FancyBboxPatch((x,0.2),2.2,1.8, boxstyle="round,pad=0.08", facecolor=MC_CARD, edgecolor=MC_BORDER, lw=1.5))
        ax.add_patch(Rectangle((x,1.95),2.2,0.05, facecolor=color))
        ax.text(x+0.15, 1.65, label, fontsize=7, color=MC_MUTED, fontweight='bold')
        ax.text(x+0.15, 0.8, value, fontsize=18, color='white', fontweight='bold')
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"kpi_cards.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_auth_flow():
    """Auth flow diagram showing login → session → protected routes."""
    fig, ax = plt.subplots(figsize=(10,5.5))
    ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis('off')

    # Step boxes
    steps=[
        (0.3,4,2,1.3,'User clicks\nprotected page\nor Login button',MC_BLUE),
        (3,4,2,1.3,'Login overlay\nappears\n(username + pwd)',MC_PINK),
        (5.7,4,2,1.3,'POST /api/login\nFlask validates\ncredentials',MC_PURPLE),
        (5.7,1.5,2,1.3,'Session created\n(30 min expiry)\nCookie set',MC_GREEN),
        (3,1.5,2,1.3,'UI updates:\n✓ Admin badge\n🔓 Pages unlock',MC_YELLOW),
        (0.3,1.5,2,1.3,'Access CRUD:\nSales, Customers\nProducts',MC_PINK),
    ]
    for x,y,w,h,label,color in steps:
        ax.add_patch(FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0.1", facecolor=color, edgecolor='white', lw=2))
        tc='white' if color!=MC_YELLOW else 'black'
        ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color=tc)

    # Arrows
    arrow_pairs=[(2.3,4.65,3,4.65),(5,4.65,5.7,4.65),(6.7,4,6.7,2.8),
                 (5.7,2.15,5,2.15),(3,2.15,2.3,2.15)]
    for x1,y1,x2,y2 in arrow_pairs:
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle='->', color=MC_MUTED, lw=2.5))

    # Expiry path
    ax.add_patch(FancyBboxPatch((8.3,2.5),1.5,1, boxstyle="round,pad=0.08", facecolor=MC_RED, edgecolor='white', lw=2))
    ax.text(9.05,3,'Session\nExpires', ha='center', va='center', fontsize=8, fontweight='bold', color='white')
    ax.annotate('', xy=(8.3,3), xytext=(7.7,2.15), arrowprops=dict(arrowstyle='->', color=MC_RED, lw=1.5, ls='dashed'))
    ax.annotate('', xy=(5,4.5), xytext=(8.3,3.3), arrowprops=dict(arrowstyle='->', color=MC_RED, lw=1.5, ls='dashed'))
    ax.text(8.8,3.8,'401 → re-login', fontsize=7, color=MC_RED)

    plt.tight_layout()
    p=os.path.join(IMG_DIR,"auth_flow.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_screenshot_login():
    """Generate a mockup of the login overlay."""
    fig, ax = plt.subplots(figsize=(10,7))
    ax.set_xlim(0,10); ax.set_ylim(0,7); ax.axis('off')

    # Dark overlay background
    ax.add_patch(Rectangle((0,0),10,7, facecolor='#0a0e1a', alpha=0.95))

    # Login card
    cx,cy,cw,ch = 2.5, 1.2, 5, 4.6
    ax.add_patch(FancyBboxPatch((cx,cy),cw,ch, boxstyle="round,pad=0.15",
                 facecolor=MC_CARD, edgecolor=MC_BORDER, lw=2))
    # Top gradient bar
    ax.add_patch(Rectangle((cx,cy+ch-0.08),cw,0.08,
                 facecolor=MC_YELLOW))

    # Logo
    ax.text(5, 5.2, 'SalesDB', ha='center', va='center', fontsize=24, fontweight='bold', color='white')
    ax.text(5, 4.8, 'ADMIN AUTHENTICATION', ha='center', va='center',
        fontsize=8, color=MC_MUTED, fontweight='bold')

    # Username field
    ax.add_patch(FancyBboxPatch((3,3.8),4,0.5, boxstyle="round,pad=0.05",
                 facecolor=MC_BG, edgecolor=MC_BORDER, lw=1.5))
    ax.text(3.15, 4.05, 'admin', fontsize=11, color='white')

    # Password field
    ax.add_patch(FancyBboxPatch((3,3.1),4,0.5, boxstyle="round,pad=0.05",
                 facecolor=MC_BG, edgecolor=MC_BORDER, lw=1.5))
    ax.text(3.15, 3.35, '• • • • • • • •', fontsize=11, color=MC_MUTED)

    # Login button
    ax.add_patch(FancyBboxPatch((3,2.2),4,0.55, boxstyle="round,pad=0.05",
                 facecolor=MC_YELLOW, edgecolor=MC_YELLOW, lw=1.5))
    ax.text(5, 2.47, '🔐  LOGIN', ha='center', va='center',
            fontsize=12, fontweight='bold', color='black')

    # Session info
    ax.text(5, 1.7, 'Session expires after 30 minutes of inactivity',
            ha='center', va='center', fontsize=7, color=MC_MUTED)

    # Close button
    ax.text(7.2, 5.5, '✕', fontsize=14, color=MC_MUTED, fontweight='bold')

    plt.tight_layout()
    p=os.path.join(IMG_DIR,"screenshot_login.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor='#0a0e1a'); plt.close(); return p


def _sidebar(ax, active_idx, xlim=12, ylim=8):
    ax.set_xlim(0,xlim); ax.set_ylim(0,ylim); ax.axis('off')
    ax.add_patch(Rectangle((0,0),xlim,ylim, facecolor=MC_BG, edgecolor=MC_BORDER, lw=2))
    ax.add_patch(Rectangle((0,0),2.2,ylim, facecolor=MC_CARD, edgecolor=MC_BORDER, lw=1))
    ax.text(0.3,ylim-0.5,'SalesDB', fontsize=10, fontweight='bold', color=MC_PINK)
    ax.text(0.3,ylim-0.9,'Analytics', fontsize=6, color=MC_MUTED)
    nav=['▦ Dashboard','◈ Sales','◉ Customers','◇ Products']
    for i,item in enumerate(nav):
        y=ylim-1.6-i*0.55
        fc=MC_PINK if i==active_idx else MC_MUTED
        ax.text(0.3, y, item, fontsize=7, color=fc)
        if i!=active_idx and i>0:
            ax.text(2, y, '🔒', fontsize=5, color=MC_MUTED)
    ax.add_patch(Rectangle((2.2,ylim-0.8),xlim-2.2,0.8, facecolor=MC_CARD, edgecolor=MC_BORDER, lw=1))
    return ax


def gen_screenshot_dashboard():
    fig, ax = plt.subplots(figsize=(12,7))
    _sidebar(ax, 0)
    ax.text(2.6, 7.25, 'Dashboard', fontsize=11, fontweight='bold', color='white')
    # Login btn in topbar
    ax.add_patch(FancyBboxPatch((9.5,7.12),1.5,0.45, boxstyle="round,pad=0.04",
                 facecolor=MC_YELLOW, edgecolor=MC_YELLOW, lw=1))
    ax.text(10.25,7.34,'🔒 Login', ha='center', fontsize=7, fontweight='bold', color='black')
    # KPIs
    kpis=[('$100K',MC_PINK),('245',MC_BLUE),('$408',MC_PURPLE),('48',MC_RED),('12',MC_GREEN)]
    for i,(val,color) in enumerate(kpis):
        x=2.6+i*1.85
        ax.add_patch(FancyBboxPatch((x,5.2),1.65,1.3, boxstyle="round,pad=0.06", facecolor=MC_CARD, edgecolor=MC_BORDER, lw=1))
        ax.add_patch(Rectangle((x,6.47),1.65,0.03, facecolor=color))
        ax.text(x+0.15, 5.9, val, fontsize=14, fontweight='bold', color='white')
    # Charts
    for i in range(3):
        x=2.6+i*3.1
        ax.add_patch(FancyBboxPatch((x,0.5),2.9,4.3, boxstyle="round,pad=0.06", facecolor=MC_CARD, edgecolor=MC_BORDER, lw=1))
        if i==0:
            for j,h in enumerate([2.5,1.8,1.2,0.6]):
                ax.add_patch(Rectangle((x+0.3+j*0.6,0.8),0.4,h, facecolor=[MC_PINK,MC_BLUE,MC_PURPLE,MC_RED][j]))
        elif i==1:
            c1=plt.Circle((x+1.45,2.3),1, facecolor=MC_PINK, edgecolor=MC_BG, lw=0); ax.add_patch(c1)
            c2=plt.matplotlib.patches.Wedge((x+1.45,2.3),1,90,220, facecolor=MC_BLUE, edgecolor=MC_BG, lw=0); ax.add_patch(c2)
            c3=plt.Circle((x+1.45,2.3),0.5, facecolor=MC_CARD); ax.add_patch(c3)
        else:
            c1=plt.Circle((x+1.45,2.3),1, facecolor=MC_YELLOW, edgecolor=MC_BG, lw=0); ax.add_patch(c1)
            c2=plt.matplotlib.patches.Wedge((x+1.45,2.3),1,0,210, facecolor='#475569', edgecolor=MC_BG, lw=0); ax.add_patch(c2)
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"screenshot_dashboard.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_screenshot_sales():
    fig, ax = plt.subplots(figsize=(12,7))
    _sidebar(ax, 1)
    ax.text(2.6, 7.25, 'Sales', fontsize=11, fontweight='bold', color='white')
    # Admin badge + logout
    ax.add_patch(FancyBboxPatch((8.5,7.12),1,0.45, boxstyle="round,pad=0.04",
                 facecolor='#3ddc8420', edgecolor=MC_GREEN, lw=1))
    ax.text(9,7.34,'✓ Admin', ha='center', fontsize=6, fontweight='bold', color=MC_GREEN)
    ax.add_patch(FancyBboxPatch((9.7,7.12),1.3,0.45, boxstyle="round,pad=0.04",
                 facecolor='none', edgecolor=MC_RED, lw=1))
    ax.text(10.35,7.34,'⏻ Logout', ha='center', fontsize=6, fontweight='bold', color=MC_RED)
    # Form
    ax.add_patch(FancyBboxPatch((2.6,4.5),9,2.3, boxstyle="round,pad=0.06", facecolor=MC_CARD, edgecolor=MC_BORDER, lw=1))
    ax.add_patch(Rectangle((2.6,6.5),9,0.3, facecolor=MC_BORDER))
    ax.text(2.8, 6.55, 'Add New Sale', fontsize=8, fontweight='bold', color='white')
    # Table
    ax.add_patch(FancyBboxPatch((2.6,0.3),9,3.8, boxstyle="round,pad=0.06", facecolor=MC_CARD, edgecolor=MC_BORDER, lw=1))
    ax.add_patch(Rectangle((2.6,3.8),9,0.3, facecolor=MC_BORDER))
    ax.text(2.8, 3.85, 'All Sales', fontsize=8, fontweight='bold', color='white')
    headers=['#','Customer','Product','Cat','Date','Qty','Price','Total','']
    for i,h in enumerate(headers):
        ax.text(2.7+i*1.0, 3.45, h, fontsize=5.5, color=MC_MUTED, fontweight='bold')
    rows=[['#5','Alice','Laptop','Elec','12-15','2','$999','$1,998','✕'],
          ['#4','Bob','T-Shirt','App','12-14','5','$29','$145','✕']]
    for r,row in enumerate(rows):
        y=2.9-r*0.7
        for c,val in enumerate(row):
            fc=MC_MUTED if c==0 else MC_PINK if c==7 else MC_RED if c==8 else 'white'
            ax.text(2.7+c*1.0, y, val, fontsize=5.5, color=fc)
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"screenshot_sales.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_screenshot_customers():
    fig, ax = plt.subplots(figsize=(12,7))
    _sidebar(ax, 2)
    ax.text(2.6, 7.25, 'Customers', fontsize=11, fontweight='bold', color='white')
    ax.add_patch(FancyBboxPatch((2.6,4),9,2.8, boxstyle="round,pad=0.06", facecolor=MC_CARD, edgecolor=MC_BORDER, lw=1))
    ax.add_patch(Rectangle((2.6,6.5),9,0.3, facecolor=MC_BORDER))
    ax.text(2.8, 6.55, 'Add Customer', fontsize=8, fontweight='bold', color='white')
    ax.add_patch(FancyBboxPatch((2.6,0.3),9,3.3, boxstyle="round,pad=0.06", facecolor=MC_CARD, edgecolor=MC_BORDER, lw=1))
    ax.add_patch(Rectangle((2.6,3.3),9,0.3, facecolor=MC_BORDER))
    ax.text(2.8, 3.35, 'All Customers', fontsize=8, fontweight='bold', color='white')
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"screenshot_customers.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


def gen_screenshot_products():
    fig, ax = plt.subplots(figsize=(12,7))
    _sidebar(ax, 3)
    ax.text(2.6, 7.25, 'Products', fontsize=11, fontweight='bold', color='white')
    ax.add_patch(FancyBboxPatch((2.6,5),9,1.8, boxstyle="round,pad=0.06", facecolor=MC_CARD, edgecolor=MC_BORDER, lw=1))
    ax.add_patch(Rectangle((2.6,6.5),9,0.3, facecolor=MC_BORDER))
    ax.text(2.8, 6.55, 'Add Product', fontsize=8, fontweight='bold', color='white')
    ax.add_patch(FancyBboxPatch((2.6,0.3),9,4.3, boxstyle="round,pad=0.06", facecolor=MC_CARD, edgecolor=MC_BORDER, lw=1))
    ax.add_patch(Rectangle((2.6,4.3),9,0.3, facecolor=MC_BORDER))
    ax.text(2.8, 4.35, 'All Products', fontsize=8, fontweight='bold', color='white')
    plt.tight_layout()
    p=os.path.join(IMG_DIR,"screenshot_products.png")
    plt.savefig(p, dpi=180, bbox_inches='tight', facecolor=MC_BG); plt.close(); return p


# ══════════════════════════════════════════
#  PPTX HELPERS
# ══════════════════════════════════════════

def set_bg(s, c=BG_DARK): f=s.background.fill; f.solid(); f.fore_color.rgb=c
def add_box(s,l,t,w,h,fc,ec=None):
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,l,t,w,h); sh.fill.solid(); sh.fill.fore_color.rgb=fc
    if ec: sh.line.color.rgb=ec; sh.line.width=Pt(1)
    else: sh.line.fill.background()
    sh.adjustments[0]=0.05; return sh
def add_bar(s,l,t,w,h,c):
    sh=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,l,t,w,h); sh.fill.solid(); sh.fill.fore_color.rgb=c; sh.line.fill.background(); return sh
def add_txt(s,l,t,w,h,text,sz=18,color=WHITE,bold=False,align=PP_ALIGN.LEFT,font='Calibri'):
    tb=s.shapes.add_textbox(l,t,w,h); tf=tb.text_frame; tf.word_wrap=True
    p=tf.paragraphs[0]; p.text=text; p.font.size=Pt(sz); p.font.color.rgb=color
    p.font.bold=bold; p.font.name=font; p.alignment=align; return tb
def add_img(s,path,l,t,w=None):
    if w: s.shapes.add_picture(path,l,t,width=w)
    else: s.shapes.add_picture(path,l,t)
def sn(s,n):
    add_txt(s,Inches(8.5),Inches(6.85),Inches(1.2),Inches(0.3),f"{n}/18",sz=9,color=MUTED,align=PP_ALIGN.RIGHT)
def sh(s,title,sub="",n=1):
    add_bar(s,Inches(0),Inches(0),Inches(10),Pt(4),PINK)
    add_txt(s,Inches(0.4),Inches(0.2),Inches(2),Inches(0.35),"SalesDB",sz=13,color=PINK,bold=True)
    add_txt(s,Inches(0.4),Inches(0.7),Inches(9),Inches(0.55),title,sz=26,color=WHITE,bold=True)
    if sub: add_txt(s,Inches(0.4),Inches(1.3),Inches(9),Inches(0.35),sub,sz=13,color=MUTED)
    add_bar(s,Inches(0.4),Inches(1.75),Inches(1.5),Pt(2),PINK); sn(s,n)


# ══════════════════════════════════════════
#  BUILD 18 SLIDES
# ══════════════════════════════════════════

def build(img):
    prs=Presentation(); prs.slide_width=Inches(10); prs.slide_height=Inches(7.5)
    bl=prs.slide_layouts[6]

    # ── 1: TITLE ────────────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    add_bar(s,Inches(0),Inches(0),Inches(10),Pt(5),PINK)
    add_bar(s,Inches(0),Inches(7.45),Inches(10),Pt(5),BLUE)
    add_txt(s,Inches(1),Inches(1.2),Inches(8),Inches(0.9),"SALESDB",sz=52,color=PINK,bold=True,align=PP_ALIGN.CENTER)
    add_txt(s,Inches(1),Inches(2.2),Inches(8),Inches(0.5),"Sales Analytics Dashboard",sz=24,color=BLUE,bold=True,align=PP_ALIGN.CENTER)
    add_bar(s,Inches(3.5),Inches(3),Inches(3),Pt(2),PINK)
    add_txt(s,Inches(1),Inches(3.3),Inches(8),Inches(0.4),"Full-Stack Web App with Admin Authentication & Real-time Analytics",sz=13,color=MUTED,align=PP_ALIGN.CENTER)
    add_box(s,Inches(2.5),Inches(4.3),Inches(5),Inches(2.2),BG_CARD,DARK_BDR)
    info=["Presented by: [Your Name]","Roll No: [Your Roll Number]","Department: [Your Department]","Guide: Prof. [Guide Name]","Institution: [Your Institution]"]
    for i,line in enumerate(info):
        add_txt(s,Inches(2.7),Inches(4.45+i*0.38),Inches(4.6),Inches(0.35),line,sz=11,color=MUTED,align=PP_ALIGN.CENTER)
    sn(s,1)

    # ── 2: AGENDA ───────────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Agenda","18-Slide Presentation Outline",2)
    items=[
        ("01","Project Overview",PINK),("02","Problem Statement",BLUE),("03","Objectives",PURPLE),
        ("04","Technology Stack",GREEN),("05","System Architecture",YELLOW),("06","Database & ER Diagram",RED),
        ("07","Data Flow Diagrams",PINK),("08","Dashboard Features",BLUE),("09","CRUD Operations",GREEN),
        ("10","Authentication & Security",YELLOW),("11","Auto-Calculation & Sequence",PURPLE),
        ("12","Program Execution Flow",RED),("13-16","Screenshots (Dashboard, Login, Sales, etc.)",PINK),
        ("17","Advantages",GREEN),("18","Conclusion & Thank You",BLUE),
    ]
    for i,(num,title,color) in enumerate(items):
        r=i//3; c=i%3
        x=Inches(0.3+c*3.2); y=Inches(2.1+r*0.75)
        add_box(s,x,y,Inches(3),Inches(0.58),BG_CARD,DARK_BDR)
        add_bar(s,x,y,Pt(3),Inches(0.58),color)
        add_txt(s,x+Inches(0.12),y+Inches(0.08),Inches(0.45),Inches(0.4),num,sz=10,color=color,bold=True)
        add_txt(s,x+Inches(0.6),y+Inches(0.1),Inches(2.2),Inches(0.35),title,sz=10,color=WHITE)

    # ── 3: OVERVIEW ─────────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Project Overview","What is SalesDB?",3)
    add_txt(s,Inches(0.4),Inches(2.0),Inches(9.2),Inches(0.7),
        "SalesDB is a full-stack web app for managing sales, customers & products with "
        "real-time analytics, admin authentication, and auto-calculation features.",sz=13,color=MUTED)
    feats=[
        ("📊","Real-time Dashboard","KPI cards + 3 interactive charts",PINK),
        ("🔐","Admin Authentication","Session-based login with 30min expiry",YELLOW),
        ("👥","Customer Management","7 fields with Gold/Regular membership",BLUE),
        ("📦","Product Catalog","Name, category & unit price tracking",PURPLE),
        ("💰","Auto-Calculation","Amount = Unit Price × Quantity",GREEN),
        ("🔗","REST API","17 endpoints — Flask + PostgreSQL",RED),
    ]
    for i,(icon,title,desc,color) in enumerate(feats):
        r=i//3; c=i%3; x=Inches(0.3+c*3.2); y=Inches(3.0+r*2.1)
        add_box(s,x,y,Inches(3),Inches(1.8),BG_CARD,DARK_BDR)
        add_bar(s,x,y,Inches(3),Pt(3),color)
        add_txt(s,x+Inches(0.15),y+Inches(0.15),Inches(2.7),Inches(0.35),f"{icon}  {title}",sz=13,color=color,bold=True)
        add_txt(s,x+Inches(0.15),y+Inches(0.6),Inches(2.7),Inches(1),desc,sz=11,color=MUTED)

    # ── 4: PROBLEM ──────────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Problem Statement","Why SalesDB is needed",4)
    probs=[
        ("📋","Scattered Data","Sales spread across spreadsheets & notebooks",RED),
        ("📉","No Analytics","Cannot quickly assess revenue or KPIs",YELLOW),
        ("🧮","Manual Errors","Computing totals is tedious and error-prone",PURPLE),
        ("📊","Poor Visualization","Raw numbers lack intuitive insights",BLUE),
        ("🔓","No Access Control","Anyone can modify or delete critical data",PINK),
        ("🔍","No Audit Trail","Can't track who changed what and when",GREEN),
    ]
    for i,(icon,title,desc,color) in enumerate(probs):
        r=i//2; c=i%2; x=Inches(0.3+c*4.85); y=Inches(2.1+r*1.6)
        add_box(s,x,y,Inches(4.6),Inches(1.3),BG_CARD,DARK_BDR)
        add_bar(s,x,y,Pt(4),Inches(1.3),color)
        add_txt(s,x+Inches(0.2),y+Inches(0.1),Inches(4.2),Inches(0.35),f"{icon}  {title}",sz=13,color=color,bold=True)
        add_txt(s,x+Inches(0.2),y+Inches(0.5),Inches(4.2),Inches(0.7),desc,sz=11,color=MUTED)

    # ── 5: OBJECTIVES ───────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Project Objectives","9 Goals Achieved",5)
    objs=[
        "Design & develop a full-stack web app for sales data management",
        "Implement CRUD operations for Customers, Products & Sales",
        "Create interactive dashboard with KPIs & Chart.js visualizations",
        "Design star schema database with dimension & fact tables",
        "Develop RESTful API using Python Flask as middleware",
        "Implement admin authentication with session-based login",
        "Auto-calculate sale amount (Unit Price × Quantity)",
        "Build responsive dark-themed UI with modern patterns",
        "Ensure data integrity via foreign keys & login protection",
    ]
    for i,obj in enumerate(objs):
        y=Inches(2.0+i*0.57)
        add_txt(s,Inches(0.4),y,Inches(0.5),Inches(0.4),f"0{i+1}",sz=11,color=PINK,bold=True)
        add_txt(s,Inches(1),y,Inches(8.5),Inches(0.45),obj,sz=12,color=WHITE)
        if i<8: add_bar(s,Inches(1),y+Inches(0.44),Inches(8.5),Pt(0.5),DARK_BDR)

    # ── 6: TECH STACK ───────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Technology Stack","Tools & Technologies (including Auth)",6)
    add_img(s,img['tech_stack'],Inches(0.5),Inches(2.1),w=Inches(9))

    # ── 7: ARCHITECTURE ─────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"System Architecture","Three-Tier + Authentication Layer",7)
    add_img(s,img['architecture'],Inches(0.3),Inches(2.0),w=Inches(9.4))

    # ── 8: ER DIAGRAM ───────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Database Design","Star Schema — Entity Relationship Diagram",8)
    add_img(s,img['er_diagram'],Inches(0.2),Inches(2.0),w=Inches(9.6))

    # ── 9: DFDs ─────────────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Data Flow Diagrams","Level 0 (Context) & Level 1 (with Auth)",9)
    add_txt(s,Inches(0.4),Inches(2.0),Inches(4.5),Inches(0.3),"DFD Level 0",sz=11,color=PINK,bold=True)
    add_img(s,img['dfd_level0'],Inches(0.2),Inches(2.4),w=Inches(4.8))
    add_txt(s,Inches(5.2),Inches(2.0),Inches(4.5),Inches(0.3),"DFD Level 1 (with Auth process)",sz=11,color=BLUE,bold=True)
    add_img(s,img['dfd_level1'],Inches(5),Inches(2.4),w=Inches(4.8))

    # ── 10: AUTHENTICATION ──────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Authentication & Security","Session-Based Admin Login System",10)

    # Left: Auth flow diagram
    add_txt(s,Inches(0.4),Inches(2.0),Inches(5),Inches(0.3),"Authentication Flow",sz=12,color=YELLOW,bold=True)
    add_img(s,img['auth_flow'],Inches(0.1),Inches(2.4),w=Inches(5.5))

    # Right: Feature list
    add_box(s,Inches(5.8),Inches(2.1),Inches(3.9),Inches(5),BG_CARD,DARK_BDR)
    add_bar(s,Inches(5.8),Inches(2.1),Inches(3.9),Pt(3),YELLOW)
    add_txt(s,Inches(6),Inches(2.2),Inches(3.5),Inches(0.3),"HOW IT WORKS",sz=10,color=YELLOW,bold=True)

    auth_features=[
        ("🔒","Dashboard = PUBLIC","Anyone can view KPIs & charts"),
        ("🔐","CRUD = PROTECTED","Sales, Customers, Products need login"),
        ("👤","Session Login","Username + password → Flask session"),
        ("⏱️","30-min Expiry","Auto-logout after inactivity"),
        ("🛡️","@login_required","Python decorator protects POST/PUT/DELETE"),
        ("401","Auto-redirect","Expired session → login overlay shown"),
        ("🟢","Admin Badge","Green ✓ Admin badge when logged in"),
        ("🟡","Login Button","Yellow button in topbar → opens overlay"),
    ]
    for i,(icon,title,desc) in enumerate(auth_features):
        y=Inches(2.6+i*0.55)
        add_txt(s,Inches(6),y,Inches(0.35),Inches(0.35),icon,sz=9,color=MUTED)
        add_txt(s,Inches(6.4),y,Inches(3.1),Inches(0.25),title,sz=9,color=WHITE,bold=True)
        add_txt(s,Inches(6.4),y+Inches(0.22),Inches(3.1),Inches(0.25),desc,sz=8,color=MUTED)

    # ── 11: DASHBOARD ───────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Dashboard Features","KPI Cards & Interactive Charts (Public)",11)
    add_img(s,img['kpi_cards'],Inches(0.2),Inches(2.0),w=Inches(9.6))
    add_img(s,img['dashboard_charts'],Inches(0.2),Inches(3.8),w=Inches(9.6))

    # ── 12: CRUD + AUTO-CALC ────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"CRUD & Auto-Calculation","Protected Operations + Smart Pricing",12)
    add_img(s,img['crud_flow'],Inches(0.3),Inches(2.0),w=Inches(5))
    add_box(s,Inches(5.5),Inches(2.1),Inches(4.3),Inches(1),BG_CARD,PINK)
    add_txt(s,Inches(5.7),Inches(2.15),Inches(3.9),Inches(0.3),"AUTO-CALCULATION",sz=10,color=PINK,bold=True,align=PP_ALIGN.CENTER)
    add_txt(s,Inches(5.7),Inches(2.5),Inches(3.9),Inches(0.45),"Amount = Price × Qty",sz=18,color=WHITE,bold=True,align=PP_ALIGN.CENTER)

    add_img(s,img['sequence'],Inches(5.3),Inches(3.3),w=Inches(4.5))

    # ── 13: FLOWCHART ───────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Program Execution Flow","Full Lifecycle with Auth Gates",13)
    add_img(s,img['flowchart'],Inches(1),Inches(1.9),w=Inches(3.5))
    add_box(s,Inches(5.2),Inches(2.2),Inches(4.5),Inches(4.8),BG_CARD,DARK_BDR)
    add_txt(s,Inches(5.4),Inches(2.3),Inches(4.1),Inches(0.3),"EXECUTION STEPS",sz=11,color=PINK,bold=True)
    flow_desc=[
        ("1.","Flask starts on port 5000",MC_GREEN),("2.","Browser loads dashboard (public)",MC_BLUE),
        ("3.","KPIs & charts render",MC_PINK),("4.","User clicks protected page",MC_YELLOW),
        ("5.","Login overlay appears",MC_YELLOW),("6.","Credentials validated",MC_RED),
        ("7.","Session created (30 min)",MC_GREEN),("8.","CRUD pages unlocked",MC_BLUE),
        ("9.","API calls include session cookie",MC_PURPLE),("10.","Session expiry → re-login",MC_RED),
    ]
    for i,(num,desc,color) in enumerate(flow_desc):
        add_txt(s,Inches(5.4),Inches(2.7+i*0.42),Inches(0.35),Inches(0.35),num,sz=9,color=RGBColor(*bytes.fromhex(color[1:])),bold=True)
        add_txt(s,Inches(5.8),Inches(2.7+i*0.42),Inches(3.7),Inches(0.35),desc,sz=9,color=MUTED)

    # ── 14: SCREENSHOT — DASHBOARD & LOGIN
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Screenshots — Dashboard & Login","Public Dashboard + Admin Login Overlay",14)
    add_txt(s,Inches(0.4),Inches(2.0),Inches(4.5),Inches(0.3),"Dashboard (Public — no login needed)",sz=11,color=PINK,bold=True)
    add_img(s,img['ss_dashboard'],Inches(0.2),Inches(2.35),w=Inches(4.8))
    add_txt(s,Inches(5.2),Inches(2.0),Inches(4.5),Inches(0.3),"Login Overlay (for admin access)",sz=11,color=YELLOW,bold=True)
    add_img(s,img['ss_login'],Inches(5),Inches(2.35),w=Inches(4.8))

    # ── 15: SCREENSHOT — SALES & CUSTOMERS
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Screenshots — Sales & Customers","Admin-Only Pages (after login)",15)
    add_txt(s,Inches(0.4),Inches(2.0),Inches(4.5),Inches(0.3),"Sales Management (Protected)",sz=11,color=BLUE,bold=True)
    add_img(s,img['ss_sales'],Inches(0.2),Inches(2.35),w=Inches(4.8))
    add_txt(s,Inches(5.2),Inches(2.0),Inches(4.5),Inches(0.3),"Customer Management (Protected)",sz=11,color=GREEN,bold=True)
    add_img(s,img['ss_customers'],Inches(5),Inches(2.35),w=Inches(4.8))

    # ── 16: SCREENSHOT — PRODUCTS
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Screenshots — Products","Admin-Only Product Management",16)
    add_txt(s,Inches(0.4),Inches(2.0),Inches(9),Inches(0.3),"Product Management (Protected — requires admin login)",sz=11,color=PURPLE,bold=True)
    add_img(s,img['ss_products'],Inches(1),Inches(2.5),w=Inches(8))

    # ── 17: ADVANTAGES ──────────────────
    s=prs.slides.add_slide(bl); set_bg(s)
    sh(s,"Advantages","Why SalesDB Stands Out",17)
    advs=[
        ("⚡","Real-time Analytics","Dashboard updates instantly — no refresh needed",PINK),
        ("🔐","Admin Authentication","Session-based login protects all data mutations",YELLOW),
        ("🔒","Data Integrity","Foreign keys + CASCADE + login = secure & clean data",BLUE),
        ("💰","Auto-Calculation","Eliminates manual errors in sale amounts",GREEN),
        ("🎨","Modern UI/UX","Dark-blue theme with login overlay & toast alerts",PURPLE),
        ("🔌","RESTful API","17 endpoints with @login_required decorator",RED),
        ("🆓","100% Open Source","All technologies are free — zero licensing costs",BLUE),
        ("📱","Responsive Design","Works on desktop, tablet & mobile screens",PINK),
    ]
    for i,(icon,title,desc,color) in enumerate(advs):
        r=i//2; c=i%2; x=Inches(0.3+c*4.85); y=Inches(2.1+r*1.25)
        add_box(s,x,y,Inches(4.6),Inches(1),BG_CARD,DARK_BDR)
        add_bar(s,x,y,Pt(4),Inches(1),color)
        add_txt(s,x+Inches(0.2),y+Inches(0.05),Inches(4.2),Inches(0.35),f"{icon}  {title}",sz=12,color=color,bold=True)
        add_txt(s,x+Inches(0.2),y+Inches(0.45),Inches(4.2),Inches(0.45),desc,sz=10,color=MUTED)

    # ── 18: CONCLUSION + THANK YOU ──────
    s=prs.slides.add_slide(bl); set_bg(s)
    add_bar(s,Inches(0),Inches(0),Inches(10),Pt(5),PINK)
    add_txt(s,Inches(0.4),Inches(0.2),Inches(2),Inches(0.35),"SalesDB",sz=13,color=PINK,bold=True)
    add_txt(s,Inches(0.4),Inches(0.7),Inches(9),Inches(0.55),"Conclusion & Thank You",sz=26,color=WHITE,bold=True)
    add_bar(s,Inches(0.4),Inches(1.4),Inches(1.5),Pt(2),PINK)

    add_box(s,Inches(0.3),Inches(1.7),Inches(9.4),Inches(1.1),BG_CARD,GREEN)
    add_bar(s,Inches(0.3),Inches(1.7),Inches(9.4),Pt(3),GREEN)
    add_txt(s,Inches(0.5),Inches(1.8),Inches(9),Inches(0.25),"✅  ALL 9 OBJECTIVES ACHIEVED — 100% TEST PASS RATE",sz=11,color=GREEN,bold=True)
    add_txt(s,Inches(0.5),Inches(2.15),Inches(9),Inches(0.5),
        "Full-stack app with CRUD, dashboard, admin login, auto-calculation, and responsive UI.",sz=11,color=MUTED)

    stats=[("4","Modules",PINK),("17","API\nEndpoints",BLUE),("3","DB\nTables",PURPLE),
           ("21","Test\nCases",GREEN),("100%","Pass\nRate",YELLOW)]
    for i,(val,label,color) in enumerate(stats):
        x=Inches(0.3+i*1.92); y=Inches(3.1)
        add_box(s,x,y,Inches(1.75),Inches(0.95),BG_CARD,color)
        add_txt(s,x+Inches(0.1),y+Inches(0.02),Inches(1.55),Inches(0.45),val,sz=20,color=color,bold=True,align=PP_ALIGN.CENTER)
        add_txt(s,x+Inches(0.1),y+Inches(0.5),Inches(1.55),Inches(0.4),label,sz=8,color=MUTED,align=PP_ALIGN.CENTER)

    add_txt(s,Inches(1),Inches(4.3),Inches(8),Inches(0.7),"Thank You!",sz=42,color=PINK,bold=True,align=PP_ALIGN.CENTER)
    add_txt(s,Inches(1),Inches(5),Inches(8),Inches(0.4),"Questions & Discussion",sz=18,color=BLUE,align=PP_ALIGN.CENTER)
    add_bar(s,Inches(3.5),Inches(5.5),Inches(3),Pt(2),PINK)
    add_box(s,Inches(2.5),Inches(5.7),Inches(5),Inches(1.5),BG_CARD,DARK_BDR)
    contacts=[("🌐","Demo: http://localhost:5000"),("🔐","Login: admin / admin123"),
              ("💻","Stack: Flask + PostgreSQL + Chart.js")]
    for i,(icon,text) in enumerate(contacts):
        add_txt(s,Inches(2.8),Inches(5.85+i*0.4),Inches(4.4),Inches(0.35),f"{icon}  {text}",sz=11,color=MUTED,align=PP_ALIGN.CENTER)
    sn(s,18)

    fname='SalesDB_Presentation.pptx'
    prs.save(fname); return fname


# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════

if __name__=='__main__':
    print('\n  ╔══════════════════════════════════════╗')
    print('  ║  SalesDB — 18-Slide PPT (with Auth)  ║')
    print('  ╚══════════════════════════════════════╝\n')
    print('  → Generating diagrams & screenshots...')

    img={}
    img['tech_stack']=gen_tech_stack();          print('    ✓ Tech Stack')
    img['architecture']=gen_architecture();      print('    ✓ Architecture')
    img['er_diagram']=gen_er_diagram();          print('    ✓ ER Diagram')
    img['dfd_level0']=gen_dfd_level0();          print('    ✓ DFD Level 0')
    img['dfd_level1']=gen_dfd_level1();          print('    ✓ DFD Level 1 (with Auth)')
    img['crud_flow']=gen_crud_flowchart();       print('    ✓ CRUD Flowchart (with Auth gate)')
    img['sequence']=gen_sequence_diagram();      print('    ✓ Sequence Diagram (with session check)')
    img['flowchart']=gen_flowchart();            print('    ✓ Program Flowchart (with login flow)')
    img['dashboard_charts']=gen_dashboard_charts(); print('    ✓ Dashboard Charts')
    img['kpi_cards']=gen_kpi_cards();            print('    ✓ KPI Cards')
    img['auth_flow']=gen_auth_flow();            print('    ✓ Auth Flow Diagram [NEW]')
    img['ss_login']=gen_screenshot_login();      print('    ✓ Screenshot: Login [NEW]')
    img['ss_dashboard']=gen_screenshot_dashboard(); print('    ✓ Screenshot: Dashboard')
    img['ss_sales']=gen_screenshot_sales();      print('    ✓ Screenshot: Sales')
    img['ss_customers']=gen_screenshot_customers(); print('    ✓ Screenshot: Customers')
    img['ss_products']=gen_screenshot_products(); print('    ✓ Screenshot: Products')

    print(f'\n  → 16 images saved to {IMG_DIR}/')
    print('  → Building 18 slides...')
    fname=build(img)
    print(f'\n  ✓ Saved: {fname}')
    print('  ✓ Total: 18 slides\n')

    slides=[
        '01. Title / Cover',
        '02. Agenda (15 items)',
        '03. Project Overview (6 features incl. Auth)',
        '04. Problem Statement (6 problems incl. No Access Control)',
        '05. Objectives (9 goals incl. Authentication)',
        '06. Technology Stack [DIAGRAM — includes Security layer]',
        '07. System Architecture [DIAGRAM — includes Auth node]',
        '08. Database & ER Diagram [DIAGRAM]',
        '09. Data Flow Diagrams [2 DIAGRAMS — DFD1 includes Auth process]',
        '10. Authentication & Security [AUTH FLOW DIAGRAM + feature list] ★NEW',
        '11. Dashboard Features [KPIs + CHARTS]',
        '12. CRUD & Auto-Calculation [CRUD FLOWCHART + SEQUENCE DIAGRAM]',
        '13. Program Execution Flow [FLOWCHART with login gates]',
        '14. Screenshots: Dashboard & Login [2 SCREENSHOTS] ★UPDATED',
        '15. Screenshots: Sales & Customers [2 SCREENSHOTS]',
        '16. Screenshots: Products [SCREENSHOT]',
        '17. Advantages (8 points incl. Auth & Security) ★UPDATED',
        '18. Conclusion + Thank You (merged — 17 endpoints, admin creds shown)',
    ]
    print('  Slides:')
    for sl in slides: print(f'    {sl}')
    print()
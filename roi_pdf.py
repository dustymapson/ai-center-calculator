# ==================== PDF ====================
GOLD = colors.HexColor("#d4af37")
GOLD_DIM = colors.HexColor("#b8962e")
WHITE = colors.HexColor("#ffffff")
DARK = colors.HexColor("#141414")
DARKER = colors.HexColor("#0f0f0f")
BLACK = colors.HexColor("#0a0a0a")
MUTED = colors.HexColor("#888888")
NOTE = colors.HexColor("#cccccc")
GRID = colors.HexColor("#2a2a2a")
GOLD_BG = colors.HexColor("#1f1a0f")


def draw_bg(canvas_obj, doc):
    page_w, page_h = letter
    canvas_obj.setFillColor(BLACK)
    canvas_obj.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    canvas_obj.setStrokeColor(GOLD)
    canvas_obj.setLineWidth(1.5)
    canvas_obj.line(40, page_h - 28, page_w - 40, page_h - 28)
    canvas_obj.line(40, 32, page_w - 40, 32)

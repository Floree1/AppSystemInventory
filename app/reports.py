from flask import Blueprint, render_template, send_file, make_response
from flask_login import login_required
from inventory_system.db.models import Product, StockMovement
import io
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    return render_template('reports/index.html')

# --- Start of New Code ---
@reports_bp.route('/export/low-stock/csv')
@login_required
def export_low_stock_csv():
    products = Product.query.filter(Product.quantity <= Product.min_stock).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'SKU', 'Category', 'Quantity', 'Min Stock'])
    
    for p in products:
        writer.writerow([p.id, p.name, p.sku, p.category.name if p.category else '', p.quantity, p.min_stock])
        
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=low_stock_report.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@reports_bp.route('/export/low-stock/pdf')
@login_required
def export_low_stock_pdf():
    products = Product.query.filter(Product.quantity <= Product.min_stock).all()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Low Stock Report", styles['Title']))
    elements.append(Spacer(1, 12))
    
    data = [['Name', 'SKU', 'Qty', 'Min Stock']]
    for p in products:
        data.append([p.name, p.sku, str(p.quantity), str(p.min_stock)])
        
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.mistyrose),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='low_stock_report.pdf', mimetype='application/pdf')

@reports_bp.route('/export/movements/csv')
@login_required
def export_movements_csv():
    movements = StockMovement.query.order_by(StockMovement.timestamp.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Product', 'Type', 'Qty', 'User', 'Reason'])
    
    for m in movements:
        writer.writerow([m.timestamp.strftime('%Y-%m-%d %H:%M'), m.product.name, m.movement_type, m.quantity, m.user.username if m.user else 'Unknown', m.reason])
        
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=stock_movements.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@reports_bp.route('/export/movements/pdf')
@login_required
def export_movements_pdf():
    movements = StockMovement.query.order_by(StockMovement.timestamp.desc()).all()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Stock Movements Report", styles['Title']))
    elements.append(Spacer(1, 12))
    
    data = [['Date', 'Product', 'Type', 'Qty', 'Reason']]
    for m in movements:
        data.append([
            m.timestamp.strftime('%Y-%m-%d %H:%M'), 
            m.product.name[:20], 
            m.movement_type, 
            str(m.quantity),
            m.reason[:20]
        ])
        
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8), # Smaller font for more columns
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='stock_movements.pdf', mimetype='application/pdf')
# --- End of New Code ---

@reports_bp.route('/export/products/csv')
@login_required
def export_products_csv():
    products = Product.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'SKU', 'Category', 'Quantity', 'Price'])
    
    for p in products:
        writer.writerow([p.id, p.name, p.sku, p.category.name if p.category else '', p.quantity, p.sell_price])
        
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=products.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@reports_bp.route('/export/products/pdf')
@login_required
def export_products_pdf():
    products = Product.query.all()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Inventory Report", styles['Title']))
    
    data = [['Name', 'SKU', 'Qty', 'Price']]
    for p in products:
        data.append([p.name, p.sku, str(p.quantity), f"${p.sell_price}"])
        
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='inventory_report.pdf', mimetype='application/pdf')

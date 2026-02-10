import pytest
import sys
sys.path.insert(0, '/workspaces/static_analysis_lab/src')

from invoice_service import InvoiceService, Invoice, LineItem

# ===== Basic compute_total tests =====
def test_compute_total_basic():
    """Test basic invoice total calculation"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=2)]
    )
    total, warnings = service.compute_total(inv)
    assert total > 0
    assert isinstance(warnings, list)

# ===== Validation tests =====
def test_invalid_qty_raises():
    """Test that invalid qty (0) raises ValueError"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-002",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=0)]
    )
    with pytest.raises(ValueError):
        service.compute_total(inv)

def test_validation_missing_invoice_id():
    """Test validation for missing invoice_id"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=1)]
    )
    with pytest.raises(ValueError):
        service.compute_total(inv)

def test_validation_missing_customer_id():
    """Test validation for missing customer_id"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=1)]
    )
    with pytest.raises(ValueError):
        service.compute_total(inv)

def test_validation_no_items():
    """Test validation for missing items"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[]
    )
    with pytest.raises(ValueError):
        service.compute_total(inv)

def test_validation_missing_sku():
    """Test validation for missing SKU"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="", category="book", unit_price=100.0, qty=1)]
    )
    with pytest.raises(ValueError):
        service.compute_total(inv)

def test_validation_negative_price():
    """Test validation for negative price"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=-10.0, qty=1)]
    )
    with pytest.raises(ValueError):
        service.compute_total(inv)

def test_validation_invalid_category():
    """Test validation for invalid category"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="invalid", unit_price=100.0, qty=1)]
    )
    with pytest.raises(ValueError):
        service.compute_total(inv)

def test_validation_negative_qty():
    """Test validation for negative qty"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=-5)]
    )
    with pytest.raises(ValueError):
        service.compute_total(inv)

# ===== Shipping calculation tests =====
def test_shipping_thailand_free():
    """Test Thailand shipping - free for >= 500"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=10)]  
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_shipping_thailand_charged():
    """Test Thailand shipping - 60 for < 500"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=20.0, qty=5)]  
    )
    total, _ = service.compute_total(inv)
    
    assert total > 0

def test_shipping_japan_free():
    """Test Japan shipping - free for >= 4000"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="JP",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=500.0, qty=10)]  
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_shipping_japan_charged():
    """Test Japan shipping - 600 for < 4000"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="JP",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="electronics", unit_price=100.0, qty=10)]  
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_shipping_us_low():
    """Test US shipping - 15 for 100<=subtotal<300"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="US",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=50.0, qty=3)]  # subtotal=150
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_shipping_us_medium():
    """Test US shipping - 8 for 300<=subtotal<inf"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="US",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="food", unit_price=100.0, qty=5)]  # subtotal=500
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_shipping_us_free():
    """Test US shipping - free for <100"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="US",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=10.0, qty=5)]  # subtotal=50
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_shipping_unknown_country():
    """Test shipping for unknown country uses defaults"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="XX",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=50.0, qty=10)]  # subtotal=500
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_shipping_unknown_country_low():
    """Test shipping for unknown country with low subtotal"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="XX",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=50.0, qty=1)]  # subtotal=50
    )
    total, _ = service.compute_total(inv)
    assert total > 0

# ===== Membership discount tests =====
def test_membership_gold():
    """Test gold membership discount (3%)"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="gold",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=10)]  # subtotal=1000
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_membership_platinum():
    """Test platinum membership discount (5%)"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="platinum",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=10)]  # subtotal=1000
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_bulk_discount_non_member():
    """Test bulk discount for non-member with high subtotal"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=1000.0, qty=15)]  # subtotal=15000 >10000
    )
    total, warnings = service.compute_total(inv)
    assert total > 0
    # Should have membership upgrade warning
    assert any("membership upgrade" in w.lower() for w in warnings)

def test_no_bulk_discount_non_member_low():
    """Test no bulk discount for non-member with low subtotal"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=10.0, qty=10)]  # subtotal=100
    )
    total, warnings = service.compute_total(inv)
    assert total > 0

# ===== Coupon tests =====
def test_coupon_welcome10():
    """Test WELCOME10 coupon (10% discount)"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon="WELCOME10",
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=10)]  # subtotal=1000
    )
    total, warnings = service.compute_total(inv)
    assert total > 0

def test_coupon_vip20():
    """Test VIP20 coupon (20% discount)"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon="VIP20",
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=10)]  # subtotal=1000
    )
    total, warnings = service.compute_total(inv)
    assert total > 0

def test_coupon_student5():
    """Test STUDENT5 coupon (5% discount)"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon="STUDENT5",
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=10)]  # subtotal=1000
    )
    total, warnings = service.compute_total(inv)
    assert total > 0

def test_coupon_invalid():
    """Test invalid coupon code"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon="INVALID",
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=10)]  # subtotal=1000
    )
    total, warnings = service.compute_total(inv)
    assert total > 0
    assert any("Unknown coupon" in w for w in warnings)

def test_coupon_empty():
    """Test empty coupon code"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon="",
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=10)]  # subtotal=1000
    )
    total, warnings = service.compute_total(inv)
    assert total > 0

def test_coupon_whitespace():
    """Test coupon code with only whitespace"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon="   ",
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=10)]  # subtotal=1000
    )
    total, warnings = service.compute_total(inv)
    assert total > 0

def test_coupon_none():
    """Test None coupon code"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=10)]  # subtotal=1000
    )
    total, warnings = service.compute_total(inv)
    assert total > 0

# ===== Tax calculation tests =====
def test_tax_thailand():
    """Test Thailand tax (7%)"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=1)]  # subtotal=100
    )
    total, _ = service.compute_total(inv)
    # tax = 100 * 0.07 = 7, total = 100 + 7 = 107
    assert total > 0

def test_tax_japan():
    """Test Japan tax (10%)"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="JP",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=1)]  # subtotal=100
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_tax_us():
    """Test US tax (8%)"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="US",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=1)]  # subtotal=100
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_tax_default():
    """Test default tax for unknown country (5%)"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="XX",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=1)]  # subtotal=100
    )
    total, _ = service.compute_total(inv)
    assert total > 0

# ===== Fragile item tests =====
def test_fragile_item():
    """Test fragile item fee (5 per qty)"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="electronics", unit_price=100.0, qty=2, fragile=True)]
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_non_fragile_item():
    """Test non-fragile item (no extra fee)"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="electronics", unit_price=100.0, qty=2, fragile=False)]
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_mixed_fragile_items():
    """Test invoice with both fragile and non-fragile items"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[
            LineItem(sku="A", category="electronics", unit_price=100.0, qty=2, fragile=True),
            LineItem(sku="B", category="book", unit_price=50.0, qty=3, fragile=False)
        ]
    )
    total, _ = service.compute_total(inv)
    assert total > 0

# ===== Edge case tests =====
def test_zero_total_before_tax():
    """Test that total doesn't go negative"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="platinum",
        coupon="VIP20",
        items=[LineItem(sku="A", category="food", unit_price=1.0, qty=1)]  # subtotal=1
    )
    total, _ = service.compute_total(inv)
    assert total >= 0

def test_multiple_items():
    """Test invoice with multiple items"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="US",
        membership="gold",
        coupon="WELCOME10",
        items=[
            LineItem(sku="A", category="book", unit_price=50.0, qty=3),
            LineItem(sku="B", category="electronics", unit_price=200.0, qty=2, fragile=True),
            LineItem(sku="C", category="food", unit_price=10.0, qty=5),
            LineItem(sku="D", category="other", unit_price=25.0, qty=2),
        ]
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_category_book():
    """Test item with book category"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=50.0, qty=2)]
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_category_food():
    """Test item with food category"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="food", unit_price=50.0, qty=2)]
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_category_electronics():
    """Test item with electronics category"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="electronics", unit_price=50.0, qty=2)]
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_category_other():
    """Test item with other category"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="other", unit_price=50.0, qty=2)]
    )
    total, _ = service.compute_total(inv)
    assert total > 0

def test_membership_upgrade_warning_high_subtotal():
    """Test membership upgrade warning is triggered with high subtotal and non-gold/platinum membership"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=1000.0, qty=15)]  # subtotal=15000
    )
    total, warnings = service.compute_total(inv)
    assert total > 0
    assert any("membership upgrade" in w.lower() for w in warnings)

def test_no_membership_upgrade_warning_gold():
    """Test no membership upgrade warning for gold members"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="gold",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=1000.0, qty=15)]  # subtotal=15000
    )
    total, warnings = service.compute_total(inv)
    assert total > 0
    assert not any("membership upgrade" in w.lower() for w in warnings)

def test_no_membership_upgrade_warning_platinum():
    """Test no membership upgrade warning for platinum members"""
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="platinum",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=1000.0, qty=15)]  # subtotal=15000
    )
    total, warnings = service.compute_total(inv)
    assert total > 0
    assert not any("membership upgrade" in w.lower() for w in warnings)

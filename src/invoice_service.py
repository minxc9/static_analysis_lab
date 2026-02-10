from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

@dataclass
class LineItem:
    sku: str
    category: str
    unit_price: float
    qty: int
    fragile: bool = False

@dataclass
class Invoice:
    invoice_id: str
    customer_id: str
    country: str
    membership: str
    coupon: Optional[str]
    items: List[LineItem]

class InvoiceService:
    # Tax rates by country
    TAX_RATES: Dict[str, float] = {
        "TH": 0.07,
        "JP": 0.10,
        "US": 0.08
    }
    
    # Default tax rate for countries not in TAX_RATES
    DEFAULT_TAX_RATE: float = 0.05
    
    # Coupon discount rates
    COUPON_RATES: Dict[str, float] = {
        "WELCOME10": 0.10,
        "VIP20": 0.20,
        "STUDENT5": 0.05
    }
    
    # Membership discounts (percentage of subtotal)
    MEMBERSHIP_DISCOUNTS: Dict[str, float] = {
        "gold": 0.03,
        "platinum": 0.05
    }
    
    # Shipping rates: (min_subtotal, shipping_cost)
    SHIPPING_RATES: Dict[str, List[Tuple[float, float]]] = {
        "TH": [(500, 0), (float('inf'), 60)],
        "JP": [(4000, 0), (float('inf'), 600)],
        "US": [(100, 15), (300, 8), (float('inf'), 0)],
    }
    
    DEFAULT_SHIPPING_RATES: List[Tuple[float, float]] = [(200, 0), (float('inf'), 25)]

    def __init__(self) -> None:
        self._coupon_rate: Dict[str, float] = self.COUPON_RATES

    def _validate(self, inv: Invoice) -> List[str]:
        problems: List[str] = []
        if inv is None:
            problems.append("Invoice is missing")
            return problems
        if not inv.invoice_id:
            problems.append("Missing invoice_id")
        if not inv.customer_id:
            problems.append("Missing customer_id")
        if not inv.items:
            problems.append("Invoice must contain items")
        for it in inv.items:
            if not it.sku:
                problems.append("Item sku is missing")
            if it.qty <= 0:
                problems.append(f"Invalid qty for {it.sku}")
            if it.unit_price < 0:
                problems.append(f"Invalid price for {it.sku}")
            if it.category not in ("book", "food", "electronics", "other"):
                problems.append(f"Unknown category for {it.sku}")
        return problems

    def _calculate_shipping(self, country: str, subtotal: float) -> float:
        """Calculate shipping based on country and subtotal."""
        rates = self.SHIPPING_RATES.get(country)
        if rates is None:
            rates = self.DEFAULT_SHIPPING_RATES
        
        for threshold, cost in rates:  # +1
            if subtotal < threshold:  # +1 (nested)
                return cost
        return 0.0

    def _calculate_discount(self, membership: str, subtotal: float) -> float:
        """Calculate membership discount."""
        if membership in self.MEMBERSHIP_DISCOUNTS:  # +1
            return subtotal * self.MEMBERSHIP_DISCOUNTS[membership]
        
        # Apply bulk discount for non-members
        if subtotal > 3000:  # +1
            return 20
        return 0.0

    def _apply_coupon(self, code: str, subtotal: float) -> Tuple[float, Optional[str]]:
        """Apply coupon code and return discount and warning if applicable."""
        if not code or not code.strip():  # +1
            return 0.0, None
        
        code = code.strip()
        if code in self._coupon_rate:  # +1
            discount = subtotal * self._coupon_rate[code]
            return discount, None
        
        return 0.0, "Unknown coupon"

    def _calculate_tax(self, country: str, taxable_amount: float) -> float:
        """Calculate tax based on country."""
        rate = self.TAX_RATES.get(country, self.DEFAULT_TAX_RATE)
        return taxable_amount * rate

    def compute_total(self, inv: Invoice) -> Tuple[float, List[str]]:  # +1 (method def counts minimal)
        warnings: List[str] = []
        problems = self._validate(inv)
        if problems:  # +1
            raise ValueError("; ".join(problems))

        # Calculate base costs
        subtotal = 0.0
        fragile_fee = 0.0
        for it in inv.items:  # +1
            line = it.unit_price * it.qty
            subtotal += line
            if it.fragile:  # +1 (nested)
                fragile_fee += 5.0 * it.qty

        # Calculate shipping
        shipping = self._calculate_shipping(inv.country, subtotal)
        
        # Calculate discounts
        membership_discount = self._calculate_discount(inv.membership, subtotal)
        coupon_discount, coupon_warning = self._apply_coupon(inv.coupon, subtotal)
        
        if coupon_warning:  # +1
            warnings.append(coupon_warning)
        
        total_discount = membership_discount + coupon_discount
        
        # Calculate tax on discounted amount
        tax = self._calculate_tax(inv.country, subtotal - total_discount)
        
        # Calculate final total
        total = subtotal + shipping + fragile_fee + tax - total_discount
        if total < 0:  # +1
            total = 0.0
        
        # Check for membership upgrade opportunity
        if subtotal > 10000 and inv.membership not in ("gold", "platinum"):  # +1 && +1 (AND operator)
            warnings.append("Consider membership upgrade")
        
        return total, warnings

# from __future__ import unicode_literals
# import frappe
# import frappe.defaults
# from frappe import _, throw
# from frappe.utils import cint, cstr, flt, get_fullname
# from frappe.utils.nestedset import get_root_of
# from erpnext.selling.doctype.quotation.quotation import _make_sales_order
# from erpnext.e_commerce.shopping_cart.cart import _get_cart_quotation
# from erpnext.utilities.product import get_web_item_qty_in_stock

# @frappe.whitelist()
# def place_order(*args,**kwargs):
#     quotation = _get_cart_quotation()
#     cart_settings = frappe.db.get_value("E Commerce Settings", None,
# 		["company", "allow_items_not_in_stock"], as_dict=1)

#     sales_order = frappe.get_doc(_make_sales_order(quotation.name, ignore_permissions=True))
#     sales_order.payment_schedule = []

#     if not cint(cart_settings.allow_items_not_in_stock):
# 	    for item in sales_order.get("items"):
# 		    item.warehouse = frappe.db.get_value(
# 				"Website Item",
# 				{
# 					"item_code": item.item_code
# 				},
# 				"website_warehouse"
# 			)
# 			is_stock_item = frappe.db.get_value("Item", item.item_code, "is_stock_item")

# 		    if is_stock_item:
# 			    item_stock = get_web_item_qty_in_stock(item.item_code, "website_warehouse")
# 			    if not cint(item_stock.in_stock):
# 				    throw(_("{0} Not in Stock").format(item.item_code))
# 			    if item.qty > item_stock.stock_qty[0][0]:
# 				    throw(_("Only {0} in Stock for item {1}").format(item_stock.stock_qty[0][0], item.item_code))

#     sales_order.flags.ignore_permissions = True
#     sales_order.insert()
#     sales_order.submit()

#     if hasattr(frappe.local, "cookie_manager"):
# 	    frappe.local.cookie_manager.delete_cookie("cart_count")

#     return sales_order.name

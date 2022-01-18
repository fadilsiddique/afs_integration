from lzma import _OpenBinaryWritingMode
import frappe
import json
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from erpnext.accounts.doctype.payment_request.payment_request import create_payment_entry

@frappe.whitelist(allow_guest=True)

def webhook(**kwargs):
    data=json.loads(frappe.request.data)
    status=data.get('result')
    order_id=data.get('id')
    amount=data.get('amount')

    pay_req=frappe.get_doc('Payment Request',order_id)
    reference_doc_id=pay_req.get('reference_name')
    reference_doc=pay_req.get('reference_doctype')
    sales_order_doc=frappe.get_doc(reference_doc,reference_doc_id)
    total=sales_order_doc.get('total')

    

    if status=='SUCCESS':
       invoice= make_sales_invoice(source_name=reference_doc_id)
       invoice.submit()

       invoice_doc=frappe.get_doc('Sales Invoice',invoice.name)
       payment_entry=invoice_doc.create_payment_entry()
       return invoice

# def invoice_testing(source_name,test_id):
#     if test_id==1:
    
#         x=make_sales_invoice(source_name)
#         x.submit()

#         return x



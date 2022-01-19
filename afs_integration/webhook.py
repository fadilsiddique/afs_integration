from http.client import OK
from urllib import request
import frappe
import requests
import json
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice


@frappe.whitelist(allow_guest=True)

def webhook(**kwargs):
    head=frappe.request.headers['X-Notification-Secret']
    secret=frappe.get_single('Webhook Secret').secret
    print(head)

    if head==secret:

        data=json.loads(frappe.request.data)
        print(data)
        status=data.get('result')
        order_id=data.get('id')
        amount=data.get('amount')

        pay_req=frappe.get_doc('Payment Request',order_id)
        reference_doc_id=pay_req.get('reference_name')
        reference_doc=pay_req.get('reference_doctype')
        sales_order_doc=frappe.get_doc(reference_doc,reference_doc_id)
        total=sales_order_doc.get('total')

        

        if status=='SUCCESS':
            invoice= make_sales_invoice(source_name=reference_doc_id,ignore_permissions=True)
            invoice.submit()

        invoice_doc=frappe.get_doc('Sales Invoice',invoice.name)
        return invoice

# def invoice_testing(source_name,test_id):
#     if test_id==1:
    
#         x=make_sales_invoice(source_name)
#         x.submit()

#         return x



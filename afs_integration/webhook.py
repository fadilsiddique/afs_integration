from http.client import OK
from urllib import request, response
import frappe
import requests
import json
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
import os


@frappe.whitelist(allow_guest=True)

def webhook_data(*args,**kwargs):
    from dotenv import load_dotenv
    load_dotenv()
    head=frappe.request.headers['X-Notification-Secret']
    secret=os.environ.get('secret')
    if head==secret:
        data=json.loads(frappe.request.data)

        doc=frappe.new_doc('Webhook Capture')
        doc.webhook_response=str(data)
        print(doc.webhook_response)
        doc.insert(ignore_permissions=True)
        doc.save(ignore_permissions=True)
        print(doc)
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
            #invoice.submit()
            return invoice

# def invoice_testing(source_name,test_id):
#     if test_id==1:
    
#         x=make_sales_invoice(source_name)
#         x.submit()

#         return x



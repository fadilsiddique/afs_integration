from distutils.log import error
from email import header
from http import HTTPStatus
from http.client import OK
from urllib import request, response
from urllib.error import HTTPError
import frappe
import requests
import json
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
import os


@frappe.whitelist(allow_guest=True)
def webhookData():
    header=frappe.request.headers['x-notification-secret']
    # if frappe.request.headers['X-Notification-Secret']=='CA30951A5324FCCC66EFE9C4890E93A5':
        # from dotenv import load_dotenv
        # load_dotenv()
    
    # secret=os.environ.get('secret')
    if header=='CA30951A5324FCCC66EFE9C4890E93A5':
        data=json.loads(frappe.request.data)
        doc=frappe.new_doc('Webhook Capture')
        doc.webhook_response=str(data)
        doc.insert(ignore_permissions=True)
        doc.save(ignore_permissions=True)
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
            invoice= make_sales_invoice(source_name=reference_doc_id,ignore_permissions=True)
            invoice.submit()

            return invoice
        
    else:
        doc=frappe.new_doc('Webhook Capture')
        doc.webhook_response=str(header)
        doc.insert(ignore_permissions=True)
        doc.save(ignore_permissions=True)
        
        return doc
    




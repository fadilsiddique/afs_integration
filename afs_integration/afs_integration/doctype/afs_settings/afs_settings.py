# Copyright (c) 2021, Tridz Technologies and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import re
from requests.api import get

from requests.sessions import session
import frappe
import requests
import json
from frappe import _,request
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from frappe.model.mapper import make_mapped_doc
from frappe.model.document import Document
from frappe.utils import get_url, call_hook_method, cint, get_timestamp
from frappe.integrations.utils import (make_get_request, make_post_request, create_request_log,
	create_payment_gateway)
import os




class AfsSettings(Document):
	supported_currencies=["BHD","INR"]

	def after_insert(self):
		doc = frappe.new_doc("Payment Gateway")
		doc.gateway_settings = "Afs Settings"
		doc.gateway_controller = self.name
		doc.gateway = self.name
		doc.save(ignore_permissions=True)

	def validate(self):
		create_payment_gateway('Afs Test')
		call_hook_method('payment_gateway_enabled', gateway='Afs Test')

	def validate_transaction_currency(self, currency):
		if currency not in self.supported_currencies:
			frappe.throw(_("Please select another payment method. Afs does not support transactions in currency '{0}'").format(currency))

	def get_payment_url(self, **kwargs):
		'''Return payment url with several params'''
		# create unique order id by making it equal to the integration request
		integration_request = create_request_log(kwargs, "Host", "Afs Test")
		kwargs.update(dict(order_id=integration_request.name))
		# add payment gateway name
		kwargs.update({'gateway':self.name})

		return integration_request

@frappe.whitelist(allow_guest=True)

def get_payment_info(order_id,dt,dn):
	# storing sensitive values in .env files
	# from dotenv import load_dotenv
	# load_dotenv()
	
	if request.method=='POST':
		payment_request = frappe.get_doc('Payment Request',order_id)
		# url=os.environ.get("url")
		url="https://afs.gateway.mastercard.com/api/rest/version/61/merchant/TEST100078691/session/"
		payload={
			"apiOperation":"CREATE_CHECKOUT_SESSION",
			"interaction":{
				"operation":"PURCHASE",
				"returnUrl":"https://dev-zoom.tridz.in/"
			},
			"order":{
				"amount":payment_request.grand_total,
				"currency":payment_request.currency,
				"id":order_id,
				"reference":dn,
				"description":'order',
			},
			"transaction":{
				"reference":order_id
			}
		}

		payload=json.dumps(payload)
		print(payload)

		headers = {
					'Authorization': "Basic bWVyY2hhbnQuVEVTVDEwMDA3ODY5MTowMGJhN2RlMDVkOTI1ODQ5YjRlNzk2MTE4NTZmMDVkMg==",
					'Content-Type': 'text/plain'
					}
		response = requests.request("POST", url=url, headers=headers, data=payload)
		return response.json()


@frappe.whitelist(allow_guest=True)
def webhook():
	header=frappe.request.headers['x-notification-secret']
	print(header)
    # if frappe.request.headers['X-Notification-Secret']=='CA30951A5324FCCC66EFE9C4890E93A5':
        # from dotenv import load_dotenv
        # load_dotenv()
    
    # secret=os.environ.get('secret')
	if header=='CA30951A5324FCCC66EFE9C4890E93A5':
		data=json.loads(frappe.request.data)
		status=data.get('result')
		doc=frappe.new_doc('Webhook Capture')
		doc.webhook_response=str(data)
		doc.insert(ignore_permissions=True)
		doc.save(ignore_permissions=True)
		order_id=data['order'].get('id')
		pay_req=frappe.get_doc('Payment Request',order_id)
		reference_doc_id=pay_req.get('reference_name')
		if status=='SUCCESS':
			invoice= make_mapped_doc(method="erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",source_name=reference_doc_id)
			invoice_frappe_json=frappe.as_json(invoice)
			invoice_json=json.loads(invoice_frappe_json)
			invoice_json.pop('docstatus',None)
			invoice_json['doctype']="Sales Invoice"
			docs=frappe.get_doc(invoice_json)
			docs.save(ignore_permissions=True)
			docs.submit()
			
			# invoice_json=json.loads(invoice_frappe_json)
			# invoice_json.pop('__unsaved',None)	
			# invoice_json.pop('docstatus',None)
			# invoice_json['doctype']="Sales Invoice"
			# docs=frappe.get_doc(invoice_json)
			
        
	# else:
	#     doc=frappe.new_doc('Webhook Capture')
	#     doc.webhook_response=str(header)
	#     doc.insert(ignore_permissions=True)
	#     doc.save(ignore_permissions=True)
	
	#     return doc

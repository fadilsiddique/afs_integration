# Copyright (c) 2021, Tridz Technologies and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

from requests.sessions import session
import frappe
import requests
import json
from frappe import _,request
from frappe.model.document import Document
from frappe.utils import get_url, call_hook_method, cint, get_timestamp
from frappe.integrations.utils import (make_get_request, make_post_request, create_request_log,
	create_payment_gateway)	




class AfsSettings(Document):
	supported_currencies=["BHD","INR"]

	def after_insert(self):
		doc = frappe.new_doc("Payment Gateway")
		doc.gateway_settings = "Afs Settings"
		doc.gateway_controller = self.name
		doc.gateway = self.name
		doc.save(ignore_permissions=True)

	def validate(self):
		create_payment_gateway('Afs')
		call_hook_method('payment_gateway_enabled', gateway='Afs')

	def validate_transaction_currency(self, currency):
		if currency not in self.supported_currencies:
			frappe.throw(_("Please select another payment method. Paystack does not support transactions in currency '{0}'").format(currency))

	def get_payment_url(self, **kwargs):
		'''Return payment url with several params'''
		# create unique order id by making it equal to the integration request
		integration_request = create_request_log(kwargs, "Host", "Afs")
		kwargs.update(dict(order_id=integration_request.name))
		# add payment gateway name
		kwargs.update({'gateway':self.name})

		return integration_request

@frappe.whitelist()
def get_payment_info(order_id,dt,dn):

	if request.method=='POST':
		payment_request = frappe.get_doc('Payment Request',order_id)
		url="https://afs.gateway.mastercard.com/api/rest/version/61/merchant/TEST100078691/session/"
		payload={
			"apiOperation":"CREATE_CHECKOUT_SESSION",
			"interaction":{
				"operation":"PURCHASE",
				"returnUrl":"http://dev-zoom.tridz.in/"
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
					'Authorization': 'Basic bWVyY2hhbnQuVEVTVDEwMDA3ODY5MTowMGJhN2RlMDVkOTI1ODQ5YjRlNzk2MTE4NTZmMDVkMg==',
					'Content-Type': 'text/plain'
					}
		response = requests.request("POST", url=url, headers=headers, data=payload)
		print(response.json())
		return response.json()


# webhook
@frappe.whitelist(allow_guest=True)
def webhook(request):
	print(request)


	



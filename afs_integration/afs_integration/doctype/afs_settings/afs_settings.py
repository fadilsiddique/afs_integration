# Copyright (c) 2021, Tridz Technologies and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from requests.api import get

from requests.sessions import session
import frappe
import requests
import json
from frappe import _,request
from frappe.model.document import Document
from frappe.utils import get_url, call_hook_method, cint, get_timestamp
from frappe.integrations.utils import (make_get_request, make_post_request, create_request_log,
	create_payment_gateway)
import os




class AfsSettings(Document):
	supported_currencies=["BHD","INR"]

	def after_insert(self):
		doc = frappe.new_doc("Payment Gateway")2
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
	from dotenv import load_dotenv
	load_dotenv()

	if request.method=='POST':
		payment_request = frappe.get_doc('Payment Request',order_id)
		url=os.environ.get("url")
		payload={
			"apiOperation":"CREATE_CHECKOUT_SESSION",
			"interaction":{
				"operation":"PURCHASE",
				"returnUrl":os.environ.get("return_url")
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
					'Authorization': os.environ.get("auth"),
					'Content-Type': 'text/plain'
					}
		response = requests.request("POST", url=url, headers=headers, data=payload)
		print(response.json())
		return response.json()


# webhook
@frappe.whitelist(allow_guest=True)
def webhook(request):
	print(request)


	



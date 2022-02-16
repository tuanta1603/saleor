from typing import TYPE_CHECKING, Any

from ..base_plugin import BasePlugin
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

if TYPE_CHECKING:
    from ...staffevent.models import StaffEvent


class StaffEventPlugin(BasePlugin):
    PLUGIN_NAME = "StaffEvent Create"
    PLUGIN_ID = "staffevent_create"
    DEFAULT_ACTIVE = True
    PLUGIN_DESCRIPTION = (
        "staffevent create"
    )


    def staffevent_created(self, staffevent: "StaffEvent", previous_value: Any) -> Any:
        print("123123")
        if StaffEvent.send_email == True:
            message = Mail(
                from_email='anhtuan95.it@gmial.com',
                to_emails='tuantk115@gmial.com',
                subject='Sending with Twilio SendGrid is Fun',
                html_content='<strong>and easy to do anywhere, even with Python</strong>')
            try:
                sg = SendGridAPIClient(os.environ.get('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'))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e.message)
        return "123"    
        # checkout = Order.objects.get_by_checkout_token(
        #     order.checkout_token
        # )
        # if checkout.is_preorder:
        #     order.is_preorder = True
        #     order.requested_shipment_date = checkout.requested_shipment_date
        #     order.save()
        # return previous_value
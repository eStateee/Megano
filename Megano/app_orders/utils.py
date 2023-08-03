class OrderDetails:
    def __init__(self, request, fullname=None, phone=None, email=None):
        self.session = request.session
        self.order_details = self.session.get("order_details", {
            "fullname": fullname,
            "phone": phone,
            "email": email,
            "delivery_type": None,
            "delivery_price": 0,
            "city": None,
            "address": None,
            "payment_type": None,
            "step_1": False,
            "step_2": False,
            "step_3": False
        })

    def set_attribute(self, attr, value):
        if attr in self.order_details:
            self.order_details[attr] = value
            self.save()

    def step_completed(self, step):
        if step in self.order_details:
            self.order_details[step] = True
            self.save()

    def save(self):
        self.session.modified = True
        self.session["order_details"] = self.order_details

    def clear(self):
        if "order_details" in self.session:
            del self.session["order_details"]
            self.session.modified = True

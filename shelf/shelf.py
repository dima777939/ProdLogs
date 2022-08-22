from orders.models import Order
from django.conf import settings


class Shelf:
    def __init__(self, request):
        self.session = request.session
        shelf = self.session.get(settings.SHELF_SESSION_ID)
        if not shelf:
            shelf = self.session[settings.SHELF_SESSION_ID] = {}
        self.shelf = shelf

    def __iter__(self):
        order_ids = self.shelf.keys()
        orders = Order.objects.filter(id__in=order_ids)
        shelf = self.shelf.copy()
        for order in orders:
            shelf[str(order.id)]["order"] = order
        for item in shelf.values():
            yield item

    def __len__(self):
        return len(self.shelf)

    def add(self, order):
        order_id = str(order.id)
        if order_id not in self.shelf:
            self.shelf[order_id] = {
                "batch_number": str(order.batch_number),
                "time": self.get_time(order),
                "operation": str(order.operation),
                "cable": str(
                    f"{ order.plastic } { order.design } { order.purpose } { order.cores }"
                    f"x{ order.crosssection }"
                ),
                "footage": str(order.footage),
                "comment": "",
            }
        self.save()

    def get_time(self, order):
        new_time = 45 * order.cores * ((order.footage // 1000) * 0.1)
        clear_time = new_time % 15
        new_time = new_time - clear_time
        return int(new_time)

    def update_time(self, order, time, update_time):
        order_id = str(order.id)
        if update_time:
            self.shelf[order_id]["time"] = time
        self.save()

    def add_comment(self, order, comment):
        order_id = str(order.id)
        self.shelf[order_id]["comment"] = comment
        self.save()

    def get_total_time(self):
        time = sum([item["time"] for item in self.shelf.values()])
        full_time = [time // 60, time % 60]
        return f"{full_time[0]}ч. {full_time[1]} мин."

    def get_id(self):
        return [int(item) for item in self.shelf.keys()]

    def remove(self, order):
        order_id = str(order.id)
        if order_id in self.shelf:
            del self.shelf[order_id]
            self.save()

    def save(self):
        self.session.modified = True

    def get_link(self):
        return "gruboe-volochenie"

    def clear(self):
        del self.session[settings.SHELF_SESSION_ID]
        self.save()

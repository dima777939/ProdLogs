from .shelf import Shelf


def shelf(request):
    return {"shelf": Shelf(request)}

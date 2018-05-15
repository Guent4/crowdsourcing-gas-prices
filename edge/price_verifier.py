import numpy


def check_if_reasonable(new_price, historical):
    if len(historical) == 0:
        return True

    historic_prices = [float(h["price"]) if isinstance(h, dict) else float(h.price) for h in historical]

    if abs(new_price - numpy.mean(historic_prices)) < 0.1:
        return True

    return False

def process_commute_manifest(manifests, booking_fee):
    if not isinstance(manifests, list) or booking_fee < 0:
        raise ValueError("Invalid manifests list or booking fee")

    total_fare = 0.0
    rejected_rides = 0

    for manifest in manifests:
        if not manifest.get("route_active", False):
            continue

        route_type = manifest.get("route_type", "local")
        commuters = manifest.get("commuters", [])

        if route_type == "express":
            base_seat = 6.0
        elif route_type == "shuttle":
            base_seat = 4.0
        elif route_type == "local":
            base_seat = 2.5
        else:
            rejected_rides += 1
            continue

        manifest_fare = 0.0

        for commuter in commuters:
            zones = commuter.get("zones", 1)
            passenger_type = commuter.get("type", "regular")
            has_blacklisted_card = commuter.get("blacklisted", False)

            if zones <= 0:
                rejected_rides += 1
                continue

            if has_blacklisted_card:
                rejected_rides += 1
                if route_type == "express":
                    manifest_fare = 0.0
                    break
                manifest_fare += 0.0
            elif passenger_type == "student":
                manifest_fare += (base_seat + (zones * 0.5)) * 0.50
            elif passenger_type == "senior":
                manifest_fare += (base_seat + (zones * 0.5)) * 0.70
            else:
                manifest_fare += base_seat + (zones * 1.0)

        if manifest.get("priority_boarding", False):
            manifest_fare += booking_fee

        total_fare += manifest_fare

    if rejected_rides > 4:
        return {"total_fare": round(total_fare, 2), "status": "AUDIT_REJECTED"}
    if total_fare == 0.0:
        return {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}
    return {"total_fare": round(total_fare, 2), "status": "COMPLETED"}


def inspect_smartcard_turnstiles(turnstile_matrix):
    if not turnstile_matrix:
        return "NO_DATA"

    for device_readings in turnstile_matrix:
        tap_failure_streak = 0
        for failures in device_readings:
            if failures > 3:
                tap_failure_streak += 1
                if tap_failure_streak >= 2:
                    return "TURNSTILE_JAM"
            else:
                tap_failure_streak = 0
    return "OPERATIONAL"
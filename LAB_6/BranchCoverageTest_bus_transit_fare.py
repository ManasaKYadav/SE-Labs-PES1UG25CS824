"""Lab 6 - Branch coverage tests for bus_transit_fare.py.

Each test targets the True and False outcome of a decision in the module.
"""
import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


def ride(route_type="local", commuters=None, active=True, priority=False):
    return {"route_active": active, "route_type": route_type,
            "priority_boarding": priority, "commuters": commuters or []}


# ---- Input validation: `not isinstance(...) or booking_fee < 0` ----
@pytest.mark.parametrize("manifests, fee", [
    ("not a list", 1.0),   # isinstance False -> True branch
    (None, 1.0),
    ([], -0.01),           # fee < 0 -> True branch
])
def test_invalid_inputs_raise(manifests, fee):
    with pytest.raises(ValueError):
        process_commute_manifest(manifests, fee)


def test_valid_empty_list_zero_ridership():
    # validation False branch, for-loop never entered
    assert process_commute_manifest([], 0.0) == {
        "total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


# ---- route_active ----
def test_inactive_and_missing_route_active_are_skipped():
    manifests = [ride(active=False, commuters=[{"zones": 3}]),
                 {"route_type": "local", "commuters": [{"zones": 3}]}]
    assert process_commute_manifest(manifests, 5.0)["status"] == "ZERO_RIDERSHIP"


# ---- route_type if / elif / elif / else ----
@pytest.mark.parametrize("route_type, expected", [
    ("express", 7.0),   # 6.0 + 1
    ("shuttle", 5.0),   # 4.0 + 1
    ("local", 3.5),     # 2.5 + 1
])
def test_each_route_type_regular_fare(route_type, expected):
    result = process_commute_manifest(
        [ride(route_type, [{"zones": 1, "type": "regular"}])], 0.0)
    assert result == {"total_fare": expected, "status": "COMPLETED"}


def test_default_route_type_is_local_and_default_commuter_values():
    # route_type missing -> "local"; commuter defaults: zones=1, regular
    result = process_commute_manifest([{"route_active": True, "commuters": [{}]}], 0.0)
    assert result == {"total_fare": 3.5, "status": "COMPLETED"}


def test_unknown_route_type_rejected():
    result = process_commute_manifest(
        [ride("ferry", [{"zones": 1}]), ride("local", [{"zones": 1}])], 0.0)
    assert result == {"total_fare": 3.5, "status": "COMPLETED"}


def test_active_route_with_no_commuters():
    # inner for-loop not entered; priority False
    assert process_commute_manifest([ride("express")], 2.0)["status"] == "ZERO_RIDERSHIP"


# ---- zones <= 0 ----
@pytest.mark.parametrize("zones", [0, -2])
def test_non_positive_zones_rejected(zones):
    result = process_commute_manifest(
        [ride("local", [{"zones": zones}, {"zones": 2}])], 0.0)
    assert result == {"total_fare": 4.5, "status": "COMPLETED"}


# ---- blacklisted card: express (break) vs non-express ----
def test_blacklisted_on_express_wipes_manifest_and_breaks():
    commuters = [{"zones": 1}, {"zones": 1, "blacklisted": True}, {"zones": 5}]
    result = process_commute_manifest([ride("express", commuters)], 0.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


@pytest.mark.parametrize("route_type", ["local", "shuttle"])
def test_blacklisted_on_non_express_adds_nothing(route_type):
    commuters = [{"zones": 1, "blacklisted": True}, {"zones": 1, "type": "student"}]
    result = process_commute_manifest([ride(route_type, commuters)], 0.0)
    base = {"local": 2.5, "shuttle": 4.0}[route_type]
    assert result == {"total_fare": round((base + 0.5) * 0.5, 2), "status": "COMPLETED"}


# ---- passenger type student / senior / regular ----
@pytest.mark.parametrize("ptype, expected", [
    ("student", 2.0),    # (2.5 + 1.5) * 0.5
    ("senior", 2.8),     # (2.5 + 1.5) * 0.7
    ("regular", 5.5),    # 2.5 + 3
    ("tourist", 5.5),    # unknown type -> regular fare
])
def test_passenger_types(ptype, expected):
    result = process_commute_manifest([ride("local", [{"zones": 3, "type": ptype}])], 0.0)
    assert result == {"total_fare": expected, "status": "COMPLETED"}


# ---- priority_boarding ----
def test_priority_boarding_adds_booking_fee():
    result = process_commute_manifest(
        [ride("shuttle", [{"zones": 2, "type": "senior"}], priority=True)], 1.5)
    assert result == {"total_fare": 5.0, "status": "COMPLETED"}   # 3.5 + 1.5


def test_priority_boarding_only_fee_counts_as_completed():
    result = process_commute_manifest([ride("local", priority=True)], 2.0)
    assert result == {"total_fare": 2.0, "status": "COMPLETED"}


# ---- final status: rejected_rides > 4 ----
def test_exactly_four_rejections_not_audited():
    commuters = [{"zones": 0}] * 4 + [{"zones": 1}]
    assert process_commute_manifest([ride("local", commuters)], 0.0)["status"] == "COMPLETED"


def test_five_rejections_audit_rejected_keeps_fare():
    manifests = [ride("bogus"), ride("bogus"),
                 ride("local", [{"zones": 0}, {"zones": -1},
                                {"zones": 1, "blacklisted": True}, {"zones": 1}])]
    assert process_commute_manifest(manifests, 0.0) == {
        "total_fare": 3.5, "status": "AUDIT_REJECTED"}


# ---- inspect_smartcard_turnstiles ----
@pytest.mark.parametrize("matrix", [[], None])
def test_turnstiles_no_data(matrix):
    assert inspect_smartcard_turnstiles(matrix) == "NO_DATA"


@pytest.mark.parametrize("matrix, expected", [
    ([[4, 4]], "TURNSTILE_JAM"),               # two consecutive > 3
    ([[0, 1], [2, 9, 10]], "TURNSTILE_JAM"),   # jam on second device
    ([[3, 3, 3]], "OPERATIONAL"),              # boundary: 3 is not a failure
    ([[4, 1, 5, 0, 6]], "OPERATIONAL"),        # streak resets each time
    ([[4], [4]], "OPERATIONAL"),               # streak resets per device
    ([[]], "OPERATIONAL"),                     # device with no readings
])
def test_turnstile_states(matrix, expected):
    assert inspect_smartcard_turnstiles(matrix) == expected

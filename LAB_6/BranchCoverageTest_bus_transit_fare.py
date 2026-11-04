import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


def ride(route_type="local", commuters=None, active=True, priority=False):
    return {"route_active": active, "route_type": route_type,
            "priority_boarding": priority, "commuters": commuters or []}


# Input validation: not a list OR booking_fee < 0
@pytest.mark.parametrize("manifests, fee", [
    ("not a list", 1.0),
    (None, 1.0),
    ([], -0.01),
])
def test_invalid_inputs_raise(manifests, fee):
    with pytest.raises(ValueError):
        process_commute_manifest(manifests, fee)


def test_valid_empty_list_zero_ridership():
    assert process_commute_manifest([], 0.0) == {
        "total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


# route_active True / False / missing
def test_inactive_and_missing_route_active_are_skipped():
    manifests = [ride(active=False, commuters=[{"zones": 3}]),
                 {"route_type": "local", "commuters": [{"zones": 3}]}]
    assert process_commute_manifest(manifests, 5.0)["status"] == "ZERO_RIDERSHIP"


# route_type: express / shuttle / local / unknown
@pytest.mark.parametrize("route_type, expected", [
    ("express", 7.0),
    ("shuttle", 5.0),
    ("local", 3.5),
])
def test_each_route_type_regular_fare(route_type, expected):
    result = process_commute_manifest(
        [ride(route_type, [{"zones": 1, "type": "regular"}])], 0.0)
    assert result == {"total_fare": expected, "status": "COMPLETED"}


def test_default_route_type_and_default_commuter_values():
    result = process_commute_manifest([{"route_active": True, "commuters": [{}]}], 0.0)
    assert result == {"total_fare": 3.5, "status": "COMPLETED"}


def test_unknown_route_type_rejected():
    result = process_commute_manifest(
        [ride("ferry", [{"zones": 1}]), ride("local", [{"zones": 1}])], 0.0)
    assert result == {"total_fare": 3.5, "status": "COMPLETED"}


def test_active_route_with_no_commuters():
    assert process_commute_manifest([ride("express")], 2.0)["status"] == "ZERO_RIDERSHIP"


# zones <= 0 True / False
@pytest.mark.parametrize("zones", [0, -2])
def test_non_positive_zones_rejected(zones):
    result = process_commute_manifest(
        [ride("local", [{"zones": zones}, {"zones": 2}])], 0.0)
    assert result == {"total_fare": 4.5, "status": "COMPLETED"}


# blacklisted: express (break) vs non-express
def test_blacklisted_on_express_wipes_manifest_and_breaks():
    commuters = [{"zones": 1}, {"zones": 1, "blacklisted": True}, {"zones": 5}]
    result = process_commute_manifest([ride("express", commuters)], 0.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


@pytest.mark.parametrize("route_type, expected", [
    ("local", 1.5),     # (2.5 + 0.5) * 0.5
    ("shuttle", 2.25),  # (4.0 + 0.5) * 0.5
])
def test_blacklisted_on_non_express_adds_nothing(route_type, expected):
    commuters = [{"zones": 1, "blacklisted": True}, {"zones": 1, "type": "student"}]
    result = process_commute_manifest([ride(route_type, commuters)], 0.0)
    assert result == {"total_fare": expected, "status": "COMPLETED"}


# passenger type: student / senior / regular / unknown
@pytest.mark.parametrize("ptype, expected", [
    ("student", 2.0),
    ("senior", 2.8),
    ("regular", 5.5),
    ("tourist", 5.5),
])
def test_passenger_types(ptype, expected):
    result = process_commute_manifest([ride("local", [{"zones": 3, "type": ptype}])], 0.0)
    assert result == {"total_fare": expected, "status": "COMPLETED"}


# priority_boarding True / False
def test_priority_boarding_adds_booking_fee():
    result = process_commute_manifest(
        [ride("shuttle", [{"zones": 2, "type": "senior"}], priority=True)], 1.5)
    assert result == {"total_fare": 5.0, "status": "COMPLETED"}


def test_priority_boarding_only_fee_counts_as_completed():
    result = process_commute_manifest([ride("local", priority=True)], 2.0)
    assert result == {"total_fare": 2.0, "status": "COMPLETED"}


# rejected_rides > 4 True / False
def test_exactly_four_rejections_not_audited():
    commuters = [{"zones": 0}] * 4 + [{"zones": 1}]
    assert process_commute_manifest([ride("local", commuters)], 0.0)["status"] == "COMPLETED"


def test_five_rejections_audit_rejected_keeps_fare():
    manifests = [ride("bogus"), ride("bogus"),
                 ride("local", [{"zones": 0}, {"zones": -1},
                                {"zones": 1, "blacklisted": True}, {"zones": 1}])]
    assert process_commute_manifest(manifests, 0.0) == {
        "total_fare": 3.5, "status": "AUDIT_REJECTED"}


# inspect_smartcard_turnstiles
@pytest.mark.parametrize("matrix", [[], None])
def test_turnstiles_no_data(matrix):
    assert inspect_smartcard_turnstiles(matrix) == "NO_DATA"


@pytest.mark.parametrize("matrix, expected", [
    ([[4, 4]], "TURNSTILE_JAM"),
    ([[0, 1], [2, 9, 10]], "TURNSTILE_JAM"),
    ([[3, 3, 3]], "OPERATIONAL"),
    ([[4, 1, 5, 0, 6]], "OPERATIONAL"),
    ([[4], [4]], "OPERATIONAL"),
    ([[]], "OPERATIONAL"),
])
def test_turnstile_states(matrix, expected):
    assert inspect_smartcard_turnstiles(matrix) == expected
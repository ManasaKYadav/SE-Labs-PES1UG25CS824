"""Lab 6 - Code (line) coverage tests for bus_transit_fare.py."""
import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


def test_single_regular_local_ride():
    manifests = [{
        "route_active": True,
        "route_type": "local",
        "priority_boarding": False,
        "commuters": [{"zones": 2, "type": "regular", "blacklisted": False}],
    }]
    result = process_commute_manifest(manifests, 2.0)
    assert result == {"total_fare": 4.5, "status": "COMPLETED"}


def test_invalid_input_raises():
    with pytest.raises(ValueError):
        process_commute_manifest("not a list", 1.0)
    with pytest.raises(ValueError):
        process_commute_manifest([], -1.0)


def test_inactive_route_gives_zero_ridership():
    manifests = [{"route_active": False, "route_type": "local",
                  "commuters": [{"zones": 2}]}]
    assert process_commute_manifest(manifests, 1.0) == {
        "total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_all_route_types_and_passenger_types():
    manifests = [
        {"route_active": True, "route_type": "express",
         "commuters": [{"zones": 2, "type": "student"}]},          # (6+1)*0.5 = 3.5
        {"route_active": True, "route_type": "shuttle",
         "priority_boarding": True,
         "commuters": [{"zones": 2, "type": "senior"}]},           # (4+1)*0.7 = 3.5 + 1.5
        {"route_active": True, "route_type": "unknown",
         "commuters": [{"zones": 1}]},                             # rejected
    ]
    result = process_commute_manifest(manifests, 1.5)
    assert result == {"total_fare": 8.5, "status": "COMPLETED"}


def test_zero_zones_and_blacklisted_cards():
    manifests = [
        {"route_active": True, "route_type": "local",
         "commuters": [{"zones": 0},                               # rejected
                       {"zones": 1, "blacklisted": True},          # rejected, +0
                       {"zones": 1, "type": "regular"}]},          # 2.5 + 1 = 3.5
        {"route_active": True, "route_type": "express",
         "commuters": [{"zones": 1, "type": "regular"},
                       {"zones": 1, "blacklisted": True}]},        # express -> 0
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 3.5, "status": "COMPLETED"}


def test_audit_rejected_when_more_than_four_rejections():
    manifests = [{"route_active": True, "route_type": "local",
                  "commuters": [{"zones": 0}] * 5}]
    assert process_commute_manifest(manifests, 0.0) == {
        "total_fare": 0.0, "status": "AUDIT_REJECTED"}


def test_turnstiles_no_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_turnstiles_jam():
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"


def test_turnstiles_operational():
    assert inspect_smartcard_turnstiles([[1, 4, 2, 4]]) == "OPERATIONAL"

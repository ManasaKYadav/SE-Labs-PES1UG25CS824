import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


def test_single_regular_local_ride():
    manifests = [{"route_active": True, "route_type": "local",
                  "priority_boarding": False,
                  "commuters": [{"zones": 2, "type": "regular", "blacklisted": False}]}]
    result = process_commute_manifest(manifests, 2.0)
    assert result["total_fare"] == 4.5
    assert result["status"] == "COMPLETED"


def test_invalid_input():                       # line 3
    with pytest.raises(ValueError):
        process_commute_manifest("abc", 1.0)
    with pytest.raises(ValueError):
        process_commute_manifest([], -1.0)


def test_inactive_route():                      # lines 10, 57
    manifests = [{"route_active": False}]
    result = process_commute_manifest(manifests, 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


def test_route_types():                         # lines 16, 18, 22-23
    manifests = [
        {"route_active": True, "route_type": "express", "commuters": [{"zones": 1}]},
        {"route_active": True, "route_type": "shuttle", "commuters": [{"zones": 1}]},
        {"route_active": True, "route_type": "ferry", "commuters": [{"zones": 1}]},
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 12.0         # 7.0 + 5.0
    assert result["status"] == "COMPLETED"


def test_zero_zones():                          # lines 33-34
    manifests = [{"route_active": True, "route_type": "local",
                  "commuters": [{"zones": 0}, {"zones": 1}]}]
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 3.5
    assert result["status"] == "COMPLETED"


def test_blacklisted_local():                   # lines 37-38, 41
    manifests = [{"route_active": True, "route_type": "local",
                  "commuters": [{"zones": 1, "blacklisted": True}, {"zones": 1}]}]
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 3.5
    assert result["status"] == "COMPLETED"


def test_blacklisted_express():                 # lines 37-40
    manifests = [{"route_active": True, "route_type": "express",
                  "commuters": [{"zones": 1}, {"zones": 1, "blacklisted": True}]}]
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 0.0
    assert result["status"] == "ZERO_RIDERSHIP"


def test_student_and_senior():                  # lines 43, 45
    manifests = [{"route_active": True, "route_type": "local",
                  "commuters": [{"zones": 1, "type": "student"},
                                {"zones": 1, "type": "senior"}]}]
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 3.6          # 1.5 + 2.1
    assert result["status"] == "COMPLETED"


def test_priority_boarding():                   # line 50
    manifests = [{"route_active": True, "route_type": "local",
                  "priority_boarding": True,
                  "commuters": [{"zones": 1}]}]
    result = process_commute_manifest(manifests, 2.0)
    assert result["total_fare"] == 5.5          # 3.5 + 2.0
    assert result["status"] == "COMPLETED"


def test_audit_rejected():                      # line 55
    manifests = [{"route_active": True, "route_type": "local",
                  "commuters": [{"zones": 0}] * 5}]
    result = process_commute_manifest(manifests, 0.0)
    assert result["status"] == "AUDIT_REJECTED"


def test_turnstiles():                          # lines 62-74
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"
    assert inspect_smartcard_turnstiles([[1, 4, 2]]) == "OPERATIONAL"
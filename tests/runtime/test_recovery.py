import hashlib
import concurrent.futures

import pytest

from agent_bazaar.errors import ProtocolError
from agent_bazaar.recovery import Recovery
from agent_bazaar.storage import Ledger


def ref(name):
    return {"id": name, "digest": "sha256:" + hashlib.sha256(name.encode()).hexdigest()}


ACCEPTED = ref("accepted")
CANDIDATE = ref("candidate")


def descriptor(principal, duration=100):
    return {
        "principal_id": principal,
        "duration_ms": duration,
        **{
            field: ref(principal + ":" + field)
            for field in (
                "principal_policy_ref",
                "notice_target_ref",
                "notice_profile_ref",
                "refusal_authority_ref",
                "refusal_mechanism_ref",
            )
        },
    }


def create(path=":memory:", principals=("alice", "bob")):
    ledger = Ledger(path)
    recovery = Recovery(ledger)
    recovery.register(
        ACCEPTED,
        candidate_ref=CANDIDATE,
        finalized_at_ms=1000,
        principal_ids=principals,
        descriptors=[descriptor(p) for p in dict.fromkeys(principals)],
    )
    return ledger, recovery


def notice(recovery, principal="alice", at=1000, order=1, name=None):
    d = descriptor(principal)
    evidence = {
        "evidence_ref": ref(name or f"notice:{principal}:{order}"),
        "principal_id": principal,
        "accepted_offer_ref": ACCEPTED,
        "candidate_ref": CANDIDATE,
        "review_duration_ms": 100,
        "verified_at_ms": at,
        "authority_order": order,
        **{
            f: d[f]
            for f in (
                "notice_target_ref",
                "notice_profile_ref",
                "refusal_mechanism_ref",
            )
        },
    }
    return recovery.notice(ACCEPTED, prevalidated_notice=evidence)


def health(
    recovery, principal="alice", start=1000, end=1101, state="usable", **overrides
):
    evidence = {
        "evidence_ref": ref(f"health:{principal}:{start}:{end}:{state}"),
        "principal_id": principal,
        "accepted_offer_ref": ACCEPTED,
        "interval_start_ms": start,
        "interval_end_ms": end,
        "state": state,
        "service_evidence_refs": [ref("service")],
        "monotonic_elapsed_ms": end - start,
        "continuity_evidence_ref": ref("clock-continuity"),
    }
    evidence.update(overrides)
    return recovery.health(ACCEPTED, prevalidated_health=evidence)


def observe(recovery, now=1101, uncertainty=0, **overrides):
    kwargs = dict(
        now_ms=now,
        uncertainty_ms=uncertainty,
        clock_evidence_ref=ref("clock"),
        authority_evidence_refs=[ref("authority")],
    )
    kwargs.update(overrides)
    return recovery.observe(ACCEPTED, **kwargs)


def admit(recovery, principal="alice", operation="refuse", lower=1100, upper=None):
    key = ("scope", "control:" + principal, operation)
    return recovery.admit_refusal(
        ACCEPTED,
        principal_id=principal,
        operation_key=key,
        request_digest=ref(operation)["digest"],
        peer_agent_id=key[1],
        admitted_lower_ms=lower,
        admitted_upper_ms=lower if upper is None else upper,
    )


def resolve(recovery, principal="alice", operation="refuse"):
    return recovery.resolve_refusal(
        ACCEPTED,
        operation_key=("scope", "control:" + principal, operation),
        prevalidated_refusal={
            "evidence_ref": ref("valid:" + operation),
            "principal_id": principal,
            "accepted_offer_ref": ACCEPTED,
            "refusal_authority_ref": descriptor(principal)["refusal_authority_ref"],
            "authority_order": 5,
        },
    )


def test_shared_principal_one_window_and_positive_exact_descriptors():
    ledger, recovery = create(principals=("alice", "alice"))
    notice(recovery)
    health(recovery)
    status = observe(recovery)
    assert status["status"] == "refusal_windows_closed"
    assert len(status["principals"]) == 1
    for descriptors in (
        [descriptor("alice"), descriptor("alice")],
        [descriptor("alice", 0)],
        [descriptor("bob")],
        [],
    ):
        with pytest.raises(ProtocolError):
            recovery.register(
                ref("bad"),
                candidate_ref=CANDIDATE,
                finalized_at_ms=1000,
                principal_ids=["alice", "alice"],
                descriptors=descriptors,
            )
    ledger.close()


def test_no_notice_never_fabricates_deadline_and_duplicates_keep_first():
    ledger, recovery = create()
    first = notice(recovery)
    later = notice(recovery, at=1050, order=2)
    assert first == later
    assert notice(recovery) == first
    health(recovery, end=2000)
    status = observe(recovery, now=2000)
    assert status["status"] == "pending_refusal_windows"
    bob = next(p for p in status["principals"] if p["principal_id"] == "bob")
    assert bob["state"] == "notice_pending"
    assert "effective_deadline_ms" not in bob
    assert first["initial_deadline_ms"] == 1100
    ledger.close()


def test_deadline_equality_is_open_and_admission_uncertainty_preserves_refusal():
    ledger, recovery = create(principals=("alice",))
    notice(recovery)
    health(recovery, end=1200)
    assert observe(recovery, now=1100)["status"] == "pending_refusal_windows"
    assert (
        observe(recovery, now=1101, uncertainty=1)["status"]
        == "pending_refusal_windows"
    )
    admitted = admit(recovery, lower=1100, upper=1110)
    assert admitted["state"] == "pending"
    assert observe(recovery, now=1150)["status"] == "unresolved"
    assert resolve(recovery)["outcome"] == "refused"
    assert observe(recovery, now=1200)["status"] == "refused"
    ledger.close()


def test_pending_admission_and_refusal_survive_restart_and_new_notice(tmp_path):
    path = tmp_path / "recovery.db"
    ledger, recovery = create(path, principals=("alice",))
    notice(recovery)
    health(recovery, end=2000)
    original = admit(recovery)
    ledger.close()
    ledger = Ledger(path)
    recovery = Recovery(ledger)
    assert admit(recovery, lower=1500) == original
    assert observe(recovery, now=1500)["status"] == "unresolved"
    resolve(recovery)
    refused = observe(recovery, now=1501)
    ledger.close()
    ledger = Ledger(path)
    recovery = Recovery(ledger)
    notice(recovery, at=1600, order=2)
    assert (
        observe(recovery, now=1800, uncertainty=None, authority_evidence_refs=[])[
            "status"
        ]
        == "refused"
    )
    assert recovery.history(ACCEPTED)[1] == refused
    with pytest.raises(ProtocolError):
        recovery.reject_refusal(
            ACCEPTED,
            operation_key=("scope", "control:alice", "refuse"),
            reason="withdrawn",
            evidence_ref=ref("withdraw"),
        )
    ledger.close()


def test_refusal_without_notice_and_wrong_target_cannot_erase_right():
    ledger, recovery = create()
    admit(recovery, lower=1000)
    assert resolve(recovery)["outcome"] == "refused"
    assert observe(recovery, now=1000)["status"] == "refused"
    wrong = dict(ACCEPTED, digest=ref("other")["digest"])
    with pytest.raises(ProtocolError):
        recovery.observe(
            wrong,
            now_ms=1000,
            uncertainty_ms=0,
            clock_evidence_ref=ref("clock"),
            authority_evidence_refs=[ref("authority")],
        )
    ledger.close()


def test_union_outages_and_unknown_continuity_never_earn_credit(tmp_path):
    path = tmp_path / "recovery.db"
    ledger, recovery = create(path, principals=("alice",))
    notice(recovery)
    health(recovery, start=1000, end=1040)
    health(recovery, start=1040, end=1080, state="unusable")
    health(recovery, start=1060, end=1100, state="unusable")
    ledger.close()
    ledger = Ledger(path)
    recovery = Recovery(ledger)
    # A service-success claim after restart cannot substantiate the missing
    # monotonic continuity; its interval remains uncredited.
    result = health(recovery, start=1100, end=1120, continuity_evidence_ref=None)
    assert result["state"] == "unknown"
    health(recovery, start=1120, end=1181)
    status = observe(recovery, now=1181)
    assert status["status"] == "refusal_windows_closed"
    principal = status["principals"][0]
    assert principal["nonusable_ms"] == 80
    assert principal["credited_usable_ms"] == 101
    assert principal["effective_deadline_ms"] == 1180
    ledger.close()


def test_gap_conflict_or_clock_fault_blocks_closure():
    ledger, recovery = create(principals=("alice",))
    notice(recovery)
    health(recovery, start=1000, end=1030)
    health(recovery, start=1040, end=1200)
    assert observe(recovery, now=1150)["status"] == "unresolved"
    health(recovery, start=1030, end=1040, state="unknown")
    assert observe(recovery, now=1151, uncertainty=1001)["status"] == "unresolved"
    assert (
        observe(recovery, now=1152, authority_evidence_refs=[])["status"]
        == "unresolved"
    )
    assert observe(recovery, now=1153)["status"] == "refusal_windows_closed"
    health(recovery, start=1050, end=1080, state="unusable")
    assert observe(recovery, now=1154)["status"] == "unresolved"
    ledger.close()


def test_late_refusal_is_terminal_and_changed_operation_conflicts():
    ledger, recovery = create(principals=("alice",))
    notice(recovery)
    health(recovery, end=1300)
    admit(recovery, lower=1101)
    result = resolve(recovery)
    assert result["outcome"] == "late"
    assert observe(recovery, now=1200)["status"] == "refusal_windows_closed"
    with pytest.raises(ProtocolError):
        recovery.admit_refusal(
            ACCEPTED,
            principal_id="alice",
            operation_key=("scope", "control:alice", "refuse"),
            request_digest=ref("changed")["digest"],
            peer_agent_id="control:alice",
            admitted_lower_ms=1000,
            admitted_upper_ms=1000,
        )
    assert resolve(recovery) == result
    ledger.close()


def test_pending_late_ingress_does_not_erase_proven_closure():
    ledger, recovery = create(principals=("alice",))
    notice(recovery)
    health(recovery, end=1300)
    admit(recovery, lower=1150)
    assert observe(recovery, now=1200)["status"] == "refusal_windows_closed"
    ledger.close()


def test_snapshot_history_is_copy_isolated_and_monotonic():
    ledger, recovery = create(principals=("alice",))
    first = observe(recovery, now=1000)
    second = observe(recovery, now=1001)
    assert first["revision"] == 1
    assert second["revision"] == 2
    first["status"] = "refused"
    assert recovery.history(ACCEPTED)[0]["status"] == "pending_refusal_windows"
    with pytest.raises(ProtocolError):
        observe(recovery, now=999)
    ledger.close()


def test_notice_rejects_wrong_descriptor_and_nonmonotonic_authority_order():
    ledger, recovery = create(principals=("alice",))
    notice(recovery, at=1000, order=2)
    with pytest.raises(ProtocolError, match="lineage_conflict"):
        notice(recovery, at=1050, order=1)
    wrong = {
        "evidence_ref": ref("wrong-notice"),
        "principal_id": "alice",
        "accepted_offer_ref": ACCEPTED,
        "candidate_ref": CANDIDATE,
        "review_duration_ms": 100,
        "verified_at_ms": 1000,
        "authority_order": 3,
        "notice_target_ref": ref("someone-elses-inbox"),
        "notice_profile_ref": descriptor("alice")["notice_profile_ref"],
        "refusal_mechanism_ref": descriptor("alice")["refusal_mechanism_ref"],
    }
    with pytest.raises(ProtocolError, match="identity_mismatch"):
        recovery.notice(ACCEPTED, prevalidated_notice=wrong)
    assert observe(recovery, now=1000)["principals"][0]["notice_ref"] == ref(
        "notice:alice:2"
    )
    ledger.close()


def test_closure_racing_pending_verification_never_skips_admission(tmp_path):
    path = tmp_path / "recovery.db"
    ledger, recovery = create(path, principals=("alice",))
    notice(recovery)
    health(recovery, end=1300)
    admit(recovery)
    other_ledger = Ledger(path)
    other = Recovery(other_ledger)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        snapshot_future = pool.submit(observe, recovery, 1200)
        refusal_future = pool.submit(resolve, other)
        assert snapshot_future.result()["status"] in ("unresolved", "refused")
        assert refusal_future.result()["outcome"] == "refused"
    assert observe(recovery, now=1201)["status"] == "refused"
    ledger.close()
    other_ledger.close()


def test_rejected_pending_admission_preserves_history_then_allows_closure():
    ledger, recovery = create(principals=("alice",))
    notice(recovery)
    health(recovery, end=1300)
    admit(recovery)
    assert observe(recovery, now=1200)["status"] == "unresolved"
    outcome = recovery.reject_refusal(
        ACCEPTED,
        operation_key=("scope", "control:alice", "refuse"),
        reason="authority_absent",
        evidence_ref=ref("rejection-evidence"),
    )
    assert outcome["state"] == "rejected"
    assert observe(recovery, now=1201)["status"] == "refusal_windows_closed"
    assert recovery.history(ACCEPTED)[0]["status"] == "unresolved"
    with pytest.raises(ProtocolError, match="operation_conflict"):
        resolve(recovery)
    ledger.close()

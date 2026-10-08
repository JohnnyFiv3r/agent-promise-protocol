"""Validate specification fixtures; does not execute an agent or a native payment flow.
Requires Python 3 and jsonschema. Run: python3 checks/validate.py
"""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import re
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((ROOT / path).read_text())
def digest(value):
    # JCS-equivalent only for these ASCII, small-integer fixtures; not a general JCS implementation.
    return 'sha256:' + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

schema = read('schemas/contract.schema.json')
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, format_checker=FormatChecker())
fixtures = {p.name: json.loads(p.read_text()) for p in (ROOT / 'examples').glob('*.json')}
records = {name: item for name, item in fixtures.items() if item.get('kind') in {'publication_contract','intent','reception_permit','offer','agreement_terms','promise_issued','external_binding','delivery'} and item.get('profile') == 'abp/0.1-draft'}
for item in records.values():
    validator.validate(item)

def check_ref(reference, target):
    assert reference['id'] == target['id']
    assert reference['digest'] == digest(target)

publications = [fixtures[p + '-publication.json'] for p in ['buyer', 'provider']]
for party, publication in zip(['buyer','provider'], publications):
    check_ref(fixtures[party+'-intent.json']['body']['publication_contract_ref'], publication)
    consent = publication['body']['consent']
    check_ref(consent['discovery']['redistribution_policy_ref'], fixtures['redistribution-policy.json'])
    check_ref(consent['contact']['admission_policy_ref'], fixtures['admission-policy.json'])
    assert consent['contact']['admission_profile'] == fixtures['admission-policy.json']['profile']

assert fixtures['reception-permit.json']['body']['intent_digest'] == digest(fixtures['buyer-intent.json'])
terms = fixtures['research-terms.json']['body']
performance = fixtures['research-performance-terms.json']
assert terms['performance_terms'] == performance
assert performance['terms']['acceptance']['rubric_digest'] == digest(fixtures['research-rubric.json'])
assert terms['offer_digests'] == [digest(fixtures['buyer-offer-v2.json']), digest(fixtures['provider-offer-v2.json'])]

def eligible_selection(selection, pubs):
    return all(any(route['route_id'] == selection['route_id'] and digest(route) == selection['route_digest'] for route in pub['body']['eligible_commercial_routes']) for pub in pubs)
assert eligible_selection(terms['commercial_route_selection'], publications)
for record in [terms] + [fixtures[name]['body'] for name in ['buyer-offer.json','provider-offer.json','buyer-offer-v2.json','provider-offer-v2.json']]:
    for ref, pub in zip(record['publication_contract_refs'], publications):
        check_ref(ref, pub)
    assert len(record['publication_contract_refs']) == len(publications)
    assert record['commercial_route_selection'] == terms['commercial_route_selection']
    assert record['settlement'] == terms['settlement']
    assert record['offering'] == terms['offering']
    check_ref(record['offering']['specification_ref'], fixtures['research-service-spec.json'])

for party in ['buyer','provider']:
    first, second = [fixtures[f'{party}-offer{suffix}.json'] for suffix in ['', '-v2']]
    assert second['body']['previous_offer_digest'] == digest(first)
    assert second['body']['offer_sequence'] == first['body']['offer_sequence'] + 1
    assert second['body']['valid_until'] == first['body']['valid_until']
    for offer in [first, second]:
        assert offer['body']['performance_terms_ref']['digest'] == digest(performance)
        assert all(p['promiser_agent_id'] == offer['issuer_agent_id'] == p['performer_agent_id'] for p in offer['body']['own_promise_proposals'])
    for promise in second['body']['own_promise_proposals']:
        assert promise in terms['promises']
assert fixtures['buyer-offer.json']['body']['based_on_peer_offer_digest'] == digest(fixtures['provider-offer.json'])
assert fixtures['provider-offer-v2.json']['body']['based_on_peer_offer_digest'] == digest(fixtures['buyer-offer.json'])
assert fixtures['buyer-offer-v2.json']['body']['based_on_peer_offer_digest'] == digest(fixtures['provider-offer-v2.json'])
for promise in fixtures['buyer-offer-v2.json']['body']['requested_counterpromises']:
    assert promise in fixtures['provider-offer-v2.json']['body']['own_promise_proposals']

negative = []
def reject(label, source, mutate):
    value = deepcopy(source)
    mutate(value)
    assert not validator.is_valid(value), label
    negative.append(label)
reject('intent is not execution authority', fixtures['buyer-intent.json'], lambda x: x['body'].update(execution_authorized=True))
reject('market role is not polarity', fixtures['provider-offer.json'], lambda x: x['body']['own_promise_proposals'][0].update(polarity='buyer'))
reject('negative reception budget', fixtures['reception-permit.json'], lambda x: x['body'].update(max_total_bytes=-1))
reject('paid is not a payment outcome mode', fixtures['research-terms.json'], lambda x: x['body']['settlement'].update(mode='paid'))
reject('research timeout cannot autoaccept', fixtures['research-terms.json'], lambda x: x['body']['performance_terms']['terms']['acceptance'].update(review_timeout_outcome='accepted'))
reject('locator is not digest', fixtures['research-terms.json'], lambda x: x['body']['performance_terms']['terms']['acceptance'].update(rubric_digest='https://example.org/rubric'))
reject('publication cannot authorize spending', publications[0], lambda x: x['body']['consent'].update(payment_authorized=True))
reject('publication pin must be immutable', fixtures['buyer-intent.json'], lambda x: x['body']['publication_contract_ref'].pop('digest'))
reject('reference formation requires its slot', fixtures['research-terms.json'], lambda x: x['body'].pop('procurement_slot_id'))
reject('selection needs complete route digest', fixtures['provider-offer.json'], lambda x: x['body']['commercial_route_selection'].pop('route_digest'))

# Additional positive/negative shape checks use synthetic native references, not verified native evidence.
fake_digest = digest({'synthetic': True})
content_ref = {'id':'fixture:reference', 'digest':fake_digest}
native = {'specification_uri':'https://example.org/native-fixture','version':'fixture-only','profile':'fixture-only'}
ap2 = {'specification_uri':'https://ap2-protocol.org/ap2/specification/','version':'0.2','profile':'fixture-only'}
route = {'route_id':'fixture:external-route','mode':'external','order_validation':ap2,'paid_exchange':native,'processor_ref':content_ref,'settlement':{'scheme_profile':native,'asset':'fixture:asset','network':'fixture:network'},'native_route_policy_ref':content_ref}
paid_pub = deepcopy(publications[0]); paid_pub['body']['eligible_commercial_routes'] = [route]
validator.validate(paid_pub)
reject('external route requires processor', paid_pub, lambda x: x['body']['eligible_commercial_routes'][0].pop('processor_ref'))
reject('external route requires AP2', paid_pub, lambda x: x['body']['eligible_commercial_routes'][0].pop('order_validation'))
reject('AP2 profile version is pinned', paid_pub, lambda x: x['body']['eligible_commercial_routes'][0]['order_validation'].update(version='unknown'))
paid_terms = deepcopy(fixtures['research-terms.json']); paid_terms['body']['settlement'] = {'mode':'external','native_protocol':native,'native_contract_ref':'fixture:commercial-terms','native_contract_digest':fake_digest,'trigger':'before_fulfillment','trigger_definition':'Synthetic prepayment shape only','payee_agent_id':'agent:sourcecheck'}
validator.validate(paid_terms)
reject('ambiguous acceptance payment trigger', paid_terms, lambda x: x['body']['settlement'].update(trigger='after_acceptance'))
base = {k:deepcopy(v) for k,v in fixtures['research-terms.json'].items() if k!='body'}
base.update(kind='external_binding',id='fixture:order-validation')
base['body']={'agreement_digest':digest(fixtures['research-terms.json']),'finalized_agreement_ref':content_ref,'subject_id':'fixture:obligation','action_id':'fixture:action','purpose':'order_validation','selected_route_digest':digest(route),'native_protocol':ap2,'native_subject_ref':'fixture:checkout','evidence_refs':[{'native_record_id':'fixture:verification','digest':fake_digest,'media_type':'application/json','locator':'https://example.org/native-evidence'}]}
validator.validate(base)
payment = deepcopy(base);payment['id']='fixture:payment';payment['body'].update(purpose='payment',native_protocol=native,order_validation_binding_ref={'id':base['id'],'digest':digest(base)})
validator.validate(payment)
reject('terms alone cannot replace finalization', payment, lambda x: x['body'].pop('finalized_agreement_ref'))
reject('payment needs order-validation reference', payment, lambda x: x['body'].pop('order_validation_binding_ref'))
reject('binding cannot issue authority', payment, lambda x: x['body'].update(execution_authorized=True))
reject('payment needs selected route', payment, lambda x: x['body'].pop('selected_route_digest'))

# A different product can use a declared performance profile without research-only fields.
generic = deepcopy(fixtures['research-terms.json'])
generic['body']['offering'].update(kind='capability',fulfillment='mcp_endpoint',description='Synthetic endpoint-access shape')
generic['body']['formation_profile']='https://example.org/profiles/fixture-formation/v1'
generic['body'].pop('procurement_slot_id')
generic['body']['performance_terms']={'profile':'https://example.org/profiles/endpoint-access/v1','terms':{'access_duration_seconds':3600}}
validator.validate(generic)  # Unknown runtime profile still blocks adoption until implemented.

wrong = deepcopy(terms['commercial_route_selection']); wrong['route_digest'] = fake_digest
assert not eligible_selection(wrong, publications)
changed = deepcopy(publications); changed[1]['body']['eligible_commercial_routes'][0]['route_id'] = 'route:other'
assert not eligible_selection(terms['commercial_route_selection'], changed)
# Native field composition must not pass by matching only separate components.
external_pubs = [deepcopy(paid_pub),deepcopy(paid_pub)]
external_selection = {'route_id':route['route_id'],'route_digest':digest(route)}
assert eligible_selection(external_selection, external_pubs)
external_pubs[1]['body']['eligible_commercial_routes'][0]['processor_ref']={'id':'fixture:another-processor','digest':digest({'processor':2})}
assert not eligible_selection(external_selection, external_pubs)

assert read('examples/a2a/intent-send-message.json')['params']['message']['parts'][0]['data'] == fixtures['buyer-intent.json']
check_ref(read('examples/a2a/agent-card-fragment.json')['capabilities']['extensions'][0]['params']['publicationContractRef'], publications[1])
coverage = read('promise-theory-reading-coverage.json')
pages = {i for item in coverage['coverage_ranges_in_page_order'] for i in range(item['pdf_page_start'],item['pdf_page_end']+1)}
assert pages == set(range(1,319))
for path in ROOT.rglob('*.md'):
    text = path.read_text()
    assert text.count('```') % 2 == 0, path
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):
            continue
        assert (path.parent / target.split('#')[0]).exists(), (path,target)
ids = re.findall(r'^\| (C\d+) \|', (ROOT/'conformance.md').read_text(), re.M)
assert len(ids) == len(set(ids)) and set(ids)=={f'C{i:02d}' for i in range(1,64)}
print(json.dumps({'schema':'Draft 2020-12 valid','semantic_record_fixtures':len(records),'additional_positive_shapes':5,'negative_structure_cases':len(negative),'route_mismatch_cases':3,'fixture_digest_and_a2a_checks':'passed','book_text_coverage_pages':len(pages),'local_links_and_fences':'passed','specified_conformance_cases':len(ids),'runtime_and_native_integration':'not executed'},indent=2))

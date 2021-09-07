from pytest_cases import parametrize_with_cases, fixture
from stix2 import Bundle
from tests.cases.entities import EntityTestCases


@fixture
@parametrize_with_cases("entity", cases=EntityTestCases)
def entity_class(entity):
    entity.setup()
    yield entity
    entity.teardown()


def test_entity_create(entity_class, api_stix, opencti_splitter):
    class_data = entity_class.data()
    stix_class = entity_class.stixclass()
    if stix_class is None:
        return

    stix_object = stix_class(**class_data)
    bundle = Bundle(objects=[stix_object]).serialize()
    split_bundle = opencti_splitter.split_bundle(bundle, True, None)[0]
    bundles_sent = api_stix.import_bundle_from_json(
        split_bundle, False, None, 0
    )

    assert len(bundles_sent) == 1
    assert bundles_sent[0]['id'] == stix_object['id']
    assert bundles_sent[0]['type'] == stix_object['type']

    entity_class.baseclass().delete(id=stix_object["id"])

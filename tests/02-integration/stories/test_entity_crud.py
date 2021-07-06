from typing import Dict, List


class Test_entity_crud:
    @staticmethod
    def compare_values(
        sdo: str, original_data: Dict, retrieved_data: Dict, exception_keys: List
    ):
        for key, value in original_data.items():
            # Attributes which aren't present in the final Stix objects
            if key in exception_keys:
                continue

            assert key in retrieved_data, f"{sdo}: Key {key} is not in retrieved_data"

            compare_data = retrieved_data.get(key, None)
            if isinstance(value, str):
                assert (
                    value == compare_data
                ), f"{sdo}: Key '{key}': {value} does't match {retrieved_data[key]} ({retrieved_data}"
            # TODO handle dicts in lists
            # elif isinstance(value, list) and len(value) > 0:
            #     assert len(value) == len(
            #         compare_data
            #     ), f"{sdo}: List '{value}' does not have the same length as '{compare_data}'"
            #     for value_key in value:
            #         if isinstance(value_key, str):
            #             assert (
            #                     value_key in compare_data
            #             ), f"{sdo}: List '{compare_data}' does not contain '{value_key}'"
            elif isinstance(value, dict):
                assert len(value) == len(
                    compare_data
                ), f"{sdo}: Dict '{value}' does not have the same length as '{compare_data}'"
                assert (
                    value == compare_data
                ), f"{sdo}: Dict '{value}' does not have the same content as'{compare_data}'"

    def test_create(self, fruit_bowl):
        for sdo, s_class in fruit_bowl.items():
            s_class.setup()
            for class_data in s_class.data():
                test_indicator = s_class.ownclass().create(**class_data)
                assert test_indicator is not None, f"{sdo}: Response is NoneType"
                assert "id" in test_indicator, f"{sdo}: No ID on object"

                # assert 'entity_type' in test_indicator, f"{sdo}: No entity_type found"
                # assert sdo == test_indicator['entity_type'], f"{sdo}: Entity type '{test_indicator['entity_type']}' doesn't match {sdo}"

    def test_read(self, fruit_bowl):
        for sdo, s_class in fruit_bowl.items():
            s_class.setup()
            for class_data in s_class.data():
                test_indicator = s_class.ownclass().create(**class_data)
                assert test_indicator is not None, f"{sdo}: Response is NoneType"
                assert "id" in test_indicator, f"{sdo}: No ID on object"
                test_indicator = s_class.ownclass().read(id=test_indicator["id"])
                self.compare_values(
                    sdo,
                    class_data,
                    test_indicator,
                    s_class.get_compare_exception_keys(),
                )

            s_class.teardown()

    def test_update(self, fruit_bowl):
        for sdo, s_class in fruit_bowl.items():
            s_class.setup()
            for class_data in s_class.data():
                test_indicator = s_class.ownclass().create(**class_data)
                assert test_indicator is not None, f"{sdo}: Response is NoneType"
                assert "id" in test_indicator, f"{sdo}: No ID on object"

                update_field = list(s_class.update_data().keys())[0]
                update_value = list(s_class.update_data().values())[0]

                class_data[update_field] = update_value
                class_data["update"] = True
                result = s_class.ownclass().create(**class_data)
                result = s_class.ownclass().read(id=result["id"])
                assert (
                    update_field in result
                ), f"{sdo}: Updated field {update_field} is not present"
                assert (
                    result[update_field] == update_value
                ), f"{sdo}: Updated field {update_field} is not '{update_value}', instead '{result[update_field]}'"
                assert (
                    result["id"] == test_indicator["id"]
                ), f"{sdo}: Updated SDO does not match old ID"
                self.compare_values(
                    sdo, class_data, result, s_class.get_compare_exception_keys()
                )

            s_class.teardown()

    def test_delete(self, fruit_bowl):
        for sdo, s_class in fruit_bowl.items():
            function_present = getattr(s_class.baseclass(), "delete", None)
            if function_present is None:
                print(f"{sdo} has no delete function")
                continue

            s_class.setup()
            for class_data in s_class.data():
                test_indicator = s_class.ownclass().create(**class_data)
                assert test_indicator is not None, f"{sdo}: Response is NoneType"
                assert "id" in test_indicator, f"{sdo}: No ID on object"
                result = s_class.baseclass().delete(id=test_indicator["id"])
                assert result is None, f"{sdo}: Delete returned value '{result}'"
                result = s_class.ownclass().read(id=test_indicator["id"])
                assert (
                    result is None
                ), f"{sdo}: Read returned value '{result}' after delete"

            s_class.teardown()

    def test_import_from_stix2(self, fruit_bowl, api_client):
        pass

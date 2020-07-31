# coding: utf-8

import json
from pycti.utils.constants import CustomProperties
from pycti.utils.opencti_stix2 import SPEC_VERSION


class Indicator:
    """Main Indicator class for OpenCTI

    :param opencti: instance of :py:class:`~pycti.api.opencti_api_client.OpenCTIApiClient`
    """

    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            standard_id
            entity_type
            parent_types
            spec_version
            created_at
            updated_at
            createdBy {
                ... on Identity {
                    id
                    standard_id
                    entity_type
                    parent_types
                    name
                    aliases
                    description
                    created
                    modified
                }
                ... on Organization {
                    x_opencti_organization_type
                    x_opencti_reliability
                }
                ... on Individual {
                    x_opencti_firstname
                    x_opencti_lastname
                }
            }
            objectMarking {
                edges {
                    node {
                        id
                        standard_id
                        entity_type
                        definition_type
                        definition
                        created
                        modified
                        x_opencti_order
                        x_opencti_color
                    }
                }
            }
            objectLabel {
                edges {
                    node {
                        id
                        value
                        color
                    }
                }
            }
            externalReferences {
                edges {
                    node {
                        id
                        standard_id
                        entity_type
                        source_name
                        description
                        url
                        hash
                        external_id
                        created
                        modified
                    }
                }
            }
            revoked
            confidence
            created
            modified
            pattern_type
            pattern_version
            pattern
            name
            description
            indicator_types
            valid_from
            valid_until
            x_opencti_score
            x_opencti_detection
            x_opencti_main_observable_type
            killChainPhases {
                edges {
                    node {
                        id
                        standard_id                            
                        entity_type
                        kill_chain_name
                        phase_name
                        x_opencti_order
                        created
                        modified
                    }
                }
            }
        """

    def list(self, **kwargs):
        """List Indicator objects

        The list method accepts the following \**kwargs:

        :param list filters: (optional) the filters to apply
        :param str search: (optional) a search keyword to apply for the listing
        :param int first: (optional) return the first n rows from the `after` ID
                            or the beginning if not set
        :param str after: (optional) OpenCTI object ID of the first row for pagination
        :param str orderBy: (optional) the field to order the response on
        :param bool orderMode: (optional) either "`asc`" or "`desc`"
        :param list customAttributes: (optional) list of attributes keys to return
        :param bool getAll: (optional) switch to return all entries (be careful to use this without any other filters)
        :param bool withPagination: (optional) switch to use pagination
        """

        filters = kwargs.get("filters", None)
        search = kwargs.get("search", None)
        first = kwargs.get("first", 500)
        after = kwargs.get("after", None)
        order_by = kwargs.get("orderBy", None)
        order_mode = kwargs.get("orderMode", None)
        custom_attributes = kwargs.get("customAttributes", None)
        get_all = kwargs.get("getAll", False)
        with_pagination = kwargs.get("withPagination", False)
        if get_all:
            first = 500

        self.opencti.log(
            "info", "Listing Indicators with filters " + json.dumps(filters) + "."
        )
        query = (
            """
            query Indicators($filters: [IndicatorsFiltering], $search: String, $first: Int, $after: ID, $orderBy: IndicatorsOrdering, $orderMode: OrderingMode) {
                indicators(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
                    edges {
                        node {
                            """
            + (custom_attributes if custom_attributes is not None else self.properties)
            + """
                        }
                    }
                    pageInfo {
                        startCursor
                        endCursor
                        hasNextPage
                        hasPreviousPage
                        globalCount
                    }
                }
            }
        """
        )
        result = self.opencti.query(
            query,
            {
                "filters": filters,
                "search": search,
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
            },
        )

        if get_all:
            final_data = []
            data = self.opencti.process_multiple(result["data"]["indicators"])
            final_data = final_data + data
            while result["data"]["indicators"]["pageInfo"]["hasNextPage"]:
                after = result["data"]["indicators"]["pageInfo"]["endCursor"]
                self.opencti.log("info", "Listing Indicators after " + after)
                result = self.opencti.query(
                    query,
                    {
                        "filters": filters,
                        "search": search,
                        "first": first,
                        "after": after,
                        "orderBy": order_by,
                        "orderMode": order_mode,
                    },
                )
                data = self.opencti.process_multiple(result["data"]["indicators"])
                final_data = final_data + data
            return final_data
        else:
            return self.opencti.process_multiple(
                result["data"]["indicators"], with_pagination
            )

    def read(self, **kwargs):
        """Read an Indicator object

        read can be either used with a known OpenCTI entity `id` or by using a
        valid filter to search and return a single Indicator entity or None.

        The list method accepts the following \**kwargs.

        Note: either `id` or `filters` is required.

        :param str id: the id of the Threat-Actor
        :param list filters: the filters to apply if no id provided
        """

        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Reading Indicator {" + id + "}.")
            query = (
                """
                query Indicator($id: String!) {
                    indicator(id: $id) {
                        """
                + (
                    custom_attributes
                    if custom_attributes is not None
                    else self.properties
                )
                + """
                    }
                }
             """
            )
            result = self.opencti.query(query, {"id": id})
            return self.opencti.process_multiple_fields(result["data"]["indicator"])
        elif filters is not None:
            result = self.list(filters=filters, customAttributes=custom_attributes)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log(
                "error", "[opencti_indicator] Missing parameters: id or filters"
            )
            return None

    """
        Create a Indicator object

        :param name: the name of the Indicator
        :return Indicator object
    """

    def create_raw(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        external_references = kwargs.get("externalReferences", None)
        revoked = kwargs.get("revoked", None)
        confidence = kwargs.get("confidence", None)
        lang = kwargs.get("lang", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        pattern_type = kwargs.get("pattern_type", None)
        pattern_version = kwargs.get("pattern_version", None)
        pattern = kwargs.get("pattern", None)
        name = kwargs.get("name", None)
        description = kwargs.get("description", None)
        indicator_types = kwargs.get("indicator_types", None)
        valid_from = kwargs.get("valid_from", None)
        valid_until = kwargs.get("valid_until", None)
        x_opencti_score = kwargs.get("x_opencti_score", 50)
        x_opencti_detection = kwargs.get("x_opencti_detection", False)
        x_opencti_main_observable_type = kwargs.get(
            "x_opencti_main_observable_type", None
        )
        kill_chain_phases = kwargs.get("killChainPhases", None)

        if (
            name is not None
            and pattern is not None
            and x_opencti_main_observable_type is not None
        ):
            self.opencti.log("info", "Creating Indicator {" + name + "}.")
            query = """
                mutation IndicatorAdd($input: IndicatorAddInput) {
                    indicatorAdd(input: $input) {
                        id
                        standard_id
                        entity_type
                        parent_types                    
                    }
                }
            """
            if pattern_type is None:
                pattern_type = "stix2"
            result = self.opencti.query(
                query,
                {
                    "input": {
                        "stix_id": stix_id,
                        "createdBy": created_by,
                        "objectMarking": object_marking,
                        "objectLabel": object_label,
                        "externalReferences": external_references,
                        "revoked": revoked,
                        "confidence": confidence,
                        "lang": lang,
                        "created": created,
                        "modified": modified,
                        "pattern_type": pattern_type,
                        "pattern_version": pattern_version,
                        "pattern": pattern,
                        "name": name,
                        "description": description,
                        "indicator_types": indicator_types,
                        "valid_until": valid_until,
                        "valid_from": valid_from,
                        "x_opencti_score": x_opencti_score,
                        "x_opencti_detection": x_opencti_detection,
                        "x_opencti_main_observable_type": x_opencti_main_observable_type,
                        "killChainPhases": kill_chain_phases,
                    }
                },
            )
            return self.opencti.process_multiple_fields(result["data"]["indicatorAdd"])
        else:
            self.opencti.log(
                "error",
                "[opencti_indicator] Missing parameters: name and indicator_pattern and main_observable_type",
            )

    """
        Create a Indicator object only if it not exists, update it on request

        :param name: the name of the Indicator
        :return Indicator object
    """

    def create(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        external_references = kwargs.get("externalReferences", None)
        revoked = kwargs.get("revoked", None)
        confidence = kwargs.get("confidence", None)
        lang = kwargs.get("lang", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        pattern_type = kwargs.get("pattern_type", None)
        pattern_version = kwargs.get("pattern_version", None)
        pattern = kwargs.get("pattern", None)
        name = kwargs.get("name", None)
        description = kwargs.get("description", None)
        indicator_types = kwargs.get("indicator_types", None)
        valid_from = kwargs.get("valid_from", None)
        valid_until = kwargs.get("valid_until", None)
        x_opencti_score = kwargs.get("x_opencti_score", 50)
        x_opencti_detection = kwargs.get("x_opencti_detection", False)
        x_opencti_main_observable_type = kwargs.get(
            "x_opencti_main_observable_type", None
        )
        kill_chain_phases = kwargs.get("killChainPhases", None)
        update = kwargs.get("update", False)
        custom_attributes = """
            id
            standard_id
            entity_type
            parent_types
            createdBy {
                ... on Identity {
                    id
                }
            }
            ... on Indicator {
                pattern_type
                pattern_version
                pattern
                name
                description
                indicator_types
                valid_from
                valid_until
                x_opencti_score
                x_opencti_detection
                x_opencti_main_observable_type
            }
        """
        object_result = None
        if stix_id is not None:
            object_result = self.read(id=stix_id, customAttributes=custom_attributes)
        if object_result is None:
            object_result = self.read(
                filters=[
                    {
                        "key": "pattern",
                        "values": [pattern],
                        "operator": "match" if len(pattern) > 500 else "eq",
                    }
                ],
                customAttributes=custom_attributes,
            )
        if object_result is not None:
            if update or object_result["createdById"] == created_by:
                # name
                if name is not None and object_result["name"] != name:
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="name", value=name
                    )
                    object_result["name"] = name
                # description
                if (
                    self.opencti.not_empty(description)
                    and object_result["description"] != description
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="description", value=description
                    )
                    object_result["description"] = description
                # score
                if (
                    self.opencti.not_empty(x_opencti_score)
                    and object_result["score"] != x_opencti_score
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="score", value=str(x_opencti_score)
                    )
                    object_result["score"] = x_opencti_score
                # confidence
                if (
                    self.opencti.not_empty(confidence)
                    and object_result["confidence"] != confidence
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="confidence", value=str(confidence)
                    )
                    object_result["confidence"] = confidence
                # detection
                if (
                    self.opencti.not_empty(x_opencti_detection)
                    and object_result["detection"] != x_opencti_detection
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"],
                        key="detection",
                        value=str(x_opencti_detection).lower(),
                    )
                    object_result["detection"] = x_opencti_detection
            return object_result
        else:
            return self.create_raw(
                stix_id=stix_id,
                createdBy=created_by,
                objectMarking=object_marking,
                objectLabel=object_label,
                externalReferences=external_references,
                revoked=revoked,
                confidence=confidence,
                lang=lang,
                created=created,
                modified=modified,
                pattern_type=pattern_type,
                pattern_version=pattern_version,
                pattern=pattern,
                name=name,
                description=description,
                indicator_types=indicator_types,
                valid_from=valid_from,
                valid_until=valid_until,
                x_opencti_score=x_opencti_score,
                x_opencti_detection=x_opencti_detection,
                x_opencti_main_observable_type=x_opencti_main_observable_type,
                killChainPhases=kill_chain_phases,
            )

    """
        Add a Stix-Observable object to Indicator object (observable_refs)

        :param id: the id of the Indicator
        :param entity_id: the id of the Stix-Observable
        :return Boolean
    """

    def add_stix_observable(self, **kwargs):
        id = kwargs.get("id", None)
        indicator = kwargs.get("indicator", None)
        stix_observable_id = kwargs.get("stix_observable_id", None)
        if id is not None and stix_observable_id is not None:
            if indicator is None:
                indicator = self.read(id=id)
            if indicator is None:
                self.opencti.log(
                    "error",
                    "[opencti_indicator] Cannot add Object Ref, indicator not found",
                )
                return False
            if stix_observable_id in indicator["observableRefsIds"]:
                return True
            else:
                self.opencti.log(
                    "info",
                    "Adding Stix-Observable {"
                    + stix_observable_id
                    + "} to Indicator {"
                    + id
                    + "}",
                )
                query = """
                   mutation IndicatorEdit($id: ID!, $input: StixMetaRelationshipAddInput) {
                       indicatorEdit(id: $id) {
                            relationAdd(input: $input) {
                                id
                            }
                       }
                   }
                """
                self.opencti.query(
                    query,
                    {
                        "id": id,
                        "input": {
                            "fromRole": "observables_aggregation",
                            "toId": stix_observable_id,
                            "toRole": "soo",
                            "through": "observable_refs",
                        },
                    },
                )
                return True
        else:
            self.opencti.log(
                "error",
                "[opencti_indicator] Missing parameters: id and stix_observable_id",
            )
            return False

    """
        Import an Indicator object from a STIX2 object

        :param stixObject: the Stix-Object Indicator
        :return Indicator object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        if stix_object is not None:
            return self.create(
                stix_id=stix_object["id"],
                createdBy=extras["created_by_id"]
                if "created_by_id" in extras
                else None,
                objectMarking=extras["object_marking_ids"]
                if "object_marking_ids" in extras
                else None,
                objectLabel=extras["object_label_ids"]
                if "object_label_ids" in extras
                else [],
                externalReferences=extras["external_references_ids"]
                if "external_references_ids" in extras
                else [],
                revoked=stix_object["revoked"] if "revoked" in stix_object else None,
                confidence=stix_object["confidence"]
                if "confidence" in stix_object
                else None,
                lang=stix_object["lang"] if "lang" in stix_object else None,
                created=stix_object["created"] if "created" in stix_object else None,
                modified=stix_object["modified"] if "modified" in stix_object else None,
                pattern_type=stix_object["pattern_type"]
                if "pattern_type" in stix_object
                else None,
                pattern_version=stix_object["pattern_version"]
                if "pattern_version" in stix_object
                else None,
                pattern=stix_object["pattern"] if "pattern" in stix_object else "",
                name=stix_object["name"] if "name" in stix_object else "",
                description=self.opencti.stix2.convert_markdown(
                    stix_object["description"]
                )
                if "description" in stix_object
                else "",
                indicator_types=stix_object["indicator_types"]
                if "indicator_types" in stix_object
                else "",
                valid_from=stix_object["valid_from"]
                if "valid_from" in stix_object
                else "",
                valid_until=stix_object["valid_until"]
                if "valid_until" in stix_object
                else "",
                x_opencti_score=stix_object["x_opencti_score"]
                if "x_opencti_score" in stix_object
                else 50,
                x_opencti_detection=stix_object["x_opencti_detection"]
                if "x_opencti_detection" in stix_object
                else False,
                x_opencti_main_observable_type=stix_object[
                    "x_opencti_main_observable_type"
                ]
                if "x_opencti_main_observable_type" in stix_object
                else False,
                killChainPhases=extras["kill_chain_phases_ids"]
                if "kill_chain_phases_ids" in extras
                else None,
                update=update,
            )
        else:
            self.opencti.log(
                "error", "[opencti_attack_pattern] Missing parameters: stixObject"
            )

    """
        Export an Indicator object in STIX2
    
        :param id: the id of the Indicator
        :return Indicator object
    """

    def to_stix2(self, **kwargs):
        id = kwargs.get("id", None)
        mode = kwargs.get("mode", "simple")
        max_marking_definition_entity = kwargs.get(
            "max_marking_definition_entity", None
        )
        entity = kwargs.get("entity", None)
        if id is not None and entity is None:
            entity = self.read(id=id)
        if entity is not None:
            indicator = dict()
            indicator["id"] = entity["stix_id"]
            indicator["type"] = "indicator"
            indicator["spec_version"] = SPEC_VERSION
            indicator["name"] = entity["name"]
            if self.opencti.not_empty(entity["stix_label"]):
                indicator["labels"] = entity["stix_label"]
            else:
                indicator["labels"] = ["indicator"]
            if self.opencti.not_empty(entity["description"]):
                indicator["description"] = entity["description"]
            indicator["pattern"] = entity["indicator_pattern"]
            indicator["valid_from"] = self.opencti.stix2.format_date(
                entity["valid_from"]
            )
            indicator["valid_until"] = self.opencti.stix2.format_date(
                entity["valid_until"]
            )
            if self.opencti.not_empty(entity["pattern_type"]):
                indicator["pattern_type"] = entity["pattern_type"]
            else:
                indicator["pattern_type"] = "stix"
            indicator["created"] = self.opencti.stix2.format_date(entity["created"])
            indicator["modified"] = self.opencti.stix2.format_date(entity["modified"])
            if self.opencti.not_empty(entity["alias"]):
                indicator[CustomProperties.ALIASES] = entity["alias"]
            if self.opencti.not_empty(entity["score"]):
                indicator[CustomProperties.SCORE] = entity["score"]
            indicator[CustomProperties.ID] = entity["id"]
            return self.opencti.stix2.prepare_export(
                entity, indicator, mode, max_marking_definition_entity
            )
        else:
            self.opencti.log("error", "Missing parameters: id or entity")

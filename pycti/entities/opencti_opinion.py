# coding: utf-8

import json

from pycti.utils.constants import CustomProperties
from pycti.utils.opencti_stix2 import SPEC_VERSION


class Opinion:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            stix_id
            entity_type
            stix_label
            name
            alias
            description
            explanation
            graph_data
            created
            modified
            created_at
            updated_at
            createdBy {
                node {
                    id
                    entity_type
                    stix_id
                    stix_label
                    name
                    alias
                    description
                    created
                    modified
                    ... on Organization {
                        x_opencti_organization_type
                    }
                }
                relation {
                    id
                }
            }
            markingDefinitions {
                edges {
                    node {
                        id
                        entity_type
                        stix_id
                        definition_type
                        definition
                        level
                        color
                        created
                        modified
                    }
                    relation {
                        id
                    }
                }
            }
            tags {
                edges {
                    node {
                        id
                        tag_type
                        value
                        color
                    }
                    relation {
                        id
                    }
                }
            }            
            externalReferences {
                edges {
                    node {
                        id
                        entity_type
                        stix_id
                        source_name
                        description
                        url
                        hash
                        external_id
                        created
                        modified
                    }
                    relation {
                        id
                    }
                }
            }
            objectRefs {
                edges {
                    node {
                        id
                        stix_id
                        entity_type
                    }
                }
            }
            observableRefs {
                edges {
                    node {
                        id
                        stix_id
                        entity_type
                        observable_value
                    }
                }
            }
            relationRefs {
                edges {
                    node {
                        id
                        stix_id
                    }
                }
            }
        """

    """
        List Opinion objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Opinion objects
    """

    def list(self, **kwargs):
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
            "info", "Listing Opinions with filters " + json.dumps(filters) + "."
        )
        query = (
            """
            query Opinions($filters: [OpinionsFiltering], $search: String, $first: Int, $after: ID, $orderBy: OpinionsOrdering, $orderMode: OrderingMode) {
                opinions(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
        return self.opencti.process_multiple(
            result["data"]["opinions"], with_pagination
        )

    """
        Read a Opinion object

        :param id: the id of the Opinion
        :param filters: the filters to apply if no id provided
        :return Opinion object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Reading Opinion {" + id + "}.")
            query = (
                """
                query Opinion($id: String!) {
                    opinion(id: $id) {
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
            return self.opencti.process_multiple_fields(result["data"]["opinion"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None

    """
        Read a Opinion object by stix_id or name

        :param type: the Stix-Domain-Entity type
        :param stix_id: the STIX ID of the Stix-Domain-Entity
        :param name: the name of the Stix-Domain-Entity
        :return Stix-Domain-Entity object
    """

    def get_by_stix_id_or_name(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        description = kwargs.get("description", None)
        explanation = kwargs.get("explanation", None)
        custom_attributes = kwargs.get(explanation, None)
        object_result = None
        if stix_id is not None:
            object_result = self.read(id=stix_id, customAttributes=custom_attributes)
        if (
            object_result is None
            and description is not None
            and explanation is not None
        ):
            object_result = self.read(
                filters=[
                    {"key": "description", "values": [description]},
                    {"key": "explanation", "values": [explanation]},
                ],
                customAttributes=custom_attributes,
            )
        return object_result

    """
        Check if a opinion already contains a STIX entity
        
        :return Boolean
    """

    def contains_opencti_stix_object_or_stix_relationship(self, **kwargs):
        id = kwargs.get("id", None)
        entity_id = kwargs.get("entity_id", None)
        if id is not None and entity_id is not None:
            self.opencti.log(
                "info",
                "Checking Stix-Entity {" + entity_id + "} in Opinion {" + id + "}",
            )
            query = """
                query OpinionContainsStixDomainEntity($id: String!, $objectId: String!) {
                    opinionContainsStixDomainEntity(id: $id, objectId: $objectId)
                }
            """
            result = self.opencti.query(query, {"id": id, "objectId": entity_id})
            if result["data"]["opinionContainsStixDomainEntity"]:
                return True
            query = """
                query OpinionContainsStixRelation($id: String!, $objectId: String!) {
                    opinionContainsStixRelation(id: $id, objectId: $objectId)
                }
            """
            result = self.opencti.query(query, {"id": id, "objectId": entity_id})
            return result["data"]["opinionContainsStixRelation"]
        else:
            self.opencti.log(
                "error", "[opencti_opinion] Missing parameters: id or entity_id",
            )

    """
        Check if a opinion already contains a STIX observable

        :return Boolean
    """

    def contains_stix_observable(self, **kwargs):
        id = kwargs.get("id", None)
        stix_observable_id = kwargs.get("stix_observable_id", None)
        if id is not None and stix_observable_id is not None:
            self.opencti.log(
                "info",
                "Checking Stix-Observable {"
                + stix_observable_id
                + "} in Opinion {"
                + id
                + "}",
            )
            query = """
                query OpinionContainsStixCyberObservable($id: String!, $objectId: String!) {
                    opinionContainsStixCyberObservable(id: $id, objectId: $objectId)
                }
            """
            result = self.opencti.query(
                query, {"id": id, "objectId": stix_observable_id}
            )
            return result["data"]["opinionContainsStixCyberObservable"]
        else:
            self.opencti.log(
                "error",
                "[opencti_opinion] Missing parameters: id or stix_observable_id",
            )

    """
        Create a Opinion object

        :param name: the name of the Opinion
        :return Opinion object
    """

    def create_raw(self, **kwargs):
        name = kwargs.get("name", None)
        description = kwargs.get("description", None)
        explanation = kwargs.get("explanation", None)
        graph_data = kwargs.get("graph_data", None)
        id = kwargs.get("id", None)
        stix_id = kwargs.get("stix_id", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)

        if name is not None and description is not None and explanation is not None:
            self.opencti.log("info", "Creating Opinion {" + name + "}.")
            query = """
                mutation OpinionAdd($input: OpinionAddInput) {
                    opinionAdd(input: $input) {
                        id
                        stix_id
                        entity_type
                        parent_types
                        observableRefs {
                            edges {
                                node {
                                    id
                                    stix_id
                                    entity_type
                                    observable_value
                                }
                            }
                        }                        
                    }
                }
            """
            result = self.opencti.query(
                query,
                {
                    "input": {
                        "name": name,
                        "description": description,
                        "explanation": explanation,
                        "graph_data": graph_data,
                        "internal_id_key": id,
                        "stix_id": stix_id,
                        "created": created,
                        "modified": modified,
                        "createdBy": created_by,
                        "objectMarking": objectMarking,
                    }
                },
            )
            return self.opencti.process_multiple_fields(result["data"]["opinionAdd"])
        else:
            self.opencti.log(
                "error",
                "[opencti_opinion] Missing parameters: name and description and explanation",
            )

    """
         Create a Opinion object only if it not exists, update it on request

         :param name: the name of the Opinion
         :param description: the description of the Opinion
         :param published: the publication date of the Opinion
         :return Opinion object
     """

    def create(self, **kwargs):
        name = kwargs.get("name", None)
        external_reference_id = kwargs.get("external_reference_id", None)
        description = kwargs.get("description", None)
        explanation = kwargs.get("explanation", None)
        graph_data = kwargs.get("graph_data", None)
        id = kwargs.get("id", None)
        stix_id = kwargs.get("stix_id", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        update = kwargs.get("update", False)
        custom_attributes = """
            id
            entity_type
            name
            description 
            createdBy {
                node {
                    id
                }
            }
            externalReferences {
                edges {
                    node {
                        id
                        stix_id
                        source_name
                        description
                        url
                    }
                }
            }            
        """
        object_result = None
        if external_reference_id is not None:
            object_result = self.opencti.stix_domain_object.read(
                types=["Opinion"],
                filters=[
                    {"key": "hasExternalReference", "values": [external_reference_id]}
                ],
                customAttributes=custom_attributes,
            )
        if (
            object_result is None
            and description is not None
            and explanation is not None
        ):
            object_result = self.get_by_stix_id_or_name(
                stix_id=stix_id,
                description=description,
                explanation=explanation,
                custom_attributes=custom_attributes,
            )
        if object_result is not None:
            if update or object_result["createdById"] == created_by:
                if name is not None and object_result["name"] != name:
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="name", value=name
                    )
                    object_result["name"] = name
                if (
                    description is not None
                    and object_result["description"] != description
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="description", value=description
                    )
                    object_result["description"] = description
                if (
                    explanation is not None
                    and object_result["explanation"] != explanation
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="explanation", value=explanation
                    )
                    object_result["explanation"] = explanation
            if external_reference_id is not None:
                self.opencti.opencti_stix_object_or_stix_relationship.add_external_reference(
                    id=object_result["id"], external_reference_id=external_reference_id,
                )
            return object_result
        else:
            opinion = self.create_raw(
                name=name,
                description=description,
                explanation=explanation,
                graph_data=graph_data,
                id=id,
                stix_id=stix_id,
                created=created,
                modified=modified,
                createdBy=created_by,
                objectMarking=object_marking,
            )
            if external_reference_id is not None:
                self.opencti.opencti_stix_object_or_stix_relationship.add_external_reference(
                    id=opinion["id"], external_reference_id=external_reference_id,
                )
            return opinion

    """
        Add a Stix-Entity object to Opinion object (object_refs)

        :param id: the id of the Opinion
        :param entity_id: the id of the Stix-Entity
        :return Boolean
    """

    def add_opencti_stix_object_or_stix_relationship(self, **kwargs):
        id = kwargs.get("id", None)
        entity_id = kwargs.get("entity_id", None)
        if id is not None and entity_id is not None:
            if self.contains_opencti_stix_object_or_stix_relationship(
                id=id, entity_id=entity_id
            ):
                return True
            self.opencti.log(
                "info",
                "Adding Stix-Entity {" + entity_id + "} to Opinion {" + id + "}",
            )
            query = """
               mutation OpinionEdit($id: ID!, $input: RelationAddInput) {
                   opinionEdit(id: $id) {
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
                        "fromRole": "knowledge_aggregation",
                        "toId": entity_id,
                        "toRole": "so",
                        "through": "object_refs",
                    },
                },
            )
            return True
        else:
            self.opencti.log(
                "error", "[opencti_opinion] Missing parameters: id and entity_id"
            )
            return False

    """
        Add a Stix-Observable object to Opinion object (observable_refs)

        :param id: the id of the Opinion
        :param entity_id: the id of the Stix-Observable
        :return Boolean
    """

    def add_stix_observable(self, **kwargs):
        id = kwargs.get("id", None)
        stix_observable_id = kwargs.get("stix_observable_id", None)
        if id is not None and stix_observable_id is not None:
            if self.contains_stix_observable(
                id=id, stix_observable_id=stix_observable_id
            ):
                return True
            self.opencti.log(
                "info",
                "Adding Stix-Observable {"
                + stix_observable_id
                + "} to Opinion {"
                + id
                + "}",
            )
            query = """
               mutation OpinionEdit($id: ID!, $input: RelationAddInput) {
                   opinionEdit(id: $id) {
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
                "[opencti_opinion] Missing parameters: id and stix_observable_id",
            )
            return False

    """
        Import a Opinion object from a STIX2 object

        :param stixObject: the Stix-Object Opinion
        :return Opinion object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        if stix_object is not None:
            return self.create(
                explanation=self.opencti.stix2.convert_markdown(
                    stix_object["explanation"]
                )
                if "explanation" in stix_object
                else "",
                description=self.opencti.stix2.convert_markdown(stix_object["opinion"])
                if "opinion" in stix_object
                else "",
                name=stix_object[CustomProperties.NAME]
                if CustomProperties.NAME in stix_object
                else "",
                graph_data=stix_object[CustomProperties.GRAPH_DATA]
                if CustomProperties.GRAPH_DATA in stix_object
                else "",
                id=stix_object[CustomProperties.ID]
                if CustomProperties.ID in stix_object
                else None,
                stix_id=stix_object["id"] if "id" in stix_object else None,
                created=stix_object["created"] if "created" in stix_object else None,
                modified=stix_object["modified"] if "modified" in stix_object else None,
                createdBy=extras["created_by_id"]
                if "created_by_id" in extras
                else None,
                markingDefinitions=extras["object_marking_ids"]
                if "object_marking_ids" in extras
                else [],
                update=update,
            )
        else:
            self.opencti.log(
                "error", "[opencti_attack_pattern] Missing parameters: stixObject"
            )

    """
        Export a Opinion object in STIX2

        :param id: the id of the Opinion
        :return Opinion object
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
            opinion = dict()
            opinion["id"] = entity["stix_id"]
            opinion["type"] = "opinion"
            opinion["spec_version"] = SPEC_VERSION
            opinion["explanation"] = entity["explanation"]
            opinion["opinion"] = entity["description"]
            if self.opencti.not_empty(entity["stix_label"]):
                opinion["labels"] = entity["stix_label"]
            else:
                opinion["labels"] = ["opinion"]
            opinion["created"] = self.opencti.stix2.format_date(entity["created"])
            opinion["modified"] = self.opencti.stix2.format_date(entity["modified"])
            if self.opencti.not_empty(entity["alias"]):
                opinion[CustomProperties.ALIASES] = entity["alias"]
            if self.opencti.not_empty(entity["name"]):
                opinion[CustomProperties.NAME] = entity["name"]
            if self.opencti.not_empty(entity["graph_data"]):
                opinion[CustomProperties.GRAPH_DATA] = entity["graph_data"]
            opinion[CustomProperties.ID] = entity["id"]
            return self.opencti.stix2.prepare_export(
                entity, opinion, mode, max_marking_definition_entity
            )
        else:
            self.opencti.log(
                "error", "[opencti_opinion] Missing parameters: id or entity"
            )

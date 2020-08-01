# coding: utf-8

import json

from dateutil.parser import parse


class Report:
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
            name
            description
            report_types
            published
            x_opencti_graph_data
            x_opencti_report_status
            objects {
                edges {
                    node {
                        ... on BasicObject {
                            id
                            entity_type
                            parent_types
                        }
                        ... on BasicRelationship {
                            id
                            entity_type
                            parent_types
                        }
                        ... on StixObject {
                            standard_id
                            spec_version
                            created_at
                            updated_at
                        }
                        ... on AttackPattern {
                            name
                        }
                        ... on Campaign {
                            name
                        }
                        ... on CourseOfAction {
                            name
                        }
                        ... on Individual {
                            name
                        }
                        ... on Organization {
                            name
                        }
                        ... on Sector {
                            name
                        }
                        ... on Indicator {
                            name
                        }
                        ... on Infrastructure {
                            name
                        }
                        ... on IntrusionSet {
                            name
                        }
                        ... on Position {
                            name
                        }
                        ... on City {
                            name
                        }
                        ... on Country {
                            name
                        }
                        ... on Region {
                            name
                        }
                        ... on Malware {
                            name
                        }
                        ... on ThreatActor {
                            name
                        }
                        ... on Tool {
                            name
                        }
                        ... on Vulnerability {
                            name
                        }
                        ... on XOpenctiIncident {
                            name
                        }                
                        ... on StixCoreRelationship {
                            standard_id
                            spec_version
                            created_at
                            updated_at
                        }
                    }
                }
            }
        """

    """
        List Report objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Report objects
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
            "info", "Listing Reports with filters " + json.dumps(filters) + "."
        )
        query = (
            """
            query Reports($filters: [ReportsFiltering], $search: String, $first: Int, $after: ID, $orderBy: ReportsOrdering, $orderMode: OrderingMode) {
                reports(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
        return self.opencti.process_multiple(result["data"]["reports"], with_pagination)

    """
        Read a Report object

        :param id: the id of the Report
        :param filters: the filters to apply if no id provided
        :return Report object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Reading Report {" + id + "}.")
            query = (
                """
                query Report($id: String!) {
                    report(id: $id) {
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
            return self.opencti.process_multiple_fields(result["data"]["report"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None

    """
        Read a Report object by stix_id or name

        :param type: the Stix-Domain-Entity type
        :param stix_id: the STIX ID of the Stix-Domain-Entity
        :param name: the name of the Stix-Domain-Entity
        :return Stix-Domain-Entity object
    """

    def get_by_stix_id_or_name(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        name = kwargs.get("name", None)
        published = kwargs.get("published", None)
        custom_attributes = kwargs.get("customAttributes", None)
        object_result = None
        if stix_id is not None:
            object_result = self.read(id=stix_id, customAttributes=custom_attributes)
        if object_result is None and name is not None and published is not None:
            published_final = parse(published).strftime("%Y-%m-%d")
            object_result = self.read(
                filters=[
                    {"key": "name", "values": [name]},
                    {"key": "published_day", "values": [published_final]},
                ],
                customAttributes=custom_attributes,
            )
        return object_result

    """
        Check if a report already contains a thing (Stix Object or Stix Relationship)
        :return Boolean
    """

    def contains_stix_object_or_stix_relationship(self, **kwargs):
        id = kwargs.get("id", None)
        stix_object_or_stix_relationship_id = kwargs.get(
            "stixObjectOrStixRelationshipId", None
        )
        if id is not None and stix_object_or_stix_relationship_id is not None:
            self.opencti.log(
                "info",
                "Checking StixObjectOrStixRelationship {"
                + stix_object_or_stix_relationship_id
                + "} in Report {"
                + id
                + "}",
            )
            query = """
                query TeportContainsStixObjectOrStixRelationship($id: String!, $stixObjectOrStixRelationshipId: String!) {
                    reportContainsStixObjectOrStixRelationship(id: $id, stixObjectOrStixRelationshipId: $objectId)
                }
            """
            result = self.opencti.query(
                query,
                {
                    "id": id,
                    "stixObjectOrStixRelationshipId": stix_object_or_stix_relationship_id,
                },
            )
            return result["data"]["reportContainsStixObjectOrStixRelationship"]
        else:
            self.opencti.log(
                "error", "[opencti_report] Missing parameters: id or entity_id",
            )

    """
        Create a Report object

        :param name: the name of the Report
        :return Report object
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
        name = kwargs.get("name", None)
        description = kwargs.get("description", "")
        report_types = kwargs.get("report_types", None)
        published = kwargs.get("published", None)
        x_opencti_graph_data = kwargs.get("x_opencti_graph_data", None)
        x_opencti_report_status = kwargs.get("x_opencti_report_status", None)

        if name is not None and description is not None and published is not None:
            self.opencti.log("info", "Creating Report {" + name + "}.")
            query = """
                mutation ReportAdd($input: ReportAddInput) {
                    reportAdd(input: $input) {
                        id
                        standard_id
                        entity_type
                        parent_types            
                    }
                }
            """
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
                        "name": name,
                        "description": description,
                        "report_types": report_types,
                        "published": published,
                        "x_opencti_graph_data": x_opencti_graph_data,
                        "x_opencti_report_status": x_opencti_report_status,
                    }
                },
            )
            return self.opencti.process_multiple_fields(result["data"]["reportAdd"])
        else:
            self.opencti.log(
                "error",
                "[opencti_report] Missing parameters: name and description and published and report_class",
            )

    """
         Create a Report object only if it not exists, update it on request

         :param name: the name of the Report
         :param description: the description of the Report
         :param published: the publication date of the Report
         :return Report object
     """

    def create(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        external_reference_id = kwargs.get("external_reference_id", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        external_references = kwargs.get("externalReferences", None)
        revoked = kwargs.get("revoked", None)
        confidence = kwargs.get("confidence", None)
        lang = kwargs.get("lang", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        name = kwargs.get("name", None)
        description = kwargs.get("description", "")
        report_types = kwargs.get("report_types", None)
        published = kwargs.get("published", None)
        x_opencti_graph_data = kwargs.get("x_opencti_graph_data", None)
        x_opencti_report_status = kwargs.get("x_opencti_report_status", None)
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
            ... on Report {
                name
                description
                report_types
                published
                aliases
                malware_types
                x_opencti_report_status
            }       
        """
        object_result = None
        if external_reference_id is not None:
            object_result = self.opencti.stix_domain_object.read(
                types=["Report"],
                filters=[
                    {"key": "hasExternalReference", "values": [external_reference_id]}
                ],
                customAttributes=custom_attributes,
            )
        if object_result is None and name is not None:
            object_result = self.get_by_stix_id_or_name(
                stix_id=stix_id,
                name=name,
                published=published,
                custom_attributes=custom_attributes,
            )
        if object_result is not None:
            if update or object_result["createdById"] == created_by:
                if object_result["name"] != name:
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
            if external_reference_id is not None:
                self.opencti.stix_domain_object.add_external_reference(
                    id=object_result["id"], external_reference_id=external_reference_id,
                )
            return object_result
        else:
            report = self.create_raw(
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
                name=name,
                description=description,
                report_types=report_types,
                published=published,
                x_opencti_graph_data=x_opencti_graph_data,
                x_opencti_report_status=x_opencti_report_status,
            )
            if external_reference_id is not None:
                self.opencti.stix_domain_object.add_external_reference(
                    id=report["id"], external_reference_id=external_reference_id,
                )
            return report

    """
        Add a Stix-Entity object to Report object (object_refs)

        :param id: the id of the Report
        :param entity_id: the id of the Stix-Entity
        :return Boolean
    """

    def add_stix_object_or_stix_relationship(self, **kwargs):
        id = kwargs.get("id", None)
        stix_object_or_stix_relationship_id = kwargs.get(
            "stixObjectOrStixRelationshipId", None
        )
        if id is not None and stix_object_or_stix_relationship_id is not None:
            if self.contains_stix_object_or_stix_relationship(
                id=id,
                stixObjectOrStixRelationshipId=stix_object_or_stix_relationship_id,
            ):
                return True
            self.opencti.log(
                "info",
                "Adding StixObjectOrStixRelationship {"
                + stix_object_or_stix_relationship_id
                + "} to Report {"
                + id
                + "}",
            )
            query = """
               mutation ReportEditRelationAdd($id: ID!, $input: StixMetaRelationshipAddInput) {
                   reportEdit(id: $id) {
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
                        "toId": stix_object_or_stix_relationship_id,
                        "relationship_type": "object",
                    },
                },
            )
            return True
        else:
            self.opencti.log(
                "error", "[opencti_report] Missing parameters: id and entity_id"
            )
            return False

    """
        Import a Report object from a STIX2 object

        :param stixObject: the Stix-Object Report
        :return Report object
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
                name=stix_object["name"],
                description=self.opencti.stix2.convert_markdown(
                    stix_object["description"]
                )
                if "description" in stix_object
                else "",
                report_types=stix_object["report_types"]
                if "report_types" in stix_object
                else None,
                published=stix_object["published"],
                x_opencti_graph_data=stix_object["x_opencti_graph_data"]
                if "x_opencti_graph_data" in stix_object
                else None,
                x_opencti_report_status=stix_object["x_opencti_report_status"]
                if "x_opencti_report_status" in stix_object
                else None,
                update=update,
            )
        else:
            self.opencti.log("error", "[opencti_report] Missing parameters: stixObject")

    """
        Export an Threat-Actor object in STIX2

        :param id: the id of the Threat-Actor
        :return Threat-Actor object
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
            report = dict()
            report["id"] = entity["stix_id"]
            report["type"] = "report"
            report["spec_version"] = SPEC_VERSION
            report["name"] = entity["name"]
            if self.opencti.not_empty(entity["stix_label"]):
                report["labels"] = entity["stix_label"]
            else:
                report["labels"] = ["report"]
            if self.opencti.not_empty(entity["description"]):
                report["description"] = entity["description"]
            report["published"] = self.opencti.stix2.format_date(entity["published"])
            report["created"] = self.opencti.stix2.format_date(entity["created"])
            report["modified"] = self.opencti.stix2.format_date(entity["modified"])
            if self.opencti.not_empty(entity["alias"]):
                report[CustomProperties.ALIASES] = entity["alias"]
            if self.opencti.not_empty(entity["report_class"]):
                report[CustomProperties.REPORT_CLASS] = entity["report_class"]
            if self.opencti.not_empty(entity["object_status"]):
                report[CustomProperties.OBJECT_STATUS] = entity["object_status"]
            if self.opencti.not_empty(entity["source_confidence_level"]):
                report[CustomProperties.SRC_CONF_LEVEL] = entity[
                    "source_confidence_level"
                ]
            if self.opencti.not_empty(entity["x_opencti_graph_data"]):
                report[CustomProperties.GRAPH_DATA] = entity["x_opencti_graph_data"]
            report[CustomProperties.ID] = entity["id"]
            return self.opencti.stix2.prepare_export(
                entity, report, mode, max_marking_definition_entity
            )
        else:
            self.opencti.log(
                "error", "[opencti_report] Missing parameters: id or entity"
            )

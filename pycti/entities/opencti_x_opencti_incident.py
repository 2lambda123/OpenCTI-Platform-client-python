# coding: utf-8

import json
from pycti.utils.constants import CustomProperties
from pycti.utils.opencti_stix2 import SPEC_VERSION


class XOpenctiIncident:
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
            aliases
            first_seen
            last_seen
            objective
        """

    """
        List Incident objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Incident objects
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
            "info", "Listing Incidents with filters " + json.dumps(filters) + "."
        )
        query = (
            """
            query XOpenctiIncidents($filters: [IncidentsFiltering], $search: String, $first: Int, $after: ID, $orderBy: IncidentsOrdering, $orderMode: OrderingMode) {
                xOpenctiIncidents(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
            result["data"]["xOpenctiIncidents"], with_pagination
        )

    """
        Read a X-Opencti-Incident object
        
        :param id: the id of the X-Opencti-Incident
        :param filters: the filters to apply if no id provided
        :return X-Opencti-Incident object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Reading Incident {" + id + "}.")
            query = (
                """
                query XOpenctiIncident($id: String!) {
                    xOpenctiIncident(id: $id) {
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
            return self.opencti.process_multiple_fields(
                result["data"]["xOpenctiIncident"]
            )
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log(
                "error", "[opencti_incident] Missing parameters: id or filters"
            )
            return None

    """
        Create a Incident object

        :param name: the name of the Incident
        :return Incident object
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
        aliases = kwargs.get("aliases", None)
        first_seen = kwargs.get("first_seen", None)
        last_seen = kwargs.get("last_seen", None)
        objective = kwargs.get("objective", None)

        if name is not None and description is not None:
            self.opencti.log("info", "Creating Incident {" + name + "}.")
            query = """
                mutation XOpenctiIncidentAdd($input: IncidentAddInput) {
                    xOpenctiIncidentAdd(input: $input) {
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
                        "aliases": aliases,
                        "first_seen": first_seen,
                        "last_seen": last_seen,
                        "objective": objective,
                    }
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["xOpenctiIncidentAdd"]
            )
        else:
            self.opencti.log("error", "Missing parameters: name and description")

    """
         Create a X-Opencti-Incident object only if it not exists, update it on request

         :param name: the name of the X-Opencti-Incident
         :return X-Opencti-Incident object
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
        name = kwargs.get("name", None)
        description = kwargs.get("description", "")
        aliases = kwargs.get("aliases", None)
        first_seen = kwargs.get("first_seen", None)
        last_seen = kwargs.get("last_seen", None)
        objective = kwargs.get("objective", None)
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
            ... on XOpenctiIncident {
                name
                description
                aliases
                first_seen
                last_seen
                objective
            }
        """
        object_result = self.opencti.stix_domain_object.get_by_stix_id_or_name(
            types=["X-Opencti-Incident"],
            stix_id=stix_id,
            name=name,
            customAttributes=custom_attributes,
        )
        if object_result is not None:
            if update or object_result["createdById"] == created_by:
                # name
                if object_result["name"] != name:
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
                # aliases
                if (
                    self.opencti.not_empty(aliases)
                    and object_result["aliases"] != aliases
                ):
                    if "aliases" in object_result:
                        new_aliases = object_result["aliases"] + list(
                            set(aliases) - set(object_result["aliases"])
                        )
                    else:
                        new_aliases = aliases
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="aliases", value=new_aliases
                    )
                    object_result["aliases"] = new_aliases
                # first_seen
                if first_seen is not None and object_result["first_seen"] != first_seen:
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="first_seen", value=first_seen
                    )
                    object_result["first_seen"] = first_seen
                # last_seen
                if last_seen is not None and object_result["last_seen"] != last_seen:
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="last_seen", value=last_seen
                    )
                    object_result["last_seen"] = last_seen
                # objective
                if (
                    self.opencti.not_empty(objective)
                    and object_result["objective"] != objective
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="objective", value=objective
                    )
                    object_result["objective"] = objective
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
                name=name,
                description=description,
                aliases=aliases,
                first_seen=first_seen,
                last_seen=last_seen,
                objective=objective,
            )

    """
        Import a X-Opencti-Incident object from a STIX2 object

        :param stixObject: the Stix-Object X-Opencti-Incident
        :return X-Opencti-Incident object
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
                aliases=self.opencti.stix2.pick_aliases(stix_object),
                objective=stix_object["objective"]
                if "objective" in stix_object
                else None,
                first_seen=stix_object["first_seen"]
                if "first_seen" in stix_object
                else None,
                last_seen=stix_object["last_seen"]
                if "last_seen" in stix_object
                else None,
                update=update,
            )
        else:
            self.opencti.log(
                "error", "[opencti_incident] Missing parameters: stixObject"
            )

    """
        Export an X-Opencti-Incident object in STIX2
    
        :param id: the id of the X-Opencti-Incident
        :return X-Opencti-Incident object
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
            incident = dict()
            incident["id"] = entity["stix_id"]
            incident["type"] = "x-opencti-incident"
            incident["spec_version"] = SPEC_VERSION
            incident["name"] = entity["name"]
            if self.opencti.not_empty(entity["stix_label"]):
                incident["labels"] = entity["stix_label"]
            else:
                incident["labels"] = ["x-opencti-incident"]
            if self.opencti.not_empty(entity["alias"]):
                incident["aliases"] = entity["alias"]
            if self.opencti.not_empty(entity["description"]):
                incident["description"] = entity["description"]
            if self.opencti.not_empty(entity["objective"]):
                incident["objective"] = entity["objective"]
            if self.opencti.not_empty(entity["first_seen"]):
                incident["first_seen"] = self.opencti.stix2.format_date(
                    entity["first_seen"]
                )
            if self.opencti.not_empty(entity["last_seen"]):
                incident["last_seen"] = self.opencti.stix2.format_date(
                    entity["last_seen"]
                )
            incident["created"] = self.opencti.stix2.format_date(entity["created"])
            incident["modified"] = self.opencti.stix2.format_date(entity["modified"])
            incident[CustomProperties.ID] = entity["id"]
            return self.opencti.stix2.prepare_export(
                entity, incident, mode, max_marking_definition_entity
            )
        else:
            self.opencti.log("error", "Missing parameters: id or entity")

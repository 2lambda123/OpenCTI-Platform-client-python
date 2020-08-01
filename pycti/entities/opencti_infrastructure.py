# coding: utf-8

import json
from pycti.utils.opencti_stix2 import SPEC_VERSION


class Infrastructure:
    """Main Infrastructure class for OpenCTI

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
            name
            description
            infrastructure_types
            first_seen
            last_seen
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
        """List Infrastructure objects

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
            "info", "Listing Infrastructures with filters " + json.dumps(filters) + "."
        )
        query = (
            """
            query Infrastructures($filters: [InfrastructuresFiltering], $search: String, $first: Int, $after: ID, $orderBy: InfrastructuresOrdering, $orderMode: OrderingMode) {
                infrastructures(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
            data = self.opencti.process_multiple(result["data"]["infrastructures"])
            final_data = final_data + data
            while result["data"]["infrastructures"]["pageInfo"]["hasNextPage"]:
                after = result["data"]["infrastructures"]["pageInfo"]["endCursor"]
                self.opencti.log("info", "Listing Infrastructures after " + after)
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
                data = self.opencti.process_multiple(result["data"]["infrastructures"])
                final_data = final_data + data
            return final_data
        else:
            return self.opencti.process_multiple(
                result["data"]["infrastructures"], with_pagination
            )

    def read(self, **kwargs):
        """Read an Infrastructure object

        read can be either used with a known OpenCTI entity `id` or by using a
        valid filter to search and return a single Infrastructure entity or None.

        The list method accepts the following \**kwargs.

        Note: either `id` or `filters` is required.

        :param str id: the id of the Threat-Actor
        :param list filters: the filters to apply if no id provided
        """

        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Reading Infrastructure {" + id + "}.")
            query = (
                """
                query Infrastructure($id: String!) {
                    infrastructure(id: $id) {
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
                result["data"]["infrastructure"]
            )
        elif filters is not None:
            result = self.list(filters=filters, customAttributes=custom_attributes)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log(
                "error", "[opencti_infrastructure] Missing parameters: id or filters"
            )
            return None

    """
        Create a Infrastructure object

        :param name: the name of the Infrastructure
        :return Infrastructure object
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
        description = kwargs.get("description", None)
        aliases = kwargs.get("aliases", None)
        infrastructure_types = kwargs.get("infrastructure_types", None)
        first_seen = kwargs.get("first_seen", None)
        last_seen = kwargs.get("last_seen", None)
        kill_chain_phases = kwargs.get("killChainPhases", None)

        if name is not None:
            self.opencti.log("info", "Creating Infrastructure {" + name + "}.")
            query = """
                mutation InfrastructureAdd($input: InfrastructureAddInput) {
                    infrastructureAdd(input: $input) {
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
                        "infrastructure_types": infrastructure_types,
                        "first_seen": first_seen,
                        "last_seen": last_seen,
                        "killChainPhases": kill_chain_phases,
                    }
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["infrastructureAdd"]
            )
        else:
            self.opencti.log(
                "error",
                "[opencti_infrastructure] Missing parameters: name and infrastructure_pattern and main_observable_type",
            )

    """
        Create a Infrastructure object only if it not exists, update it on request

        :param name: the name of the Infrastructure
        :return Infrastructure object
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
        description = kwargs.get("description", None)
        aliases = kwargs.get("aliases", None)
        infrastructure_types = kwargs.get("infrastructure_types", None)
        first_seen = kwargs.get("first_seen", None)
        last_seen = kwargs.get("last_seen", None)
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
            ... on Infrastructure {
                name
                description
                aliases
                infrastructure_types
                first_seen
                last_seen
            }
        """
        object_result = self.opencti.stix_domain_object.get_by_stix_id_or_name(
            types=["Infrastructure"],
            stix_id=stix_id,
            name=name,
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
                # confidence
                if (
                    self.opencti.not_empty(confidence)
                    and object_result["confidence"] != confidence
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="confidence", value=str(confidence)
                    )
                    object_result["confidence"] = confidence
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
                infrastructure_types=infrastructure_types,
                aliases=aliases,
                first_seen=first_seen,
                last_seen=last_seen,
                killChainPhases=kill_chain_phases,
            )

    """
        Import an Infrastructure object from a STIX2 object

        :param stixObject: the Stix-Object Infrastructure
        :return Infrastructure object
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
                infrastructure_types=stix_object["infrastructure_types"]
                if "infrastructure_types" in stix_object
                else "",
                first_seen=stix_object["first_seen"]
                if "first_seen" in stix_object
                else None,
                last_seen=stix_object["last_seen"]
                if "last_seen" in stix_object
                else None,
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
        Export an Infrastructure object in STIX2
    
        :param id: the id of the Infrastructure
        :return Infrastructure object
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
            infrastructure = dict()
            infrastructure["id"] = entity["stix_id"]
            infrastructure["type"] = "infrastructure"
            infrastructure["spec_version"] = SPEC_VERSION
            infrastructure["name"] = entity["name"]
            if self.opencti.not_empty(entity["stix_label"]):
                infrastructure["labels"] = entity["stix_label"]
            else:
                infrastructure["labels"] = ["infrastructure"]
            if self.opencti.not_empty(entity["description"]):
                infrastructure["description"] = entity["description"]
            infrastructure["pattern"] = entity["infrastructure_pattern"]
            infrastructure["valid_from"] = self.opencti.stix2.format_date(
                entity["valid_from"]
            )
            infrastructure["valid_until"] = self.opencti.stix2.format_date(
                entity["valid_until"]
            )
            if self.opencti.not_empty(entity["pattern_type"]):
                infrastructure["pattern_type"] = entity["pattern_type"]
            else:
                infrastructure["pattern_type"] = "stix"
            infrastructure["created"] = self.opencti.stix2.format_date(
                entity["created"]
            )
            infrastructure["modified"] = self.opencti.stix2.format_date(
                entity["modified"]
            )
            if self.opencti.not_empty(entity["alias"]):
                infrastructure[CustomProperties.ALIASES] = entity["alias"]
            if self.opencti.not_empty(entity["score"]):
                infrastructure[CustomProperties.SCORE] = entity["score"]
            infrastructure[CustomProperties.ID] = entity["id"]
            return self.opencti.stix2.prepare_export(
                entity, infrastructure, mode, max_marking_definition_entity
            )
        else:
            self.opencti.log("error", "Missing parameters: id or entity")

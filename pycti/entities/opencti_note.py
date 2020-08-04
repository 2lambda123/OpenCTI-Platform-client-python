# coding: utf-8

import json


class Note:
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
            attribute_abstract
            content
            authors
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
                        ... on XOpenCTIIncident {
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
        List Note objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Note objects
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
            "info", "Listing Notes with filters " + json.dumps(filters) + "."
        )
        query = (
            """
            query Notes($filters: [NotesFiltering], $search: String, $first: Int, $after: ID, $orderBy: NotesOrdering, $orderMode: OrderingMode) {
                notes(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
        return self.opencti.process_multiple(result["data"]["notes"], with_pagination)

    """
        Read a Note object

        :param id: the id of the Note
        :param filters: the filters to apply if no id provided
        :return Note object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Reading Note {" + id + "}.")
            query = (
                """
                query Note($id: String!) {
                    note(id: $id) {
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
            return self.opencti.process_multiple_fields(result["data"]["note"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None

    """
        Check if a note already contains a STIX entity
        
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
                + "} in Note {"
                + id
                + "}",
            )
            query = """
                query NoteContainsStixObjectOrStixRelationship($id: String!, $stixObjectOrStixRelationshipId: String!) {
                    noteContainsStixObjectOrStixRelationship(id: $id, stixObjectOrStixRelationshipId: $stixObjectOrStixRelationshipId)
                }
            """
            result = self.opencti.query(
                query,
                {
                    "id": id,
                    "stixObjectOrStixRelationshipId": stix_object_or_stix_relationship_id,
                },
            )
            return result["data"]["noteContainsStixObjectOrStixRelationship"]
        else:
            self.opencti.log(
                "error", "[opencti_note] Missing parameters: id or entity_id",
            )

    """
        Create a Note object

        :param name: the name of the Note
        :return Note object
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
        abstract = kwargs.get("abstract", None)
        content = kwargs.get("content", None)
        authors = kwargs.get("authors", None)

        if content is not None:
            self.opencti.log("info", "Creating Note {" + content + "}.")
            query = """
                mutation NoteAdd($input: NoteAddInput) {
                    noteAdd(input: $input) {
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
                        "attribute_abstract": abstract,
                        "content": content,
                        "authors": authors,
                    }
                },
            )
            return self.opencti.process_multiple_fields(result["data"]["noteAdd"])
        else:
            self.opencti.log(
                "error", "[opencti_note] Missing parameters: content",
            )

    """
         Create a Note object only if it not exists, update it on request

         :param name: the name of the Note
         :param description: the description of the Note
         :param published: the publication date of the Note
         :return Note object
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
        abstract = kwargs.get("abstract", None)
        content = kwargs.get("content", None)
        authors = kwargs.get("authors", None)
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
            ... on Note {
                attribute_abstract
                content
                authors
            }
        """
        object_result = self.read(id=stix_id, customAttributes=custom_attributes)
        if object_result is not None:
            if update or object_result["createdById"] == created_by:
                if (
                    abstract is not None
                    and object_result["attribute_abstract"] != abstract
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="attribute_abstract", value=abstract
                    )
                    object_result["attribute_abstract"] = abstract
                if content is not None and object_result["content"] != content:
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="content", value=content
                    )
                    object_result["content"] = content
            return object_result
        else:
            note = self.create_raw(
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
                abstract=abstract,
                content=content,
                authors=authors,
            )
            return note

    """
        Add a Stix-Entity object to Note object (object_refs)

        :param id: the id of the Note
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
                + "} to Note {"
                + id
                + "}",
            )
            query = """
               mutation NoteEdit($id: ID!, $input: StixMetaRelationshipAddInput) {
                   noteEdit(id: $id) {
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
                "error",
                "[opencti_note] Missing parameters: id and stix_object_or_stix_relationship_id",
            )
            return False

    """
        Import a Note object from a STIX2 object

        :param stixObject: the Stix-Object Note
        :return Note object
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
                abstract=self.opencti.stix2.convert_markdown(stix_object["abstract"])
                if "abstract" in stix_object
                else "",
                content=self.opencti.stix2.convert_markdown(stix_object["content"])
                if "content" in stix_object
                else "",
                authors=stix_object["authors"] if "authors" in stix_object else None,
                update=update,
            )
        else:
            self.opencti.log(
                "error", "[opencti_attack_pattern] Missing parameters: stixObject"
            )

    """
        Export a Note object in STIX2

        :param id: the id of the Note
        :return Note object
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
            note = dict()
            note["id"] = entity["stix_id"]
            note["type"] = "note"
            note["spec_version"] = SPEC_VERSION
            note["content"] = entity["content"]
            if self.opencti.not_empty(entity["stix_label"]):
                note["labels"] = entity["stix_label"]
            else:
                note["labels"] = ["note"]
            if self.opencti.not_empty(entity["description"]):
                note["abstract"] = entity["description"]
            elif self.opencti.not_empty(entity["name"]):
                note["abstract"] = entity["name"]
            note["created"] = self.opencti.stix2.format_date(entity["created"])
            note["modified"] = self.opencti.stix2.format_date(entity["modified"])
            if self.opencti.not_empty(entity["alias"]):
                note[CustomProperties.ALIASES] = entity["alias"]
            if self.opencti.not_empty(entity["name"]):
                note[CustomProperties.NAME] = entity["name"]
            if self.opencti.not_empty(entity["graph_data"]):
                note[CustomProperties.GRAPH_DATA] = entity["graph_data"]
            note[CustomProperties.ID] = entity["id"]
            return self.opencti.stix2.prepare_export(
                entity, note, mode, max_marking_definition_entity
            )
        else:
            self.opencti.log("error", "[opencti_note] Missing parameters: id or entity")

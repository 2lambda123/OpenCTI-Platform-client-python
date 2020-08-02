# coding: utf-8

import json


class CourseOfAction:
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
            x_opencti_aliases
        """

    """
        List Course-Of-Action objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Course-Of-Action objects
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
            "info",
            "Listing Course-Of-Actions with filters " + json.dumps(filters) + ".",
        )
        query = (
            """
            query CourseOfActions($filters: [CourseOfActionsFiltering], $search: String, $first: Int, $after: ID, $orderBy: CoursesOfActionOrdering, $orderMode: OrderingMode) {
                courseOfActions(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
            result["data"]["courseOfActions"], with_pagination
        )

    """
        Read a Course-Of-Action object
        
        :param id: the id of the Course-Of-Action
        :param filters: the filters to apply if no id provided
        :return Course-Of-Action object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Reading Course-Of-Action {" + id + "}.")
            query = (
                """
                query CourseOfAction($id: String!) {
                    courseOfAction(id: $id) {
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
                result["data"]["courseOfAction"]
            )
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log(
                "error", "[opencti_course_of_action] Missing parameters: id or filters"
            )
            return None

    """
        Create a Course Of Action object

        :param name: the name of the Course Of Action
        :return Course Of Action object
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
        x_opencti_aliases = kwargs.get("x_opencti_aliases", None)

        if name is not None and description is not None:
            self.opencti.log("info", "Creating Course Of Action {" + name + "}.")
            query = """
                mutation CourseOfActionAdd($input: CourseOfActionAddInput) {
                    courseOfActionAdd(input: $input) {
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
                        "x_opencti_aliases": x_opencti_aliases,
                    }
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["courseOfActionAdd"]
            )
        else:
            self.opencti.log(
                "error",
                "[opencti_course_of_action] Missing parameters: name and description",
            )

    """
        Create a Course Of Action object only if it not exists, update it on request

        :param name: the name of the Course Of Action
        :return Course Of Action object
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
        x_opencti_aliases = kwargs.get("x_opencti_aliases", None)
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
            ... on CourseOfAction {
                name
                description
                x_opencti_aliases
            } 
        """
        object_result = self.opencti.stix_domain_object.get_by_stix_id_or_name(
            types=["Course-Of-Action"],
            stix_id=stix_id,
            name=name,
            fieldName="x_opencti_alias",
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
                # alias
                if (
                    self.opencti.not_empty(x_opencti_aliases)
                    and object_result["x_opencti_aliases"] != x_opencti_aliases
                ):
                    if "x_opencti_aliases" in object_result:
                        new_aliases = object_result["x_opencti_aliases"] + list(
                            set(x_opencti_aliases)
                            - set(object_result["x_opencti_aliases"])
                        )
                    else:
                        new_aliases = x_opencti_aliases
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"],
                        key="x_opencti_aliases",
                        value=new_aliases,
                    )
                    object_result["x_opencti_aliases"] = new_aliases
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
                x_opencti_aliases=x_opencti_aliases,
            )

    """
        Import an Course-Of-Action object from a STIX2 object

        :param stixObject: the Stix-Object Course-Of-Action
        :return Course-Of-Action object
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
                x_opencti_aliases=self.opencti.stix2.pick_aliases(stix_object),
                update=update,
            )
        else:
            self.opencti.log(
                "error", "[opencti_course_of_action] Missing parameters: stixObject"
            )

    """
        Export an Course-Of-Action object in STIX2
    
        :param id: the id of the Course-Of-Action
        :return Course-Of-Action object
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
            course_of_action = dict()
            course_of_action["id"] = entity["stix_id"]
            course_of_action["type"] = "course-of-action"
            course_of_action["spec_version"] = entity["spec_version"]
            course_of_action["name"] = entity["name"]
            if self.opencti.not_empty(entity["stix_label"]):
                course_of_action["labels"] = entity["stix_label"]
            else:
                course_of_action["labels"] = ["course-of-action"]
            if self.opencti.not_empty(entity["description"]):
                course_of_action["description"] = entity["description"]
            course_of_action["created"] = self.opencti.stix2.format_date(
                entity["created"]
            )
            course_of_action["modified"] = self.opencti.stix2.format_date(
                entity["modified"]
            )
            if self.opencti.not_empty(entity["alias"]):
                course_of_action[CustomProperties.ALIASES] = entity["alias"]
            course_of_action[CustomProperties.ID] = entity["id"]
            return self.opencti.stix2.prepare_export(
                entity, course_of_action, mode, max_marking_definition_entity
            )
        else:
            self.opencti.log("error", "Missing parameters: id or entity")

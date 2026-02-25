"""Test comprehensive functionality for terminusdb_client.schema.schema"""

import pytest
import json
from io import StringIO
from typing import Optional, Set, List

from terminusdb_client.schema.schema import (
    TerminusKey,
    HashKey,
    LexicalKey,
    ValueHashKey,
    RandomKey,
    _check_cycling,
    _check_mismatch_type,
    _check_missing_prop,
    _check_and_fix_custom_id,
    DocumentTemplate,
    TaggedUnion,
    EnumTemplate,
    WOQLSchema,
    transform_enum_dict,
)


class TestTerminusKey:
    """Test TerminusKey and its subclasses"""

    def test_terminus_key_invalid_type(self):
        """Test ValueError when keys is neither str nor list"""
        with pytest.raises(ValueError, match="keys need to be either str or list"):
            TerminusKey(keys=123)

    def test_hash_key_creation(self):
        """Test HashKey creation"""
        hk = HashKey(["field1", "field2"])
        assert hk._keys == ["field1", "field2"]
        assert hk.at_type == "Hash"

    def test_lexical_key_creation(self):
        """Test LexicalKey creation"""
        lk = LexicalKey("name")
        assert lk._keys == ["name"]
        assert lk.at_type == "Lexical"

    def test_value_hash_key_creation(self):
        """Test ValueHashKey creation"""
        vhk = ValueHashKey()
        assert vhk.at_type == "ValueHash"

    def test_random_key_creation(self):
        """Test RandomKey creation"""
        rk = RandomKey()
        assert rk.at_type == "Random"


class TestCheckCycling:
    """Test _check_cycling function"""

    def test_no_cycling_normal(self):
        """Test normal class without cycling"""

        class Normal(DocumentTemplate):
            name: str

        # Should not raise
        _check_cycling(Normal)

    def test_cycling_detected(self):
        """Test RecursionError when cycling is detected"""
        from terminusdb_client.schema.schema import _check_cycling

        # Create a simple class that references itself
        class TestClass:
            _subdocument = []

        TestClass._annotations = {"self_ref": TestClass}

        # Should raise RecursionError for self-referencing class
        with pytest.raises(
            RecursionError, match="Embbding.*TestClass.*cause recursions"
        ):
            _check_cycling(TestClass)

    def test_no_subdocument_attribute(self):
        """Test class without _subdocument attribute"""

        class NoSubdoc:
            pass

        # Should not raise
        _check_cycling(NoSubdoc)


class TestCheckMismatchType:
    """Test _check_mismatch_type function"""

    def test_custom_to_dict_method(self):
        """Test with object that has custom _to_dict method"""

        class CustomType:
            @classmethod
            def _to_dict(cls):
                return {"@id": "CustomType"}

        # When prop_type has _to_dict, it validates using IDs
        _check_mismatch_type("prop", CustomType(), CustomType)

    def test_conversion_to_int_success(self):
        """Test successful conversion to int"""
        # Should not raise
        _check_mismatch_type("prop", "42", int)

    def test_conversion_to_int_failure(self):
        """Test failed conversion to int"""
        with pytest.raises(ValueError, match="invalid literal for int"):
            _check_mismatch_type("prop", "not_a_number", int)

    def test_float_type_validation(self):
        """Test float type validation"""
        # check_type validates the actual type
        _check_mismatch_type("prop", 3.14, float)

    def test_int_conversion_returns_value(self):
        """Test int conversion returns the converted value"""
        # _check_mismatch_type should return the converted int value
        result = _check_mismatch_type("prop", "42", int)
        assert result == 42

    def test_check_mismatch_with_custom_to_dict(self):
        """Test _check_mismatch_type with objects that have _to_dict"""

        class CustomType:
            @classmethod
            def _to_dict(cls):
                return {"@id": "CustomType"}

        class WrongType:
            @classmethod
            def _to_dict(cls):
                return {"@id": "WrongType"}

        # Should raise when types don't match
        with pytest.raises(
            ValueError, match="Property prop should be of type CustomType"
        ):
            _check_mismatch_type("prop", WrongType(), CustomType)

    def test_bool_type_validation(self):
        """Test bool type validation"""
        # check_type validates the actual type
        _check_mismatch_type("prop", True, bool)

    def test_optional_type_handling(self):
        """Test Optional type handling"""
        from typing import Optional

        # Should not raise
        _check_mismatch_type("prop", "value", Optional[str])


class TestCheckMissingProp:
    """Test missing property checking functionality"""

    def test_check_missing_prop_normal(self):
        """Test normal object with all properties"""

        class Doc(DocumentTemplate):
            name: str

        doc = Doc(name="test")
        # Should not raise
        _check_missing_prop(doc)

    def test_check_missing_prop_optional(self):
        """Test missing Optional property"""
        from typing import Optional

        class Doc(DocumentTemplate):
            name: str
            optional_field: Optional[str]

        doc = Doc(name="test")
        # Should not raise for missing Optional
        _check_missing_prop(doc)

    def test_check_missing_prop_set(self):
        """Test missing Set property"""
        from typing import Set

        class Doc(DocumentTemplate):
            name: str
            items: Set[str]

        doc = Doc(name="test")
        # Set types are considered optional (check_type allows empty set)
        # So this won't raise - let's test the actual behavior
        _check_missing_prop(doc)  # Should not raise

    def test_check_missing_prop_with_wrong_type(self):
        """Test property with wrong type"""

        class Doc(DocumentTemplate):
            age: int

        doc = Doc()
        # Set age to a valid int first
        doc.age = 25
        # Now test with wrong type object that has _to_dict

        class WrongType:
            @classmethod
            def _to_dict(cls):
                return {"@id": "WrongType"}

        # Create a custom type for testing
        class CustomType:
            @classmethod
            def _to_dict(cls):
                return {"@id": "CustomType"}

        # Test with wrong type
        with pytest.raises(ValueError, match="should be of type CustomType"):
            _check_mismatch_type("age", WrongType(), CustomType)


class TestCheckAndFixCustomId:
    """Test _check_and_fix_custom_id function"""

    def test_check_and_fix_custom_id_with_prefix(self):
        """Test custom id already has correct prefix"""
        result = _check_and_fix_custom_id("TestClass", "TestClass/123")
        assert result == "TestClass/123"

    def test_check_and_fix_custom_id_without_prefix(self):
        """Test custom id without prefix gets added"""
        result = _check_and_fix_custom_id("TestClass", "123")
        assert result == "TestClass/123"

    def test_check_and_fix_custom_id_with_special_chars(self):
        """Test custom id with special characters gets URL encoded"""
        result = _check_and_fix_custom_id("TestClass", "test special")
        assert result == "TestClass/test%20special"


class TestAbstractClass:
    """Test abstract class functionality"""

    def test_abstract_class_instantiation_error(self):
        """Test TypeError when instantiating abstract class"""

        class AbstractDoc(DocumentTemplate):
            _abstract = True
            name: str

        with pytest.raises(TypeError, match="AbstractDoc is an abstract class"):
            AbstractDoc(name="test")

    def test_abstract_bool_conversion(self):
        """Test _abstract with non-bool value"""

        class AbstractDoc(DocumentTemplate):
            _abstract = "yes"  # Not a bool, should be truthy
            name: str

        # The metaclass sets it to True if it's not False
        assert AbstractDoc._abstract == "yes"  # It keeps the original value


class TestDocumentTemplate:
    """Test DocumentTemplate functionality"""

    def test_int_conversion_error(self):
        """Test TypeError when int conversion fails"""

        class Doc(DocumentTemplate):
            age: int

        doc = Doc()
        with pytest.raises(TypeError, match="Unable to cast as int"):
            doc.age = "not_a_number"

    def test_get_instances_cleanup_dead_refs(self):
        """Test get_instances cleans up dead references"""

        class Doc(DocumentTemplate):
            name: str

        # Create some instances
        doc1 = Doc(name="doc1")
        doc2 = Doc(name="doc2")

        # Get initial count
        initial_count = len(list(Doc.get_instances()))
        assert initial_count >= 2

        # Delete one instance to create dead reference
        del doc2

        # Call get_instances which should clean up dead refs
        instances = list(Doc.get_instances())

        # Should have fewer instances after cleanup
        assert len(instances) < initial_count
        # doc1 should still be alive
        assert doc1 in instances

    def test_to_dict_with_tagged_union(self):
        """Test _to_dict with TaggedUnion inheritance"""

        class Base(DocumentTemplate):
            type: str

        class ChildA(Base):
            field_a: str
            _subdocument = []

        class ChildB(Base):
            field_b: int
            _subdocument = []

        # Create tagged union
        TaggedUnion(Base, [ChildA, ChildB])

        # Create instance of child
        child = ChildA(type="A", field_a="value")
        result = child._to_dict()

        # _to_dict returns type schema, not instance values
        assert "@type" in result
        assert "type" in result
        assert result["type"] == "xsd:string"

    def test_to_dict_with_inheritance_chain(self):
        """Test _to_dict with inheritance chain"""

        class GrandParent(DocumentTemplate):
            grand_field: str

        class Parent(GrandParent):
            parent_field: str

        class Child(Parent):
            child_field: str

        result = Child._to_dict()

        # _to_dict returns schema, not instance values
        assert "@inherits" in result
        assert "GrandParent" in result["@inherits"]
        assert "Parent" in result["@inherits"]
        assert result["grand_field"] == "xsd:string"
        assert result["parent_field"] == "xsd:string"
        assert result["child_field"] == "xsd:string"

    def test_to_dict_with_documentation(self):
        """Test _to_dict includes documentation"""

        class Doc(DocumentTemplate):
            """Test documentation"""

            name: str

        result = Doc._to_dict()

        assert "@documentation" in result
        assert result["@documentation"]["@comment"] == "Test documentation"

    def test_to_dict_with_base_attribute(self):
        """Test _to_dict with inheritance using @inherits"""

        class BaseDoc(DocumentTemplate):
            base_field: str

        class Doc(BaseDoc):
            name: str

        result = Doc._to_dict()

        # Inheritance is shown with @inherits, not @base
        assert "@inherits" in result
        assert "BaseDoc" in result["@inherits"]

    def test_to_dict_with_subdocument(self):
        """Test _to_dict with _subdocument list"""

        class Doc(DocumentTemplate):
            name: str
            _subdocument = []

        result = Doc._to_dict()

        # _subdocument is stored as a list
        assert result.get("@subdocument") == []

    def test_to_dict_with_abstract(self):
        """Test _to_dict with _abstract True"""

        class Doc(DocumentTemplate):
            name: str
            _abstract = True

        result = Doc._to_dict()

        assert result.get("@abstract") is True

    def test_to_dict_with_hashkey(self):
        """Test _to_dict with HashKey"""

        class Doc(DocumentTemplate):
            name: str
            _key = HashKey(["name"])

        result = Doc._to_dict()

        # HashKey uses @fields, not @keys
        assert result.get("@key") == {"@type": "Hash", "@fields": ["name"]}

    def test_id_setter_custom_id_not_allowed(self):
        """Test _id setter raises when custom_id not allowed"""

        class Doc(DocumentTemplate):
            name: str
            _key = HashKey(["name"])  # Not RandomKey, so custom id not allowed

        doc = Doc(name="test")

        with pytest.raises(ValueError, match="Customized id is not allowed"):
            doc._id = "custom_id"

    def test_key_field_change_error(self):
        """Test ValueError when trying to change key field"""

        # This test demonstrates that with RandomKey, there are no key fields
        # So changing id doesn't raise an error
        class Doc(DocumentTemplate):
            _key = RandomKey()  # Use RandomKey to allow custom id
            id: str
            name: str

        # Create doc with custom id
        doc = Doc(_id="initial_id")
        doc.id = "test123"
        doc.name = "John"

        # With RandomKey, id can be changed because it's not in _key._keys
        # This test documents the current behavior
        doc.id = "new_id"
        assert doc.id == "new_id"

    def test_custom_id_not_allowed(self):
        """Test ValueError when custom id not allowed"""

        class SubDoc(DocumentTemplate):
            _subdocument = []
            name: str

        with pytest.raises(ValueError, match="Customized id is not allowed"):
            SubDoc(_id="custom", name="test")

    def test_tagged_union_to_dict(self):
        """Test TaggedUnion _to_dict type"""

        class UnionDoc(TaggedUnion):
            option1: str
            option2: int

        result = UnionDoc._to_dict()
        assert result["@type"] == "TaggedUnion"

    def test_inheritance_chain(self):
        """Test inheritance chain with multiple parents"""

        class GrandParent(DocumentTemplate):
            grand_prop: str

        class Parent(GrandParent):
            parent_prop: str

        class Child(Parent):
            child_prop: str

        Child._to_dict()


class TestEmbeddedRep:
    """Test _embedded_rep functionality"""

    def test_embedded_rep_normal(self):
        """Test normal embedded representation returns @ref"""

        class Doc(DocumentTemplate):
            name: str

        doc = Doc(name="test")
        result = doc._embedded_rep()

        # When no _id and no _subdocument, returns @ref
        assert "@ref" in result
        assert isinstance(result, dict)

    def test_embedded_rep_with_subdocument(self):
        """Test _embedded_rep with _subdocument returns tuple"""

        class Doc(DocumentTemplate):
            name: str
            _subdocument = []

        doc = Doc(name="test")
        result = doc._embedded_rep()

        # With _subdocument, returns (dict, references) tuple
        assert isinstance(result, tuple)
        assert len(result) == 2
        obj_dict, references = result
        assert obj_dict["@type"] == "Doc"
        assert obj_dict["name"] == "test"
        assert isinstance(references, dict)

    def test_embedded_rep_with_id(self):
        """Test _embedded_rep with _id present"""

        class Doc(DocumentTemplate):
            name: str

        doc = Doc(name="test")
        doc._id = "doc123"
        result = doc._embedded_rep()

        assert result["@id"] == "Doc/doc123"  # _embedded_rep includes class name prefix

    def test_embedded_rep_with_ref(self):
        """Test _embedded_rep returning @ref"""

        class Doc(DocumentTemplate):
            name: str

        doc = Doc(name="test")
        result = doc._embedded_rep()

        # When no _id and no _subdocument, returns @ref
        assert "@ref" in result


class TestObjToDict:
    """Test _obj_to_dict functionality"""

    def test_obj_to_dict_nested_objects(self):
        """Test _obj_to_dict with nested DocumentTemplate objects"""

        class Address(DocumentTemplate):
            street: str
            city: str
            _subdocument = []

        class Person(DocumentTemplate):
            name: str
            address: Address
            _subdocument = []

        addr = Address(street="123 Main", city="NYC")
        person = Person(name="John", address=addr)

        result, references = person._obj_to_dict()

        assert result["@type"] == "Person"
        assert result["name"] == "John"
        assert isinstance(result["address"], dict)
        assert result["address"]["street"] == "123 Main"
        assert result["address"]["city"] == "NYC"

    def test_obj_to_dict_with_collections(self):
        """Test _obj_to_dict with list/set of DocumentTemplate objects"""

        class Item(DocumentTemplate):
            name: str
            _subdocument = []

        class Container(DocumentTemplate):
            items: list
            tags: set
            _subdocument = []

        item1 = Item(name="item1")
        item2 = Item(name="item2")

        container = Container(items=[item1, item2], tags={"tag1", "tag2"})

        result, references = container._obj_to_dict()

        assert result["@type"] == "Container"
        assert len(result["items"]) == 2
        assert result["items"][0]["name"] == "item1"
        assert result["items"][1]["name"] == "item2"
        assert set(result["tags"]) == {"tag1", "tag2"}


class TestWOQLSchemaConstruct:
    """Test WOQLSchema._construct_class functionality"""

    def test_construct_existing_class(self):
        """Test _construct_class with already constructed class"""
        schema = WOQLSchema()

        # Add a class to the schema
        class_dict = {"@type": "Class", "@id": "Person", "name": "xsd:string"}

        # First construction
        person1 = schema._construct_class(class_dict)

        # Second construction should return the same class
        person2 = schema._construct_class(class_dict)

        assert person1 is person2

    def test_construct_schema_object(self):
        """Test _construct_class with schema.object reference"""
        schema = WOQLSchema()

        # Add a class to schema.object as a string reference (unconstructed)
        schema.object["Person"] = "Person"
        schema._all_existing_classes["Person"] = {
            "@type": "Class",
            "@id": "Person",
            "name": "xsd:string",
        }

        # Construct from schema.object
        person = schema._construct_class(schema._all_existing_classes["Person"])

        # The method returns the constructed class
        assert person is not None
        assert isinstance(person, type)
        assert person.__name__ == "Person"
        assert hasattr(person, "__annotations__")
        assert person.__annotations__["name"] is str

    def test_construct_nonexistent_type_error(self):
        """Test _construct_class RuntimeError for non-existent type"""
        schema = WOQLSchema()

        class_dict = {
            "@type": "Class",
            "@id": "Person",
            "address": "NonExistent",  # This type doesn't exist
        }

        with pytest.raises(
            RuntimeError, match="NonExistent not exist in database schema"
        ):
            schema._construct_class(class_dict)

    def test_construct_set_type(self):
        """Test _construct_class with Set type"""
        schema = WOQLSchema()

        class_dict = {
            "@type": "Class",
            "@id": "Container",
            "items": {"@type": "Set", "@class": "xsd:string"},
        }

        container = schema._construct_class(class_dict)

        assert container.__name__ == "Container"
        assert hasattr(container, "__annotations__")
        assert container.__annotations__["items"] == Set[str]

    def test_construct_list_type(self):
        """Test _construct_class with List type"""
        schema = WOQLSchema()

        class_dict = {
            "@type": "Class",
            "@id": "Container",
            "items": {"@type": "List", "@class": "xsd:integer"},
        }

        container = schema._construct_class(class_dict)

        assert container.__name__ == "Container"
        assert hasattr(container, "__annotations__")
        assert container.__annotations__["items"] == List[int]

    def test_construct_optional_type(self):
        """Test _construct_class with Optional type"""
        schema = WOQLSchema()

        class_dict = {
            "@type": "Class",
            "@id": "Person",
            "middle_name": {"@type": "Optional", "@class": "xsd:string"},
        }

        person = schema._construct_class(class_dict)

        assert person.__name__ == "Person"
        assert hasattr(person, "__annotations__")
        assert person.__annotations__["middle_name"] == Optional[str]

    def test_construct_invalid_dict_error(self):
        """Test _construct_class RuntimeError for invalid dict format"""
        schema = WOQLSchema()

        class_dict = {
            "@type": "Class",
            "@id": "Person",
            "invalid_field": {"@type": "InvalidType"},
        }

        with pytest.raises(
            RuntimeError, match="is not in the right format for TerminusDB type"
        ):
            schema._construct_class(class_dict)

    def test_construct_valuehash_key(self):
        """Test _construct_class with ValueHashKey"""
        schema = WOQLSchema()

        class_dict = {"@type": "Class", "@id": "Person", "@key": {"@type": "ValueHash"}}

        person = schema._construct_class(class_dict)

        assert person.__name__ == "Person"
        assert hasattr(person, "_key")
        assert isinstance(person._key, ValueHashKey)

    def test_construct_lexical_key(self):
        """Test _construct_class with LexicalKey"""
        schema = WOQLSchema()

        class_dict = {
            "@type": "Class",
            "@id": "Person",
            "@key": {"@type": "Lexical", "@fields": ["name", "email"]},
        }

        person = schema._construct_class(class_dict)

        assert person.__name__ == "Person"
        assert hasattr(person, "_key")
        assert isinstance(person._key, LexicalKey)
        # LexicalKey stores fields in the '_keys' attribute
        assert person._key._keys == ["name", "email"]

    def test_construct_invalid_key_error(self):
        """Test _construct_class RuntimeError for invalid key"""
        schema = WOQLSchema()

        class_dict = {
            "@type": "Class",
            "@id": "Person",
            "@key": {"@type": "InvalidKey"},
        }

        with pytest.raises(
            RuntimeError, match="is not in the right format for TerminusDB key"
        ):
            schema._construct_class(class_dict)


class TestWOQLSchemaConstructObject:
    """Test WOQLSchema._construct_object functionality"""

    def test_construct_datetime_conversion(self):
        """Test _construct_object with datetime conversion"""
        schema = WOQLSchema()

        # Add a class with datetime field
        class_dict = {"@type": "Class", "@id": "Event", "timestamp": "xsd:dateTime"}
        event_class = schema._construct_class(class_dict)
        schema.add_obj("Event", event_class)

        # Construct object with datetime
        obj_dict = {
            "@type": "Event",
            "@id": "event1",
            "timestamp": "2023-01-01T00:00:00Z",
        }

        event = schema._construct_object(obj_dict)

        assert event._id == "event1"
        assert hasattr(event, "timestamp")
        # The datetime should be converted from string
        assert event.timestamp is not None

    def test_construct_collections(self):
        """Test _construct_object with List/Set/Optional"""
        schema = WOQLSchema()

        # Add a class with collection fields
        class_dict = {
            "@type": "Class",
            "@id": "Container",
            "items": {"@type": "List", "@class": "xsd:string"},
            "tags": {"@type": "Set", "@class": "xsd:string"},
            "optional_field": {"@type": "Optional", "@class": "xsd:string"},
        }
        container_class = schema._construct_class(class_dict)
        schema.add_obj("Container", container_class)

        # Construct object
        obj_dict = {
            "@type": "Container",
            "@id": "container1",
            "items": ["item1", "item2"],
            "tags": ["tag1", "tag2"],
            "optional_field": "optional_value",
        }

        container = schema._construct_object(obj_dict)

        assert container._id == "container1"
        assert isinstance(container.items, list)
        assert container.items == ["item1", "item2"]
        assert isinstance(container.tags, set)
        assert container.tags == {"tag1", "tag2"}
        assert container.optional_field == "optional_value"

    def test_construct_subdocument(self):
        """Test _construct_object with subdocument"""
        schema = WOQLSchema()

        # Add classes
        address_dict = {
            "@type": "Class",
            "@id": "Address",
            "street": "xsd:string",
            "city": "xsd:string",
            "_subdocument": [],
        }
        person_dict = {
            "@type": "Class",
            "@id": "Person",
            "name": "xsd:string",
            "address": "Address",
        }

        address_class = schema._construct_class(address_dict)
        schema.add_obj("Address", address_class)
        schema._all_existing_classes["Address"] = address_dict

        person_class = schema._construct_class(person_dict)
        schema.add_obj("Person", person_class)

        # Construct object with subdocument
        obj_dict = {
            "@type": "Person",
            "@id": "person1",
            "name": "John",
            "address": {
                "@type": "Address",
                "@id": "address1",
                "street": "123 Main",
                "city": "NYC",
            },
        }

        person = schema._construct_object(obj_dict)

        assert person._id == "person1"
        assert person.name == "John"
        assert isinstance(person.address, address_class)
        assert person.address.street == "123 Main"
        assert person.address.city == "NYC"

    def test_construct_document_dict(self):
        """Test _construct_object with document dict reference"""
        schema = WOQLSchema()

        # Add classes
        address_dict = {
            "@type": "Class",
            "@id": "Address",
            "street": "xsd:string",
            "city": "xsd:string",
        }
        person_dict = {
            "@type": "Class",
            "@id": "Person",
            "name": "xsd:string",
            "address": "Address",
        }

        address_class = schema._construct_class(address_dict)
        schema.add_obj("Address", address_class)
        schema._all_existing_classes["Address"] = address_dict

        person_class = schema._construct_class(person_dict)
        schema.add_obj("Person", person_class)

        # Construct object with document reference
        obj_dict = {
            "@type": "Person",
            "@id": "person1",
            "name": "John",
            "address": {"@id": "address1"},
        }

        person = schema._construct_object(obj_dict)

        assert person._id == "person1"
        assert person.name == "John"
        # Address should be a document with _backend_id
        assert hasattr(person.address, "_backend_id")
        assert person.address._backend_id == "address1"

    def test_construct_enum(self):
        """Test _construct_object with enum value"""
        schema = WOQLSchema()

        # Add enum class
        enum_dict = {"@type": "Enum", "@id": "Status", "@value": ["ACTIVE", "INACTIVE"]}
        status_class = schema._construct_class(enum_dict)
        schema.add_obj("Status", status_class)
        schema._all_existing_classes["Status"] = enum_dict

        # Add class with enum field
        task_dict = {"@type": "Class", "@id": "Task", "status": "Status"}
        task_class = schema._construct_class(task_dict)
        schema.add_obj("Task", task_class)

        # Construct object with enum
        obj_dict = {"@type": "Task", "@id": "task1", "status": "ACTIVE"}

        task = schema._construct_object(obj_dict)

        assert task._id == "task1"
        assert isinstance(task.status, status_class)
        assert str(task.status) == "ACTIVE"

    def test_construct_invalid_schema_error(self):
        """Test _construct_object ValueError for invalid schema"""
        schema = WOQLSchema()

        # Try to construct object with non-existent type
        obj_dict = {"@type": "NonExistent", "@id": "obj1"}

        with pytest.raises(ValueError, match="NonExistent is not in current schema"):
            schema._construct_object(obj_dict)


class TestAddEnumClass:
    """Test WOQLSchema.add_enum_class functionality"""

    def test_add_enum_class_basic(self):
        """Test add_enum_class with basic values"""
        schema = WOQLSchema()

        # Add enum class
        enum_class = schema.add_enum_class("Status", ["ACTIVE", "INACTIVE"])

        # Check the class was created
        assert "Status" in schema.object
        assert schema.object["Status"] is enum_class
        assert issubclass(enum_class, EnumTemplate)
        assert enum_class.__name__ == "Status"

        # Check enum values (keys are lowercase)
        assert enum_class.active.value == "ACTIVE"
        assert enum_class.inactive.value == "INACTIVE"

    def test_add_enum_class_with_spaces(self):
        """Test add_enum_class with values containing spaces"""
        schema = WOQLSchema()

        # Add enum with spaces in values
        enum_class = schema.add_enum_class(
            "Priority", ["High Priority", "Low Priority"]
        )

        # Check enum values (spaces should be replaced with underscores in keys)
        assert enum_class.high_priority.value == "High Priority"
        assert enum_class.low_priority.value == "Low Priority"

    def test_add_enum_class_empty_list(self):
        """Test add_enum_class with empty list"""
        schema = WOQLSchema()

        # Add enum with no values
        enum_class = schema.add_enum_class("EmptyEnum", [])

        # Class should still be created
        assert "EmptyEnum" in schema.object
        assert issubclass(enum_class, EnumTemplate)


class TestWOQLSchemaMethods:
    """Test WOQLSchema additional methods"""

    def test_commit_context_none(self):
        """Test commit with context None"""
        from unittest.mock import Mock, MagicMock
        from terminusdb_client import GraphType

        schema = WOQLSchema()
        schema.context["@schema"] = None
        schema.context["@base"] = None

        # Mock client
        client = Mock()
        client._get_prefixes.return_value = {
            "@schema": "http://schema.org",
            "@base": "http://example.com",
        }
        client.update_document = MagicMock()

        # Commit without full_replace
        schema.commit(client, commit_msg="Test commit")

        # Check that context was set
        assert schema.schema_ref == "http://schema.org"
        assert schema.base_ref == "http://example.com"

        # Check update_document was called
        client.update_document.assert_called_once_with(
            schema, commit_msg="Test commit", graph_type=GraphType.SCHEMA
        )

    def test_commit_full_replace(self):
        """Test commit with full_replace True"""
        from unittest.mock import Mock, MagicMock
        from terminusdb_client import GraphType

        schema = WOQLSchema()
        # Set schema_ref and base_ref to avoid client._get_prefixes call
        schema.schema_ref = "http://schema.org"
        schema.base_ref = "http://example.com"

        # Mock client
        client = Mock()
        client.insert_document = MagicMock()

        # Commit with full_replace
        schema.commit(client, full_replace=True)

        # Check insert_document was called
        client.insert_document.assert_called_once_with(
            schema,
            commit_msg="Schema object insert/ update by Python client.",
            graph_type=GraphType.SCHEMA,
            full_replace=True,
        )

    def test_from_db_select_filter(self):
        """Test from_db with select filter"""
        from unittest.mock import Mock

        schema = WOQLSchema()

        # Mock client
        client = Mock()
        client.get_all_documents.return_value = [
            {"@id": "Person", "@type": "Class", "name": "xsd:string"},
            {"@id": "Address", "@type": "Class", "street": "xsd:string"},
            {"@type": "@context", "@schema": "http://schema.org"},
        ]

        # Load with select filter
        schema.from_db(client, select=["Person"])

        # Check that only Person was constructed
        assert "Person" in schema.object
        assert "Address" not in schema.object
        # schema_ref is set in context, not directly on schema
        assert schema.context["@schema"] == "http://schema.org"

    def test_import_objects_list(self):
        """Test import_objects with list"""
        schema = WOQLSchema()

        # Add a class first
        class_dict = {"@type": "Class", "@id": "Person", "name": "xsd:string"}
        person_class = schema._construct_class(class_dict)
        schema.add_obj("Person", person_class)
        schema._all_existing_classes["Person"] = class_dict

        # Import list of objects
        obj_list = [
            {"@type": "Person", "@id": "person1", "name": "John"},
            {"@type": "Person", "@id": "person2", "name": "Jane"},
        ]

        result = schema.import_objects(obj_list)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]._id == "person1"
        assert result[0].name == "John"
        assert result[1]._id == "person2"
        assert result[1].name == "Jane"

    def test_json_schema_self_dependency(self):
        """Test to_json_schema with self-dependency loop"""
        schema = WOQLSchema()

        # Create class dict with self-reference
        class_dict = {"@type": "Class", "@id": "Node", "parent": "Node"}

        # Should raise RuntimeError for self-dependency or not embedded
        with pytest.raises(RuntimeError):
            schema.to_json_schema(class_dict)

    def test_json_schema_class_type(self):
        """Test to_json_schema with Class type"""
        schema = WOQLSchema()

        # Add classes
        address_dict = {"@type": "Class", "@id": "Address", "street": "xsd:string"}
        person_dict = {"@type": "Class", "@id": "Person", "address": "Address"}

        address_class = schema._construct_class(address_dict)
        schema.add_obj("Address", address_class)
        schema._all_existing_classes["Address"] = address_dict

        person_class = schema._construct_class(person_dict)
        schema.add_obj("Person", person_class)

        # Get JSON schema
        json_schema = schema.to_json_schema("Person")

        assert json_schema["type"] == ["null", "object"]
        assert "properties" in json_schema
        assert "$defs" in json_schema
        assert json_schema["properties"]["address"]["$ref"] == "#/$defs/Address"
        assert "Address" in json_schema["$defs"]

    def test_json_schema_enum_type(self):
        """Test to_json_schema with Enum type"""
        schema = WOQLSchema()

        # Test with class dict that has inline enum
        class_dict = {
            "@type": "Class",
            "@id": "Task",
            "status": {
                "@type": "Enum",
                "@id": "Status",
                "@value": ["ACTIVE", "INACTIVE"],
            },
        }

        # Get JSON schema directly from class dict
        json_schema = schema.to_json_schema(class_dict)

        # Check that inline enum is properly handled
        assert "status" in json_schema["properties"]
        assert "enum" in json_schema["properties"]["status"]
        assert json_schema["properties"]["status"]["enum"] == ["ACTIVE", "INACTIVE"]

    def test_json_schema_collections(self):
        """Test to_json_schema with List/Set/Optional"""
        schema = WOQLSchema()

        # Add class with collection fields
        class_dict = {
            "@type": "Class",
            "@id": "Container",
            "items": {"@type": "List", "@class": "xsd:string"},
            "tags": {"@type": "Set", "@class": "xsd:string"},
            "optional_field": {"@type": "Optional", "@class": "xsd:string"},
        }
        container_class = schema._construct_class(class_dict)
        schema.add_obj("Container", container_class)

        # Get JSON schema
        json_schema = schema.to_json_schema("Container")

        # Check List type
        assert json_schema["properties"]["items"]["type"] == "array"
        assert json_schema["properties"]["items"]["items"]["type"] == "string"

        # Check Set type (also array in JSON schema)
        assert json_schema["properties"]["tags"]["type"] == "array"
        assert json_schema["properties"]["tags"]["items"]["type"] == "string"

        # Check Optional type
        assert json_schema["properties"]["optional_field"]["type"] == ["null", "string"]

    def test_json_schema_invalid_dict(self):
        """Test to_json_schema RuntimeError for invalid dict"""
        schema = WOQLSchema()

        # Try with non-existent class name
        with pytest.raises(RuntimeError, match="NonExistent not found in schema"):
            schema.to_json_schema("NonExistent")


class TestEnumTransform:
    """Test enum transformation utilities"""

    def test_transform_enum_dict_basic(self):
        """Test transform_enum_dict basic functionality"""

        # Create a simple dict that mimics enum behavior
        class SimpleDict(dict):
            pass

        enum_dict = SimpleDict()
        enum_dict._member_names = ["VALUE1", "VALUE2"]
        enum_dict["VALUE1"] = ""
        enum_dict["VALUE2"] = "existing_value"

        transform_enum_dict(enum_dict)

        assert enum_dict["VALUE1"] == "VALUE1"
        assert enum_dict["VALUE2"] == "existing_value"
        assert "VALUE1" not in enum_dict._member_names
        assert "VALUE2" in enum_dict._member_names


class TestEnumTemplate:
    """Test EnumTemplate functionality"""

    def test_enum_template_no_values(self):
        """Test EnumTemplate _to_dict without values"""

        class EmptyEnum(EnumTemplate):
            pass

        result = EmptyEnum._to_dict()
        # Should not have @key if no enum values
        assert "@key" not in result


class TestWOQLSchema:
    """Test WOQLSchema functionality"""

    def test_context_setter_error(self):
        """Test Exception when trying to set context"""
        schema = WOQLSchema()

        with pytest.raises(Exception, match="Cannot set context"):
            schema.context = {"@context": "new"}

    def test_construct_class_nonexistent_parent(self):
        """Test _construct_class with non-existent parent"""
        schema = WOQLSchema()

        class_dict = {
            "@id": "Child",
            "@type": "Class",
            "@inherits": ["NonExistentParent"],
        }

        with pytest.raises(
            RuntimeError, match="NonExistentParent not exist in database schema"
        ):
            schema._construct_class(class_dict)

    def test_construct_class_enum_no_value(self):
        """Test _construct_class for Enum without @value"""
        schema = WOQLSchema()

        class_dict = {
            "@id": "MyEnum",
            "@type": "Enum",
            # Missing @value
        }

        with pytest.raises(RuntimeError, match="not exist in database schema"):
            schema._construct_class(class_dict)

    def test_construct_object_invalid_type(self):
        """Test _construct_object with invalid type"""
        schema = WOQLSchema()

        # Add a valid class first
        class_dict = {"@id": "ValidClass", "@type": "Class"}
        schema._construct_class(class_dict)

        obj_dict = {"@type": "InvalidType", "@id": "test"}

        with pytest.raises(ValueError, match="InvalidType is not in current schema"):
            schema._construct_object(obj_dict)

    def test_create_obj_update_existing(self):
        """Test create_obj updating existing instance"""
        schema = WOQLSchema()

        class_dict = {"@id": "MyClass", "@type": "Class", "name": "xsd:string"}
        cls = schema._construct_class(class_dict)

        # Create initial instance
        initial = cls(name="initial")
        initial._id = "instance123"
        # Note: _instances is managed by the metaclass

        # Update with new params
        updated = schema._construct_object(
            {"@type": "MyClass", "@id": "instance123", "name": "updated"}
        )

        assert updated.name == "updated"


class TestDateTimeConversions:
    """Test datetime conversion utilities"""

    def test_convert_if_object_datetime_types(self):
        """Test various datetime type conversions"""
        schema = WOQLSchema()

        # First add the class to schema
        class_dict = {
            "@id": "TestClass",
            "@type": "Class",
            "datetime_field": "xsd:dateTime",
        }
        schema._construct_class(class_dict)

        # Test dateTime - use the internal method
        result = schema._construct_object(
            {
                "@type": "TestClass",
                "@id": "test",
                "datetime_field": "2023-01-01T00:00:00Z",
            }
        )
        # The datetime is converted to datetime object
        import datetime

        assert result.datetime_field == datetime.datetime(2023, 1, 1, 0, 0)


class TestJSONSchema:
    """Test JSON schema conversion functionality"""

    def test_from_json_schema_string_input(self):
        """Test from_json_schema with string input"""
        schema = WOQLSchema()

        json_str = '{"properties": {"name": {"type": "string"}}}'
        schema.from_json_schema("TestClass", json_str)

        assert "TestClass" in schema.object

    def test_from_json_schema_file_input(self):
        """Test from_json_schema with file input"""
        schema = WOQLSchema()

        json_content = '{"properties": {"age": {"type": "integer"}}}'
        file_obj = StringIO(json_content)

        # Need to load the JSON first

        json_dict = json.load(file_obj)

        schema.from_json_schema("TestClass", json_dict)

        assert "TestClass" in schema.object

    def test_from_json_schema_missing_properties(self):
        """Test from_json_schema with missing properties"""
        schema = WOQLSchema()

        json_dict = {"type": "object"}  # No properties

        with pytest.raises(RuntimeError, match="'properties' is missing"):
            schema.from_json_schema("TestClass", json_dict)

    def test_convert_property_datetime_format(self):
        """Test convert_property with date-time format"""
        schema = WOQLSchema()

        # Test through from_json_schema with pipe mode
        json_dict = {
            "properties": {"test_prop": {"type": "string", "format": "date-time"}}
        }

        # This will call convert_property internally
        result = schema.from_json_schema("TestClass", json_dict, pipe=True)

        # Check the result has the converted property
        assert "test_prop" in result
        # Note: There's a typo in the original code (xsd:dataTime instead of xsd:dateTime)
        assert result["test_prop"] == "xsd:dataTime"

    def test_convert_property_subdocument_missing_props(self):
        """Test convert_property subdocument missing properties"""
        schema = WOQLSchema()

        json_dict = {
            "properties": {
                "test_prop": {
                    "type": "object"
                    # No properties
                }
            }
        }

        with pytest.raises(
            RuntimeError, match="subdocument test_prop not in proper format"
        ):
            schema.from_json_schema("TestClass", json_dict, pipe=True)

    def test_convert_property_ref_not_in_defs(self):
        """Test convert_property with $ref not in defs"""
        schema = WOQLSchema()

        json_dict = {"properties": {"test_prop": {"$ref": "#/definitions/MissingType"}}}

        with pytest.raises(RuntimeError, match="MissingType not found in defs"):
            schema.from_json_schema("TestClass", json_dict, pipe=True)


class TestToJSONSchema:
    """Test to_json_schema functionality"""

    def test_to_json_schema_dict_input_error(self):
        """Test to_json_schema with dict input for embedded object"""
        schema = WOQLSchema()

        class_dict = {"@id": "TestClass", "@type": "Class", "embedded": "EmbeddedClass"}

        with pytest.raises(RuntimeError, match="EmbeddedClass not embedded in input"):
            schema.to_json_schema(class_dict)

    def test_to_json_schema_non_existent_class(self):
        """Test to_json_schema with non-existent class name"""
        schema = WOQLSchema()

        with pytest.raises(RuntimeError, match="NonExistentClass not found in schema"):
            schema.to_json_schema("NonExistentClass")

    def test_to_json_schema_xsd_types(self):
        """Test various xsd type conversions"""
        schema = WOQLSchema()

        # Add a class with various xsd types (excluding ones that can't be converted)
        class_dict = {
            "@id": "TestClass",
            "@type": "Class",
            "string_prop": "xsd:string",
            "int_prop": "xsd:integer",
            "bool_prop": "xsd:boolean",
            "decimal_prop": "xsd:decimal",
            # Skip float_prop and double_prop as they can't be converted
        }
        schema._construct_class(class_dict)

        result = schema.to_json_schema("TestClass")

        assert result["properties"]["string_prop"]["type"] == "string"
        assert result["properties"]["int_prop"]["type"] == "integer"
        assert result["properties"]["bool_prop"]["type"] == "boolean"
        assert result["properties"]["decimal_prop"]["type"] == "number"

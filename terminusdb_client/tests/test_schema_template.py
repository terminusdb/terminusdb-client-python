"""Tests for scripts/schema_template.py module."""
from terminusdb_client.scripts import schema_template
from terminusdb_client.woqlschema import DocumentTemplate, EnumTemplate, TaggedUnion


def test_schema_template_imports():
    """Test that schema_template module can be imported."""
    assert schema_template is not None
    assert schema_template.__doc__ is not None


def test_country_class_exists():
    """Test that Country class is defined."""
    assert hasattr(schema_template, 'Country')
    assert issubclass(schema_template.Country, DocumentTemplate)


def test_country_has_key():
    """Test that Country has HashKey configured."""
    assert hasattr(schema_template.Country, '_key')


def test_country_attributes():
    """Test that Country has expected attributes."""
    country = schema_template.Country
    # Check type hints exist
    assert hasattr(country, '__annotations__')
    assert 'name' in country.__annotations__
    assert 'also_know_as' in country.__annotations__


def test_address_class_exists():
    """Test that Address class is defined."""
    assert hasattr(schema_template, 'Address')
    assert issubclass(schema_template.Address, DocumentTemplate)


def test_address_is_subdocument():
    """Test that Address is configured as subdocument."""
    assert hasattr(schema_template.Address, '_subdocument')


def test_address_attributes():
    """Test that Address has expected attributes."""
    address = schema_template.Address
    assert 'street' in address.__annotations__
    assert 'postal_code' in address.__annotations__
    assert 'country' in address.__annotations__


def test_person_class_exists():
    """Test that Person class is defined."""
    assert hasattr(schema_template, 'Person')
    assert issubclass(schema_template.Person, DocumentTemplate)


def test_person_has_docstring():
    """Test that Person has numpydoc formatted docstring."""
    assert schema_template.Person.__doc__ is not None
    assert 'Attributes' in schema_template.Person.__doc__


def test_person_attributes():
    """Test that Person has expected attributes."""
    person = schema_template.Person
    assert 'name' in person.__annotations__
    assert 'age' in person.__annotations__
    assert 'friend_of' in person.__annotations__


def test_employee_inherits_person():
    """Test that Employee inherits from Person."""
    assert hasattr(schema_template, 'Employee')
    assert issubclass(schema_template.Employee, schema_template.Person)


def test_employee_attributes():
    """Test that Employee has expected attributes."""
    employee = schema_template.Employee
    assert 'address_of' in employee.__annotations__
    assert 'contact_number' in employee.__annotations__
    assert 'managed_by' in employee.__annotations__


def test_coordinate_class_exists():
    """Test that Coordinate class is defined."""
    assert hasattr(schema_template, 'Coordinate')
    assert issubclass(schema_template.Coordinate, DocumentTemplate)


def test_coordinate_is_abstract():
    """Test that Coordinate is configured as abstract."""
    assert hasattr(schema_template.Coordinate, '_abstract')


def test_coordinate_attributes():
    """Test that Coordinate has x and y attributes."""
    coordinate = schema_template.Coordinate
    assert 'x' in coordinate.__annotations__
    assert 'y' in coordinate.__annotations__


def test_location_multiple_inheritance():
    """Test that Location inherits from both Address and Coordinate."""
    assert hasattr(schema_template, 'Location')
    assert issubclass(schema_template.Location, schema_template.Address)
    assert issubclass(schema_template.Location, schema_template.Coordinate)


def test_location_attributes():
    """Test that Location has its own attributes."""
    location = schema_template.Location
    assert 'name' in location.__annotations__


def test_team_enum_exists():
    """Test that Team enum is defined."""
    assert hasattr(schema_template, 'Team')
    assert issubclass(schema_template.Team, EnumTemplate)


def test_team_enum_values():
    """Test that Team has expected enum values."""
    team = schema_template.Team
    assert hasattr(team, 'IT')
    assert hasattr(team, 'Marketing')
    assert team.IT.value == "Information Technology"


def test_contact_tagged_union_exists():
    """Test that Contact tagged union is defined."""
    assert hasattr(schema_template, 'Contact')
    assert issubclass(schema_template.Contact, TaggedUnion)


def test_contact_union_attributes():
    """Test that Contact has union type attributes."""
    contact = schema_template.Contact
    assert 'local_number' in contact.__annotations__
    assert 'international' in contact.__annotations__


def test_all_classes_importable():
    """Test that all template classes can be imported."""
    classes = [
        'Country', 'Address', 'Person', 'Employee',
        'Coordinate', 'Location', 'Team', 'Contact'
    ]
    for cls_name in classes:
        assert hasattr(schema_template, cls_name), f"{cls_name} should be importable"


def test_module_docstring():
    """Test that module has docstring with metadata."""
    doc = schema_template.__doc__
    assert doc is not None
    assert 'Title:' in doc
    assert 'Description:' in doc
    assert 'Authors:' in doc

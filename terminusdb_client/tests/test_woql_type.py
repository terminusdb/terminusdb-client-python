"""Tests for woql_type.py"""
import datetime as dt
from enum import Enum
from typing import ForwardRef, List, Optional, Set
import pytest
from terminusdb_client.woql_type import (
    # Type aliases
    anyURI,
    anySimpleType,
    decimal,
    dateTimeStamp,
    gYear,
    gMonth,
    gDay,
    gYearMonth,
    yearMonthDuration,
    dayTimeDuration,
    byte,
    short,
    long,
    unsignedByte,
    unsignedShort,
    unsignedInt,
    unsignedLong,
    positiveInteger,
    negativeInteger,
    nonPositiveInteger,
    nonNegativeInteger,
    base64Binary,
    hexBinary,
    language,
    normalizedString,
    token,
    NMTOKEN,
    Name,
    NCName,
    CONVERT_TYPE,
    to_woql_type,
    from_woql_type,
    datetime_to_woql,
    datetime_from_woql,
)


class TestTypeAliases:
    """Test all type aliases are properly defined"""
    
    def test_all_type_aliases_exist(self):
        """Test that all type aliases are defined"""
        # Test string-based types
        assert anyURI("test") == "test"
        assert anySimpleType("test") == "test"
        assert decimal("123.45") == "123.45"
        assert gYear("2023") == "2023"
        assert gMonth("01") == "01"
        assert gDay("01") == "01"
        assert gYearMonth("2023-01") == "2023-01"
        assert yearMonthDuration("P1Y2M") == "P1Y2M"
        assert dayTimeDuration("PT1H2M3S") == "PT1H2M3S"
        assert base64Binary("dGVzdA==") == "dGVzdA=="
        assert hexBinary("74657474") == "74657474"
        assert language("en") == "en"
        assert normalizedString("test") == "test"
        assert token("test") == "test"
        assert NMTOKEN("test") == "test"
        assert Name("test") == "test"
        assert NCName("test") == "test"
        
        # Test integer-based types
        assert byte(127) == 127
        assert short(32767) == 32767
        assert long(2147483647) == 2147483647
        assert unsignedByte(255) == 255
        assert unsignedShort(65535) == 65535
        assert unsignedInt(4294967295) == 4294967295
        assert unsignedLong(18446744073709551615) == 18446744073709551615
        assert positiveInteger(1) == 1
        assert negativeInteger(-1) == -1
        assert nonPositiveInteger(0) == 0
        assert nonNegativeInteger(0) == 0
        
        # Test datetime type
        now = dt.datetime.now()
        assert dateTimeStamp(now) == now


class TestConvertType:
    """Test CONVERT_TYPE dictionary"""
    
    def test_convert_type_mappings(self):
        """Test all mappings in CONVERT_TYPE"""
        # Basic types
        assert CONVERT_TYPE[str] == "xsd:string"
        assert CONVERT_TYPE[bool] == "xsd:boolean"
        assert CONVERT_TYPE[float] == "xsd:double"
        assert CONVERT_TYPE[int] == "xsd:integer"
        assert CONVERT_TYPE[dict] == "sys:JSON"
        
        # Datetime types
        assert CONVERT_TYPE[dt.datetime] == "xsd:dateTime"
        assert CONVERT_TYPE[dt.date] == "xsd:date"
        assert CONVERT_TYPE[dt.time] == "xsd:time"
        assert CONVERT_TYPE[dt.timedelta] == "xsd:duration"
        
        # Custom types
        assert CONVERT_TYPE[anyURI] == "xsd:anyURI"
        assert CONVERT_TYPE[anySimpleType] == "xsd:anySimpleType"
        assert CONVERT_TYPE[decimal] == "xsd:decimal"
        assert CONVERT_TYPE[dateTimeStamp] == "xsd:dateTimeStamp"
        assert CONVERT_TYPE[gYear] == "xsd:gYear"
        assert CONVERT_TYPE[gMonth] == "xsd:gMonth"
        assert CONVERT_TYPE[gDay] == "xsd:gDay"
        assert CONVERT_TYPE[gYearMonth] == "xsd:gYearMonth"
        assert CONVERT_TYPE[yearMonthDuration] == "xsd:yearMonthDuration"
        assert CONVERT_TYPE[dayTimeDuration] == "xsd:dayTimeDuration"
        assert CONVERT_TYPE[byte] == "xsd:byte"
        assert CONVERT_TYPE[short] == "xsd:short"
        assert CONVERT_TYPE[long] == "xsd:long"
        assert CONVERT_TYPE[unsignedByte] == "xsd:unsignedByte"
        assert CONVERT_TYPE[unsignedShort] == "xsd:unsignedShort"
        assert CONVERT_TYPE[unsignedInt] == "xsd:unsignedInt"
        assert CONVERT_TYPE[unsignedLong] == "xsd:unsignedLong"
        assert CONVERT_TYPE[positiveInteger] == "xsd:positiveInteger"
        assert CONVERT_TYPE[negativeInteger] == "xsd:negativeInteger"
        assert CONVERT_TYPE[nonPositiveInteger] == "xsd:nonPositiveInteger"
        assert CONVERT_TYPE[nonNegativeInteger] == "xsd:nonNegativeInteger"
        assert CONVERT_TYPE[base64Binary] == "xsd:base64Binary"
        assert CONVERT_TYPE[hexBinary] == "xsd:hexBinary"
        assert CONVERT_TYPE[language] == "xsd:language"
        assert CONVERT_TYPE[normalizedString] == "xsd:normalizedString"
        assert CONVERT_TYPE[token] == "xsd:token"
        assert CONVERT_TYPE[NMTOKEN] == "xsd:NMTOKEN"
        assert CONVERT_TYPE[Name] == "xsd:Name"
        assert CONVERT_TYPE[NCName] == "xsd:NCName"


class TestToWoqlType:
    """Test to_woql_type function"""
    
    def test_to_woql_basic_types(self):
        """Test conversion of basic types"""
        assert to_woql_type(str) == "xsd:string"
        assert to_woql_type(bool) == "xsd:boolean"
        assert to_woql_type(float) == "xsd:double"
        assert to_woql_type(int) == "xsd:integer"
        assert to_woql_type(dict) == "sys:JSON"
        assert to_woql_type(dt.datetime) == "xsd:dateTime"
    
    def test_to_woql_forward_ref(self):
        """Test ForwardRef handling"""
        ref = ForwardRef("MyClass")
        assert to_woql_type(ref) == "MyClass"
    
    def test_to_woql_typing_with_name(self):
        """Test typing types with _name attribute"""
        # List type
        list_type = List[str]
        result = to_woql_type(list_type)
        assert result["@type"] == "List"
        assert result["@class"] == "xsd:string"
        
        # Set type
        set_type = Set[int]
        result = to_woql_type(set_type)
        assert result["@type"] == "Set"
        assert result["@class"] == "xsd:integer"
    
    def test_to_woql_optional_type(self):
        """Test Optional type"""
        optional_type = Optional[str]
        result = to_woql_type(optional_type)
        assert result["@type"] == "Optional"
        assert result["@class"] == "xsd:string"
    
    def test_to_woql_optional_without_name(self):
        """Test Optional type without _name to cover line 89"""
        # Create a type that looks like Optional but has no _name
        class FakeOptional:
            __module__ = "typing"
            __args__ = (str,)
            _name = None  # Explicitly set _name to None
        
        result = to_woql_type(FakeOptional)
        assert result["@type"] == "Optional"
        assert result["@class"] == "xsd:string"
    
    def test_to_woql_enum_type(self):
        """Test Enum type"""
        class TestEnum(Enum):
            A = "a"
            B = "b"
        
        assert to_woql_type(TestEnum) == "TestEnum"
    
    def test_to_woql_unknown_type(self):
        """Test unknown type fallback"""
        class CustomClass:
            pass
        
        result = to_woql_type(CustomClass)
        assert result == "<class 'terminusdb_client.tests.test_woql_type.TestToWoqlType.test_to_woql_unknown_type.<locals>.CustomClass'>"


class TestFromWoqlType:
    """Test from_woql_type function"""
    
    def test_from_woql_list_type(self):
        """Test List type conversion"""
        # As object - returns ForwardRef for basic types
        from typing import ForwardRef
        result = from_woql_type({"@type": "List", "@class": "xsd:string"})
        assert result == List[ForwardRef('str')]
        
        # As string
        result = from_woql_type({"@type": "List", "@class": "xsd:string"}, as_str=True)
        assert result == "List[str]"
    
    def test_from_woql_set_type(self):
        """Test Set type conversion"""
        # As object - returns ForwardRef for basic types
        from typing import ForwardRef
        result = from_woql_type({"@type": "Set", "@class": "xsd:integer"})
        assert result == Set[ForwardRef('int')]
        
        # As string
        result = from_woql_type({"@type": "Set", "@class": "xsd:integer"}, as_str=True)
        assert result == "Set[int]"
    
    def test_from_woql_optional_type(self):
        """Test Optional type conversion"""
        # As object - returns ForwardRef for basic types
        from typing import ForwardRef
        result = from_woql_type({"@type": "Optional", "@class": "xsd:boolean"})
        assert result == Optional[ForwardRef('bool')]
        
        # As string
        result = from_woql_type({"@type": "Optional", "@class": "xsd:boolean"}, as_str=True)
        assert result == "Optional[bool]"
    
    def test_from_woql_invalid_dict_type(self):
        """Test invalid dict type"""
        with pytest.raises(TypeError) as exc_info:
            from_woql_type({"@type": "Invalid", "@class": "xsd:string"})
        assert "cannot be converted" in str(exc_info.value)
    
    def test_from_woql_basic_string_types(self):
        """Test basic string type conversions"""
        assert from_woql_type("xsd:string") == str
        assert from_woql_type("xsd:boolean") == bool
        assert from_woql_type("xsd:double") == float
        assert from_woql_type("xsd:integer") == int
        
        # As string
        assert from_woql_type("xsd:string", as_str=True) == "str"
        assert from_woql_type("xsd:boolean", as_str=True) == "bool"
    
    def test_from_woql_skip_convert_error(self):
        """Test skip_convert_error functionality"""
        # Skip error as object
        result = from_woql_type("custom:type", skip_convert_error=True)
        assert result == "custom:type"
        
        # Skip error as string
        result = from_woql_type("custom:type", skip_convert_error=True, as_str=True)
        assert result == "'custom:type'"
    
    def test_from_woql_type_error(self):
        """Test TypeError for unknown types"""
        with pytest.raises(TypeError) as exc_info:
            from_woql_type("unknown:type")
        assert "cannot be converted" in str(exc_info.value)


class TestDatetimeConversions:
    """Test datetime conversion functions"""
    
    def test_datetime_to_woql_datetime(self):
        """Test datetime conversion"""
        dt_obj = dt.datetime(2023, 1, 1, 12, 0, 0)
        result = datetime_to_woql(dt_obj)
        assert result == "2023-01-01T12:00:00"
    
    def test_datetime_to_woql_date(self):
        """Test date conversion"""
        date_obj = dt.date(2023, 1, 1)
        result = datetime_to_woql(date_obj)
        assert result == "2023-01-01"
    
    def test_datetime_to_woql_time(self):
        """Test time conversion"""
        time_obj = dt.time(12, 0, 0)
        result = datetime_to_woql(time_obj)
        assert result == "12:00:00"
    
    def test_datetime_to_woql_timedelta(self):
        """Test timedelta conversion"""
        delta = dt.timedelta(hours=1, minutes=30, seconds=45)
        result = datetime_to_woql(delta)
        assert result == "PT5445.0S"  # 1*3600 + 30*60 + 45 = 5445 seconds
    
    def test_datetime_to_woql_passthrough(self):
        """Test non-datetime passthrough"""
        obj = "not a datetime"
        result = datetime_to_woql(obj)
        assert result == obj
    
    def test_datetime_from_woql_duration_positive(self):
        """Test duration conversion positive"""
        # Simple duration
        result = datetime_from_woql("PT1H30M", "xsd:duration")
        assert result == dt.timedelta(hours=1, minutes=30)
        
        # Duration with days
        result = datetime_from_woql("P2DT3H4M", "xsd:duration")
        assert result == dt.timedelta(days=2, hours=3, minutes=4)
        
        # Duration with seconds only
        result = datetime_from_woql("PT30S", "xsd:duration")
        assert result == dt.timedelta(seconds=30)
    
    def test_datetime_from_woql_duration_negative(self):
        """Test duration conversion negative (lines 164, 188-189)"""
        result = datetime_from_woql("-PT1H30M", "xsd:duration")
        assert result == dt.timedelta(hours=-1, minutes=-30)
    
    def test_datetime_from_woql_duration_undetermined(self):
        """Test undetermined duration error"""
        with pytest.raises(ValueError) as exc_info:
            datetime_from_woql("P1Y2M", "xsd:duration")
        assert "undetermined" in str(exc_info.value)
    
    def test_datetime_from_woql_duration_zero_days(self):
        """Test duration with zero days"""
        result = datetime_from_woql("PT1H", "xsd:duration")
        assert result == dt.timedelta(hours=1)
    
    def test_datetime_from_woql_datetime_type(self):
        """Test datetime type conversion"""
        result = datetime_from_woql("2023-01-01T12:00:00Z", "xsd:dateTime")
        assert result == dt.datetime(2023, 1, 1, 12, 0, 0)
    
    def test_datetime_from_woql_date_type(self):
        """Test date type conversion"""
        result = datetime_from_woql("2023-01-01Z", "xsd:date")
        assert result == dt.date(2023, 1, 1)
    
    def test_datetime_from_woql_time_type(self):
        """Test time type conversion"""
        # The function tries to parse time as datetime first, then extracts time
        result = datetime_from_woql("1970-01-01T12:00:00", "xsd:time")
        assert result == dt.time(12, 0, 0)
    
    def test_datetime_from_woql_unsupported_type(self):
        """Test unsupported datetime type error"""
        with pytest.raises(ValueError) as exc_info:
            datetime_from_woql("2023-01-01T12:00:00Z", "xsd:unsupported")
        assert "not supported" in str(exc_info.value)

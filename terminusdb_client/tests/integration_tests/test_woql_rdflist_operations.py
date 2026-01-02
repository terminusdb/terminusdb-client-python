"""
Integration tests for WOQL rdf:List operations.

These tests verify the rdflist operations:
- rdflist_list, rdflist_peek, rdflist_last, rdflist_member, rdflist_length
- rdflist_pop, rdflist_push, rdflist_append
- rdflist_insert, rdflist_drop, rdflist_clear
- rdflist_swap, rdflist_reverse
- rdflist_empty, rdflist_is_empty, rdflist_slice
"""

import pytest

from terminusdb_client import Client
from terminusdb_client.woqlquery.woql_query import WOQLQuery

test_user_agent = "terminusdb-client-python-tests"


def extract_values(result_list):
    """Extract raw values from a list of typed literals."""
    if not result_list:
        return []
    return [
        item["@value"] if isinstance(item, dict) and "@value" in item else item
        for item in result_list
    ]


def create_test_list(client, values):
    """Create a test rdf:List with the given values and return the list head IRI."""
    if not values:
        raise ValueError("Cannot create empty list with this helper")

    # Build query to create the list
    query_parts = []

    # Create cells with deterministic IDs
    cell_ids = [f"terminusdb://data/Cons/test_{i}" for i in range(len(values))]

    for i, (cell_id, value) in enumerate(zip(cell_ids, values)):
        query_parts.append(WOQLQuery().add_triple(cell_id, "rdf:type", "rdf:List"))
        query_parts.append(
            WOQLQuery().add_triple(
                cell_id,
                "rdf:first",
                {"@type": "xsd:string", "@value": value},
            )
        )
        if i < len(values) - 1:
            query_parts.append(
                WOQLQuery().add_triple(cell_id, "rdf:rest", cell_ids[i + 1])
            )
        else:
            query_parts.append(WOQLQuery().add_triple(cell_id, "rdf:rest", "rdf:nil"))

    create_query = WOQLQuery().woql_and(*query_parts)
    client.query(create_query)

    # Return the head cell IRI
    return cell_ids[0]


class TestWOQLRdfListOperations:
    """Tests for WOQL rdf:List operations."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        """Setup and teardown for each test."""
        # Try without auth first (AUTOLOGIN mode), fallback to admin/root
        try:
            self.client = Client(docker_url, user_agent=test_user_agent)
            self.client.connect()
        except Exception:
            # Fallback to authenticated connection
            self.client = Client(
                docker_url, user="admin", key="root", user_agent=test_user_agent
            )
            self.client.connect()

        self.db_name = "test_woql_rdflist_operations"

        # Create database for tests
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)

        yield

        # Cleanup
        self.client.delete_database(self.db_name)

    def test_rdflist_list_collects_all_elements(self):
        """Test rdflist_list collects all elements into array."""
        list_head = create_test_list(self.client, ["A", "B", "C"])

        query = WOQLQuery().rdflist_list(list_head, "v:all")
        result = self.client.query(query)

        assert len(result["bindings"]) == 1
        assert extract_values(result["bindings"][0]["all"]) == ["A", "B", "C"]

    def test_rdflist_peek_gets_first_element(self):
        """Test rdflist_peek gets the first element."""
        list_head = create_test_list(self.client, ["First", "Second", "Third"])

        query = WOQLQuery().rdflist_peek(list_head, "v:first")
        result = self.client.query(query)

        assert len(result["bindings"]) == 1
        first = result["bindings"][0].get("first") or result["bindings"][0].get("v:first")
        assert first["@value"] == "First"

    def test_rdflist_last_gets_last_element(self):
        """Test rdflist_last gets the last element."""
        list_head = create_test_list(self.client, ["First", "Second", "Last"])

        query = WOQLQuery().rdflist_last(list_head, "v:last")
        result = self.client.query(query)

        assert len(result["bindings"]) == 1
        last = result["bindings"][0].get("last") or result["bindings"][0].get("v:last")
        assert last["@value"] == "Last"

    def test_rdflist_member_iterates_elements(self):
        """Test rdflist_member yields one binding per element."""
        list_head = create_test_list(self.client, ["X", "Y", "Z"])

        query = WOQLQuery().rdflist_member(list_head, "v:item")
        result = self.client.query(query)

        assert len(result["bindings"]) == 3
        items = [
            (b.get("item") or b.get("v:item"))["@value"]
            for b in result["bindings"]
        ]
        assert items == ["X", "Y", "Z"]

    def test_rdflist_length_counts_elements(self):
        """Test rdflist_length returns correct count."""
        list_head = create_test_list(self.client, ["A", "B", "C", "D"])

        query = WOQLQuery().rdflist_length(list_head, "v:len")
        result = self.client.query(query)

        assert len(result["bindings"]) == 1
        length = result["bindings"][0].get("len") or result["bindings"][0].get("v:len")
        assert int(length["@value"]) == 4

    def test_rdflist_push_adds_to_front(self):
        """Test rdflist_push adds element to front in-place."""
        list_head = create_test_list(self.client, ["B", "C"])

        # Push "A" to front
        push_query = WOQLQuery().rdflist_push(
            list_head, {"@type": "xsd:string", "@value": "A"}
        )
        self.client.query(push_query)

        # Verify list is now [A, B, C]
        verify_query = WOQLQuery().rdflist_list(list_head, "v:all")
        result = self.client.query(verify_query)
        assert extract_values(result["bindings"][0]["all"]) == ["A", "B", "C"]

    def test_rdflist_pop_removes_from_front(self):
        """Test rdflist_pop removes and returns first element."""
        list_head = create_test_list(self.client, ["X", "Y", "Z"])

        # Get first element before pop
        peek_query = WOQLQuery().rdflist_peek(list_head, "v:first")
        peek_result = self.client.query(peek_query)
        first_val = peek_result["bindings"][0]["first"]["@value"]
        assert first_val == "X"

        # Pop first element (write operation)
        pop_query = WOQLQuery().rdflist_pop(list_head, "v:popped")
        self.client.query(pop_query)

        # Verify list is now [Y, Z]
        verify_query = WOQLQuery().rdflist_list(list_head, "v:all")
        verify_result = self.client.query(verify_query)
        assert extract_values(verify_result["bindings"][0]["all"]) == ["Y", "Z"]

    def test_rdflist_append_adds_to_end(self):
        """Test rdflist_append adds element to end."""
        list_head = create_test_list(self.client, ["A", "B"])

        # Append "C" to end
        append_query = WOQLQuery().rdflist_append(
            list_head, {"@type": "xsd:string", "@value": "C"}, "v:new_cell"
        )
        self.client.query(append_query)

        # Verify list is now [A, B, C]
        verify_query = WOQLQuery().rdflist_list(list_head, "v:all")
        result = self.client.query(verify_query)
        assert extract_values(result["bindings"][0]["all"]) == ["A", "B", "C"]

    def test_rdflist_insert_at_position(self):
        """Test rdflist_insert adds element at specified position."""
        list_head = create_test_list(self.client, ["A", "C", "D"])

        # Insert "B" at position 1
        insert_query = WOQLQuery().rdflist_insert(
            list_head, 1, {"@type": "xsd:string", "@value": "B"}
        )
        self.client.query(insert_query)

        # Verify list is now [A, B, C, D]
        verify_query = WOQLQuery().rdflist_list(list_head, "v:all")
        result = self.client.query(verify_query)
        assert extract_values(result["bindings"][0]["all"]) == ["A", "B", "C", "D"]

    def test_rdflist_insert_at_position_zero(self):
        """Test rdflist_insert at position 0 works like push."""
        list_head = create_test_list(self.client, ["B", "C"])

        # Insert "A" at position 0
        insert_query = WOQLQuery().rdflist_insert(
            list_head, 0, {"@type": "xsd:string", "@value": "A"}
        )
        self.client.query(insert_query)

        # Verify list is now [A, B, C]
        verify_query = WOQLQuery().rdflist_list(list_head, "v:all")
        result = self.client.query(verify_query)
        assert extract_values(result["bindings"][0]["all"]) == ["A", "B", "C"]

    def test_rdflist_drop_removes_at_position(self):
        """Test rdflist_drop removes element at specified position."""
        list_head = create_test_list(self.client, ["A", "B", "C", "D"])

        # Drop element at position 1 (B)
        drop_query = WOQLQuery().rdflist_drop(list_head, 1)
        self.client.query(drop_query)

        # Verify list is now [A, C, D]
        verify_query = WOQLQuery().rdflist_list(list_head, "v:all")
        result = self.client.query(verify_query)
        assert extract_values(result["bindings"][0]["all"]) == ["A", "C", "D"]

    def test_rdflist_drop_at_position_zero(self):
        """Test rdflist_drop at position 0 removes first element."""
        list_head = create_test_list(self.client, ["X", "Y", "Z"])

        # Drop element at position 0
        drop_query = WOQLQuery().rdflist_drop(list_head, 0)
        self.client.query(drop_query)

        # Verify list is now [Y, Z]
        verify_query = WOQLQuery().rdflist_list(list_head, "v:all")
        result = self.client.query(verify_query)
        assert extract_values(result["bindings"][0]["all"]) == ["Y", "Z"]

    def test_rdflist_swap_exchanges_elements(self):
        """Test rdflist_swap exchanges elements at two positions."""
        list_head = create_test_list(self.client, ["A", "B", "C", "D"])

        # Swap positions 0 and 2 (A and C)
        swap_query = WOQLQuery().rdflist_swap(list_head, 0, 2)
        self.client.query(swap_query)

        # Verify list is now [C, B, A, D]
        verify_query = WOQLQuery().rdflist_list(list_head, "v:all")
        result = self.client.query(verify_query)
        assert extract_values(result["bindings"][0]["all"]) == ["C", "B", "A", "D"]

    def test_rdflist_swap_same_position_is_noop(self):
        """Test rdflist_swap with same position does nothing."""
        list_head = create_test_list(self.client, ["A", "B", "C"])

        # Swap position 1 with itself
        swap_query = WOQLQuery().rdflist_swap(list_head, 1, 1)
        self.client.query(swap_query)

        # Verify list is unchanged
        verify_query = WOQLQuery().rdflist_list(list_head, "v:all")
        result = self.client.query(verify_query)
        assert extract_values(result["bindings"][0]["all"]) == ["A", "B", "C"]

    def test_rdflist_clear_removes_all_elements(self):
        """Test rdflist_clear removes all cons cells."""
        list_head = create_test_list(self.client, ["A", "B", "C"])

        # Clear the list (write operation returns string)
        clear_query = WOQLQuery().rdflist_clear(list_head, "v:empty")
        self.client.query(clear_query)

        # Verify list head no longer exists as rdf:List
        verify_query = WOQLQuery().triple(list_head, "rdf:type", "rdf:List")
        verify_result = self.client.query(verify_query)
        assert len(verify_result["bindings"]) == 0

    def test_rdflist_empty_creates_nil_reference(self):
        """Test rdflist_empty returns rdf:nil."""
        query = WOQLQuery().rdflist_empty("v:empty_list")
        result = self.client.query(query)

        assert len(result["bindings"]) == 1
        empty = result["bindings"][0].get("empty_list") or result["bindings"][0].get("v:empty_list")
        assert empty == "rdf:nil"

    def test_rdflist_is_empty_succeeds_for_nil(self):
        """Test rdflist_is_empty succeeds for rdf:nil."""
        query = WOQLQuery().rdflist_is_empty("rdf:nil")
        result = self.client.query(query)

        assert len(result["bindings"]) == 1

    def test_rdflist_is_empty_fails_for_non_empty_list(self):
        """Test rdflist_is_empty fails for non-empty list."""
        list_head = create_test_list(self.client, ["A"])

        query = WOQLQuery().rdflist_is_empty(list_head)
        result = self.client.query(query)

        assert len(result["bindings"]) == 0

    def test_rdflist_slice_extracts_range(self):
        """Test rdflist_slice extracts a range of elements."""
        list_head = create_test_list(self.client, ["A", "B", "C", "D", "E"])

        # Get elements 1-3 (B, C, D)
        query = WOQLQuery().rdflist_slice(list_head, 1, 4, "v:slice")
        result = self.client.query(query)

        assert len(result["bindings"]) == 1
        assert extract_values(result["bindings"][0]["slice"]) == ["B", "C", "D"]

    def test_rdflist_slice_first_two(self):
        """Test rdflist_slice gets first two elements."""
        list_head = create_test_list(self.client, ["X", "Y", "Z"])

        query = WOQLQuery().rdflist_slice(list_head, 0, 2, "v:slice")
        result = self.client.query(query)

        assert len(result["bindings"]) == 1
        assert extract_values(result["bindings"][0]["slice"]) == ["X", "Y"]

    def test_rdflist_slice_single_element(self):
        """Test rdflist_slice gets single element."""
        list_head = create_test_list(self.client, ["A", "B", "C"])

        query = WOQLQuery().rdflist_slice(list_head, 1, 2, "v:slice")
        result = self.client.query(query)

        assert len(result["bindings"]) == 1
        assert extract_values(result["bindings"][0]["slice"]) == ["B"]

    def test_rdflist_slice_empty_range(self):
        """Test rdflist_slice returns empty for start >= end."""
        list_head = create_test_list(self.client, ["A", "B", "C"])

        query = WOQLQuery().rdflist_slice(list_head, 2, 2, "v:slice")
        result = self.client.query(query)

        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["slice"] == []

    def test_rdflist_reverse_reverses_list(self):
        """Test rdflist_reverse reverses the list in-place."""
        list_head = create_test_list(self.client, ["A", "B", "C", "D"])

        # Reverse the list
        reverse_query = WOQLQuery().rdflist_reverse(list_head)
        self.client.query(reverse_query)

        # Verify list is now [D, C, B, A]
        verify_query = WOQLQuery().rdflist_list(list_head, "v:all")
        result = self.client.query(verify_query)
        assert extract_values(result["bindings"][0]["all"]) == ["D", "C", "B", "A"]

    def test_rdflist_insert_negative_position_raises(self):
        """Test rdflist_insert raises for negative position."""
        with pytest.raises(ValueError, match="position >= 0"):
            WOQLQuery().rdflist_insert("v:list", -1, "value")

    def test_rdflist_drop_negative_position_raises(self):
        """Test rdflist_drop raises for negative position."""
        with pytest.raises(ValueError, match="position >= 0"):
            WOQLQuery().rdflist_drop("v:list", -1)

    def test_rdflist_swap_negative_position_raises(self):
        """Test rdflist_swap raises for negative position."""
        with pytest.raises(ValueError, match="positions >= 0"):
            WOQLQuery().rdflist_swap("v:list", -1, 0)

    def test_rdflist_slice_negative_raises(self):
        """Test rdflist_slice raises for negative indices."""
        with pytest.raises(ValueError, match="negative indices"):
            WOQLQuery().rdflist_slice("v:list", -1, 2, "v:result")

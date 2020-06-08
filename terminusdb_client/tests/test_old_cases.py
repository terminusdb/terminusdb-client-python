#TODO: update these tests
"""
test_client = WOQLClient(server="http://localhost:6363",
                         key="mykey",
                         db="mydb")

@mock.patch('requests.get')
def test_database_document_id(mocked_requests):
    woqlObject=WOQLQuery().limit(2).start(0)
    #woqlObject.execute(test_client)
    assert True


class TestPreRollQuery:

    def test_get_everything_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, {"quad": ["v:Subject", "v:Predicate", "v:Object", "db:Graph" ] } ] } ] }
        assert woqlObject.get_everything("Graph").json() == jsonObj

    def test_get_all_documents_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [ { "triple": [ "v:Subject", "rdf:type", "v:Type"] }, { "sub": ["v:Type", "tcs:Document" ] } ] } ] } ] }
        assert woqlObject.get_all_documents().json() == jsonObj

    def test_document_metadata_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
            { "triple": [ "v:ID", "rdf:type", "v:Class"] },
            { "sub": ["v:Class", "tcs:Document" ] },
            { "opt": [ { "triple": [ "v:ID", "rdfs:label", "v:Label"] } ] },
            { "opt": [ { "triple": [ "v:ID", "rdfs:comment", "v:Comment"] } ] },
            { "opt": [ { "quad": [ "v:Class", "rdfs:label", "v:Type", "db:schema"] } ] },
            { "opt": [ { "quad": [ "v:Class", "rdfs:comment", "v:Type_Comment", "db:schema"] } ] }
            ] } ] } ] }
        assert woqlObject.document_metadata().json() == jsonObj

    def test_concrete_document_classes_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
            { "sub": [ "v:Class", "tcs:Document"] },
            { "not": [ { "quad": ["v:Class", "tcs:tag", "tcs:abstract", "db:schema"] } ] },
            { "opt": [ { "quad": ["v:Class", "rdfs:label", "v:Label", "db:schema"] } ] },
            { "opt": [ { "quad": ["v:Class", "rdfs:comment", "v:Comment","db:schema"] } ] }
            ] } ] } ] }
        assert woqlObject.concrete_document_classes().json() == jsonObj

    def test_property_metadata_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        {  "or": [ { "quad": ["v:Property", "rdf:type", "owl:DatatypeProperty", "db:schema"] },
                   { "quad": ["v:Property", "rdf:type", "owl:ObjectProperty", "db:schema"] }
                 ] },
        { "opt": [ { "quad": ["v:Property", "rdfs:range", "v:Range", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Property", "rdf:type", "v:Type", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Property", "rdfs:label", "v:Label", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Property", "rdfs:comment", "v:Comment", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Property", "rdfs:domain", "v:Domain", "db:schema" ] } ] }
        ] } ] } ] }
        assert woqlObject.property_metadata().json() == jsonObj

    def test_element_metadata_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "quad": ["v:Element", "rdf:type", "v:Type", "db:schema"] },
        { "opt": [ { "quad": ["v:Element", "tcs:tag", "v:Abstract", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Element", "rdfs:label", "v:Label", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Element", "rdfs:comment", "v:Comment", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Element", "rdfs:subClassOf", "v:Parent", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Element", "rdfs:domain", "v:Domain", "db:schema"] } ] },
        {  "opt": [ { "quad": ["v:Element", "rdfs:range", "v:Range", "db:schema"] } ] }
        ] } ] } ] }
        assert woqlObject.element_metadata().json() == jsonObj

    def test_class_metadata_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "quad": [ "v:Element", "rdf:type", "owl:Class", "db:schema"] },
        { "opt": [ { "quad": ["v:Element", "rdfs:label", "v:Label", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Element", "rdfs:comment", "v:Comment", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Element", "tcs:tag", "v:Abstract", "db:schema"] } ] }
        ] } ] } ] }
        assert woqlObject.class_metadata().json() == jsonObj

    def test_get_data_of_class_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "triple": [ "v:Subject", "rdf:type", {"@language": "en", "@value": "ClassID"}] },
        { "opt": [ { "triple": ["v:Subject", "v:Property", "v:Value"] } ] }
        ] } ] } ] }
        assert woqlObject.get_data_of_class('ClassID').json() == jsonObj

    def test_get_data_of_property_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "triple": [ "v:Subject", "scm:PropID", "v:Value"] },
        { "opt": [ { "triple": ["v:Subject", "rdfs:label", "v:Label"] } ] }
        ] } ] } ] }
        assert woqlObject.get_data_of_property("PropID").json() == jsonObj

    def test_document_properties_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "triple": [ "doc:docid", "v:Property", "v:Property_Value"] },
        { "opt": [ { "quad": ["v:Property", "rdfs:label", "v:Property_Label", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Property", "rdf:type", "v:Property_Type", "db:schema"] } ] }
        ] } ] } ] }
        assert woqlObject.document_properties("docid").json() == jsonObj

    def test_get_document_connections_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        {"eq": ["v:Docid", "doc:docid"]},
        { "or": [
            { "triple": ["doc:docid", "v:Outgoing", "v:Entid"] },
            { "triple": ["v:Entid", "v:Incoming", "doc:docid" ] },
        ] },
        { "isa": [ "v:Entid", "v:Enttype"] },
        { "sub": [ "v:Enttype", "tcs:Document"] },
        { "opt": [ { "triple": ["v:Entid", "rdfs:label", "v:Label"] } ] },
        { "opt": [ { "quad": ["v:Enttype", "rdfs:label", "v:Class_Label", "db:schema"] } ] }
        ] } ] } ] }
        assert woqlObject.get_document_connections("doc:docid").json() == jsonObj

    def test_get_instance_meta_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "triple": [ "doc:docid", "rdf:type", "v:InstanceType"] },
        { "opt": [ { "triple": ["doc:docid", "rdfs:label", "v:InstanceLabel"] } ] },
        { "opt": [ { "triple": ["doc:docid", "rdfs:comment", "v:InstanceComment"] } ] },
        { "opt": [ { "quad": ["v:InstanceType", "rdfs:label", "v:ClassLabel", "db:schema"] } ] }
        ] } ] } ] }
        assert woqlObject.get_instance_meta("docid").json() == jsonObj

    def test_simple_graph_query_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "triple": [ "v:Source", "v:Edge", "v:Target"] },
        { "isa": [ "v:Source", "v:Source_Class"] },
        { "sub": [ "v:Source_Class", "tcs:Document"] },
        { "isa": [ "v:Target", "v:Target_Class"] },
        { "sub": [ "v:Target_Class", "tcs:Document"] },
        { "opt": [ { "triple": ["v:Source", "rdfs:label", "v:Source_Label"] } ] },
        { "opt": [ { "triple": ["v:Source", "rdfs:comment", "v:Source_Comment"] } ] },
        { "opt": [ { "quad": ["v:Source_Class", "rdfs:label", "v:Source_Type", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Source_Class", "rdfs:comment", "v:Source_Type_Comment", "db:schema"] } ] },
        { "opt": [ { "triple": ["v:Target", "rdfs:label", "v:Target_Label"] } ] },
        { "opt": [ { "triple": ["v:Target", "rdfs:comment", "v:Target_Comment"] } ] },
        { "opt": [ { "quad": ["v:Target_Class", "rdfs:label", "v:Target_Type", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Target_Class", "rdfs:comment", "v:Target_Type_Comment","db:schema"] } ] },
        { "opt": [ { "quad": ["v:Edge", "rdfs:label", "v:Edge_Type", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Edge", "rdfs:comment", "v:Edge_Type_Comment", "db:schema"] } ] }
        ] } ] } ] }
        assert woqlObject.simple_graph_query().json() == jsonObj


class TestWoqlQueryObject:

    def test_set_vocabulary_and_get_vocabulary_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        woqlObject.set_vocabulary("vocab")
        assert woqlObject.get_vocabulary() == "vocab"

    @mock.patch('requests.get')
    def test_load_vocabulary_method(self, mocked_requests):
        woqlObject=WOQLQuery().limit(2).start(0)
       # woqlObject.load_vocabulary(test_client)
        assert True

    def test_is_paged_method(self):
        woqlObjectTrue=WOQLQuery().limit(2).start(0)
        woqlObjectFalse=WOQLQuery().select("V1", WOQLQuery().triple("a", "b", "c"))
        assert woqlObjectTrue.is_paged() == True
        assert woqlObjectFalse.is_paged() == False

    def test_get_page_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        woqlObject2=WOQLQuery().limit(3).start(10)
        woqlObject3=WOQLQuery().limit(2).start(10)

        assert woqlObject.get_page() == 1
        assert woqlObject2.get_page() == 4
        assert woqlObject3.get_page() == 6

    def test_set_page_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 2, {} ] } ] }
        assert woqlObject.set_page(2).json() == jsonObj

    def test_next_page_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 2, {} ] } ] }
        assert woqlObject.next_page().json() == jsonObj

    def test_first_page_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, {} ] } ] }
        assert woqlObject.first_page().json() == jsonObj

    def test_previous_page_method(self):
        woqlObject=WOQLQuery().limit(2).start(4)
        jsonObj={ 'limit': [ 2, { 'start': [ 2, {} ] } ] }
        assert woqlObject.previous_page().json() == jsonObj

    def test_set_page_size_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 3, { 'start': [ 0, {} ] } ] }
        assert woqlObject.set_page_size(3).json() == jsonObj

    def test_set_page_size_method_not_first(self):
        woqlObject=WOQLQuery().limit(2).start(10)
        jsonObj={ 'limit': [ 3, { 'start': [ 0, {} ] } ] }
        assert woqlObject.set_page_size(3).json() == jsonObj

    def test_add_start_method(self):
        woqlObject=WOQLQuery().limit(2)
        woqlObject2=WOQLQuery().start(5).limit(2)
        jsonObj={ 'start': [ 10, { 'limit': [ 2, {} ] } ] }
        assert woqlObject.add_start(10).json() == jsonObj
        assert woqlObject2.add_start(10).json() == jsonObj

    def test_has_start_method(self):
        woqlObjectTrue=WOQLQuery().limit(2).start(10)
        woqlObjectFalse=WOQLQuery().limit(2)
        assert woqlObjectTrue.has_start() == True
        assert woqlObjectFalse.has_start() == False

    def test_get_start_method(self):
        woqlObject=WOQLQuery().limit(2).start(10)
        assert woqlObject.get_start() == 10

    def test_set_limit_method_not_first(self):
        woqlObject=WOQLQuery().limit(2).start(10)
        jsonObj={ 'limit': [ 3, { 'start': [ 10, {} ] } ] }
        assert woqlObject.set_limit(3).json() == jsonObj

    def test_get_limit_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        assert woqlObject.get_limit() == 2

    def test_has_select_method(self):
        woqlObjectTrue=WOQLQuery().select("V1", WOQLQuery().triple("a", "b", "c"))
        woqlObjectFalse=WOQLQuery().limit(2).start(0)
        assert woqlObjectTrue.has_select() == True
        assert woqlObjectFalse.has_select() == False

    def test_get_select_variables_method(self):
        woqlObject=WOQLQuery().select("V1", WOQLQuery().triple("a", "b", "c"))
        assert woqlObject.get_select_variables() == ["V1"]

    def test_context_and_get_context_method(self):
        contextObj = {"@import": "https://terminusdb/contexts/woql/syntax/context.jsonld",
           "@propagate": True,
           "db" : "http://localhost:6363/testDB004/"}
        woqlObject=WOQLQuery().limit(2).start(0)
        woqlObject.context(contextObj)
        assert woqlObject.get_context() == contextObj
"""

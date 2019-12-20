import pytest
import unittest.mock as mock
from woqlclient import WOQLQuery
from woqlclient import WOQLClient

test_client = WOQLClient({'server':"http://localhost:6363",
                    'key':'mykey',
                    'db':'mydb'})

@mock.patch('requests.get')
def test_database_document_id(mocked_requests):
    woqlObject=WOQLQuery().limit(2).start(0)
    woqlObject.execute(test_client)
    assert True


class TestPreRollQuery:

    def test_getEverything_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, {"quad": ["v:Subject", "v:Predicate", "v:Object", "db:Graph" ] } ] } ] }
        assert woqlObject.getEverything("Graph").json() == jsonObj

    def test_getAllDocuments_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [ { "triple": [ "v:Subject", "rdf:type", "v:Type"] }, { "sub": ["v:Type", "tcs:Document" ] } ] } ] } ] }
        assert woqlObject.getAllDocuments().json() == jsonObj

    def test_documentMetadata_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
            { "triple": [ "v:ID", "rdf:type", "v:Class"] },
            { "sub": ["v:Class", "tcs:Document" ] },
            { "opt": [ { "triple": [ "v:ID", "rdfs:label", "v:Label"] } ] },
            { "opt": [ { "triple": [ "v:ID", "rdfs:comment", "v:Comment"] } ] },
            { "opt": [ { "quad": [ "v:Class", "rdfs:label", "v:Type", "db:schema"] } ] },
            { "opt": [ { "quad": [ "v:Class", "rdfs:comment", "v:Type_Comment", "db:schema"] } ] }
            ] } ] } ] }
        assert woqlObject.documentMetadata().json() == jsonObj

    def test_concreteDocumentClasses_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
            { "sub": [ "v:Class", "tcs:Document"] },
            { "not": [ { "quad": ["v:Class", "tcs:tag", "tcs:abstract", "db:schema"] } ] },
            { "opt": [ { "quad": ["v:Class", "rdfs:label", "v:Label", "db:schema"] } ] },
            { "opt": [ { "quad": ["v:Class", "rdfs:comment", "v:Comment","db:schema"] } ] }
            ] } ] } ] }
        assert woqlObject.concreteDocumentClasses().json() == jsonObj

    def test_propertyMetadata_method(self):
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
        assert woqlObject.propertyMetadata().json() == jsonObj

    def test_elementMetadata_method(self):
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
        assert woqlObject.elementMetadata().json() == jsonObj

    def test_classMetadata_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "quad": [ "v:Element", "rdf:type", "owl:Class", "db:schema"] },
        { "opt": [ { "quad": ["v:Element", "rdfs:label", "v:Label", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Element", "rdfs:comment", "v:Comment", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Element", "tcs:tag", "v:Abstract", "db:schema"] } ] }
        ] } ] } ] }
        assert woqlObject.classMetadata().json() == jsonObj

    def test_getDataOfClass_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "triple": [ "v:Subject", "rdf:type", {"@language": "en", "@value": "ClassID"}] },
        { "opt": [ { "triple": ["v:Subject", "v:Property", "v:Value"] } ] }
        ] } ] } ] }
        assert woqlObject.getDataOfClass('ClassID').json() == jsonObj

    def test_getDataOfProperty_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "triple": [ "v:Subject", "scm:PropID", "v:Value"] },
        { "opt": [ { "triple": ["v:Subject", "rdfs:label", "v:Label"] } ] }
        ] } ] } ] }
        assert woqlObject.getDataOfProperty("PropID").json() == jsonObj

    def test_documentProperties_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "triple": [ "doc:docid", "v:Property", "v:Property_Value"] },
        { "opt": [ { "quad": ["v:Property", "rdfs:label", "v:Property_Label", "db:schema"] } ] },
        { "opt": [ { "quad": ["v:Property", "rdf:type", "v:Property_Type", "db:schema"] } ] }
        ] } ] } ] }
        assert woqlObject.documentProperties("docid").json() == jsonObj

    def test_getDocumentConnections_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "or": [
            { "triple": ["doc:docid", "v:Outgoing", "v:Entid"] },
            { "triple": ["v:Entid", "v:Incoming", { "@language": "en", "@value": "docid" } ] },
        ] },
        { "isa": [ "v:Entid", "v:Enttype"] },
        { "sub": [ "v:Enttype", "tcs:Document"] },
        { "opt": [ { "triple": ["v:Entid", "rdfs:label", "v:Label"] } ] },
        { "opt": [ { "quad": ["v:Enttype", "rdfs:label", "v:Class_Label", "db:schema"] } ] }
        ] } ] } ] }
        assert woqlObject.getDocumentConnections("docid").json() == jsonObj

    def test_getInstanceMeta_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, { "and": [
        { "triple": [ "doc:docid", "rdf:type", "v:InstanceType"] },
        { "opt": [ { "triple": ["doc:docid", "rdfs:label", "v:InstanceLabel"] } ] },
        { "opt": [ { "triple": ["doc:docid", "rdfs:comment", "v:InstanceComment"] } ] },
        { "opt": [ { "quad": ["v:InstanceType", "rdfs:label", "v:ClassLabel", "db:schema"] } ] }
        ] } ] } ] }
        assert woqlObject.getInstanceMeta("docid").json() == jsonObj

    def test_simpleGraphQuery_method(self):
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
        assert woqlObject.simpleGraphQuery().json() == jsonObj


class TestWoqlQueryObject:

    def test_setVocabulary_and_getVocabulary_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        woqlObject.setVocabulary("vocab")
        assert woqlObject.getVocabulary() == "vocab"

    @mock.patch('requests.get')
    def test_loadVocabulary_method(self, mocked_requests):
        woqlObject=WOQLQuery().limit(2).start(0)
        woqlObject.loadVocabulary(test_client)
        assert True

    def test_isPaged_method(self):
        woqlObjectTrue=WOQLQuery().limit(2).start(0)
        woqlObjectFalse=WOQLQuery().select("V1", WOQLQuery().triple("a", "b", "c"))
        assert woqlObjectTrue.isPaged() == True
        assert woqlObjectFalse.isPaged() == False

    def test_getPage_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        woqlObject2=WOQLQuery().limit(3).start(10)
        woqlObject3=WOQLQuery().limit(2).start(10)

        assert woqlObject.getPage() == 1
        assert woqlObject2.getPage() == 4
        assert woqlObject3.getPage() == 6

    def test_setPage_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 2, {} ] } ] }
        assert woqlObject.setPage(2).json() == jsonObj

    def test_nextPage_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 2, {} ] } ] }
        assert woqlObject.nextPage().json() == jsonObj

    def test_firstPage_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 2, { 'start': [ 0, {} ] } ] }
        assert woqlObject.firstPage().json() == jsonObj

    def test_previousPage_method(self):
        woqlObject=WOQLQuery().limit(2).start(4)
        jsonObj={ 'limit': [ 2, { 'start': [ 2, {} ] } ] }
        assert woqlObject.previousPage().json() == jsonObj

    def test_setPageSize_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        jsonObj={ 'limit': [ 3, { 'start': [ 0, {} ] } ] }
        assert woqlObject.setPageSize(3).json() == jsonObj

    def test_setPageSize_method_not_first(self):
        woqlObject=WOQLQuery().limit(2).start(10)
        jsonObj={ 'limit': [ 3, { 'start': [ 0, {} ] } ] }
        assert woqlObject.setPageSize(3).json() == jsonObj

    def test_addStart_method(self):
        woqlObject=WOQLQuery().limit(2)
        woqlObject2=WOQLQuery().start(5).limit(2)
        jsonObj={ 'start': [ 10, { 'limit': [ 2, {} ] } ] }
        assert woqlObject.addStart(10).json() == jsonObj
        assert woqlObject2.addStart(10).json() == jsonObj

    def test_hasStart_method(self):
        woqlObjectTrue=WOQLQuery().limit(2).start(10)
        woqlObjectFalse=WOQLQuery().limit(2)
        assert woqlObjectTrue.hasStart() == True
        assert woqlObjectFalse.hasStart() == False

    def test_getStart_method(self):
        woqlObject=WOQLQuery().limit(2).start(10)
        assert woqlObject.getStart() == 10

    def test_setLimit_method_not_first(self):
        woqlObject=WOQLQuery().limit(2).start(10)
        jsonObj={ 'limit': [ 3, { 'start': [ 10, {} ] } ] }
        assert woqlObject.setLimit(3).json() == jsonObj

    def test_getLimit_method(self):
        woqlObject=WOQLQuery().limit(2).start(0)
        assert woqlObject.getLimit() == 2

    def test_hasSelect_method(self):
        woqlObjectTrue=WOQLQuery().select("V1", WOQLQuery().triple("a", "b", "c"))
        woqlObjectFalse=WOQLQuery().limit(2).start(0)
        assert woqlObjectTrue.hasSelect() == True
        assert woqlObjectFalse.hasSelect() == False

    def test_getSelectVariables_method(self):
        woqlObject=WOQLQuery().select("V1", WOQLQuery().triple("a", "b", "c"))
        assert woqlObject.getSelectVariables() == ["V1"]

    def test_context_and_getContext_method(self):
        contextObj = {"@import": "https://terminusdb/contexts/woql/syntax/context.jsonld",
           "@propagate": True,
           "db" : "http://localhost:6363/testDB004/"}
        woqlObject=WOQLQuery().limit(2).start(0)
        woqlObject.context(contextObj)
        assert woqlObject.getContext() == contextObj

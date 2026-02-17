Class dc.facialmatching.FacialData Extends (%Persistent, %JSON.Adaptor)
{

Property FaceVector As %Vector(%JSONINCLUDE = "none", DATATYPE = "float", LEN = 4096);

Property Name As %String(MAXLEN = 100);

Property Age As %Integer;

Property Gender As %String;

Property Ethnicity As %String;

Property SSN As %String;

Storage Default
{
<Data name="FacialDataDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>FaceEmbedding</Value>
</Value>
<Value name="3">
<Value>Name</Value>
</Value>
<Value name="4">
<Value>Age</Value>
</Value>
<Value name="5">
<Value>Gender</Value>
</Value>
<Value name="6">
<Value>Ethnicity</Value>
</Value>
<Value name="7">
<Value>SSN</Value>
</Value>
<Value name="8">
<Value>FaceVector</Value>
</Value>
</Data>
<DataLocation>^dc.facialmatching.FacialDataD</DataLocation>
<DefaultData>FacialDataDefaultData</DefaultData>
<IdLocation>^dc.facialmatching.FacialDataD</IdLocation>
<IndexLocation>^dc.facialmatching.FacialDataI</IndexLocation>
<StreamLocation>^dc.facialmatching.FacialDataS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}

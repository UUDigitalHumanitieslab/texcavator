<!--?xml version="1.0" encoding="UTF-8"? -->

<xsl:stylesheet
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	version="1.0"
	xmlns:srw="http://www.loc.gov/zing/srw/"
	xmlns:tel="http://krait.kb.nl/coop/tel/handbook/telterms.html" 
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
	xmlns:diag="http://www.loc.gov/zing/srw/diagnostic/" 
	xmlns:dc="http://purl.org/dc/elements/1.1/"
	xmlns:dcterms="http://purl.org/dc/terms/"
	xmlns:ddd="http://www.kb.nl/ddd">

	<xsl:output 
		method="html" 
		encoding="UTF-8" 
		doctype-public="-//W3C//DTD HTML 4.01//EN" 
		doctype-system="http://www.w3.org/TR/html4/strict.dtd" />

	<xsl:template match="srw:searchRetrieveResponse">
		<html>
			<head>
				<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
			</head>
			<body>
				<xsl:apply-templates select="srw:echoedSearchRetrieveRequest" />
				<xsl:apply-templates select="srw:numberOfRecords" />
				<ol>
					<xsl:attribute name="start">
						<xsl:value-of select="srw:echoedSearchRetrieveRequest/srw:startRecord"/>
					</xsl:attribute>
					<xsl:apply-templates select="srw:records" />
				</ol>
			</body>
		</html>
	</xsl:template>

	<xsl:template match="srw:numberOfRecords">
		<p>Found <xsl:value-of select="."/> records.</p>
	</xsl:template>

	<xsl:template match="srw:echoedSearchRetrieveRequest">
		<span style="float:right">
			<xsl:if test="srw:startRecord &gt; 1">
				<a>
					<xsl:attribute name="href">javascript:nextResults(-<xsl:value-of select="srw:maximumRecords"/>);</xsl:attribute>
					previous
				</a> | 
			</xsl:if>
			<a>
				<xsl:attribute name="href">javascript:nextResults(<xsl:value-of select="srw:maximumRecords"/>);</xsl:attribute>
				next
			</a>
		</span>
	</xsl:template>

	<xsl:template match="srw:records">
		<xsl:apply-templates select="srw:record/srw:recordData" /> 
	</xsl:template>


<!--
Old Verity example response
<srw:record>
	<srw:recordPacking>xml</srw:recordPacking>
	<srw:recordSchema>http://www.kb.nl/ddd</srw:recordSchema>
	<srw:recordData>
		<ddd:accessible>1</ddd:accessible>
		<ddd:paperurl>http://resolver.kb.nl/resolve?urn=ddd:010015649:mpeg21</ddd:paperurl>
		<ddd:pageurl>ddd:010015649:mpeg21:p002</ddd:pageurl>
		<dc:title>INTERNAT. BENDE VAN OPIUMSMOKKELAARS ONTMASKERD Een wijd vertakte bende, met vele chineezen, Grieken en a.s. ook een inspecteur van politie als leden</dc:title>
		<ddd:papertitle>Het Vaderland : staat- en letterkundig nieuwsblad</ddd:papertitle>
		<ddd:publisher>M. Nĳhoff [etc.]</ddd:publisher>
		<dc:date>1934/11/03 00:00:00</dc:date>
		<ddd:alternative>Het Vaderland</ddd:alternative>
		<ddd:edition>Avond</ddd:edition>
		<ddd:ppn>832689858</ddd:ppn>
		<ddd:url>http://resources2.kb.nl/010015000/articletext/010015649/DDD_010015649_0021_articletext.xml</ddd:url>
		<dc:type>artikel</dc:type>
		<ddd:issue>0</ddd:issue>
		<ddd:spatialCreation>'s-Gravenhage</ddd:spatialCreation>
		<ddd:year>1934</ddd:year>
		<ddd:page>2</ddd:page>
		<ddd:vdkvgwkey>http://resolver.kb.nl/resolve?urn=ddd:010015649:mpeg21:a0021:ocr</ddd:vdkvgwkey>
		<dc:identifier>http://resolver.kb.nl/resolve?urn=ddd:010015649:mpeg21:a0021:ocr</dc:identifier>
		<dc:source>KB NBM C 44 [Microfilm]</dc:source>
	</srw:recordData>
	<srw:recordPosition>1</srw:recordPosition>
</srw:record>

New Lucene example response
	<srw:record>
		<srw:recordPacking>xml</srw:recordPacking>
		<srw:recordSchema>http://www.kb.nl/ddd</srw:recordSchema>
		<srw:recordData>
			<ddd:metadataKey>http://resolver.kb.nl/resolve?urn=ddd:010013335:mpeg21:a0295</ddd:metadataKey>
			<dc:type>artikel</dc:type>
			<ddd:spatial>Landelijk</ddd:spatial>
			<ddd:page>1</ddd:page>
			<ddd:edition>Dag</ddd:edition>
			<ddd:pageurl>ddd:010013335:mpeg21:p013</ddd:pageurl>
			<ddd:paperurl>http://resolver.kb.nl/resolve?urn=ddd:010013335:mpeg21</ddd:paperurl>
			<ddd:yearsdigitized>1920-1945</ddd:yearsdigitized>
			<ddd:alternative>Het Vaderland</ddd:alternative>
			<ddd:publisher>M. Nĳhoff [etc.]</ddd:publisher>
			<dc:source>KB NBM C 44 [Microfilm]</dc:source>
			<ddd:ppn>832689858</ddd:ppn>
			<ddd:accessible>1</ddd:accessible>
			<ddd:papertitle>Het Vaderland : staat- en letterkundig nieuwsblad</ddd:papertitle>
			<dc:date>1931/02/01 00:00:00</dc:date>
			<ddd:issued>1869-1945</ddd:issued>
			<ddd:spatialCreation>'s-Gravenhage</ddd:spatialCreation>
			<dc:title>OPIUM</dc:title>
		</srw:recordData>
		<srw:recordPosition>0</srw:recordPosition>
	</srw:record>
-->

	<xsl:template match="srw:recordData">
	<!-- previous Verity response -->
	<!--<xsl:value-of select="substring-after(dc:identifier, 'http://resolver.kb.nl/resolve?urn=')" />-->

	<!-- current Lucene response -->
		<xsl:variable name="identifier"><xsl:value-of select="substring-after(ddd:metadataKey, 'http://resolver.kb.nl/resolve?urn=')" />:ocr</xsl:variable>
		<li>
			<a>
			<!--<xsl:attribute name="href">javascript:dojo.publish("/kb/record/selected", ["<xsl:copy-of select="$identifier" />"]);</xsl:attribute> -->
				<xsl:attribute name="href">javascript:retrieveRecord("DSTORE_MONGODB", "kb_2013","<xsl:copy-of select="$identifier" />");</xsl:attribute>
				<xsl:attribute name="title"><xsl:value-of select="dc:title" /></xsl:attribute>
				<b><xsl:value-of select="substring(dc:title, 0, 45)" /></b>
				<xsl:if test="string-length(dc:title) &gt; 45">...</xsl:if>
			</a>
			<br />
			<xsl:value-of select="ddd:papertitle" />
			<br />
			<xsl:value-of select="substring-before(dc:date, ' ')" />, 
			<xsl:value-of select="ddd:edition" />. 
			<xsl:value-of select="ddd:spatial" /> 
			<em><xsl:value-of select="dcterms:abstract" /></em>
		</li>
	</xsl:template>

	<!--
	<xsl:template match="cd">
	<h1><xsl:value-of select="title"/></h1>
	<h2>by <xsl:value-of select="artist"/> - <xsl:value-of select="year"/></h2>
	<hr />
	</xsl:template>
	-->

</xsl:stylesheet>
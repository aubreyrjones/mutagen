<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
    <office---text>
        <xsl:apply-templates />
    </office---text>
</xsl:template>

<xsl:template match="section">
    <xsl:apply-templates />
</xsl:template>


<xsl:template match="m-stitle">
    <text---p text---style-name="SECTION_TITLE"><xsl:value-of select="."/></text---p>
</xsl:template>

<xsl:template match="m-sdesc">
    <text---p text---style-name="SECTION_DESCRIPTION"><xsl:value-of select="."/></text---p>
</xsl:template>


<xsl:template match="m-i">
    <text---p text---style-name="ITEM_BLOCK">
        <xsl:apply-templates />
    </text---p>
</xsl:template>

<xsl:template match="m-ih">
        <text---span text---style-name="ITEM_TITLE"><xsl:apply-templates /></text---span>
</xsl:template>

<xsl:template match="m-it">
    <xsl:value-of select="."/>
</xsl:template>

<xsl:template match="m-id">
    <text---span text---style-name="ITEM_DESC">
        <xsl:apply-templates />
    </text---span>
</xsl:template>


<xsl:template match="m-in">
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="m-il">
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="m-inv">
    <xsl:apply-templates />
</xsl:template>


<xsl:template match="m-c">
    <xsl:apply-templates />
</xsl:template>


<xsl:template match="m-s">
    <xsl:apply-templates />
</xsl:template>

</xsl:stylesheet> 
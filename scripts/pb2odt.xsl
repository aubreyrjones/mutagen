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
    <text---h text---style-name="SECTION_TITLE"><xsl:value-of select="."/></text---h>
</xsl:template>

<xsl:template match="m-sdesc">
    <text---p text---style-name="SECTION_DESCRIPTION"><xsl:value-of select="."/></text---p>
</xsl:template>


<xsl:template match="item-header-p">
    <text---p text---style-name="ITEM_DESC"><xsl:apply-templates /></text---p>
</xsl:template>

<xsl:template match="m-ih">
    <text---span text---style-name="ITEM_TITLE"><xsl:apply-templates /></text---span>
</xsl:template>

<xsl:template match='m-p'>
    <text---p text---style-name="ITEM_DESC"><xsl:apply-templates /></text---p>
</xsl:template>

<xsl:template match="labeled-input">
    <text---p text---style-name="FIRST_INPUT_LINE">⎧</text---p>
    <text---p text---style-name="INPUT_LINE"><xsl:apply-templates select="m-il" /></text---p>
    <text---p text---style-name="INPUT_LINE">⎩</text---p>
</xsl:template>

<xsl:template match="m-li">
    <text---p text---style-name="LINE_ITEM"><xsl:apply-templates /></text---p>
</xsl:template>

<xsl:template match="m-il">
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="box-input">
    <text---p text---style-name="FIRST_INPUT_LINE">⎧</text---p>
    <text---p text---style-name="INPUT_LINE">⎩</text---p>
</xsl:template>

<xsl:template match="m-res">
    <text---p text---style-name="LINE_ITEM"><xsl:apply-templates /></text---p>
</xsl:template>


<xsl:template match="m-c">
    <xsl:apply-templates />
</xsl:template>


<xsl:template match="m-s">
    <xsl:apply-templates />
</xsl:template>

</xsl:stylesheet> 
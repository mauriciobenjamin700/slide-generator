"""Default ABNT-flavored CSS used when converting Markdown to PDF."""


ABNT_CSS: str = """
@page {
	size: A4;
	margin: 3cm 2cm;
	@bottom-center {
		content: counter(page);
		font-family: "Times New Roman";
		font-size: 10pt;
	}
}

body {
	font-family: "Times New Roman", serif;
	font-size: 12pt;
	text-align: justify;
	line-height: 1.5;
	color: #000000;
	padding-top: 20px;
}

h1 {
	font-size: 14pt;
	font-weight: bold;
	text-align: center;
	margin-top: 30pt;
	margin-bottom: 18pt;
	text-transform: uppercase;
}

h2 {
	font-size: 12pt;
	font-weight: bold;
	text-align: left;
	margin-top: 24pt;
	margin-bottom: 12pt;
}

h3, h4, h5, h6 {
	font-size: 12pt;
	font-weight: bold;
	text-align: left;
	margin-top: 18pt;
	margin-bottom: 12pt;
}

p {
	margin-bottom: 12pt;
	text-indent: 1.25cm;
}

ul, ol {
	margin-bottom: 12pt;
	margin-left: 1.25cm;
}

li {
	margin-bottom: 6pt;
}

.codehilite, pre {
	background: #f8f8f8;
	border: 1px solid #ddd;
	border-radius: 3px;
	padding: 10px;
	margin: 15px 0;
	overflow: auto;
	font-family: "Courier New", monospace;
	font-size: 10pt;
}

table {
	border-collapse: collapse;
	width: 100%;
	margin: 15px 0;
	font-size: 10pt;
}

th, td {
	border: 1px solid #000;
	padding: 5px 8px;
	text-align: center;
}

th {
	background-color: #f2f2f2;
	font-weight: bold;
}

.MathJax_Display, .arithmatex {
	text-align: center;
	margin: 15px 0;
	font-size: 11pt;
}

strong, b {
	font-weight: bold;
}

em, i {
	font-style: italic;
}

img {
	max-width: 100%;
	display: block;
	margin: 15px auto;
	text-align: center;
}

.footnote {
	font-size: 10pt;
}

.mermaid-diagram {
	text-align: center;
	margin: 15px auto;
	page-break-inside: avoid;
	overflow: hidden;
}

.mermaid-diagram svg {
	max-width: 100%;
	max-height: 220mm;
	height: auto;
	width: auto;
	display: block;
	margin: 0 auto;
}

.mermaid-error {
	background: #fff3cd;
	border: 1px solid #ffc107;
	border-radius: 4px;
	padding: 10px;
	margin: 15px 0;
	font-family: "Courier New", monospace;
	font-size: 9pt;
	color: #856404;
	white-space: pre-wrap;
	page-break-inside: avoid;
}
"""

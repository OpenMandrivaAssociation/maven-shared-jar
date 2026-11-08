Name:		maven-shared-jar
Version:	3.2.1
Release:	1
Epoch:		1
Summary:	Maven JAR identification utilities
Group:		Development/Java
License:	Apache-2.0
URL:		https://maven.apache.org/shared/maven-shared-jar/
Source0:	https://github.com/apache/maven-shared-jar/archive/refs/tags/maven-shared-jar-%{version}.tar.gz#/maven-shared-jar-%{version}.tar.gz
BuildArch:	noarch
BuildRequires:	python
# The maven RPM holds the class jars. maven-components owns the coordinates.
BuildRequires:	maven
BuildRequires:	maven-components >= 3.10.0
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.apache.maven:maven-model)
BuildRequires:	mvn(org.apache.maven:maven-artifact)
BuildRequires:	mvn(org.apache.bcel:bcel)
BuildRequires:	apache-commons-bcel >= 6.13.0
Requires:	apache-commons-bcel >= 6.13.0
BuildRequires:	mvn(commons-codec:commons-codec)
BuildRequires:	apache-commons-codec >= 1.23.0
Requires:	apache-commons-codec >= 1.23.0
BuildRequires:	mvn(org.apache.commons:commons-collections4)
BuildRequires:	apache-commons-collections4 >= 4.6.0
Requires:	apache-commons-collections4 >= 4.6.0
BuildRequires:	mvn(org.codehaus.plexus:plexus-utils)
BuildRequires:	plexus-utils >= 3.6.2
Requires:	plexus-utils >= 3.6.2
BuildRequires:	mvn(org.slf4j:slf4j-api)
BuildRequires:	mvn(javax.inject:javax.inject)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
Identifies a JAR from its classes, manifest, filenames, and bytecode
hash. 3.2.1 reads multi-release entries through JDK 25. plexus-xml is
not packaged; the pull-parser exception comes from plexus-utils 3.6.2.
Tests are not run.

%prep
%autosetup -n maven-shared-jar-maven-shared-jar-%{version}
rm -rf src/test .github
python - <<'PY'
import xml.etree.ElementTree as ET
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def tag(name):
    return "{" + NS + "}" + name

def add(parent, name, text):
    node = ET.SubElement(parent, tag(name))
    node.text = text
    return node

root = ET.Element(tag("project"))
add(root, "modelVersion", "4.0.0")
add(root, "groupId", "org.apache.maven.shared")
add(root, "artifactId", "maven-shared-jar")
add(root, "version", "%{version}")
add(root, "name", "Apache Maven JAR Utilities")
props = ET.SubElement(root, tag("properties"))
add(props, "maven.compiler.release", "8")
add(props, "project.build.sourceEncoding", "UTF-8")
deps = ET.SubElement(root, tag("dependencies"))
for group, artifact, version, scope in (
    ("org.apache.maven", "maven-model", "3.10.0", "provided"),
    ("org.apache.maven", "maven-artifact", "3.10.0", "provided"),
    ("org.apache.bcel", "bcel", "6.13.0", ""),
    ("commons-codec", "commons-codec", "1.23.0", ""),
    ("org.apache.commons", "commons-collections4", "4.6.0", ""),
    ("org.codehaus.plexus", "plexus-utils", "3.6.2", ""),
    ("org.slf4j", "slf4j-api", "1.7.36", ""),
    ("javax.inject", "javax.inject", "1", ""),
):
    dep = ET.SubElement(deps, tag("dependency"))
    add(dep, "groupId", group)
    add(dep, "artifactId", artifact)
    add(dep, "version", version)
    if scope:
        add(dep, "scope", scope)
ET.ElementTree(root).write("pom.xml", encoding="utf-8", xml_declaration=True)
PY
# Sisu loads @Named classes from this index. The indexer plugin is not packaged.
python - <<'PY'
import re
from pathlib import Path
root = Path("src/main/java")
names = []
for path in sorted(root.rglob("*.java")):
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//.*?$", "", text, flags=re.M)
    match = re.search(r"\b(?:class|interface|enum)\s+([A-Za-z0-9_]+)", text)
    if not match:
        continue
    if "@Named" not in text[:match.start()]:
        continue
    pkg = re.search(r"(?m)^package\s+([A-Za-z0-9_.]+)\s*;", text)
    if not pkg:
        continue
    names.append(pkg.group(1) + "." + match.group(1))
if names:
    dest = Path("src/main/resources/META-INF/sisu")
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "javax.inject.Named").write_text("\n".join(names) + "\n", encoding="utf-8")
PY

%files -f .mfiles
%doc LICENSE README.md

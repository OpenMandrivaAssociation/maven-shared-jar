%_javapackages_macros
Name:           maven-shared-jar
Version:        1.1
Release:        5.0%{?dist}
# Maven-shared defines maven-shared-jar version as 1.1
Epoch:          1
Summary:        Maven JAR Utilities
License:        ASL 2.0
URL:            http://maven.apache.org/shared/maven-shared-jar
Source0:        http://repo1.maven.org/maven2/org/apache/maven/shared/%{name}/%{version}/%{name}-%{version}-source-release.zip

BuildArch:      noarch

BuildRequires:  maven-local
BuildRequires:  mvn(commons-collections:commons-collections)
BuildRequires:  mvn(org.apache.bcel:bcel)
BuildRequires:  mvn(org.apache.maven.shared:maven-shared-components)
BuildRequires:  mvn(org.apache.maven:maven-artifact)
BuildRequires:  mvn(org.apache.maven:maven-model)
BuildRequires:  mvn(org.codehaus.plexus:plexus-container-default)
BuildRequires:  mvn(org.codehaus.plexus:plexus-digest)


Obsoletes:      maven-shared-jar < %{epoch}:%{version}-%{release} 
Provides:       maven-shared-jar = %{epoch}:%{version}-%{release}

%description
Utilities that help identify the contents of a JAR, including Java class
analysis and Maven metadata analysis.

This is a replacement package for maven-shared-jar

%package javadoc
Summary:        Javadoc for %{name}
    
%description javadoc
API documentation for %{name}.


%prep
%setup -q

%pom_add_dep org.codehaus.plexus:plexus-container-default

find -type f -iname '*.jar' -delete

# Replace plexus-maven-plugin with plexus-component-metadata
find -name 'pom.xml' -exec sed \
    -i 's/<artifactId>plexus-maven-plugin<\/artifactId>/<artifactId>plexus-component-metadata<\/artifactId>/' '{}' ';'
find -name 'pom.xml' -exec sed \
    -i 's/<goal>descriptor<\/goal>/<goal>generate-metadata<\/goal>/' '{}' ';'

%build
# Tests require the jars that were removed
%mvn_build -f

%install
%mvn_install

%files -f .mfiles
%doc LICENSE NOTICE

%files javadoc -f .mfiles-javadoc
%doc LICENSE NOTICE

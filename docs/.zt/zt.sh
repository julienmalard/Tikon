#!/usr/bin/env bash

if [ "$TRAVIS_BRANCH" = "master" ] ; then
 # cd .misc
 instalar_zanata
 jalar_de_zanata
 mandar_a_zanata
fi

instalar_zanata() {
  if [ ! -f ./zanata-cli-3.6.0/bin/zanata-cli ] ; then
    echo Descargando Zanata...
    wget http://search.maven.org/remotecontent?filepath=org/zanata/zanata-cli/3.6.0/zanata-cli-3.6.0-dist.zip -O dist.zip -o /dev/null
    echo Extraendo Zanata...
    unzip dist.zip > /dev/null
    rm dist.zip
  fi
}

jalar_de_zanata() {
  
}

mandar_a_zanata() {
  zanata-cli-3.6.0/bin/zanata-cli -B push --key $ZANATA_API --username julienmalard --url https://translate.zanata.org/zanata/
}
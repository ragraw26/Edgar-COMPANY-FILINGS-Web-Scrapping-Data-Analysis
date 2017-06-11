#!/bin/bash

python3 /src/assignment1/parsingHTML.py $CIK  $ACCESSION

mv /src/*zip /src/assignment1/Output/
mv /src/log*.txt /src/assignment1/Output/

if [ $? -eq 0 ]
then
  echo "Successfully created file"
  sh /src/assignment1/awsS3Upload.sh
else
  echo "Could not create file" >&2
fi

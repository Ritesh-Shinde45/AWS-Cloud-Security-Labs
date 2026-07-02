#!/bin/bash

BUCKET_NAME=" "
LOCAL_FILE="report.csv"
S3_KEY=""

aws s3 mb s3://$BUCKET_NAME
aws s3 cp $LOCAL_FILE s3://$BUCKET_NAME/$S3_KEY
aws s3 ls s3://$BUCKET_NAME --recursive --human-readable --summarize
aws s3 cp s3://$BUCKET_NAME/$S3_KEY ./downloaded_report.csv
aws s3 sync ./my_local_folder s3://$BUCKET_NAME/folder-backup/
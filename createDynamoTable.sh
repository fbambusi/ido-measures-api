  aws dynamodb create-table --table-name ido-sensors-prod --attribute-definitions \
  AttributeName=hashKey,AttributeType=S  \
  AttributeName=sortKey,AttributeType=S \
  --key-schema AttributeName=hashKey,KeyType=HASH AttributeName=sortKey,KeyType=RANGE \
  --provisioned-throughput \
  ReadCapacityUnits=2,WriteCapacityUnits=2 $EP
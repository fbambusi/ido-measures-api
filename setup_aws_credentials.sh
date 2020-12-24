token="z-y9MxTXFURSTbZ17m6d"
AWS_ACCESS_KEY_ID="AKIAR4O2IG25ECI55ATM"
AWS_SECRET_ACCESS_KEY="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"
URL_ENCODED_PROJECT_NAME="wiseair-serverless%2Fhistorical-data"

curl -X POST --header "PRIVATE-TOKEN: $token" "https://gitlab.com/api/v4/projects/$URL_ENCODED_PROJECT_NAME/variables" \
-H "Content-Type: application/json; charset=utf-8" \
-d "{\"key\":\"AWS_ACCESS_KEY_ID\",\"value\":\"$AWS_ACCESS_KEY_ID\",\"protected\":\"true\",\"masked\":\"true\"}"
curl -X POST --header "PRIVATE-TOKEN: $token" "https://gitlab.com/api/v4/projects/wiseair-serverless%2Fpredictions/variables" \
-H "Content-Type: application/json; charset=utf-8" \
-d "{\"key\":\"AWS_SECRET_ACCESS_KEY\",\"value\":\"$AWS_SECRET_ACCESS_KEY\",\"protected\":\"true\",\"masked\":\"true\"}"


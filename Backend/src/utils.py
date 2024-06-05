# AWS Cognitoの設定情報を定義します。
COGNITO_JWKS_URL = "https://cognito-idp.<region>.amazonaws.com/<user-pool-id>/.well-known/jwks.json"
COGNITO_AUDIENCE = "<user-pool-client-id>"
COGNITO_ISSUER = "https://cognito-idp.<region>.amazonaws.com/<user-pool-id>"

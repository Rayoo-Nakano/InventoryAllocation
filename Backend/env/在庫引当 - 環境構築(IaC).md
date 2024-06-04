IaC (Infrastructure as Code) を使用して AWS 環境を構築し、CI/CD パイプラインを設定する方法を以下に示します。

## 1. AWS 環境の IaC (Infrastructure as Code)

AWS CloudFormationを使用して、AWS 環境のインフラストラクチャをコードとして定義および管理します。

以下は、AWS 環境の構築を図式化したものです。

```mermaid
graph LR
    A[AWS CloudFormation] --> B(VPC)
    A --> C(インターネットゲートウェイ)
    A --> D(サブネット)
    A --> E(セキュリティグループ)
    A --> F(RDS - PostgreSQL)
    A --> G(Lambda 関数)
    A --> H(API Gateway)
    B --> D
    C --> B
    D --> E
    E --> F
    E --> G
    G --> H
    H --> I((API エンドポイント))
```

1. AWS CloudFormation テンプレートが環境のリソースを定義します。

2. VPC (Virtual Private Cloud) が作成されます。

3. インターネットゲートウェイが作成され、VPC に接続されます。

4. サブネットが VPC 内に作成されます。

5. セキュリティグループが作成され、サブネットに関連付けられます。

6. RDS (PostgreSQL) インスタンスが作成され、セキュリティグループによって保護されます。

7. Lambda 関数が作成され、セキュリティグループによって保護されます。

8. API Gateway が作成され、Lambda 関数と統合されます。

9. API エンドポイントが公開され、クライアントからアクセス可能になります。

この図は、AWS CloudFormation を使用して環境のリソースを定義し、それらのリソースが相互に関連付けられる方法を示しています。VPC とサブネットが作成され、セキュリティグループによってリソースが保護されます。RDS と Lambda 関数がデータベースとアプリケーションロジックを提供し、API Gateway がクライアントからのリクエストを受け付けます。

これらの図を組み合わせることで、インフラストラクチャとCI/CDパイプラインの全体像を把握することができます。AWS CloudFormation はインフラストラクチャをコードとして管理し、AWS CodePipeline、AWS CodeBuild、AWS CodeArtifact はアプリケーションのビルド、テスト、デプロイを自動化します。




```yaml
# AWS CloudFormation テンプレート例

AWSTemplateFormatVersion: '2010-09-09'
Description: 'Inventory Allocation System Infrastructure'

Resources:
  # VPC
  VPC:
    Type: 'AWS::EC2::VPC'
    Properties:
      CidrBlock: '10.0.0.0/16'
      EnableDnsHostnames: true
      EnableDnsSupport: true
      InstanceTenancy: default
      Tags:
        - Key: Name
          Value: 'Inventory-Allocation-VPC'

  # インターネットゲートウェイ
  InternetGateway:
    Type: 'AWS::EC2::InternetGateway'
    Properties:
      Tags:
        - Key: Name
          Value: 'Inventory-Allocation-IGW'

  # サブネット
  PublicSubnet1:
    Type: 'AWS::EC2::Subnet'
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: '10.0.1.0/24'
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: 'Inventory-Allocation-Public-Subnet-1'

  # セキュリティグループ
  WebSecurityGroup:
    Type: 'AWS::EC2::SecurityGroup'
    Properties:
      GroupDescription: 'Security group for web servers'
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: '0.0.0.0/0'
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: '0.0.0.0/0'

  # RDS (PostgreSQL)
  RDSInstance:
    Type: 'AWS::RDS::DBInstance'
    Properties:
      Engine: postgres
      EngineVersion: '12.7'
      DBInstanceClass: db.t3.micro
      AllocatedStorage: '20'
      StorageType: gp2
      MultiAZ: false
      PubliclyAccessible: false
      DBName: 'inventory_allocation_db'
      MasterUsername: 'admin'
      MasterUserPassword: !Ref DBPassword
      VPCSecurityGroups:
        - !Ref DBSecurityGroup

  # Lambda 関数
  AllocationLambdaFunction:
    Type: 'AWS::Lambda::Function'
    Properties:
      FunctionName: 'inventory-allocation-function'
      Runtime: 'python3.8'
      Handler: 'main.lambda_handler'
      Role: !GetAtt LambdaExecutionRole.Arn
      Code:
        S3Bucket: 'inventory-allocation-code-bucket'
        S3Key: 'lambda_function.zip'
      Environment:
        Variables:
          DB_HOST: !GetAtt RDSInstance.Endpoint.Address
          DB_PORT: !GetAtt RDSInstance.Endpoint.Port
          DB_NAME: 'inventory_allocation_db'
          DB_USER: 'admin'
          DB_PASSWORD: !Ref DBPassword

  # API Gateway
  APIGateway:
    Type: 'AWS::ApiGateway::RestApi'
    Properties:
      Name: 'Inventory Allocation API'
      Description: 'API for Inventory Allocation System'

  # API Gateway リソース
  OrdersResource:
    Type: 'AWS::ApiGateway::Resource'
    Properties:
      RestApiId: !Ref APIGateway
      ParentId: !GetAtt APIGateway.RootResourceId
      PathPart: 'orders'

  InventoriesResource:
    Type: 'AWS::ApiGateway::Resource'
    Properties:
      RestApiId: !Ref APIGateway
      ParentId: !GetAtt APIGateway.RootResourceId
      PathPart: 'inventories'

  AllocateResource:
    Type: 'AWS::ApiGateway::Resource'
    Properties:
      RestApiId: !Ref APIGateway
      ParentId: !GetAtt APIGateway.RootResourceId
      PathPart: 'allocate'

  AllocationResultsResource:
    Type: 'AWS::ApiGateway::Resource'
    Properties:
      RestApiId: !Ref APIGateway
      ParentId: !GetAtt APIGateway.RootResourceId
      PathPart: 'allocation-results'

  # API Gateway メソッド
  # Orders リソースのメソッド
  OrdersPostMethod:
    Type: 'AWS::ApiGateway::Method'
    Properties:
      RestApiId: !Ref APIGateway
      ResourceId: !Ref OrdersResource
      HttpMethod: POST
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${AllocationLambdaFunction.Arn}/invocations'

  OrdersGetMethod:
    Type: 'AWS::ApiGateway::Method'
    Properties:
      RestApiId: !Ref APIGateway
      ResourceId: !Ref OrdersResource
      HttpMethod: GET
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${AllocationLambdaFunction.Arn}/invocations'

  # Inventories リソースのメソッド
  InventoriesPostMethod:
    Type: 'AWS::ApiGateway::Method'
    Properties:
      RestApiId: !Ref APIGateway
      ResourceId: !Ref InventoriesResource
      HttpMethod: POST
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${AllocationLambdaFunction.Arn}/invocations'

  InventoriesGetMethod:
    Type: 'AWS::ApiGateway::Method'
    Properties:
      RestApiId: !Ref APIGateway
      ResourceId: !Ref InventoriesResource
      HttpMethod: GET
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${AllocationLambdaFunction.Arn}/invocations'

  # Allocate リソースのメソッド
  AllocatePostMethod:
    Type: 'AWS::ApiGateway::Method'
    Properties:
      RestApiId: !Ref APIGateway
      ResourceId: !Ref AllocateResource
      HttpMethod: POST
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${AllocationLambdaFunction.Arn}/invocations'

  # AllocationResults リソースのメソッド
  AllocationResultsGetMethod:
    Type: 'AWS::ApiGateway::Method'
    Properties:
      RestApiId: !Ref APIGateway
      ResourceId: !Ref AllocationResultsResource
      HttpMethod: GET
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${AllocationLambdaFunction.Arn}/invocations'

# パラメータ
Parameters:
  DBPassword:
    Type: String
    NoEcho: true
    Description: 'Password for the RDS database'
```

上記の AWS CloudFormation テンプレートは、在庫引当システムのインフラストラクチャを定義しています。主要なリソースとして、VPC、サブネット、セキュリティグループ、RDS（PostgreSQL）、Lambda 関数、API Gateway が含まれています。

## 2. CI/CD パイプラインの IaC

以下は、CI/CD パイプラインの構成を図式化したものです。

```mermaid
graph LR
    A[GitHub] --> |ソースコード| B(AWS CodePipeline)
    B --> |ソースアクション| C(ソース)
    C --> |ビルドアクション| D(ビルド)
    D --> |単体テストアクション| E(テスト)
    E --> |デプロイアクション| F(デプロイ)
    D -.-> |アーティファクト| G(AWS CodeArtifact)
    G -.-> |アーティファクト| F
    F --> |CloudFormation| H(AWS CloudFormation)
    H --> |デプロイ| I((AWS リソース))
```

1. GitHub からソースコードが AWS CodePipeline に取り込まれます。

2. CodePipeline のソースアクションがソースコードを取得します。

3. ビルドアクションが AWS CodeBuild を使用してソースコードをビルドします。

4. 単体テストアクションが、ビルドされたアーティファクトに対して JUnit を使用して単体テストを実行します。

5. ビルドアクションの出力アーティファクトが AWS CodeArtifact に格納されます。

6. デプロイアクションが、CodeArtifact から取得したアーティファクトを使用して、AWS CloudFormation を介してデプロイを実行します。

7. CloudFormation がアプリケーションを AWS リソース（Lambda、API Gateway、RDS など）にデプロイします。

この図は、ソースコードが GitHub から取得され、AWS CodePipeline を通じてビルド、テスト、デプロイの各ステージが実行される流れを示しています。ビルドアーティファクトは AWS CodeArtifact に格納され、デプロイ時に取得されます。最終的に、AWS CloudFormation を使用してアプリケーションが AWS リソースにデプロイされます。


```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'CI/CD Pipeline for Inventory Allocation System'

Resources:
  # CodeBuild プロジェクト
  CodeBuildProject:
    Type: 'AWS::CodeBuild::Project'
    Properties:
      Name: 'inventory-allocation-build'
      Description: 'Build project for Inventory Allocation System'
      ServiceRole: !GetAtt CodeBuildServiceRole.Arn
      Artifacts:
        Type: CODEPIPELINE
      Environment:
        Type: LINUX_CONTAINER
        ComputeType: BUILD_GENERAL1_SMALL
        Image: 'aws/codebuild/standard:4.0'
      Source:
        Type: CODEPIPELINE
        BuildSpec: 'buildspec.yml'

  # CodePipeline
  CodePipeline:
    Type: 'AWS::CodePipeline::Pipeline'
    Properties:
      Name: 'inventory-allocation-pipeline'
      RoleArn: !GetAtt CodePipelineServiceRole.Arn
      Stages:
        - Name: Source
          Actions:
            - Name: SourceAction
              ActionTypeId:
                Category: Source
                Owner: ThirdParty
                Provider: GitHub
                Version: '1'
              Configuration:
                Owner: 'your-github-username'
                Repo: 'your-github-repo'
                Branch: 'main'
                OAuthToken: '{{resolve:secretsmanager:github-token}}'
              OutputArtifacts:
                - Name: SourceOutput
        - Name: Build
          Actions:
            - Name: BuildAction
              ActionTypeId:
                Category: Build
                Owner: AWS
                Provider: CodeBuild
                Version: '1'
              Configuration:
                ProjectName: !Ref CodeBuildProject
              InputArtifacts:
                - Name: SourceOutput
              OutputArtifacts:
                - Name: BuildOutput
        - Name: Test
          Actions:
            - Name: UnitTestAction
              ActionTypeId:
                Category: Test
                Owner: AWS
                Provider: CodeBuild
                Version: '1'
              Configuration:
                ProjectName: !Ref CodeBuildProject
              InputArtifacts:
                - Name: BuildOutput
        - Name: Deploy
          Actions:
            - Name: DeployAction
              ActionTypeId:
                Category: Deploy
                Owner: AWS
                Provider: CloudFormation
                Version: '1'
              Configuration:
                ActionMode: CREATE_UPDATE
                StackName: 'inventory-allocation-stack'
                TemplatePath: 'BuildOutput::template.yml'
                RoleArn: !GetAtt CloudFormationExecutionRole.Arn
              InputArtifacts:
                - Name: BuildOutput

  # CodeArtifact リポジトリ
  CodeArtifactRepository:
    Type: 'AWS::CodeArtifact::Repository'
    Properties:
      RepositoryName: 'inventory-allocation-repo'
      DomainName: 'my-domain'
      PermissionsPolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal: '*'
            Action:
              - 'codeartifact:GetPackageVersionAsset'
              - 'codeartifact:ReadFromRepository'
            Resource: '*'

  # 必要な IAM ロールとポリシーを定義
  CodeBuildServiceRole:
    Type: 'AWS::IAM::Role'
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: 'codebuild.amazonaws.com'
            Action: 'sts:AssumeRole'
      Policies:
        - PolicyName: 'CodeBuildPolicy'
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - 'logs:CreateLogGroup'
                  - 'logs:CreateLogStream'
                  - 'logs:PutLogEvents'
                Resource: '*'
              - Effect: Allow
                Action:
                  - 'codeartifact:GetPackageVersionAsset'
                  - 'codeartifact:PublishPackageVersion'
                  - 'codeartifact:PutPackageMetadata'
                Resource: !GetAtt CodeArtifactRepository.Arn

  CodePipelineServiceRole:
    Type: 'AWS::IAM::Role'
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: 'codepipeline.amazonaws.com'
            Action: 'sts:AssumeRole'
      Policies:
        - PolicyName: 'CodePipelinePolicy'
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - 'codebuild:BatchGetBuilds'
                  - 'codebuild:StartBuild'
                Resource: !GetAtt CodeBuildProject.Arn
              - Effect: Allow
                Action:
                  - 'codeartifact:GetPackageVersionAsset'
                  - 'codeartifact:PublishPackageVersion'
                  - 'codeartifact:PutPackageMetadata'
                Resource: !GetAtt CodeArtifactRepository.Arn
```



## 3.Jenkinsを利用した際の例
この例では、Jenkins パイプラインが GitHub からソースコードを取得し、Maven を使用してビルドとテストを行い、AWS CLI を使用して CloudFormation スタックを更新しています。AWS 認証情報は、Jenkins の認証情報管理を使用して安全に管理されます。

Jenkins を使用することで、AWS CodePipeline、AWS CodeBuild、AWS CodeArtifact と同様の CI/CD 機能を実現できます。また、Jenkins の豊富なプラグインエコシステムを活用して、パイプラインをカスタマイズし、特定のニーズに合わせて拡張することができます。

```mermaid
graph LR
    A[GitHub] --> |Webhook| B(Jenkins)
    B --> |ソースコード取得| C(ソース)
    C --> |ビルド| D(ビルド)
    D --> |単体テスト| E(テスト)
    E --> |デプロイ| F(デプロイ)
    D -.-> |アーティファクト| G(Artifactory)
    G -.-> |アーティファクト| F
    F --> |AWS CLI| H(AWS CloudFormation)
    H --> |デプロイ| I((AWS リソース))
```

1. GitHub にプッシュされたソースコードが Webhook を介して Jenkins に通知されます。

2. Jenkins のジョブがトリガーされ、ソースコードを取得します。

3. ビルドステップでソースコードがビルドされます。

4. 単体テストステップで、ビルドされたアーティファクトに対して JUnit を使用して単体テストが実行されます。

5. ビルドアーティファクトが Artifactory などのアーティファクトリポジトリに格納されます。

6. デプロイステップで、Artifactory から取得したアーティファクトを使用して、AWS CLI を介して AWS CloudFormation スタックが更新されます。

7. CloudFormation がアプリケーションを AWS リソース（Lambda、API Gateway、RDS など）にデプロイします。

Jenkins パイプラインは、Jenkinsfile を使用して定義できます。Jenkinsfile は、パイプラインのステップとその設定を含む Groovy スクリプトです。以下は、上記の CI/CD パイプラインを表す Jenkinsfile の例です。

```groovy
pipeline {
    agent any

    stages {
        stage('Source') {
            steps {
                git 'https://github.com/your-repo.git'
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
        stage('Deploy') {
            steps {
                withAWS(credentials: 'aws-credentials', region: 'us-west-2') {
                    sh 'aws cloudformation update-stack --stack-name my-stack --template-body file://template.yml'
                }
            }
        }
    }
}
```


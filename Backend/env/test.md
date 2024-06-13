以下の図は、CI/CDパイプラインのアーキテクチャ概要と処理の流れを示しています。

```mermaid
graph LR
    A[ソースコード] --> B[AWS CodePipeline]
    B --> C{Lambdaファンクション存在チェック}
    C -->|存在する| D[AWS CodeBuild]
    C -->|存在しない| E[Lambdaファンクション作成]
    E --> D
    D --> F{ビルド成功?}
    F -->|Yes| G[AWS CodeDeploy]
    F -->|No| H[ビルド失敗]
    G --> I{デプロイ成功?}
    I -->|Yes| J[本番環境]
    I -->|No| K[デプロイ失敗]

    subgraph 処理概要
        B["1. CodePipelineがソースコードの変更を検知"]
        C["2. Lambdaファンクションの存在チェック"]
        E["3. Lambdaファンクションが存在しない場合は新規作成"]
        D["4. CodeBuildでソースコードのビルド"]
        G["5. CodeDeployを使用してLambdaファンクションへデプロイ"]
        J["6. 本番環境で新しいバージョンのLambdaファンクションが稼働"]
    end
```

処理の流れ:
1. AWS CodePipelineがソースコードの変更を検知します。
2. Lambdaファンクションの存在チェックを行います。
3. Lambdaファンクションが存在しない場合は、新規作成します。
4. AWS CodeBuildを使用してソースコードのビルドを行います。
5. ビルドが成功した場合、AWS CodeDeployを使用してLambdaファンクションへデプロイします。
6. デプロイが成功すると、本番環境で新しいバージョンのLambdaファンクションが稼働します。

ビルドまたはデプロイが失敗した場合は、それぞれのエラー処理が行われます。
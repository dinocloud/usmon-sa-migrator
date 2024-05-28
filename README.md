## Script para la migracion de un Azure SA a AWS s3

1. Crear instacia E2 la cual cuente con un rol para escribir en el bucket S3 donde se migrara el servicio. El rol debe contar con la siguiente politica:

    > [!IMPORTANT]
    > Remplazar BUCKET_NAME por nombre real de bucket

    ```
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:DeleteObject",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:PutObjectAcl"
                ],
                "Resource": [
                "arn:aws:s3:::BUCKET_NAME/*",
                "arn:aws:s3:::BUCKET_NAME"
                ]
            },
            {
                "Effect": "Allow",
                "Action": "s3:ListAllMyBuckets",
                "Resource": "arn:aws:s3:::*"
            }    
        ]
    }
    ```

2. Instalar AWS Cli y probar listar buckets

    * https://docs.aws.amazon.com/es_es/cli/v1/userguide/cli-chap-install.html
    * aws s3 ls

2. Instalar Azure Cli

    * https://learn.microsoft.com/es-es/cli/azure/install-azure-cli


1. Instalar rclone  

    * https://rclone.org/install/

4.


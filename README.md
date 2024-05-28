## Script para la migracion de un Azure SA a AWS s3

1. Crear instacia E2, preferentemente Amazon Linux 2, la cual cuente con un rol para escribir en el bucket S3 donde se migrara el servicio. El rol debe contar con la siguiente politica:

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

2. Instalar GIT y clonar este repositorio

    * yum install git
    * git clone https://github.com/dinocloud/usmon-sa-migrator.git
    * python3 dependencias/get-pip.py --user

3. Si no usamos Amazon Linux debemos instalar AWS Cli y probar listar buckets

    * https://docs.aws.amazon.com/es_es/cli/v1/userguide/cli-chap-install.html
    * Para comprobar la funcionalidad: aws s3 ls
    ```
    2024-05-10 05:32:26 cdk-platformr-assets-xxxx-us-west-2
    2023-06-28 04:08:27 cf-templates-xxx-us-west-2
    2024-05-22 19:44:52 poc-xxxx-usmon
    2024-04-24 20:48:34 asd-data-xxxx-poc-us-xxxx-2
    2024-04-24 20:17:11 asd-dev-tfstates-xxxxx-west-2
    2024-05-19 03:43:24 asd-xxx-tf-states-xxxx-xxxx-2
    ```

4. Instalar Azure Cli e iniciar sesion para configurar la SP (Service principal), que le dara el acceso al RCLONE para realizar el copiado.

    * curl -L https://aka.ms/InstallAzureCli | bash
    * az login 
    * Para comprobar la funcionalidad: az vm list

    A continuacion crear la SP. Los datos entre llaves {} se deben obtener desde la consola visitando el recurso a clonar.

    ```
    {Subscription ID} -> Subscription ID    
    {Resource Group Name} -> Argumento "Resource group"
    {Storage Account Name} -> Nombre de storage account
    ```
    
    * az ad sp create-for-rbac --name AWS-Rclone-Reader --role "Storage Blob Data Reader" --scopes /subscriptions/{Subscription ID}/resourceGroups/{Resource Group Name}/providers/Microsoft.Storage/storageAccounts/{Storage Account Name} 

    Si todo es correcto deberia generar el recurso y devolver por unica vez un Json con las credenciales

    ```
    {
        "appId": "xxxxxx-fc8d-4b73-9a58-xxxxxx",
        "displayName": "AWS-Rclone-Reader-TEST",
        "password": "bRu8Q~xxxxx~2eu2TLtcZ11.xxxxxxxx",
        "tenant": "xxxx-dd10-4cf6-xxxxx-xxxxx"
    }
    ```
    Estas credenciales debemos crear e insertarlas en el archivo azure-principal.json usando como template el archivo azure-principal.json.template

5. Instalar rclone y configurar

    * sudo -v ; curl https://rclone.org/install.sh | sudo bash
    * rclone --version

    ```
    rclone v1.66.0
    - os/version: amazon 2023.4.20240513 (64 bit)
    - os/kernel: 6.1.90-99.173.amzn2023.x86_64 (x86_64)
    - os/type: linux
    - os/arch: amd64
    - go/version: go1.22.1
    - go/linking: static
    - go/tags: none
    ```

    Una vez instalado debemos crear el siguiente archivo

    * mkdir -p ~/.config/rclone
    * touch ~/.config/rclone/rclone.conf
    * vim ~/.config/rclone/rclone.conf

    A continaucion insertar el siguiente contenido y guardarlo

    ```
    [AZStorageAccount]
    type = azureblob
    account = NOMBRE_DEL_STORAGE
    service_principal_file = azure-principal.json
    env_auth = false

    [s3]
    type = s3
    provider = AWS
    env_auth = true
    region = us-west-2
    ```
    
    Para corroborar que se haya configurado bien ingresamos el siguiente comando

    * rclone listremotes 

    Debe devolver lo siguiente: 

    ```
    AZStorageAccount:
    s3:
    ```

5. Para iniciar el proceso de migracion se debe ejcutar el siguiente comando:

    Antes de iniciar el proceso de migracion de archivos debemos crear un archivo containers_file.json en el root de este proyecto y definirle todos los containers que se van a usar en formato json.

    * python3 migration.py --bucket NOMBRE_DEL_BUCKET_DE_DESTINO --containers_json containers_file.json --transfers 8 --checkers 16

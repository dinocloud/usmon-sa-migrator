## Script para la migracion de un Azure SA a AWS s3

1. Configurar rclone

    * vim ~/.config/rclone/rclone.conf

    A continaucion remplazar el valor NOMBRE_DEL_STORAGE por el de origen

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

2. Clonar repositorio e instalar dependencias

    * git clone https://github.com/dinocloud/usmon-sa-migrator.git
    * cd usmon-sa-migrator
    * python3 dependencias/get-pip.py --user

2. Instalar Azure Cli e iniciar sesion para configurar la SP (Service principal), que le dara el acceso al RCLONE para realizar el copiado.

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

4. Antes de iniciar el proceso de migracion de archivos debemos crear un archivo containers_file.json en el root de este proyecto y definirle todos los containers que se van a usar en formato json. Ver referencia en archivo containers_file.json.template.

    Para descargar los container usando la cli de Azure se debe correr el siguiente comando:

    * az storage container list --account-name NOMBRE_DE_STORAGE_ACCOUNT --query '[].name'

    Para iniciar el proceso de migracion se debe ejcutar el siguiente comando:

    * python3 migration.py --bucket NOMBRE_DEL_BUCKET_DE_DESTINO --containers_json containers_file.json --transfers 8 --checkers 16

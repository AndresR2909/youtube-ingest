from azure.storage.blob import BlobServiceClient, StorageStreamDownloader
import logging
import os

logging.basicConfig(level=logging.ERROR)

containerName = os.environ.get("CONTAINERNAME_BLOBSTORAGE")
connectionString = os.environ.get("CONNECTION_STRING")


class BlobStorageManager:
    def __init__(self) -> None:
        try:
            blob_service_client = BlobServiceClient.from_connection_string(
                connectionString
            )
            self.container_client = blob_service_client.get_container_client(
                containerName
            )
        except Exception as e:
            logging.error("Error connecting to blob storage: %s", str(e))

    def list_files_from_container(self):
        try:
            blob_list = [
                {"filename": elemento.name, "lastupdate": elemento.last_modified}
                for elemento in self.container_client.list_blobs()
            ]
            return blob_list
        except Exception as e:
            logging.error("error: %s, message: error al listar archivos", str(e))
            return None

    def download_file_from_blob(self, blob_name: str) -> StorageStreamDownloader:
        try:

            file = self.container_client.download_blob(blob_name)

            return file

        except Exception as e:
            logging.error("error: %s, message: error al descargar el archivo", str(e))
            return None

    def upload_blob(self, blob_name, file_data):
        try:

            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(file_data, overwrite=True)

            return {
                "filename": blob_name,
                "message": "Archivo cargado exitosamente en Blob Storage",
            }

        except Exception as e:
            return {"error": str(e), "message": "error al cargar el archivo"}

    def delete_blob(self, blob_name):
        try:
            if self.container_client.get_blob_client(blob_name).exists():
                # Elimina el blob
                self.container_client.get_blob_client(blob_name).delete_blob()
                logging.info("El archivo '%s' ha sido eliminado.", blob_name)
            else:
                logging.info(
                    "El archivo '%s' no existe en el contenedor '%s'.",
                    blob_name, self.container_client
                )

                return {"mensaje": f"El archivo '{blob_name}' ha sido eliminado."}

        except Exception as e:
            return {"error": str(e), "message": "error al eliminar el archivo"}

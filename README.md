# Extraccion de transcripciones y metadata canales YouTube

![arquitectura](https://github.com/user-attachments/assets/a356cd16-5f48-434e-bc32-351a75327ca0)

## Descripción del proyecto
Este proyecto se encarga de extraer transcripciones e información de videos de canales predefinidos y almacenarlo en la zona landing de un Datalake Gen2 de Azure a través de una Azure Function que se dispara con un trigger de tiempo (cada x horas o x días).

![datalake](https://github.com/user-attachments/assets/11c54820-4fbd-4722-8573-40c3675050f6)

![landing](https://github.com/user-attachments/assets/213bc7e8-96bc-43f8-b540-534574e5e51f)

![function app](https://github.com/user-attachments/assets/26adf62a-2d80-4e1d-a720-e881d7fd62fe)


## Instrucciones de instalación
seguir las instrucciones de creacion de az function en [link](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python)

## Uso del proyecto
Ejemplos de uso del proyecto se pueden encontrar en los siguientes notebooks:
- [create_delta_dataset.ipynb](https://github.com/AndresR2909/youtube-ingest/blob/master/create_delta_dataset.ipynb)
- [create_full_dataset.ipynb](https://github.com/AndresR2909/youtube-ingest/blob/master/create_full_dataset.ipynb)


## Información de contacto
Para más información, puedes contactarme en: afrestrepa@eafit.edu.co

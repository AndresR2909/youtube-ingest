# Extraccion de transcripciones y metadata canales YouTube

![arquitectura](https://github.com/user-attachments/assets/862ee5e3-81f0-4837-bf5c-3d57ea86b5e4)


## Descripción del proyecto
Este proyecto se encarga de extraer transcripciones e información de videos de canales predefinidos y almacenarlo en la zona landing de un Datalake Gen2 de Azure a través de una Azure Function que se dispara con un trigger de tiempo (cada x horas o x días).

## Instrucciones de instalación
seguir las instrucciones de creacion de az function en [link](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python)

## Uso del proyecto
Ejemplos de uso del proyecto se pueden encontrar en los siguientes notebooks:
- [create_delta_dataset.ipynb](https://github.com/AndresR2909/youtube-ingest/blob/master/create_delta_dataset.ipynb)
- [create_full_dataset.ipynb](https://github.com/AndresR2909/youtube-ingest/blob/master/create_full_dataset.ipynb)


## Información de contacto
Para más información, puedes contactarme en: afrestrepa@eafit.edu.co

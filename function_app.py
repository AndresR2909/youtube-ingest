import os
import logging
from datetime import datetime
import io
from dotenv import load_dotenv
import azure.functions as func
from logic.data_ingestion import DataIngestion
from logic.blob_storage import BlobStorageManager

load_dotenv()

DELTA_DAYS = os.environ.get("DELTA_DAYS")
DELTA_HOURS = os.environ.get("DELTA_HOURS")
CHANNEL_LIST = os.environ.get("CHANNEL_LIST")
SCHEDULE = os.environ.get("CRON_SCHEDULE")

app = func.FunctionApp()

data_ingestion = DataIngestion()
bsm = BlobStorageManager()



@app.timer_trigger(schedule=SCHEDULE, arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    """
    Función que se ejecuta cada cierto intervalo de tiempo para obener trnascripciones y metadata videos
    """
    timestamp = datetime.now()
    logging.info("cron: %s", SCHEDULE)
    if CHANNEL_LIST:
        # Convertir la cadena de elementos separados por comas en una lista
        chanel_list = CHANNEL_LIST.split(",")
        logging.info(chanel_list)
        if DELTA_DAYS and (DELTA_DAYS != "0"):
            delta_days = int(DELTA_DAYS)
            logging.info("delta days: %s", delta_days)
            df_delta = data_ingestion.delta_load_from_youtube_channel_by_days(
                url_channel_list=chanel_list, delta_days=delta_days
            )
            if len(df_delta) != 0:
                data = df_delta.to_csv(header=True, index=False, sep=";", mode="w")
                logging.info("Numero de registros: %s", len(df_delta))
            else:
                logging.info("df_delta sin registros")
                data = None

        elif DELTA_HOURS:
            delta_hours = int(DELTA_HOURS)
            logging.info("delta hours: %s", delta_hours)
            df_delta = data_ingestion.delta_load_from_youtube_channel_by_hours(
                url_channel_list=chanel_list, delta_hours=delta_hours
            )
            if len(df_delta) != 0:
                data = df_delta.to_csv(header=True, index=False, sep=";", mode="w")
                logging.info("Numero de registros: %s", len(df_delta))
            else:
                logging.info("df_delta sin registros")
                data = None
        else:
            data = None
            logging.info("lack delta parameters")

        if data:
            buffer = io.StringIO()
            df_delta.info(buf=buffer)
            s = buffer.getvalue()
            logging.info(s)
            # outputblob.set(data)
            file_path = f"youtube_transcripts/pending/youtube_delta_data_{timestamp.strftime('%Y-%m-%d-%H_%M')}.csv"
            bsm.upload_blob(file_path, data)
        else:
            logging.info("No se ingestaron datos")
    else:
        logging.info("please, configure the channel list urls")

    if myTimer.past_due:
        logging.info("The timer is past due!")
    logging.info("Python timer trigger function ran at %s", timestamp.isoformat())

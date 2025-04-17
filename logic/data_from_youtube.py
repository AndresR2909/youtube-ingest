from __future__ import annotations

import logging
from datetime import datetime
from datetime import timedelta

import pandas as pd
import yt_dlp
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeScraper:
    def __init__(self):
        # Configuración de yt-dlp para obtener la metadata y título de los videos del canal
        self.ydl_opts = {
            'quiet': True,  # Para desactivar la salida en la consola
            'ignoreerrors': True,
            'extract_flat': True,  # Extrae la información en formato plano para un archivo CSV
            'skip_download': True,  # No descargar los videos, solo obtener la información
        }

    def _get_metadata_from_youtube_channel_url(self, url: str) -> dict:
        """Funcion para obtener metadata de url de canal de yotutube"""
        # Crea el objeto yt-dlp y descarga la información del canal
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            # Obtiene la información del canal
            info_dict = ydl.extract_info(url, download=False)
        return info_dict

    def _get_youtube_video_info_from_url(self, link: str) -> dict:
        """Agregar metadatos al video youtube"""
        try:
            yt = YouTube(link)
            try:
                relativeDateText = yt.initial_data['contents'][
                    'twoColumnWatchNextResults'
                ]['results']['results']['contents'][0]['videoPrimaryInfoRenderer'][
                    'relativeDateText'
                ][
                    'simpleText'
                ]
            except:
                relativeDateText = ''
            try:
                total_length = yt.length
            except:
                total_length = 0
            try:
                total_views = yt.views
            except:
                total_views = 0
            try:
                video_rating = yt.rating
            except:
                video_rating = 0
            metadata_dict = {
                #'author': yt.author,
                #'keywords': yt.keywords,
                #'description': yt.description,
                'publish_date': yt.publish_date,
                'total_length': total_length,
                'total_views': total_views,
                'video_rating': video_rating,
                'relativeDateText': relativeDateText,
            }
        except Exception as e:
            metadata_dict = None
            logging.error(f"error: {e} youtube link {link}")

        return metadata_dict

    @staticmethod
    def get_transcript_by_id(video_id, language='es'):
        """Get the transcript of a video by its id"""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=[language],
            )
            full_transcript = ' '.join([entry['text'] for entry in transcript])
            return full_transcript
        except Exception as e:
            logging.error(f"Error al obtener el transcript del video {video_id}: {e}")
            return None

    def _download_transcripts(self, video_id: str) -> dict:
        """Agregar las transcripciones a cada video_id"""
        # Variables forstore the downloaded captions:
        transcripts_dict = {}
        caption = None
        captions_text = ''

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except Exception as e:
            transcript_list = None
            print(f"Something went wrong with transcript_list {e}")

        if transcript_list:
            # Loop all languages available for this video and download the generated captions:
            for x, tr in enumerate(transcript_list):

                try:
                    captions_text = self.get_transcript_by_id(
                        video_id, language=tr.language_code,
                    )
                except Exception as e:
                    print(f"Something went wrong transcript obtained in language: {e}")

                key_value = f"caption_text_{tr.language_code}"
                transcripts_dict[key_value] = captions_text
        return transcripts_dict

    def _filter_delta_hours(
        self, relativeDateText: str, publish_date: datetime | str, delta_hours: int = 24,
    ) -> bool:
        """Calcular fecha de dias delta para filtrar la extraccion de
        la informacion
        """
        # fecha actual
        # today = datetime.now()
        today_utc = datetime.now()

        # Convertir la fecha de publicación a datetime
        if type(publish_date) == str:
            publish_date_dt = datetime.strptime(publish_date, '%Y-%m-%d %H:%M:%S')
        else:
            publish_date_dt = publish_date

        publish_date_dt = self._clean_relative_date(relativeDateText, publish_date_dt)

        # Restar los días a la fecha actual
        delta_date = today_utc - timedelta(hours=delta_hours)

        print(f"delta_date: {delta_date}")
        print(f"published_date: {publish_date_dt}")

        # Comparar las fechas
        if publish_date_dt >= delta_date:
            return True
        else:
            return False

    def _filter_delta_days(
        self, relativeDateText: str, publish_date: datetime | str, delta_days: int = 1,
    ):
        """Calcular fecha de dias delta para filtrar la extraccion de
        la informacion
        """
        # fecha actual
        # today = datetime.now()
        today_utc = datetime.now()

        # Convertir la fecha de publicación a datetime
        if type(publish_date) == str:
            publish_date_dt = datetime.strptime(publish_date, '%Y-%m-%d %H:%M:%S')
        else:
            publish_date_dt = publish_date

        publish_date_dt = self._clean_relative_date(relativeDateText, publish_date_dt)

        # Restar los días a la fecha actual
        delta_date = today_utc - timedelta(days=delta_days)

        # Comparar las fechas
        try:
            if publish_date_dt >= delta_date:
                return True
            else:
                return False
        except Exception as e:
            print(f"error {e}")
            return True

    def _clean_relative_date(self, relativeDateText: str, publish_date: datetime | str):
        # Eliminar "Streamed" si está presente
        relativeDateText = relativeDateText.replace('Streamed ', '')

        # Obtener la fecha actual en formato UTC
        today = datetime.now()
        try:
            # Convertir el texto a timedelta
            if 'minute' in relativeDateText:
                minutes = int(relativeDateText.split()[0])
                calculated_date = today - timedelta(minutes=minutes)
            elif 'hour' in relativeDateText:
                hours = int(relativeDateText.split()[0])
                calculated_date = today - timedelta(hours=hours)
            elif 'day' in relativeDateText:
                days = int(relativeDateText.split()[0])
                calculated_date = today - timedelta(days=days)
            elif 'month' in relativeDateText:
                months = int(relativeDateText.split()[0])
                calculated_date = today - timedelta(
                    days=months * 30,
                )  # Assuming 30 days per month for simplicity
            elif 'year' in relativeDateText:
                years = int(relativeDateText.split()[0])
                calculated_date = today - timedelta(
                    days=years * 365,
                )  # Assuming 365 days per year for simplicity
            else:
                calculated_date = publish_date
        except:
            calculated_date = publish_date

        return calculated_date

    def create_delta_dataset_from_channel_url(
        self, channel_url: str, delta_days: int = 0,
    ) -> pd.DataFrame:
        """Crear dataframe con la información extraída de cada video publicado dentro de los delta_days
        de la URL del canal ingresado como parámetro."""
        video_metadata_list = []
        info_dict = self._get_metadata_from_youtube_channel_url(channel_url)

        if info_dict:
            channel_name = info_dict.get('channel')
            channel_id = info_dict.get('channel_id')
            channel_url = info_dict.get('channel_url')
            logging.info(f"Extrayendo información de canal {channel_name}")

            for video in info_dict.get('entries', []):
                video_url = video.get('url')
                video_id = video.get('id')
                transcripts = self._download_transcripts(video_id) if video_id else {}

                metadata_dict = (
                    self._get_youtube_video_info_from_url(video_url)
                    if video_url
                    else None
                )
                if metadata_dict:
                    publish_date = metadata_dict.get('publish_date')
                    relativeDateText = metadata_dict.get('relativeDateText')

                    if self._filter_delta_days(
                        relativeDateText, publish_date, delta_days,
                    ):
                        tmp_video_metadata = {
                            'channel_name': channel_name,
                            'channel_id': channel_id,
                            'channel_url': channel_url,
                            'video_id': video_id,
                            'title': video.get('title'),
                            'url': video_url,
                            'description': video.get('description'),
                            'duration': (
                                int(video['duration'])
                                if video.get('duration')
                                else None
                            ),
                        }

                        tmp_video_metadata.update(
                            {
                                'keywords': metadata_dict.get('keywords'),
                                'publish_date': publish_date,
                                'relativeDateText': relativeDateText,
                                'total_length': metadata_dict.get('total_length'),
                                'total_views': metadata_dict.get('total_views'),
                                'video_rating': metadata_dict.get('video_rating'),
                            },
                        )

                        video_metadata = {**tmp_video_metadata, **transcripts}
                        video_metadata_list.append(video_metadata)
                    else:
                        break
        else:
            logging.info(
                f"info_dict: {info_dict}, error al extraer datos de URL {channel_url}",
            )

        return pd.DataFrame(video_metadata_list)

    def create_delta_hours_dataset_from_channel_url(
        self, channel_url: str, delta: int = 24,
    ) -> pd.DataFrame:
        """Crear dataframe con la información extraída de cada video publicado dentro de las últimas `delta` horas
        de la URL del canal ingresado como parámetro."""
        video_metadata_list = []
        info_dict = self._get_metadata_from_youtube_channel_url(channel_url)

        if info_dict:
            channel_name = info_dict.get('channel')
            channel_id = info_dict.get('channel_id')
            channel_url = info_dict.get('channel_url')
            logging.info(f"Extrayendo información de canal {channel_name}")

            for video in info_dict.get('entries', []):
                try:
                    video_url = video.get('url')
                    video_id = video.get('id')
                    transcripts = (
                        self._download_transcripts(video_id) if video_id else {}
                    )

                    metadata_dict = (
                        self._get_youtube_video_info_from_url(video_url)
                        if video_url
                        else None
                    )
                    if metadata_dict:
                        publish_date = metadata_dict.get('publish_date')
                        relativeDateText = metadata_dict.get('relativeDateText')

                        if self._filter_delta_hours(
                            relativeDateText, publish_date, delta,
                        ):
                            tmp_video_metadata = {
                                'channel_name': channel_name,
                                'channel_id': channel_id,
                                'channel_url': channel_url,
                                'video_id': video_id,
                                'title': video.get('title'),
                                'url': video_url,
                                'description': video.get('description'),
                                'duration': (
                                    int(video['duration'])
                                    if video.get('duration')
                                    else None
                                ),
                            }

                            tmp_video_metadata.update(
                                {
                                    'keywords': metadata_dict.get('keywords'),
                                    'publish_date': publish_date,
                                    'relativeDateText': relativeDateText,
                                    'total_length': metadata_dict.get('total_length'),
                                    'total_views': metadata_dict.get('total_views'),
                                    'video_rating': metadata_dict.get('video_rating'),
                                },
                            )

                            video_metadata = {**tmp_video_metadata, **transcripts}
                            video_metadata_list.append(video_metadata)
                        else:
                            break
                except Exception as e:
                    logging.error(f"Error: {e} extrayendo {video.get('title')}")
        else:
            logging.info(
                f"info_dict: {info_dict}, error al extraer datos de URL {channel_url}",
            )

        return pd.DataFrame(video_metadata_list)

    def create_full_dataset_from_channel_url(self, channel_url: str) -> pd.DataFrame:
        """Crear dataframe con la información extraída de cada video del canal de la URL ingresada como parámetro."""
        video_metadata_list = []
        info_dict = self._get_metadata_from_youtube_channel_url(channel_url)

        if not info_dict:
            logging.info(
                f"info_dict: {info_dict}, error al extraer datos de URL {channel_url}",
            )
            return pd.DataFrame([])

        channel_name = info_dict.get('channel')
        channel_id = info_dict.get('channel_id')
        channel_url = info_dict.get('channel_url')
        channel_type = info_dict.get('webpage_url_basename')
        logging.info(f"Extrayendo información del canal {channel_name}")

        for video in info_dict.get('entries', []):
            try:
                video_id = video.get('id')
                video_url = video.get('url')
                transcripts = self._download_transcripts(video_id) if video_id else {}

                tmp_video_metadata = {
                    'channel_name': channel_name,
                    'channel_id': channel_id,
                    'channel_url': channel_url,
                    'channel_type': channel_type,
                    'video_id': video_id,
                    'title': video.get('title'),
                    'url': video_url,
                    'description': video.get('description'),
                    'duration': video.get('duration'),
                    'view_count': video.get('view_count'),
                }

                metadata_dict = (
                    self._get_youtube_video_info_from_url(video_url)
                    if video_url
                    else {}
                )
                tmp_video_metadata.update(
                    {
                        'keywords': metadata_dict.get('keywords'),
                        'publish_date': metadata_dict.get('publish_date'),
                        'relativeDateText': metadata_dict.get('relativeDateText'),
                        'total_length': metadata_dict.get('total_length'),
                        'total_views': metadata_dict.get('total_views'),
                        'video_rating': metadata_dict.get('video_rating'),
                    },
                )

                video_metadata = {**tmp_video_metadata, **transcripts}
                video_metadata_list.append(video_metadata)

            except Exception as e:
                logging.error(
                    f"Error extrayendo datos del video {video.get('title', 'Desconocido')}: {e}",
                )

        return pd.DataFrame(video_metadata_list)

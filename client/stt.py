#!/usr/bin/env python2
# -*- coding: utf-8-*-
import os
import wave
import json
import tempfile
import logging
import urllib
import urlparse
import re
import subprocess
from abc import ABCMeta, abstractmethod
import requests
import yaml
import shellapath
import diagnose
import vocabcompiler


class AbstractSTTEngine(object):
    """
    Generic parent class for all STT engines
    """

    __metaclass__ = ABCMeta
    VOCABULARY_TYPE = None

    @classmethod
    def get_config(cls):
        return {}

    @classmethod
    def get_instance(cls, vocabulary_name, phrases):
        config = cls.get_config()
        if cls.VOCABULARY_TYPE:
            vocabulary = cls.VOCABULARY_TYPE(vocabulary_name,
                                             path=shellapath.config(
                                                 'vocabularies'))
            if not vocabulary.matches_phrases(phrases):
                vocabulary.compile(phrases)
            config['vocabulary'] = vocabulary
        instance = cls(**config)
        return instance

    @classmethod
    def get_passive_instance(cls):
        phrases = vocabcompiler.get_keyword_phrases()
        return cls.get_instance('keyword', phrases)

    @classmethod
    def get_active_instance(cls):
        phrases = vocabcompiler.get_all_phrases()
        return cls.get_instance('default', phrases)

    @classmethod
    @abstractmethod
    def is_available(cls):
        return True

    @abstractmethod
    def transcribe(self, fp):
        pass


class PocketSphinxSTT(AbstractSTTEngine):
    """
    The default Speech-to-Text implementation which relies on PocketSphinx.
    """

    SLUG = 'sphinx'
    VOCABULARY_TYPE = vocabcompiler.PocketsphinxVocabulary

    def __init__(self, vocabulary, hmm_dir="/usr/local/share/" +
                 "pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k"):

        """
        Initiates the pocketsphinx instance.

        Arguments:
            vocabulary -- a PocketsphinxVocabulary instance
            hmm_dir -- the path of the Hidden Markov Model (HMM)
        """

        self._logger = logging.getLogger(__name__)

        # quirky bug where first import doesn't work
        try:
            import pocketsphinx as ps
        except:
            import pocketsphinx as ps

        with tempfile.NamedTemporaryFile(prefix='psdecoder_',
                                         suffix='.log', delete=False) as f:
            self._logfile = f.name

        self._logger.debug("Initializing PocketSphinx Decoder with hmm_dir " +
                           "'%s'", hmm_dir)

        # Perform some checks on the hmm_dir so that we can display more
        # meaningful error messages if neccessary
        if not os.path.exists(hmm_dir):
            msg = ("hmm_dir '%s' does not exist! Please make sure that you " +
                   "have set the correct hmm_dir in your profile.") % hmm_dir
            self._logger.error(msg)
            raise RuntimeError(msg)
        # Lets check if all required files are there. Refer to:
        # http://cmusphinx.sourceforge.net/wiki/acousticmodelformat
        # for details
        missing_hmm_files = []
        for fname in ('mdef', 'feat.params', 'means', 'noisedict',
                      'transition_matrices', 'variances'):
            if not os.path.exists(os.path.join(hmm_dir, fname)):
                missing_hmm_files.append(fname)
        mixweights = os.path.exists(os.path.join(hmm_dir, 'mixture_weights'))
        sendump = os.path.exists(os.path.join(hmm_dir, 'sendump'))
        if not mixweights and not sendump:
            # We only need mixture_weights OR sendump
            missing_hmm_files.append('mixture_weights or sendump')
        if missing_hmm_files:
            self._logger.warning("hmm_dir '%s' is missing files: %s. Please " +
                                 "make sure that you have set the correct " +
                                 "hmm_dir in your profile.",
                                 hmm_dir, ', '.join(missing_hmm_files))

        self._decoder = ps.Decoder(hmm=hmm_dir, logfn=self._logfile,
                                   **vocabulary.decoder_kwargs)

    def __del__(self):
        os.remove(self._logfile)

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        # HMM dir
        # Try to get hmm_dir from config
        profile_path = shellapath.config('profile.yml')

        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                try:
                    config['hmm_dir'] = profile['pocketsphinx']['hmm_dir']
                except KeyError:
                    pass

        return config

    def transcribe(self, fp):
        """
        Performs STT, transcribing an audio file and returning the result.

        Arguments:
            fp -- a file object containing audio data
        """

        fp.seek(44)

        # FIXME: Can't use the Decoder.decode_raw() here, because
        # pocketsphinx segfaults with tempfile.SpooledTemporaryFile()
        data = fp.read()
        self._decoder.start_utt()
        self._decoder.process_raw(data, False, True)
        self._decoder.end_utt()

        result = self._decoder.get_hyp()
        with open(self._logfile, 'r+') as f:
            for line in f:
                self._logger.debug(line.strip())
            f.truncate()

        transcribed = [result[0]]
        self._logger.info('Transcribed: %r', transcribed)
        return transcribed

    @classmethod
    def is_available(cls):
        return diagnose.check_python_import('pocketsphinx')


class JuliusSTT(AbstractSTTEngine):
    """
    A very basic Speech-to-Text engine using Julius.
    """

    SLUG = 'julius'
    VOCABULARY_TYPE = vocabcompiler.JuliusVocabulary

    def __init__(self, vocabulary=None, hmmdefs="/usr/share/voxforge/julius/" +
                 "acoustic_model_files/hmmdefs", tiedlist="/usr/share/" +
                 "voxforge/julius/acoustic_model_files/tiedlist"):
        self._logger = logging.getLogger(__name__)
        self._vocabulary = vocabulary
        self._hmmdefs = hmmdefs
        self._tiedlist = tiedlist
        self._pattern = re.compile(r'sentence(\d+): <s> (.+) </s>')

        # Inital test run: we run this command once to log errors/warnings
        cmd = ['julius',
               '-input', 'stdin',
               '-dfa', self._vocabulary.dfa_file,
               '-v', self._vocabulary.dict_file,
               '-h', self._hmmdefs,
               '-hlist', self._tiedlist,
               '-forcedict']
        cmd = [str(x) for x in cmd]
        self._logger.debug('Executing: %r', cmd)
        with tempfile.SpooledTemporaryFile() as out_f:
            with tempfile.SpooledTemporaryFile() as f:
                with tempfile.SpooledTemporaryFile() as err_f:
                    subprocess.call(cmd, stdin=f, stdout=out_f, stderr=err_f)
            out_f.seek(0)
            for line in out_f.read().splitlines():
                line = line.strip()
                if len(line) > 7 and line[:7].upper() == 'ERROR: ':
                    if not line[7:].startswith('adin_'):
                        self._logger.error(line[7:])
                elif len(line) > 9 and line[:9].upper() == 'WARNING: ':
                    self._logger.warning(line[9:])
                elif len(line) > 6 and line[:6].upper() == 'STAT: ':
                    self._logger.debug(line[6:])

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        # HMM dir
        # Try to get hmm_dir from config
        profile_path = shellapath.config('profile.yml')

        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'julius' in profile:
                    if 'hmmdefs' in profile['julius']:
                        config['hmmdefs'] = profile['julius']['hmmdefs']
                    if 'tiedlist' in profile['julius']:
                        config['tiedlist'] = profile['julius']['tiedlist']
        return config

    def transcribe(self, fp, mode=None):
        cmd = ['julius',
               '-quiet',
               '-nolog',
               '-input', 'stdin',
               '-dfa', self._vocabulary.dfa_file,
               '-v', self._vocabulary.dict_file,
               '-h', self._hmmdefs,
               '-hlist', self._tiedlist,
               '-forcedict']
        cmd = [str(x) for x in cmd]
        self._logger.debug('Executing: %r', cmd)
        with tempfile.SpooledTemporaryFile() as out_f:
            with tempfile.SpooledTemporaryFile() as err_f:
                subprocess.call(cmd, stdin=fp, stdout=out_f, stderr=err_f)
            out_f.seek(0)
            results = [(int(i), text) for i, text in
                       self._pattern.findall(out_f.read())]
        transcribed = [text for i, text in
                       sorted(results, key=lambda x: x[0])
                       if text]
        if not transcribed:
            transcribed.append('')
        self._logger.info('Transcribed: %r', transcribed)
        return transcribed

    @classmethod
    def is_available(cls):
        return diagnose.check_executable('julius')


class GoogleSTT(AbstractSTTEngine):

    SLUG = 'google'

    def __init__(self, api_key=None, language='en-us'):

        self._logger = logging.getLogger(__name__)
        self._request_url = None
        self._language = None
        self._api_key = None
        self._http = requests.Session()
        self.language = language
        self.api_key = api_key

    @property
    def request_url(self):
        return self._request_url

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        self._language = value
        self._regenerate_request_url()

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value
        self._regenerate_request_url()

    def _regenerate_request_url(self):
        if self.api_key and self.language:
            query = urllib.urlencode({'output': 'json',
                                      'client': 'chromium',
                                      'key': self.api_key,
                                      'lang': self.language,
                                      'maxresults': 6,
                                      'pfilter': 2})
            self._request_url = urlparse.urlunparse(
                ('https', 'www.google.com', '/speech-api/v2/recognize', '',
                 query, ''))
        else:
            self._request_url = None

    @classmethod
    def get_config(cls):
        config = {}
        # HMM dir
        # Try to get hmm_dir from config
        profile_path = shellapath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'stt-keys' in profile and 'GOOGLE_KEY' in profile['stt-keys']:
                    config['api_key'] = profile['stt-keys']['GOOGLE_KEY']
        return config

    def transcribe(self, fp):

        if not self.api_key:
            self._logger.critical('API key missing, transcription request ' +
                                  'aborted.')
            return []
        elif not self.language:
            self._logger.critical('Language info missing, transcription ' +
                                  'request aborted.')
            return []

        wav = wave.open(fp, 'rb')
        frame_rate = wav.getframerate()
        wav.close()
        data = fp.read()

        headers = {'content-type': 'audio/l16; rate=%s' % frame_rate}
        r = self._http.post(self.request_url, data=data, headers=headers)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self._logger.critical('Request failed with http status %d',
                                  r.status_code)
            if r.status_code == requests.codes['forbidden']:
                self._logger.warning('Status 403 is probably caused by an ' +
                                     'invalid Google API key.')
            return []
        r.encoding = 'utf-8'
        try:
            response = json.loads(list(r.text.strip().split('\n', 1))[-1])
            if len(response['result']) == 0:
                # Response result is empty
                raise ValueError('Nothing has been transcribed.')
            results = [alt['transcript'] for alt
                       in response['result'][0]['alternative']]
        except ValueError as e:
            self._logger.warning('Empty response: %s', e.args[0])
            results = []
        except (KeyError, IndexError):
            self._logger.warning('Cannot parse response.', exc_info=True)
            results = []
        else:
            # Convert all results to uppercase
            results = tuple(result.upper() for result in results)
            self._logger.info('Transcribed: %r', results)
        return results

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()

class WatsonSTT(AbstractSTTEngine):
    """ Watson Speech-To-Text implementation
    """
    SLUG = "watson"

    def __init__(self, app_username, app_password):
        self._logger = logging.getLogger(__name__)
        self._session = None
        self._cookies  = []
        self.auth = (app_username, app_password)


    @classmethod
    def get_config(cls):
        config = {}
        profile_path = jasperpath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'watson-stt' in profile:
                    if 'username' in profile['watson-stt']:
                        config['app_username'] = profile['watson-stt']['username']
                    if 'password' in profile['watson-stt']:
                        config['app_password'] = profile['watson-stt']['password']
        return config

    @property
    def session(self):
        if not self._session:

            r = requests.post('https://stream.watsonplatform.net/speech-to-text/api/v1/sessions',
                auth = self.auth
            )
            self._session = r.json()
            self._cookies = r.cookies

        return self._session

    def recognise(self, data):
        r = requests.get(self.session['recognize'],
                auth=self.auth,
                cookies = self._cookies)

        print r.json()

        if r.status_code == 404 or r.json()['session']['state'] != "initialized":
            # Request token invalid, retry once with a new token
            self._logger.warning('STT session has expired. Generating a ' +
                                 'new one and retrying...')
            self._session = None

        #post the file data
        headers = {"Content-type" : "audio/wav"}
        r = requests.post(self.session['recognize'], 
                auth=self.auth, 
                cookies = self._cookies,
                headers=headers,
                data=data)

        print r.json()
        return r



    def transcribe(self, fp):
        data = fp.read()
            

        r = self.recognise(data)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self._logger.critical('Request failed with response: %r',
                                  r.text,
                                  exc_info=True)
            return []
        except requests.exceptions.RequestException:
            self._logger.critical('Request failed.', exc_info=True)
            return []
        else:
            try:

                results = r.json()['results']

                if(len(results) < 1):
                    return[]
                else:
                    results = results[0]['alternatives']
            except ValueError as e:
                self._logger.debug('Recognition failed with status: %s',
                                   e.args[0])
                return []
            except KeyError:
                self._logger.critical('Cannot parse response.',
                                      exc_info=True)
                return []
            else:
                transcribed = [x['transcript'].upper() for x in sorted(results,
                                                            key=lambda x: x['confidence'],
                                                            reverse=True)]
                self._logger.info('Transcribed: %r', transcribed)
                return transcribed


    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()


class WitAiSTT(AbstractSTTEngine):

    SLUG = "witai"

    def __init__(self, access_token):
        self._logger = logging.getLogger(__name__)
        self.token = access_token

    @classmethod
    def get_config(cls):
        config = {}
        # Try to get wit.ai Auth token from config
        profile_path = shellapath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'stt-keys' in profile:
                    if 'WITAI_KEY' in profile['stt-keys']:
                        config['access_token'] = \
                            profile['witai-stt']['WITAI_KEY']
        return config

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        self._headers = {'Authorization': 'Bearer %s' % self.token,
                         'accept': 'application/json',
                         'Content-Type': 'audio/wav'}

    @property
    def headers(self):
        return self._headers

    def transcribe(self, fp):
        data = fp.read()
        r = requests.post('https://api.wit.ai/speech?v=20150101',
                          data=data,
                          headers=self.headers)
        try:
            r.raise_for_status()
            text = r.json()['_text']
        except requests.exceptions.HTTPError:
            self._logger.critical('Request failed with response: %r',
                                  r.text,
                                  exc_info=True)
            return []
        except requests.exceptions.RequestException:
            self._logger.critical('Request failed.', exc_info=True)
            return []
        except ValueError as e:
            self._logger.critical('Cannot parse response: %s',
                                  e.args[0])
            return []
        except KeyError:
            self._logger.critical('Cannot parse response.',
                                  exc_info=True)
            return []
        else:
            transcribed = []
            if text:
                transcribed.append(text.upper())
            self._logger.info('Transcribed: %r', transcribed)
            return transcribed

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()


def get_engine_by_slug(slug=None):
    """
    Returns:
        An STT Engine implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

    if not slug or type(slug) is not str:
        raise TypeError("Invalid slug '%s'", slug)

    selected_engines = filter(lambda engine: hasattr(engine, "SLUG") and
                              engine.SLUG == slug, get_engines())
    if len(selected_engines) == 0:
        raise ValueError("No STT engine found for slug '%s'" % slug)
    else:
        if len(selected_engines) > 1:
            print(("WARNING: Multiple STT engines found for slug '%s'. " +
                   "This is most certainly a bug.") % slug)
        engine = selected_engines[0]
        if not engine.is_available():
            raise ValueError(("STT engine '%s' is not available (due to " +
                              "missing dependencies, missing " +
                              "dependencies, etc.)") % slug)
        return engine


def get_engines():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [tts_engine for tts_engine in
            list(get_subclasses(AbstractSTTEngine))
            if hasattr(tts_engine, 'SLUG') and tts_engine.SLUG]
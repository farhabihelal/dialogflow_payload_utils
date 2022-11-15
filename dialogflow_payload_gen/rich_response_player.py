from time import time, sleep
import rospy
import threading

from std_msgs.msg import Header
from idmind_tabletop_msgs.msg import TTSCommand, TTSStatus

from csv_parser import CSVParser


class TTSPlaylist:
    def __init__(self, rich_responses=None):
        self.rich_responses = rich_responses

        self.data = None

        self.generate()

    def generate(self):
        data = {}

        for key in self.rich_responses:
            ssml_collection = []
            rfmc = self.rich_responses[key]

            for container in rfmc:
                ssml_texts = []
                for text in container:
                    ssml_text = ""
                    for sent in text.sentences:
                        ssml_text += sent.ssml_text
                    ssml_texts.append(ssml_text)
                ssml_collection.append(ssml_texts)

            data[key] = ssml_collection

        self.data = data

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        return self.data.__getitem__(key)


class RichResponsePlayer:
    def __init__(self, config) -> None:
        self.config = config

        self._is_playing = False

        self.init_ros()

    def init_ros(self):
        rospy.init_node("rich_response_player")

        self.tts_publisher = rospy.Publisher(
            "/idmind_tabletop/cmd_tts", TTSCommand, queue_size=10, latch=True
        )

        rospy.Subscriber("/idmind_tabletop/tts_status", TTSStatus, self.on_tts_status)

    def play(self, playlist=None):

        playlist = playlist if playlist else self.config["playlist"]

        for key in playlist:
            for lines in playlist[key]:
                for line in lines:
                    print(f"[ LINE ] : {line}")
                    self.publish(line)
                    sleep(3)
                    print()

    def publish(self, msg: str):
        while self.is_playing:
            # print("TTS is playing. Sleeping...")
            sleep(0.2)
        sleep(1)

        # print("TTS is ready. Preparing to publish... ", end="")
        cmd = TTSCommand()
        # cmd.header = Header()
        cmd.message = msg
        cmd.disable_lipsync = False
        self.tts_publisher.publish(cmd)
        # print("done")

    def on_tts_status(self, msg: TTSStatus):
        # print(f"TTS status received: {msg}")
        if msg.status == TTSStatus.PLAYING:
            # print("TTS is playing.")
            self.is_playing = True

        elif msg.status == TTSStatus.LISTENING:
            # print("TTS is listening.")
            self.is_playing = False

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @is_playing.setter
    def is_playing(self, status: bool):
        # cooldown period for switching from playing to listening
        # if not status:
        #     sleep(1)

        self._is_playing = status


if __name__ == "__main__":

    title = "rich response player"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    default_config = {}

    import os

    export_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../exports")

    parser_config = {
        "filepath": f"{export_dir}/haru-games-demo.tsv",
    }

    parser = CSVParser(parser_config)
    parser.run()

    key = "game-would-you-rather-prompt"
    rich_responses = {
        key: parser.parsed_data[key],
    }
    playlist = TTSPlaylist(rich_responses)

    player_config = {
        "playlist": playlist,
    }
    rr_player = RichResponsePlayer(player_config)
    rr_player.play()

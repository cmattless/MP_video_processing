from pymediainfo import MediaInfo


class MetadataProcessor:
    def __init__(self, file_path):
        """Initializes the MetadataProcessor class."""
        self.file_path = file_path
        self.data = None

    def __extract_metadata(self):
        """Extracts metadata from the file."""
        media_info = MediaInfo.parse(self.file_path)
        self.data = media_info.to_data()

    def __get_general_info(self):
        """Returns general information about the file."""
        for track in self.data.tracks:
            if track.track_type == "General":
                return track.to_data()
        return None
    
    def __get_video_info(self):
        """Returns video information about the file."""
        for track in self.data.tracks:
            if track.track_type == "Video":
                return track.to_data()
        return None
    
    def __get_audio_info(self):
        """Returns audio information about the file."""
        for track in self.data.tracks:
            if track.track_type == "Audio":
                return track.to_data()
        return None
    
    def get_metadata(self):
        """Returns metadata information about the file."""
        if self.data is None:
            self.__extract_metadata()
        general_info = self.__get_general_info()
        video_info = self.__get_video_info()
        audio_info = self.__get_audio_info()
        return general_info, video_info, audio_info
        
    

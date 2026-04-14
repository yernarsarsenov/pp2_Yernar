import pygame
import os

class MusicPlayer:
    def __init__(self, music_folder):
        self.playlist = []
        self.current_index = 0
        self.is_paused = False
        self.started = False
        
        if os.path.exists(music_folder):
            for file in os.listdir(music_folder):
                if file.lower().endswith(".mp3"):
                    self.playlist.append(os.path.join(music_folder, file))
        
        if self.playlist:
            pygame.mixer.music.load(self.playlist[self.current_index])

    def play_toggle(self):
        if not self.playlist: return
        if not self.started:
            pygame.mixer.music.play()
            self.started = True
            self.is_paused = False
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            pygame.mixer.music.pause()
            self.is_paused = True

    def stop(self):
        """Stops and resets the track."""
        pygame.mixer.music.stop()
        self.started = False
        self.is_paused = False

    def next_track(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.load_and_play_fresh()

    def prev_track(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.load_and_play_fresh()

    def load_and_play_fresh(self):
        pygame.mixer.music.load(self.playlist[self.current_index])
        pygame.mixer.music.play()
        self.started = True
        self.is_paused = False

    def get_current_track_name(self):
        if not self.playlist:
            return "No Music Found"
        return os.path.basename(self.playlist[self.current_index])
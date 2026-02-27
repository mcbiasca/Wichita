from __future__ import annotations

import os
from typing import Dict, Optional
import pygame
import numpy as np


class AudioManager:
    def __init__(self, audio_root: str = "assets/audio") -> None:
        self.audio_root = audio_root
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_volume = 0.12
        self.sfx_volume = 0.5
        self.current_music = None
        self.music_end_ms: int | None = None
        
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except pygame.error:
            print("Warning: Audio system not available")
            return
        
        self._generate_sounds()
        self._load_music()
    
    def _load_music(self) -> None:
        """Load background music"""
        try:
            music_path = "assets/Action.wav"
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                self.current_music = music_path
                print(f"Loaded music: {music_path}")
            else:
                print(f"Music file not found: {music_path}")
        except pygame.error as e:
            print(f"Warning: pygame cannot load MIDI: {e}")
            print("Note: pygame.mixer may not support MIDI files on this system.")
        except Exception as e:
            print(f"Warning: Could not load music: {e}")
    
    def _generate_background_music(self) -> pygame.mixer.Sound:
        """Generate a simple RPG background loop"""
        # Create an 8-second looping track
        duration = 8.0
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        
        # Create a simple chord progression
        wave = np.zeros(num_samples)
        
        # 4 beats per phrase
        beat_sample = int(sample_rate * 0.5)
        
        # Chord progression: C, C, Dm, Dm, G, G, C, C
        chords = [
            [261.6, 329.6, 392.0],      # C major (C, E, G)
            [261.6, 329.6, 392.0],
            [293.7, 369.9, 440.0],      # D minor (D, F, A)
            [293.7, 369.9, 440.0],
            [392.0, 493.9, 587.3],      # G major (G, B, D)
            [392.0, 493.9, 587.3],
            [261.6, 329.6, 392.0],      # C major
            [261.6, 329.6, 392.0],
        ]
        
        # Apply chords to the wave
        for chord_idx, chord in enumerate(chords):
            start_sample = chord_idx * beat_sample * 4
            end_sample = start_sample + beat_sample * 4
            
            if start_sample >= num_samples:
                break
            if end_sample > num_samples:
                end_sample = num_samples
            
            chord_t = t[start_sample:end_sample]
            chord_wave = np.zeros(len(chord_t))
            
            for freq in chord:
                chord_wave += np.sin(2 * np.pi * freq * chord_t) / len(chord)
            
            # Add fade at section boundaries
            fade_len = int(sample_rate * 0.1)
            if chord_idx > 0:
                fade_in = np.linspace(0, 1, min(fade_len, len(chord_wave)))
                chord_wave[:len(fade_in)] *= fade_in
            if chord_idx < len(chords) - 1:
                fade_out = np.linspace(1, 0.3, min(fade_len, len(chord_wave)))
                chord_wave[-len(fade_out):] *= fade_out
            
            wave[start_sample:end_sample] = chord_wave
        
        # Overall fade in and out
        fade_in_len = int(sample_rate * 0.5)
        fade_out_len = int(sample_rate * 0.5)
        fade_in = np.linspace(0, 1, fade_in_len)
        fade_out = np.linspace(1, 0.2, fade_out_len)
        wave[:fade_in_len] *= fade_in
        wave[-fade_out_len:] *= fade_out
        
        # Convert to 16-bit audio
        wave = (wave * 32767 * 0.8).astype(np.int16)
        # Make stereo
        wave = np.column_stack((wave, wave))
        
        return pygame.mixer.Sound(wave)
    
    def _generate_sounds(self) -> None:
        """Generate procedural sound effects"""
        try:
            # Shoot sound - quick blip
            shoot_sound = self._generate_tone(440, 0.1, fade_out=True)
            self.sounds['shoot'] = pygame.mixer.Sound(shoot_sound)
            
            # Hit sound - lower thud
            hit_sound = self._generate_tone(220, 0.15, fade_out=True)
            self.sounds['hit'] = pygame.mixer.Sound(hit_sound)
            
            # Pickup sound - ascending chirp
            pickup_sound = self._generate_sweep(440, 880, 0.2)
            self.sounds['pickup'] = pygame.mixer.Sound(pickup_sound)
            
            # Level up sound - triumphant chord
            levelup_sound = self._generate_chord([523, 659, 784], 0.4)
            self.sounds['levelup'] = pygame.mixer.Sound(levelup_sound)
            
            # Death sound - descending
            death_sound = self._generate_sweep(440, 110, 0.3)
            self.sounds['death'] = pygame.mixer.Sound(death_sound)
            
            # Menu sound - soft click
            menu_sound = self._generate_tone(660, 0.05, fade_out=True)
            self.sounds['menu'] = pygame.mixer.Sound(menu_sound)
            
            # Load woman scream for player damage
            scream_path = "assets/woman_scream.mp3"
            if os.path.exists(scream_path):
                self.sounds['scream'] = pygame.mixer.Sound(scream_path)
                print(f"Loaded scream sound: {scream_path}")
            else:
                print(f"Warning: Scream sound not found: {scream_path}")
            
            # Load game over sound
            game_over_path = "assets/game_over.mp3"
            if os.path.exists(game_over_path):
                self.sounds['game_over'] = pygame.mixer.Sound(game_over_path)
                print(f"Loaded game over sound: {game_over_path}")
            else:
                print(f"Warning: Game over sound not found: {game_over_path}")
            
        except Exception as e:
            print(f"Warning: Could not generate sounds: {e}")
    
    def _generate_tone(self, frequency: float, duration: float, fade_out: bool = False) -> np.ndarray:
        """Generate a simple sine wave tone"""
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        wave = np.sin(2 * np.pi * frequency * t)
        
        if fade_out:
            fade = np.linspace(1, 0, num_samples)
            wave = wave * fade
        
        # Convert to 16-bit audio
        wave = (wave * 32767).astype(np.int16)
        # Make stereo
        wave = np.column_stack((wave, wave))
        return wave
    
    def _generate_sweep(self, start_freq: float, end_freq: float, duration: float) -> np.ndarray:
        """Generate a frequency sweep"""
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        
        # Linear frequency sweep
        freq = np.linspace(start_freq, end_freq, num_samples)
        phase = np.cumsum(2 * np.pi * freq / sample_rate)
        wave = np.sin(phase)
        
        # Fade out
        fade = np.linspace(1, 0.2, num_samples)
        wave = wave * fade
        
        # Convert to 16-bit audio
        wave = (wave * 32767).astype(np.int16)
        # Make stereo
        wave = np.column_stack((wave, wave))
        return wave
    
    def _generate_chord(self, frequencies: list[float], duration: float) -> np.ndarray:
        """Generate multiple tones played together"""
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        
        wave = np.zeros(num_samples)
        for freq in frequencies:
            wave += np.sin(2 * np.pi * freq * t) / len(frequencies)
        
        # Fade in and out
        fade_in = np.linspace(0, 1, num_samples // 10)
        fade_out = np.linspace(1, 0, num_samples // 4)
        wave[:len(fade_in)] *= fade_in
        wave[-len(fade_out):] *= fade_out
        
        # Convert to 16-bit audio
        wave = (wave * 32767).astype(np.int16)
        # Make stereo
        wave = np.column_stack((wave, wave))
        return wave
    
    def play_sound(self, sound_name: str) -> None:
        """Play a sound effect"""
        if sound_name in self.sounds:
            try:
                sound = self.sounds[sound_name]
                sound.set_volume(self.sfx_volume)
                sound.play()
            except:
                pass
    
    def set_sfx_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except:
            pass
    
    def play_music(self, loops: int = -1) -> None:
        """Play background music once"""
        if self.current_music:
            try:
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops=0)
                self.music_end_ms = None
                print(f"Playing music: {self.current_music} at volume {self.music_volume}")
            except pygame.error as e:
                print(f"Error playing music: {e}")
            except Exception as e:
                print(f"Exception during music playback: {e}")
    
    def stop_music(self) -> None:
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
        except:
            pass
    
    def stop_all_sounds(self) -> None:
        """Stop all sound effects and music"""
        try:
            pygame.mixer.stop()  # Stop all sound effects
            pygame.mixer.music.stop()  # Stop music
        except:
            pass
    
    def play_game_over(self) -> None:
        """Stop everything and play game over sound"""
        self.stop_all_sounds()
        if 'game_over' in self.sounds:
            try:
                sound = self.sounds['game_over']
                sound.set_volume(self.sfx_volume)
                sound.play()
            except:
                pass
    
    def is_music_playing(self) -> bool:
        """Check if music is currently playing"""
        try:
            return pygame.mixer.music.get_busy()
        except:
            return False
    
    def update_music(self) -> None:
        """Restart music 0.25s after it finishes."""
        if not self.current_music:
            return
        if self.is_music_playing():
            self.music_end_ms = None
            return
        now_ms = pygame.time.get_ticks()
        if self.music_end_ms is None:
            self.music_end_ms = now_ms
            return
        if now_ms - self.music_end_ms >= 250:
            try:
                pygame.mixer.music.play(loops=0)
                self.music_end_ms = None
            except:
                pass

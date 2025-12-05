import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private darkMode = false;
  private storageKey = 'darkMode';

  constructor() {
    // Load saved preference
    const saved = localStorage.getItem(this.storageKey);
    if (saved !== null) {
      this.darkMode = saved === 'true';
    } else {
      // Check system preference
      this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    this.applyTheme();
  }

  isDarkMode(): boolean {
    return this.darkMode;
  }

  toggle(): void {
    this.darkMode = !this.darkMode;
    localStorage.setItem(this.storageKey, String(this.darkMode));
    this.applyTheme();
  }

  private applyTheme(): void {
    if (this.darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }
}

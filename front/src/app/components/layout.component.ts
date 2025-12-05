import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { ThemeService } from '../services/theme.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <nav aria-label="Main navigation">
      <span class="brand">B58</span>
      <a routerLink="/create" routerLinkActive="active">Create</a>
      <a routerLink="/history" routerLinkActive="active">History</a>
      <a routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
      <a routerLink="/summary" routerLinkActive="active">Summary</a>
      <a routerLink="/reports" routerLinkActive="active">Reports</a>
      <div class="nav-right">
        <button (click)="toggleTheme()" class="theme-toggle" [class.dark]="isDark()" [attr.aria-label]="isDark() ? 'Switch to light mode' : 'Switch to dark mode'">
          <span class="toggle-knob"></span>
        </button>
        <button (click)="logout()" class="logout-btn">Logout</button>
      </div>
    </nav>
    <main>
      <router-outlet></router-outlet>
    </main>
  `,
  styles: [`
    nav {
      background: #333;
      padding: 10px 20px;
      display: flex;
      align-items: center;
      gap: 20px;
    }
    .brand {
      color: white;
      font-weight: bold;
      font-size: 1.2em;
      margin-right: 20px;
    }
    a {
      color: #ccc;
      text-decoration: none;
      padding: 5px 10px;
    }
    a:hover, a.active {
      color: white;
    }
    .nav-right {
      margin-left: auto;
      display: flex;
      align-items: center;
      gap: 15px;
    }
    .logout-btn {
      background: none;
      border: 1px solid #ccc;
      color: #ccc;
      padding: 5px 15px;
      cursor: pointer;
    }
    .logout-btn:hover {
      background: #555;
      color: white;
    }
    .theme-toggle {
      width: 44px;
      height: 24px;
      background: #ccc;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      position: relative;
      transition: background 0.3s;
    }
    .theme-toggle.dark {
      background: #007bff;
    }
    .toggle-knob {
      position: absolute;
      top: 2px;
      left: 2px;
      width: 20px;
      height: 20px;
      background: white;
      border-radius: 50%;
      transition: transform 0.3s;
    }
    .theme-toggle.dark .toggle-knob {
      transform: translateX(20px);
    }
    main {
      padding: 80px 20px;
      max-width: 600px;
      margin: 0 auto;
    }
  `]
})
export class LayoutComponent {
  constructor(private auth: AuthService, private theme: ThemeService) {}

  logout() {
    this.auth.logout();
  }

  toggleTheme() {
    this.theme.toggle();
  }

  isDark(): boolean {
    return this.theme.isDarkMode();
  }
}
